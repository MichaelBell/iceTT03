# Project setup
PROJ      = iceTT03

# Files
FILES = ledscan.v big_7seg.v scanchain.v tt_scan_wrapper.v test_modules.v tt_top.v 
FILES += tt03-hovalaag/src/hovalaag_tiny_tapeout.v tt03-hovalaag/src/hovalaag_wrapper.v ring_oscillator.v tt03-hovalaag/src/decoder.v tt03-hovalaag/src/HovalaagCPU/Hovalaag.v
FILES += tt03-fifo/src/fifo_top.v tt03-fifo/src/ff_fifo.v tt03-fifo/src/delay_cells.v

.PHONY: iceFUN clean burn

iceFUN: $(FILES)
	# Synthesize using Yosys
	yosys -p "synth_ice40 -top tt_top -json $(PROJ).json" -DSIM -DICE40 $(FILES) > yosys.log
	@grep Warn yosys.log || true
	@grep Error yosys.log || true
	@echo

	# Place and route using nextpnr
	nextpnr-ice40 -r --hx8k --json $(PROJ).json --package cb132 --pre-pack timing.py --asc $(PROJ).asc --opt-timing --pcf iceFUN.pcf > nextpnr.log 2>& 1
	@grep Warn nextpnr.log || true
	@grep Error nextpnr.log || true
	@echo

	# Convert to bitstream using IcePack
	icepack $(PROJ).asc $(PROJ).bin

burn:
	iceFUNprog $(PROJ).bin

clean:
	rm *.asc *.bin *blif tt_scan_wrapper.v

tt_scan_wrapper.v: make_scanchain.py
	python3 make_scanchain.py
