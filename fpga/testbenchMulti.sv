module testbench();

	// Set the intial logic elements
	logic clk, block_load, message_load, done, sck, sdi, sdo, load;
	logic [255:0] hash, expected;
	logic [511:0] init_message, init_message_2, comb, comb_2;
	logic [31:0] i;

	// Create the test device
	uPcoin dut(clk, sck, sdi, sdo, block_load, message_load, load, done);

	// Get the test cases 
	initial begin
		// Test case for 'abc'
		init_message  <=  512'h61626364656667686263646566676869636465666768696a6465666768696a6b65666768696a6b6c666768696a6b6c6d6768696a6b6c6d6e68696a6b6c6d6e6;
		init_message_2 <= 512'hf696a6b6c6d6e6f706a6b6c6d6e6f70716b6c6d6e6f7071726c6d6e6f707172736d6e6f70717273746e6f70717273747580000000000000000000000000000380;
		expected <= 256'hcf5b16a778af8380036ce59e7b0492370b249b11e8f07a51afac45037afee9d1;
		// Test case for ''
//		init_message  <= 512'h61626364656667686263646566676869636465666768696a6465666768696a6b65666768696a6b6c666768696a6b6c6d6768696a6b6c6d6e68696a6b6c6d6e6;
//		expected <= 256'hcf5b16a778af8380036ce59e7b0492370b249b11e8f07a51afac45037afee9d1;
		
		// Test case for 'abc'
		
//		init_message  <= 512'h61626380000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000018;
//		expected <= 256'hba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad;

	end 
	
	// generate clock and load signals
	initial
		forever begin
			clk = 1'b0; #5;
			clk = 1'b1; #5;
		end	
	initial begin
		i = 0;
		load = 1'b1;
		block_load   = 1'b1;
		message_load = 1'b1;
	end
	
	// Put the initial message in comb
	assign comb = init_message;
	assign comb_2 = init_message_2;
	
	// Test for the positive edge clock cycles
	always @(posedge clk) begin
		// Read in values and stop loading after 512 bits
		if (i == 512)begin
			load = 1'b0;
			block_load = 1'b0; 
			#10000;
			block_load   = 1'b1;
		end else if (i == 1024)begin
			block_load = 1'b0; 
			#10000;
			message_load = 1'b0;
		end

		if (i < 512) begin
			#1; sdi = comb[511-i];
			#1; sck = 1; #5; sck = 0;
			i = i + 1;
		end else if (i < 1024) begin
			#1; sdi = comb_2[1023-i];
			#1; sck = 1; #5; sck = 0;
			i = i + 1;
		end else if (done && i < 1280) begin
			#1; sck = 1;
			#1; hash[1279-i] = sdo;
			#4; sck = 0;
			i = i + 1;
		
		end else if (i == 1280) begin
			if (hash == expected)
				$display("Testbench ran successfully");
			else $display("Error: hash = %h, expected %h", hash, expected);
			$stop();
		end
		$display("i = ", i);
	end
	
//	always @(posedge clk) begin
//		// Read in values and stop loading after 512 bits
//		if (i == 512)begin
//			block_load = 1'b0; 
//			message_load = 1'b0;
//		// Keep loading values if < 512 bits
//		end 
//	
//		if (i < 512) begin
//			#1; sdi = comb[511-i];
//			#1; sck = 1; #5; sck = 0;
//			i = i + 1;
//			
//		// After 512 bits of mesage, add the hash to sdo and check if it is valid.
//		end else if (done && i < 768) begin
//			#1; sck = 1;
//			#1; hash[767-i] = sdo;
//			#4; sck = 0;
//			i = i + 1;
//		
//		end else if (i == 768) begin
//			if (hash == expected)
//				$display("Testbench ran successfully");
//			else $display("Error: hash = %h, expected %h", hash, expected);
//			$stop();
//		end
//		$display("i = ", i);
//	end
//	
	
endmodule
