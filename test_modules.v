module test_straight (
  input [7:0] io_in,
  output [7:0] io_out
);
    assign io_out = io_in;
endmodule

module test_invert (
  input [7:0] io_in,
  output [7:0] io_out
);
    assign io_out = ~io_in;
endmodule
