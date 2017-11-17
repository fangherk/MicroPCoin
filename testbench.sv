module testbench();

	// Set the intial logic elements
	logic clk, block_load, message_load, done, sck, sdi, sdo;
	logic [255:0] hash, expected;
	logic [511:0] init_message, comb;
	logic [31:0] i;

	// Create the test device
	uPcoin dut(clk, sck, sdi, sdo, block_load, message_load, done);

	// Get the test cases 
	initial begin
		// Test case for 'abc'
		init_message  <= 512'h61626380000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000018;
		expected <= 256'hba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad;
	
		// Test case for ''
		// message  <= 512'h80000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000;
		// expected <= 256'he3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855;
	end 
	
	// generate clock and load signals
	initial
		forever begin
			clk = 1'b0; #5;
			clk = 1'b1; #5;
		end	
	initial begin
		i = 0;
		block_load   = 1'b1;
		message_load = 1'b1;
	end
	
	// Put the initial message in comb
	assign comb = init_message;
	
	// Test for the positive edge clock cycles
	always @(posedge clk) begin
		// Read in values and stop loading after 512 bits
		if (i == 512)begin
			block_load = 1'b0; 
			message_load = 1'b0;
		// Keep loading values if < 512 bits
		end 
		
		if (i < 512) begin
			#1; sdi = comb[511-i];
			#1; sck = 1; #5; sck = 0;
			i = i + 1;
			
		// After 512 bits of mesage, add the hash to sdo and check if it is valid.
		end else if (done && i < 768) begin
			#1; sck = 1;
			#1; hash[255-i] = sdo;
			#4; sck = 0;
			i = i + 1;
		
		end else if (i == 768) begin
			if (hash == expected)
				$display("Testbench ran successfully");
			else $display("Error: hash = %h, expected %h", hash, expected);
			$stop();
		end
		$display("i = ", i);
	end
	
	
endmodule
