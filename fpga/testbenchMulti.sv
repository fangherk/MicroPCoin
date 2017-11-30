module testbench();

	// Set the intial logic elements
	logic clk, block_load, message_load, done, sck, sdi, sdo, load;
	logic [255:0] hash, expected;
	logic [511:0] init_message, init_message_2, init_message_3, comb, comb_2, comb_3;
	logic [31:0] i;
	logic inputReady;
	// Create the test device
	uPcoin dut(clk, sck, sdi, sdo, block_load, message_load, load, inputReady, done);

	// Get the test cases 
	initial begin
		// Test case for 'abc'
		init_message  <=  512'h61616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161;
		init_message_2<=  512'h61616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161618000000000000000;
		init_message_3<=  512'h000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000003c0;
		expected      <=  256'h2f3d335432c70b580af0e8e1b3674a7c020d683aa5f73aaaedfdc55af904c21c;
//		init_message  <=  512'h61626364656667686263646566676869636465666768696a6465666768696a6b65666768696a6b6c666768696a6b6c6d6768696a6b6c6d6e68696a6b6c6d6e6f;//
//		init_message_2 <= 512'h696a6b6c6d6e6f706a6b6c6d6e6f70716b6c6d6e6f7071726c6d6e6f707172736d6e6f70717273746e6f70717273747580000000000000000000000000000380;
//		expected <= 256'hcf5b16a778af8380036ce59e7b0492370b249b11e8f07a51afac45037afee9d1;
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
	assign comb_3 = init_message_3;
	
	// Test for the positive edge clock cycles
	always @(posedge clk) begin
		// Read in values and stop loading after 512 bits
		if (i == 512 && ~inputReady)begin
			block_load = 1'b0; 
			load = 1'b0;
		end else if (i == 512 && inputReady)begin
			block_load = 1'b1;
			#1; sdi = comb[1023-i];
			#1; sck = 1; #5; sck = 0;
			i = i + 1;
		end else if (i == 1024 && ~inputReady)begin
			block_load = 1'b0; 
		end else if (i == 1024 && inputReady)begin
			block_load = 1'b1;
			#1; sdi = comb_2[1535-i];
			#1; sck = 1; #5; sck = 0;
			i = i + 1;
		end else if (i == 1536) begin
			block_load = 1'b0;
			message_load = 1'b0;
		end
		
		  

		if (i < 512) begin
			#1; sdi = comb[511-i];
			#1; sck = 1; #5; sck = 0;
			i = i + 1;
		end else if (512 < i && i < 1024) begin
			#1; sdi = comb_2[1023-i];
			#1; sck = 1; #5; sck = 0;
			i = i + 1;
		end else if (1024 < i && i < 1536) begin
			#1; sdi = comb_3[1535-i];
			#1; sck = 1; #5; sck = 0;
			i = i + 1;
		end else if (done && i < 1792) begin
			#1; sck = 1;
			#1; hash[1791-i] = sdo;
			#4; sck = 0;
			i = i + 1;
		
		end else if (i == 1792) begin
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
