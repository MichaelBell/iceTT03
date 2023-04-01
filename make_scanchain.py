projects = [
    "test_straight",  # 000
    "test_invert",    # 001
    "test_straight",  # 002
    "test_invert",    # 003
    "test_straight",  # 004
    "test_invert",    # 005
    "test_straight",  # 006
    "test_invert",    # 007
    "test_straight",  # 008
    "MichaelBell_hovalaag",    # 009
    "test_straight",  # 010
    "test_invert",    # 011
    "test_straight",  # 012
    "test_invert",    # 013
    "test_straight",  # 014
    "test_invert",    # 015
]

f = open("tt_scan_wrapper.v", "w")

f.write("""
module tt_scan_wrapper (
        input scan_clk_in,
        input scan_data_in,
        input scan_latch_en,
        input scan_select,

        output scan_clk_out,
        output scan_data_out,
);

    // Setup for first scanchain block
    wire first_data_out = scan_data_in;
    wire first_scan_out = scan_select;
    wire first_latch_out = scan_latch_en;
""")

for i in range(len(projects)):
    project = projects[i]

    pfx = f"sw_{i:03d}"
    prev_pfx = f"sw_{i-1:03d}" if i > 0 else "first"
    f.write(f"""
        // [{i:03d}] {project}
        wire {pfx}_data_out, {pfx}_scan_out, {pfx}_latch_out;
        wire [7:0] {pfx}_module_data_in;
        wire [7:0] {pfx}_module_data_out;
        scanchain #(.NUM_IOS(8)) scanchain_{i:03d} (
            .clk_in          (scan_clk_in),
            .data_in         ({prev_pfx}_data_out),
            .scan_select_in  ({prev_pfx}_scan_out),
            .latch_enable_in ({prev_pfx}_latch_out),
            .data_out        ({pfx}_data_out),
            .scan_select_out ({pfx}_scan_out),
            .latch_enable_out({pfx}_latch_out),
            .module_data_in  ({pfx}_module_data_in),
            .module_data_out ({pfx}_module_data_out)
        );

        {project} project_{i:03d} (
            .io_in  ({pfx}_module_data_in),
            .io_out ({pfx}_module_data_out)
        );
    """)

f.write("""
endmodule
""")

f.close()