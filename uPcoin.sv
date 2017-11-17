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
				  input logic  block_load,
				  input logic  message_load,
				  output logic done);
				  
	logic [255:0] hash;
	logic [511:0] message;
	
	uPcoin_spi  spi(sck, sdi, sdo, done, message, hash);
	uPcoin_core core(clk, block_load, message_load, message, done, hash);
	
endmodule 



module uPcoin_spi(input  logic sck, 
               input  logic sdi,
               output logic sdo,
               input  logic done,
               output logic [511:0] message,
               input  logic [255:0] hash);

    logic         sdodelayed, wasdone;
    logic [255:0] hashcaptured;
               
    always_ff @(posedge sck)
        if (!wasdone)  {hashcaptured, message} = {hash, message[510:0], sdi};
        else           {hashcaptured, message} = {hashcaptured[254:0], message, sdi}; 
    
    // sdo should change on the negative edge of sck
    always_ff @(negedge sck) begin
        wasdone = done;
        sdodelayed = hashcaptured[254];
    end
    
    // when done is first asserted, shift out msb before clock edge
    assign sdo = (done & !wasdone) ? hash[255] : sdodelayed;
endmodule




module uPcoin_core(input logic clk, 
						 input logic block_load,
						 input logic message_load,
						 input logic [511:0] block,
						 output logic done,
						 output logic [255:0] hash);
						 
	// Set two variables for the state transition
	logic falling_edge_block, rising_edge_block, falling_edge_message;
	logic [5:0] roundNumber, messageScheduleCounter;
	logic [3:0] counter2;
	logic [255:0] intermediate_hash;
	logic [31:0] a, b, c, d, e, f, g, h;
	logic [31:0] new_a, new_b, new_c, new_d, new_e, new_f, new_g, new_h;
	logic [31:0] W[0:15], newW;
	logic [31:0] K;
	typedef enum logic [5:0]{preProcessing, prepareMessageStep, intermediateStep, waiting, thirdStep, doneHashing} statetype;
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
	
	always_ff @(posedge clk, negedge block_load)
		if(~block_load) falling_edge_block <= 1;
		else            falling_edge_block <= 0;
		
		
		/*
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
	assign W[15] = block[511:480];*/
	always_ff @(posedge clk)
	begin
		if (state == intermediateStep) roundNumber <=0;
		else  								 roundNumber <= roundNumber + 1;
		
		if(state == preProcessing)     messageScheduleCounter <= 0;
		else if(state == prepareMessageStep)  messageScheduleCounter <= messageScheduleCounter + 1;
		else                                  messageScheduleCounter <= messageScheduleCounter;
		
		if(state == preProcessing)            counter2 <= 0;
		else if(state == prepareMessageStep)  counter2 <= counter2 + 1;
		else                                  counter2 <= counter2;
		
		if(state == prepareMessageStep) begin
			if(messageScheduleCounter == 0)      W[counter2] <= block[31:0];
			else if(messageScheduleCounter == 1) W[counter2] <= block[63:32];
			else if(messageScheduleCounter == 2) W[counter2] <= block[95:64];
			else if(messageScheduleCounter == 3) W[counter2] <= block[127:96];
			else if(messageScheduleCounter == 4) W[counter2] <= block[159:128];
			else if(messageScheduleCounter == 5) W[counter2] <= block[191:160];
			else if(messageScheduleCounter == 6) W[counter2] <= block[223:192];
			else if(messageScheduleCounter == 7) W[counter2] <= block[255:224];
			else if(messageScheduleCounter == 8) W[counter2] <= block[287:256];
			else if(messageScheduleCounter == 9) W[counter2] <= block[319:288];
			else if(messageScheduleCounter ==10) W[counter2] <= block[351:320];
			else if(messageScheduleCounter ==11) W[counter2] <= block[383:352];
			else if(messageScheduleCounter ==12) W[counter2] <= block[415:384];
			else if(messageScheduleCounter ==13) W[counter2] <= block[447:416];
			else if(messageScheduleCounter ==14) W[counter2] <= block[479:448];
			else if(messageScheduleCounter ==15) W[counter2] <= block[511:480];
			else W[counter2] <= newW;
		end
	end
		
	always_comb
		case(state) 
			preProcessing:
				if(falling_edge_block)           nextstate = prepareMessageStep;
				else            		            nextstate = preProcessing;
			prepareMessageStep:
				if(messageScheduleCounter == 63) nextstate = intermediateStep;
				else                             nextstate = prepareMessageStep;
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
	prepareMessage ppM(W[counter2-2], W[counter2-7], W[counter2-15], W[counter2-16], newW);
	thirdComp(a,b,c,d,e,f,g,h,W[roundNumber],K, new_a, new_b, new_c, new_d, new_e, new_f, new_g, new_h);

	assign {a,b,c,d,e,f,g,h} = intermediate_hash;
	assign done = (state==doneHashing);
	assign hash = intermediate_hash;
	
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


module prepareMessage(input logic [31:0] Wprev2, Wprev7, Wprev15, Wprev16,
                      output logic [31:0] newW);
	logic [31:0] output_sigma0;
	logic [31:0] output_sigma1;	
	sigma0 s0(Wprev2 , output_sigma0);
	sigma1 s1(Wprev15, output_sigma1);
	assign newW = output_sigma1 + Wprev7 + output_sigma0 + Wprev16;
endmodule
