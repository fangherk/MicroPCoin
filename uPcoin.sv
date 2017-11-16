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

module uPcoin(input logic clk);
	logic [31:0] x,y,z,w;
	SIGMA0 a(32'h00000000, x);
	SIGMA1 b(32'h00000000, y);
	sigma0 c(32'h00000000, z);
	sigma1 d(32'h00000000, w);
endmodule 
