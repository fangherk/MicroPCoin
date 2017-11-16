/*  
 *  Ch(x,y,z) function 
 *  Defined by FIPS 180-4 on Page 10 Section 4.1.2
 */
module Ch(input logic  [31:0] x, y, z,
          output logic [31:0] out);
	assign out = (x & y) ^ (~x & z); 
endmodule
			 
			 
/*  
 *  Maj(x,y,z) function 
 *  Defined by FIPS 180-4 on Page 10 Section 4.1.2
 */
module Maj(input logic  [31:0] x, y, z,
           output logic [31:0] out);
	assign out = (x & y) ^ (x & z) ^ (y & z);
endmodule

/*  
 *  SIGMA_0^{(256)}(x,y,z) function 
 *  Defined by FIPS 180-4 on Page 10 Section 4.1.2
 */
module SIGMA0(input logic  [31:0] x,
              output logic [31:0] out);
	logic [31:0] ROTR2, ROTR13, ROTR22;
	assign ROTR2  = (x >>  2) | (x << 30);
	assign ROTR13 = (x >> 13) | (x << 19);
	assign ROTR22 = (x >> 22) | (x << 10);
 	assign out = ROTR2 ^ ROTR13 ^ ROTR22;
endmodule

/*  
 *  SIGMA_1^{(256)}(x,y,z) function 
 *  Defined by FIPS 180-4 on Page 10 Section 4.1.2
 */
module SIGMA1(input logic  [31:0] x,
              output logic [31:0] out);
	logic [31:0] ROTR6, ROTR11, ROTR25;
	assign ROTR6  = (x >>  6) | (x << 26);
	assign ROTR11 = (x >> 11) | (x << 21);
	assign ROTR25 = (x >> 25) | (x << 7);
 	assign out = ROTR6 ^ ROTR11 ^ ROTR25;
endmodule

/*  
 *  sigma_0^{(256)}(x,y,z) function 
 *  Defined by FIPS 180-4 on Page 10 Section 4.1.2
 */
module sigma0(input logic  [31:0] x,
              output logic [31:0] out);
	logic [31:0] ROTR7, ROTR18, SHR3;
	assign ROTR7  = (x >>  7) | (x << 25);
	assign ROTR18 = (x >> 18) | (x << 14);
	assign SHR3   = (x >>  3);
 	assign out = ROTR7 ^ ROTR18 ^ SHR3;
endmodule

/*  
 *  sigma_1^{(256)}(x,y,z) function 
 *  Defined by FIPS 180-4 on Page 10 Section 4.1.2
 */
module sigma1(input logic  [31:0] x,
              output logic [31:0] out);
	logic [31:0] ROTR17, ROTR19, SHR10;
	assign ROTR17 = (x >> 17) | (x << 15);
	assign ROTR19 = (x >> 19) | (x << 13);
	assign SHR10  = (x >> 10);
 	assign out = ROTR17 ^ ROTR19 ^ SHR10;
endmodule

module uPcoin(input logic  clk,
				  input logic  sck,
				  input logic  sdi,
				  output logic sdo,
				  input logic  load,
				  output logic done);
				  
	logic [31:0] x,y,z,w;
	logic[31:0] H0, H1, H2, H3, H4, H5, H6, H7;
	SIGMA0 a(32'h00000000, x);
	SIGMA1 b(32'h00000000, y);
	sigma0 c(32'h00000000, z);
	sigma1 d(32'h00000000, w);
	
	uPcoin_core core(clk, block_load, message_load, message, done);
	
endmodule 





module uPcoin_core(input logic clk, 
						 input logic block_load,
						 input logic message_load,
						 input logic [511:0] block,
						 output logic done,
						 output logic [255:0] hash);
						 
	// Set two variables for the state transition
	logic falling_edge_block, falling_edge_message;
	typedef enum logic [3:0]{preProcessing, intermediateStep, waiting, doneHashing} statetype;
	statetype state, nextstate;
	
	
	always_ff @(posedge clk, posedge message_load)
		if (message_load) state <= preProcessing;
		else              state <= nextstate;
	
	always_ff @(posedge clk, negedge block_load)
		if(~block_load) falling_edge_block <= 1;
		else            falling_edge_block <= 0;
		
	always_comb
		case(state) 
			preProcessing:
				if(falling_edge_block)           nextstate = intermediateStep;
				else            		            nextstate = preProcessing;
			intermediateStep:		               nextstate = waiting;
			waiting:
				if(message_load == 0) 	         nextstate = doneHashing;
				else if(falling_edge_block == 1) nextstate = intermediateStep;
				else 									   nextstate = waiting;
			doneHashing:				            nextstate = doneHashing;			
		endcase
		
	assign done = (state==doneHashing);
	
endmodule
