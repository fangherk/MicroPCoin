/* 
 * uPcoin main module based on FIPS 180-4 for SHA 256
 * Herrick Fang and Teerapat (Mek) Jenrungrot
 * 11/17/2017
 *
 */
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



/*  
 *  uPcoin_spi function 
 *  Sets up the transfer rate for the SPI protocol
 *
 */
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


/*  
 *  uPcoin_core function 
 *  Generates a hash from a set of 512 bit message blocks
 *
 */
module uPcoin_core(input logic clk, 
                   input logic block_load,
                   input logic message_load,
                   input logic [511:0] block,
                   output logic done,
                   output logic [255:0] hash);

  // Set falling/rising block and message signals;
  logic falling_edge_block, rising_edge_block, falling_edge_message;
  // Set up the round numbers and counter
  logic [5:0] roundNumber, messageScheduleCounter;
  // Set up counters for preparing the message schedule
  logic [3:0] counter3, counter2, next14, next9, next1, next15;
  // Store the intermediate hash value for future updating
  logic [255:0] intermediate_hash;
  // 6.2.2 variables and temp variables
  logic [31:0] a, b, c, d, e, f, g, h;
  logic [31:0] new_a, new_b, new_c, new_d, new_e, new_f, new_g, new_h;
  logic [31:0] W[0:15], newW;
  logic [31:0] K;

  // Set up State transition diagram
  typedef enum logic [5:0]{preProcessing, intermediateStep, waiting, thirdStep, doneHashing} statetype;
  statetype state, nextstate;



  //  Set up the intermediate hash values to change only when returning to the doneHashing or intermediateState steps.
  //  Set up initial hashes.
  always_ff @(posedge clk, posedge message_load)
    if (message_load) state <= preProcessing;
  else begin
    state <= nextstate;
    if(nextstate == intermediateStep) begin
      {a,b,c,d,e,f,g,h} <= 256'h6a09e667bb67ae853c6ef372a54ff53a510e527f9b05688c1f83d9ab5be0cd19;
      intermediate_hash <= 256'h6a09e667bb67ae853c6ef372a54ff53a510e527f9b05688c1f83d9ab5be0cd19;
    end else if(state == intermediateStep && nextstate == thirdStep) begin
      intermediate_hash <= intermediate_hash;
    end else if(state == waiting && nextstate == doneHashing) begin
      intermediate_hash[255:224]  <= a + intermediate_hash[255:224];
      intermediate_hash[223:192]  <= b + intermediate_hash[223:192];
      intermediate_hash[191:160]  <= c + intermediate_hash[191:160];
      intermediate_hash[159:128]  <= d + intermediate_hash[159:128];
      intermediate_hash[127:96]   <= e + intermediate_hash[127:96];
      intermediate_hash[95:64]    <= f + intermediate_hash[95:64];
      intermediate_hash[63:32]    <= g + intermediate_hash[63:32];
      intermediate_hash[31:0]     <= h + intermediate_hash[31:0];
    end else if(state == waiting && nextstate == intermediateStep) begin
      intermediate_hash[255:224]  <= a + intermediate_hash[255:224];
      intermediate_hash[223:192]  <= b + intermediate_hash[223:192];
      intermediate_hash[191:160]  <= c + intermediate_hash[191:160];
      intermediate_hash[159:128]  <= d + intermediate_hash[159:128];
      intermediate_hash[127:96]   <= e + intermediate_hash[127:96];
      intermediate_hash[95:64]    <= f + intermediate_hash[95:64];
      intermediate_hash[63:32]    <= g + intermediate_hash[63:32];
      intermediate_hash[31:0]     <= h + intermediate_hash[31:0];
    end else begin
      intermediate_hash <= intermediate_hash;
    end
  end

  // Set up falling edge block 
  always_ff @(posedge clk, negedge block_load)
    if(~block_load) falling_edge_block <= 1;
  else            falling_edge_block <= 0;

  // Increase counters for the number of rounds in 6.2.2
  // Set up the intermediate values for the intermediate steps
  always_ff @(posedge clk)
    begin
      if (state == intermediateStep)      roundNumber <=0;
      else  								                      roundNumber <= roundNumber + 1;

      if(state == preProcessing)          messageScheduleCounter <= 0;
      else if(state == intermediateStep)  messageScheduleCounter <= messageScheduleCounter + 1;
      else                                messageScheduleCounter <= messageScheduleCounter;

      if(state == intermediateStep)       counter2 <= 0;
      else if(state == thirdStep)         counter2 <= counter2 + 1;
      else                                counter2 <= counter2;

      // Generate the W values in 6.2.2.1
      if(state == intermediateStep) begin
        W[15] <= block[31:0];
        W[14] <= block[63:32];
        W[13] <= block[95:64];
        W[12] <= block[127:96];
        W[11] <= block[159:128];
        W[10] <= block[191:160];
        W[9] <= block[223:192];
        W[8] <= block[255:224];
        W[7] <= block[287:256];
        W[6] <= block[319:288];
        W[5] <= block[351:320];
        W[4] <= block[383:352];
        W[3] <= block[415:384];
        W[2] <= block[447:416];
        W[1] <= block[479:448];
        W[0] <= block[511:480];
      end 
      else if(state == thirdStep) begin
        if(roundNumber < 16) W <= W;
        else                 W[counter3] <= newW;
      end
      
      // Update the variables in 6.2.2.4
      if(state == thirdStep) begin
        a <= new_a;
        b <= new_b;
        c <= new_c;
        d <= new_d;
        e <= new_e;
        f <= new_f;
        g <= new_g;
        h <= new_h;
      end
    end

  // Set up the next state logic, which depends on the roundNumber and the
  // falling edges of the blocks and full message
  always_comb
    case(state) 
      preProcessing:
        if(falling_edge_block)           nextstate = intermediateStep;
        else            		               nextstate = preProcessing;
      intermediateStep:		                nextstate = thirdStep;
      thirdStep:
        if(roundNumber == 63) 				       nextstate = waiting;
        else										                   nextstate = thirdStep;
      waiting:
        if(message_load == 0) 	          nextstate = doneHashing;
        else if(falling_edge_block == 1) nextstate = intermediateStep;
        else 									                   nextstate = waiting;
      doneHashing:				                   nextstate = doneHashing;			
    endcase



  // Prepare the message using newW in 6.2.2.1
  // Generate the K value for each round in 6.2.2.3
  // Apply the transformations in 6.2.2.3
  prepareMessage ppM(W[next1], W[next6], W[next14], W[snext15], newW);
  getConstant kHelper(roundNumber, K);
  thirdComp  thirdComputation(a,b,c,d,e,f,g,h,W[counter2],K, new_a, new_b, new_c, new_d, new_e, new_f, new_g, new_h);


  // Increase the counters to match up with 6.2.2.3
  assign counter3 = counter2+1;
  assign next1 = counter2 - 1;
  assign next6 = counter2 - 6;
  assign next14 = counter2 - 14;
  assign next15 = counter2 - 15;
  
  // Assign final values for completion
  assign done = (state==doneHashing);
  assign hash = intermediate_hash;

endmodule



/*  
 *  getConstant() function 
 *  get the corresponding K value from the sha256constants.txt file
 *
 */
module getConstant(input logic [5:0] roundNumber,
                   output logic [31:0] K);

  logic [31:0] constant[0:63];

  initial   $readmemh("sha256constants.txt", constant);
  assign K = constant[roundNumber]; 
endmodule


/*  
 *  thirdComp() function 
 *  apply the thirdComp function given by 6.2.2.3 
 *
 */
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


/*  
 *  prepareMessage() function 
 *  generate the message schedule based on 6.2.2.1 
 *
 */
module prepareMessage(input logic [31:0] Wprev2, Wprev7, Wprev15, Wprev16,
                      output logic [31:0] newW);
  logic [31:0] output_sigma0;
  logic [31:0] output_sigma1;	
  sigma0 s0(Wprev15 , output_sigma0);
  sigma1 s1(Wprev2, output_sigma1);
  assign newW = output_sigma1 + Wprev7 + output_sigma0 + Wprev16;
endmodule
