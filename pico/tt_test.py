import time
import random
from machine import Pin

from tt_pio import TT_PIO
from tt_hova_fifo import TT_Hova

# Pin mapping - names from FPGA's point of view
clk = Pin(12, Pin.OUT)
data_in = Pin(13, Pin.OUT)
latch_en = Pin(11, Pin.OUT)
scan_select = Pin(10, Pin.OUT)

clk_out = Pin(9, Pin.IN)
data_out = Pin(8, Pin.IN)

seg_latch = Pin(7, Pin.OUT)

clk.off()
data_in.off()
latch_en.off()
scan_select.off()
seg_latch.off()

chain_len = 34

# Test pattern
if False:
    for i in range(256+chain_len+1):
        # Send i % 256
        d = i & 0xFF
        d_out = 0
        
        # Data goes MSB first
        for j in range(8):
            data_in.value(d >> 7)
            d_out = (d_out << 1) | data_out.value()
            d = (d & 0x7F) << 1
            clk.on()
            clk.off()

        print(i, d_out)
        time.sleep(0.01)

tt = TT_PIO(0, data_in, data_out, scan_select)

@micropython.native
def send_byte(d, read=False, latch=False, scan=False):
    return tt.send_byte_blocking(d, latch, scan)
    
@micropython.native
def send_bytes(d, read=False, latch=False, scan=False):
    return tt.send_bytes_blocking(d, latch, scan)
    
@micropython.native
def send_zeroes(num, read=False, latch=False, scan=False):
    return tt.send_zeroes_blocking(num, latch, scan)
    
def old_send_byte(d, read=False, latch=False, scan=False):
    d_out = 0
    
    if scan:
        scan_select.on()
        clk.on()
        clk.off()
        scan_select.off()
        #time.sleep(1)
    
    # Data goes MSB first
    for j in range(8):
        data_in.value(d >> 7)
        d_out = (d_out << 1) | data_out.value()
        d = (d & 0x7F) << 1
        if j == 7 and latch:
            latch_en.on()
        clk.on()
        clk.off()

    #if latch:
    #    time.sleep(1)
    latch_en.off()

    return d_out

@micropython.native
def clock_byte(d):
    tt.send_bytes_blocking(((d & 0xFE), (d | 1)))

# Test invert
if True:
    for i in range(chain_len):
        send_byte(i)

    send_byte(0xAA)
    send_byte(0, latch=True)
    #send_byte(0, scan=True)
    #for i in range(chain_len-3):
    #    print("{:02x}".format(send_byte(0, read=True)))
    #    
    #print("{:02x}".format(send_byte(0, read=True)))
    print("{:02x} (expected 55)".format(send_zeroes(chain_len-1, read=True, scan=True)))

# Test Hovalaag
hova = TT_Hova(tt, seg_latch)

#NOP
hova.execute_instr(0)
hova.execute_instr(0)
hova.execute_instr(0)

# Repeatedly add one to A
if False:
    for i in range(50):
        #               ALU- A- B- C- D W- F- PC O I X K----- L-----
        hova.execute_instr(0b0101_01_11_00_0_01_00_01_1_0_0_000001_000000) # A=A+B,B=1,W=A+B,OUT1=W,JMP 0
        time.sleep(0.1)
    
# Example loop 1:
example_loop1 = [
    0b0000_11_00_00_0_00_00_00_0_0_0_000000_000000,  # A=IN1
    0b0000_00_10_00_0_00_00_00_0_0_0_000000_000000,  # B=A
    0b0101_01_01_00_0_00_00_00_0_0_0_000000_000000,  # A=B=A+B
    0b0101_01_01_00_0_00_00_00_0_0_0_000000_000000,  # A=B=A+B
    0b0101_00_00_00_0_01_00_00_0_0_0_000000_000000,  # W=A+B
    0b0000_00_00_00_0_00_00_00_1_0_0_000000_000000,  # OUT1=W
    0b0000_00_00_00_0_00_00_01_0_0_0_000000_000000,  # JMP 0
]

if True:
    print("Running example loop 1")
    NUM_VALUES = 14
    in1 = [random.randint(-2048 // 8,2047 // 8) for x in range(NUM_VALUES)]
    print(in1)
    correct = [8*x for x in in1]
    start = time.ticks_ms()
    result = hova.run_program(example_loop1, in1, NUM_VALUES)
    runtime = time.ticks_diff(time.ticks_ms(), start)
    for i in range(NUM_VALUES):
        if result[i] != correct[i]:
            print("Got {}, expected {}".format(result[i], correct[i]))
    print(result)
    print("Took {}ms".format(runtime))
    print()

# Loop via IN2
in2_test = [
#     ALU- A- B- C- D W- F- PC O I X K----- L-----
    0b0000_11_00_00_0_00_00_00_0_0_0_000000_000000,  # A=IN1
    0b0000_00_00_00_0_10_00_00_0_0_0_000000_000000,  # W=A
    0b0000_00_00_00_0_00_00_00_1_1_0_000000_000000,  # OUT2=W
    0b0000_00_00_00_0_00_00_00_0_0_0_000000_000000,  # NOP
    0b0000_11_00_00_0_00_00_00_0_1_0_000000_000000,  # A=IN2
    0b0000_00_00_00_0_10_00_00_0_0_0_000000_000000,  # W=A
    0b0000_00_00_00_0_00_00_01_1_0_0_000000_000000,  # OUT1=W, JMP 0
]

print("Running test of IN2")
NUM_VALUES = 14
in1 = [random.randint(0,2047) for x in range(NUM_VALUES)]
print(in1)
correct = [x for x in in1]
start = time.ticks_ms()
result = hova.run_program(in2_test, in1, NUM_VALUES)
runtime = time.ticks_diff(time.ticks_ms(), start)
for i in range(NUM_VALUES):
    if result[i] != correct[i]:
        print("Got {}, expected {}".format(result[i], correct[i]))
print(result)
print("Took {}ms".format(runtime))
print()
