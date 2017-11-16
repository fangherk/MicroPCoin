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
	logic falling_edge_block, rising_edge_block, falling_edge_message;
	logic [5:0] roundNumber;
	logic [255:0] intermediate_hash;
	logic [31:0] a, b, c, d, e, f, g, h;
	logic [31:0] new_a, new_b, new_c, new_d, new_e, new_f, new_g, new_h;
	logic [31:0] W[0:63];
	logic [31:0] K;
	typedef enum logic [5:0]{preProcessing, intermediateStep, waiting, thirdStep, doneHashing} statetype;
	statetype state, nextstate;
	
	
	always_ff @(posedge clk, posedge message_load)
		if (message_load) state <= preProcessing;
		else begin
			state <= nextstate;
			if(nextstate == waiting) begin
				intermediate_hash <= {new_a, new_b, new_c, new_d, new_e, new_f, new_g, new_h} + intermediate_hash;
			end else begin
				intermediate_hash <= intermediate_hash;
			end
		end
		
	/*always_ff @(negedge clk)
		if (!block_load) edge_block <= 0;
		else edge_block <= edge_block;*/
	
	always_ff @(posedge clk, negedge block_load)
		if(~block_load) falling_edge_block <= 1;
		else            falling_edge_block <= 0;
		
	always_ff @(posedge clk)
		if (state == intermediateStep) roundNumber <=0;
		else  								 roundNumber <= roundNumber + 1;
		
	always_comb
		case(state) 
			preProcessing:
				if(falling_edge_block)           nextstate = intermediateStep;
				else            		            nextstate = preProcessing;
			intermediateStep:		               nextstate = thirdStep;
			thirdStep:
				if(roundNumber == 63) 				nextstate = waiting;
				else										nextstate = thirdStep;
			waiting:
				if(message_load == 0) 	         nextstate = doneHashing;
				else if(falling_edge_block == 1) nextstate = intermediateStep;
				else 									   nextstate = waiting;
			doneHashing:				            nextstate = doneHashing;			
		endcase
		
	
		
	getConstant kHelper(roundNumber, K);
	prepareMessage ppM(block, W);
	thirdComp(a,b,c,d,e,f,g,h,W[roundNumber],K, new_a, new_b, new_c, new_d, new_e, new_f, new_g, new_h);
	
	
	assign {a,b,c,d,e,f,g,h} = intermediate_hash;
	assign done = (state==doneHashing);
	
endmodule


module getConstant(input logic [5:0] roundNumber,
					output logic [31:0] K);
					
		logic [31:0] constant[0:63];

		initial   $readmemh("sha256constants.txt", constant);
		assign K = constant[roundNumber]; 
endmodule

module thirdComp(input logic  [31:0] a,b,c,d,e,f,g,h,
					  input logic  [31:0] W, K, 
					  output logic [31:0] new_a, new_b, new_c, new_d, new_e, new_f, new_g, new_h);
							
	logic [31:0] T1, T2;
	logic [31:0] tempSigma1, tempSigma0, tempCh, tempMaj;
	
	SIGMA0 sigma0_temp(a, tempSigma0);
	SIGMA1 sigma1_temp(e, tempSigma1);
	Maj    maj_temp(a,b,c, tempMaj);
	Ch     ch_temp(e,f,g, tempCh);
	
	assign T1 = h + tempSigma1 + tempCh + K + W;
	assign T2 = tempSigma0 + tempMaj;
	assign new_h = g;
	assign new_g = f;
	assign new_f = e;
	assign new_e = d + T1;
	assign new_d = c;
	assign new_c = b;
	assign new_b = a;
	assign new_a = T1 + T2;

endmodule


module prepareMessage(input logic [511:0] block,
							 output logic [31:0] W[0:63]);
	logic [31:0] output_sigma0[16:63];
	logic [31:0] output_sigma1[16:63];
	
	assign W[ 0] = block[ 31:  0];
	assign W[ 1] = block[ 63: 32];
	assign W[ 2] = block[ 95: 64];
	assign W[ 3] = block[127: 96];
	assign W[ 4] = block[159:128];
	assign W[ 5] = block[191:160];
	assign W[ 6] = block[223:192];
	assign W[ 7] = block[255:224];
	assign W[ 8] = block[287:256];
	assign W[ 9] = block[319:288];
	assign W[10] = block[351:320];
	assign W[11] = block[383:352];
	assign W[12] = block[415:384];
	assign W[13] = block[447:416];
	assign W[14] = block[479:448];
	assign W[15] = block[511:480];
	
	/* W[16] */
	sigma0 sigma0_16(W[ 1], output_sigma0[16]);
	sigma1 sigma1_16(W[14], output_sigma1[16]);
	assign W[16] = output_sigma1[16] + W[ 9] + output_sigma0[16] + W[ 0];

	/* W[17] */
	sigma0 sigma0_17(W[ 2], output_sigma0[17]);
	sigma1 sigma1_17(W[15], output_sigma1[17]);
	assign W[17] = output_sigma1[17] + W[10] + output_sigma0[17] + W[ 1];

	/* W[18] */
	sigma0 sigma0_18(W[ 3], output_sigma0[18]);
	sigma1 sigma1_18(W[16], output_sigma1[18]);
	assign W[18] = output_sigma1[18] + W[11] + output_sigma0[18] + W[ 2];

	/* W[19] */
	sigma0 sigma0_19(W[ 4], output_sigma0[19]);
	sigma1 sigma1_19(W[17], output_sigma1[19]);
	assign W[19] = output_sigma1[19] + W[12] + output_sigma0[19] + W[ 3];

	/* W[20] */
	sigma0 sigma0_20(W[ 5], output_sigma0[20]);
	sigma1 sigma1_20(W[18], output_sigma1[20]);
	assign W[20] = output_sigma1[20] + W[13] + output_sigma0[20] + W[ 4];

	/* W[21] */
	sigma0 sigma0_21(W[ 6], output_sigma0[21]);
	sigma1 sigma1_21(W[19], output_sigma1[21]);
	assign W[21] = output_sigma1[21] + W[14] + output_sigma0[21] + W[ 5];

	/* W[22] */
	sigma0 sigma0_22(W[ 7], output_sigma0[22]);
	sigma1 sigma1_22(W[20], output_sigma1[22]);
	assign W[22] = output_sigma1[22] + W[15] + output_sigma0[22] + W[ 6];

	/* W[23] */
	sigma0 sigma0_23(W[ 8], output_sigma0[23]);
	sigma1 sigma1_23(W[21], output_sigma1[23]);
	assign W[23] = output_sigma1[23] + W[16] + output_sigma0[23] + W[ 7];

	/* W[24] */
	sigma0 sigma0_24(W[ 9], output_sigma0[24]);
	sigma1 sigma1_24(W[22], output_sigma1[24]);
	assign W[24] = output_sigma1[24] + W[17] + output_sigma0[24] + W[ 8];

	/* W[25] */
	sigma0 sigma0_25(W[10], output_sigma0[25]);
	sigma1 sigma1_25(W[23], output_sigma1[25]);
	assign W[25] = output_sigma1[25] + W[18] + output_sigma0[25] + W[ 9];

	/* W[26] */
	sigma0 sigma0_26(W[11], output_sigma0[26]);
	sigma1 sigma1_26(W[24], output_sigma1[26]);
	assign W[26] = output_sigma1[26] + W[19] + output_sigma0[26] + W[10];

	/* W[27] */
	sigma0 sigma0_27(W[12], output_sigma0[27]);
	sigma1 sigma1_27(W[25], output_sigma1[27]);
	assign W[27] = output_sigma1[27] + W[20] + output_sigma0[27] + W[11];

	/* W[28] */
	sigma0 sigma0_28(W[13], output_sigma0[28]);
	sigma1 sigma1_28(W[26], output_sigma1[28]);
	assign W[28] = output_sigma1[28] + W[21] + output_sigma0[28] + W[12];

	/* W[29] */
	sigma0 sigma0_29(W[14], output_sigma0[29]);
	sigma1 sigma1_29(W[27], output_sigma1[29]);
	assign W[29] = output_sigma1[29] + W[22] + output_sigma0[29] + W[13];

	/* W[30] */
	sigma0 sigma0_30(W[15], output_sigma0[30]);
	sigma1 sigma1_30(W[28], output_sigma1[30]);
	assign W[30] = output_sigma1[30] + W[23] + output_sigma0[30] + W[14];

	/* W[31] */
	sigma0 sigma0_31(W[16], output_sigma0[31]);
	sigma1 sigma1_31(W[29], output_sigma1[31]);
	assign W[31] = output_sigma1[31] + W[24] + output_sigma0[31] + W[15];

	/* W[32] */
	sigma0 sigma0_32(W[17], output_sigma0[32]);
	sigma1 sigma1_32(W[30], output_sigma1[32]);
	assign W[32] = output_sigma1[32] + W[25] + output_sigma0[32] + W[16];

	/* W[33] */
	sigma0 sigma0_33(W[18], output_sigma0[33]);
	sigma1 sigma1_33(W[31], output_sigma1[33]);
	assign W[33] = output_sigma1[33] + W[26] + output_sigma0[33] + W[17];

	/* W[34] */
	sigma0 sigma0_34(W[19], output_sigma0[34]);
	sigma1 sigma1_34(W[32], output_sigma1[34]);
	assign W[34] = output_sigma1[34] + W[27] + output_sigma0[34] + W[18];

	/* W[35] */
	sigma0 sigma0_35(W[20], output_sigma0[35]);
	sigma1 sigma1_35(W[33], output_sigma1[35]);
	assign W[35] = output_sigma1[35] + W[28] + output_sigma0[35] + W[19];

	/* W[36] */
	sigma0 sigma0_36(W[21], output_sigma0[36]);
	sigma1 sigma1_36(W[34], output_sigma1[36]);
	assign W[36] = output_sigma1[36] + W[29] + output_sigma0[36] + W[20];

	/* W[37] */
	sigma0 sigma0_37(W[22], output_sigma0[37]);
	sigma1 sigma1_37(W[35], output_sigma1[37]);
	assign W[37] = output_sigma1[37] + W[30] + output_sigma0[37] + W[21];

	/* W[38] */
	sigma0 sigma0_38(W[23], output_sigma0[38]);
	sigma1 sigma1_38(W[36], output_sigma1[38]);
	assign W[38] = output_sigma1[38] + W[31] + output_sigma0[38] + W[22];

	/* W[39] */
	sigma0 sigma0_39(W[24], output_sigma0[39]);
	sigma1 sigma1_39(W[37], output_sigma1[39]);
	assign W[39] = output_sigma1[39] + W[32] + output_sigma0[39] + W[23];

	/* W[40] */
	sigma0 sigma0_40(W[25], output_sigma0[40]);
	sigma1 sigma1_40(W[38], output_sigma1[40]);
	assign W[40] = output_sigma1[40] + W[33] + output_sigma0[40] + W[24];

	/* W[41] */
	sigma0 sigma0_41(W[26], output_sigma0[41]);
	sigma1 sigma1_41(W[39], output_sigma1[41]);
	assign W[41] = output_sigma1[41] + W[34] + output_sigma0[41] + W[25];

	/* W[42] */
	sigma0 sigma0_42(W[27], output_sigma0[42]);
	sigma1 sigma1_42(W[40], output_sigma1[42]);
	assign W[42] = output_sigma1[42] + W[35] + output_sigma0[42] + W[26];

	/* W[43] */
	sigma0 sigma0_43(W[28], output_sigma0[43]);
	sigma1 sigma1_43(W[41], output_sigma1[43]);
	assign W[43] = output_sigma1[43] + W[36] + output_sigma0[43] + W[27];

	/* W[44] */
	sigma0 sigma0_44(W[29], output_sigma0[44]);
	sigma1 sigma1_44(W[42], output_sigma1[44]);
	assign W[44] = output_sigma1[44] + W[37] + output_sigma0[44] + W[28];

	/* W[45] */
	sigma0 sigma0_45(W[30], output_sigma0[45]);
	sigma1 sigma1_45(W[43], output_sigma1[45]);
	assign W[45] = output_sigma1[45] + W[38] + output_sigma0[45] + W[29];

	/* W[46] */
	sigma0 sigma0_46(W[31], output_sigma0[46]);
	sigma1 sigma1_46(W[44], output_sigma1[46]);
	assign W[46] = output_sigma1[46] + W[39] + output_sigma0[46] + W[30];

	/* W[47] */
	sigma0 sigma0_47(W[32], output_sigma0[47]);
	sigma1 sigma1_47(W[45], output_sigma1[47]);
	assign W[47] = output_sigma1[47] + W[40] + output_sigma0[47] + W[31];

	/* W[48] */
	sigma0 sigma0_48(W[33], output_sigma0[48]);
	sigma1 sigma1_48(W[46], output_sigma1[48]);
	assign W[48] = output_sigma1[48] + W[41] + output_sigma0[48] + W[32];

	/* W[49] */
	sigma0 sigma0_49(W[34], output_sigma0[49]);
	sigma1 sigma1_49(W[47], output_sigma1[49]);
	assign W[49] = output_sigma1[49] + W[42] + output_sigma0[49] + W[33];

	/* W[50] */
	sigma0 sigma0_50(W[35], output_sigma0[50]);
	sigma1 sigma1_50(W[48], output_sigma1[50]);
	assign W[50] = output_sigma1[50] + W[43] + output_sigma0[50] + W[34];

	/* W[51] */
	sigma0 sigma0_51(W[36], output_sigma0[51]);
	sigma1 sigma1_51(W[49], output_sigma1[51]);
	assign W[51] = output_sigma1[51] + W[44] + output_sigma0[51] + W[35];

	/* W[52] */
	sigma0 sigma0_52(W[37], output_sigma0[52]);
	sigma1 sigma1_52(W[50], output_sigma1[52]);
	assign W[52] = output_sigma1[52] + W[45] + output_sigma0[52] + W[36];

	/* W[53] */
	sigma0 sigma0_53(W[38], output_sigma0[53]);
	sigma1 sigma1_53(W[51], output_sigma1[53]);
	assign W[53] = output_sigma1[53] + W[46] + output_sigma0[53] + W[37];

	/* W[54] */
	sigma0 sigma0_54(W[39], output_sigma0[54]);
	sigma1 sigma1_54(W[52], output_sigma1[54]);
	assign W[54] = output_sigma1[54] + W[47] + output_sigma0[54] + W[38];

	/* W[55] */
	sigma0 sigma0_55(W[40], output_sigma0[55]);
	sigma1 sigma1_55(W[53], output_sigma1[55]);
	assign W[55] = output_sigma1[55] + W[48] + output_sigma0[55] + W[39];

	/* W[56] */
	sigma0 sigma0_56(W[41], output_sigma0[56]);
	sigma1 sigma1_56(W[54], output_sigma1[56]);
	assign W[56] = output_sigma1[56] + W[49] + output_sigma0[56] + W[40];

	/* W[57] */
	sigma0 sigma0_57(W[42], output_sigma0[57]);
	sigma1 sigma1_57(W[55], output_sigma1[57]);
	assign W[57] = output_sigma1[57] + W[50] + output_sigma0[57] + W[41];

	/* W[58] */
	sigma0 sigma0_58(W[43], output_sigma0[58]);
	sigma1 sigma1_58(W[56], output_sigma1[58]);
	assign W[58] = output_sigma1[58] + W[51] + output_sigma0[58] + W[42];

	/* W[59] */
	sigma0 sigma0_59(W[44], output_sigma0[59]);
	sigma1 sigma1_59(W[57], output_sigma1[59]);
	assign W[59] = output_sigma1[59] + W[52] + output_sigma0[59] + W[43];

	/* W[60] */
	sigma0 sigma0_60(W[45], output_sigma0[60]);
	sigma1 sigma1_60(W[58], output_sigma1[60]);
	assign W[60] = output_sigma1[60] + W[53] + output_sigma0[60] + W[44];

	/* W[61] */
	sigma0 sigma0_61(W[46], output_sigma0[61]);
	sigma1 sigma1_61(W[59], output_sigma1[61]);
	assign W[61] = output_sigma1[61] + W[54] + output_sigma0[61] + W[45];

	/* W[62] */
	sigma0 sigma0_62(W[47], output_sigma0[62]);
	sigma1 sigma1_62(W[60], output_sigma1[62]);
	assign W[62] = output_sigma1[62] + W[55] + output_sigma0[62] + W[46];

	/* W[63] */
	sigma0 sigma0_63(W[48], output_sigma0[63]);
	sigma1 sigma1_63(W[61], output_sigma1[63]);
	assign W[63] = output_sigma1[63] + W[56] + output_sigma0[63] + W[47];
endmodule
