`default_nettype none

module scanchain (
    input wire clk_in,
    input wire data_in,
    input wire scan_select_in,
    input wire latch_enable_in,
    output wire clk_out,
    output wire data_out,
    output wire scan_select_out,
    output wire latch_enable_out,

    // io, names from point of view of the user module
    input wire [NUM_IOS-1:0] module_data_out,
    output reg [NUM_IOS-1:0] module_data_in
    );

    parameter NUM_IOS = 8;

    wire clk = clk_in;
    reg [NUM_IOS-1:0] scan_data_out;   // output of the each scan chain flop
    wire [NUM_IOS-1:0] scan_data_in;    // input of each scan chain flop

    assign clk_out = clk;
    assign data_out = scan_data_out[NUM_IOS-1];
    assign scan_select_out = scan_select_in;
    assign latch_enable_out = latch_enable_in;

    // scan chain - link all the flops, with data coming from data_in
    assign scan_data_in = {scan_data_out[NUM_IOS-2:0], data_in};

    always @(posedge clk)
        scan_data_out <= scan_select_in ? module_data_out : scan_data_in;

    // No latches so can't emulate the TT version precisely
    //always @(latch_enable_in or scan_data_in)
    //    if (latch_enable_in)
    //        module_data_in <= scan_data_out;
    
    // Instead must latch on the clock that moves the data into place
    // This is one clock prior to when you would do it with TT (and there you don't clock when latching)
    always @(posedge clk)
        if (latch_enable_in)
            module_data_in <= scan_data_in;

endmodule
