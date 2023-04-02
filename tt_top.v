/* Copyright (C) 2023 Michael Bell

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
*/

parameter CLK_BIT=19;

module tt_top (
        input clk12MHz,
        input button1,
        input button2,
        input button3,
        input button4,

        input scan_clk_in,
        input scan_data_in,
        input scan_latch_en,
        input scan_select,

        output scan_clk_out,
        output scan_data_out,

        input seg_latch,

        output led1,
        output led2,
        output led3,
        output led4,
        output led5,
        output led6,
        output led7,
        output led8,
        output lcol1,
        output lcol2,
        output lcol3,
        output lcol4
        );

    //wire [7:0] tapped_data_in;
    //wire [7:0] tapped_data_out;
    //reg [7:0] tapped_data_out_reg;

    tt_scan_wrapper wrapper(
        .scan_clk_in(scan_clk_in),
        .scan_data_in(scan_data_in),
        .scan_latch_en(scan_latch_en),
        .scan_select(scan_select),
        .scan_clk_out(scan_clk_out),
        .scan_data_out(scan_data_out),

        //.module_data_in_tap(tapped_data_in),
        //.module_data_out_tap(tapped_data_out),
    );

    reg [7:0] last_scan_data;
    reg [7:0] out_as_7seg = 0;

    always @(posedge scan_clk_in) begin
        last_scan_data[7:1] <= last_scan_data[6:0];
        last_scan_data[0] <= scan_data_out;

        //if (scan_select) begin
        //    tapped_data_out_reg <= tapped_data_out;
        //end
    end

    always @(posedge clk12MHz)
        if (seg_latch) begin
            out_as_7seg <= last_scan_data;
        end

    wire [7:0] leds1_7seg;
    wire [7:0] leds2_7seg;
    wire [7:0] leds3_7seg;
    wire [7:0] leds4_7seg;
    big7_seg seg_decode(out_as_7seg, leds1_7seg, leds2_7seg, leds3_7seg, leds4_7seg);

    // map the output of ledscan to the port pins
    wire [7:0] leds_out;
    wire [3:0] lcol;
    assign { led8, led7, led6, led5, led4, led3, led2, led1 } = leds_out[7:0];
    assign { lcol4, lcol3, lcol2, lcol1 } = lcol[3:0];

    LedScan scan (
                .clk12MHz(clk12MHz),
                .leds1(button1 ? last_scan_data : leds1_7seg),
                .leds2(button1 ? /*tapped_data_in*/ 8'h00 : leds2_7seg),
                .leds3(button1 ? /*tapped_data_out_reg*/ 8'h00 : leds3_7seg),
                .leds4(button1 ? 8'h00          : leds4_7seg),
                .leds(leds_out),
                .lcol(lcol)
        );

endmodule