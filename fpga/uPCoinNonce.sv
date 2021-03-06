/*
 * uPcoin main module
 *
 */
module uPcoin(input logic  clk,
              input logic  sck,
              input logic  sdi,
              output logic sdo,
              input logic block_load, 
              input logic message_load,
              input logic load,
              output logic inputReady,
              output logic doneSPI);

    logic [31:0] currentNonce;
    logic [31:0] blockchainDifficulty, blockDifficulty;
    logic [31:0] numberOfBlocks, numberOfCurrentBlock;
    logic checkedDifficulty;
    logic writeEnabled;
	 logic loadDifficulty;
    logic [255:0] previousHash, hash;
    logic [511:0] message, loadedMessage, processedMessage;
    logic         message_start, doneSHA256;
	 logic block_load_core;
	 logic finalDone;
	 
	 logic [31:0] counter;
	 logic counterClk;
	 assign counterClk = counter[4];
    always_ff @(posedge clk)
		 counter <= counter + 1;
    always_ff @(posedge counterClk)
       if(load)    message_start <= 0;
       else        message_start <= 1; 
		  
	 always_ff @(posedge counterClk)
		if(inputReady)     blockchainDifficulty <= message[511:480];
		else 					 blockchainDifficulty <= blockchainDifficulty;

		
	 // logic for previous hash
	 always_ff @(posedge counterClk)
		 if(numberOfCurrentBlock == 0) previousHash <= 256'h6a09e667bb67ae853c6ef372a54ff53a510e527f9b05688c1f83d9ab5be0cd19;
		 else if(doneSHA256)           previousHash <= hash;
		 else									 previousHash <= previousHash;
		
    uPcoin_spi spi(sck, sdi, sdo, doneSPI, message, {hash, currentNonce});
    
    uPcoin_loadStoreMessage loadstore(counterClk, message, writeEnabled, numberOfCurrentBlock, loadedMessage);
    uPcoin_modifyMessage modify(counterClk, currentNonce, loadedMessage, numberOfCurrentBlock, processedMessage);
    uPcoin_roundController controller(counterClk, message, message_start, block_load, message_load, writeEnabled, doneSHA256, checkedDifficulty, currentNonce, numberOfBlocks, numberOfCurrentBlock, loadDifficulty, block_load_core, inputReady, doneSPI);
    
    uPcoin_core core(counterClk, block_load_core, numberOfBlocks, numberOfCurrentBlock, processedMessage, previousHash, doneSHA256, hash);

    uPcoin_computeDifficulty compute(hash, doneSHA256, blockDifficulty);
    uPcoin_checkDifficulty check(blockDifficulty, blockchainDifficulty, checkedDifficulty);
endmodule

module uPcoin_roundController(input logic clk,
										input logic [511:0] message,
										input logic message_start,
                              input logic block_load,
                              input logic message_load,
                              output logic writeEnabled,
                              input logic doneSHA256,
                              input logic checkedDifficulty,
                              output logic [31:0] nonce,
                              output logic [31:0] numberOfBlocks,
                              output logic [31:0] numberOfCurrentBlock,
										output logic loadDifficulty,
										output logic block_load_core,
										output logic inputReady,
										output logic doneSPI);
    typedef enum logic [5:0] {initialization, getMessageSPI, storeMessage, doneStoreMessage, tryNonce, 
										loadMessage, doneLoadMessage, checkDifficulty,
										runHash, doneHash, foundNonce} statetype;
    statetype state, nextstate;
	
	 
    always_ff @(posedge clk)
		  if(block_load && message_load && ~message_start) state <= initialization;
        else state <= nextstate;
		 
	 // inputReady logic
	 assign inputReady = (state == doneStoreMessage);
	 
	 // block_load_core logic
	 assign block_load_core = (state == doneLoadMessage);

    // number of current block logic
    always_ff @(posedge clk)
        if(state == initialization)        numberOfCurrentBlock <= 0;
        else if(state == getMessageSPI)    numberOfCurrentBlock <= numberOfCurrentBlock;
        else if(state == storeMessage)     numberOfCurrentBlock <= numberOfCurrentBlock;
        else if(state == doneStoreMessage) numberOfCurrentBlock <= numberOfCurrentBlock + 1;
        else if(state == tryNonce)         numberOfCurrentBlock <= 0;
        else if(state == loadMessage)      numberOfCurrentBlock <= numberOfCurrentBlock;
        else if(state == doneLoadMessage)  numberOfCurrentBlock <= numberOfCurrentBlock;
        else if(state == runHash)          numberOfCurrentBlock <= numberOfCurrentBlock;
        else if(state == doneHash)         numberOfCurrentBlock <= numberOfCurrentBlock + 1;
        else if(state == foundNonce)       numberOfCurrentBlock <= 0;

    // number of blocks logic
    always_ff @(posedge clk)
        if(state == initialization)			  numberOfBlocks <= 0;
		  else if(state == getMessageSPI)     numberOfBlocks <= numberOfBlocks;
        else if(state == storeMessage)      numberOfBlocks <= numberOfBlocks + 1;
        else if(state == doneStoreMessage && nextstate == getMessageSPI)  numberOfBlocks <= numberOfBlocks; 	
		  else if(state == doneStoreMessage && nextstate == tryNonce) numberOfBlocks <= numberOfBlocks - 2; // remove the block containing only difficulty
		  else										  numberOfBlocks <= numberOfBlocks;

    // nonce logic
    always_ff @(posedge clk)
        if(state == getMessageSPI)                         nonce <= 0;
        else if(state == storeMessage | state == doneStoreMessage | state == tryNonce | state == loadMessage | state == doneLoadMessage | state == runHash | state == doneHash) nonce <= nonce;
        else if(state == checkDifficulty & nextstate == tryNonce)   nonce <= nonce + 1;
        else if(state == checkDifficulty & nextstate == foundNonce) nonce <= nonce;
        else if(state == foundNonce)                         nonce <= nonce;
		  else																 nonce <= nonce;

    // nextstate logic
    always_comb
        case(state)
		  initialization:					
            nextstate = getMessageSPI;
        getMessageSPI: 
            if(block_load == 0)     nextstate = storeMessage;
            else                    nextstate = getMessageSPI;
        storeMessage:               nextstate = doneStoreMessage;            
        doneStoreMessage:
            if(message[200:0] == 0)         nextstate = tryNonce;
				else                     		  nextstate = getMessageSPI;
        tryNonce:
            nextstate = loadMessage;
        loadMessage:								  nextstate = doneLoadMessage;
        doneLoadMessage:					     nextstate = runHash;
        runHash:
            if(doneSHA256)                  nextstate = doneHash;
            else                            nextstate = runHash;
        doneHash:         
            if(numberOfCurrentBlock < numberOfBlocks)  nextstate = loadMessage;
            else                                       nextstate = checkDifficulty;
		  checkDifficulty:
				if(checkedDifficulty)			  nextstate = foundNonce;
				else									  nextstate = tryNonce;
        foundNonce:                         nextstate = foundNonce;
        endcase	

	  assign writeEnabled = (state == storeMessage);
     assign doneSPI = (state == foundNonce);
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
                  input  logic [287:0] hashAndNonce);

  logic         sdodelayed, wasdone;
  logic [287:0] hashcaptured;

  always_ff @(posedge sck)
    if (!wasdone)  {hashcaptured, message} = {hashAndNonce, message[510:0], sdi};
  else           {hashcaptured, message} = {hashcaptured[286:0], message, sdi}; 

  // sdo should change on the negative edge of sck
  always_ff @(negedge sck) begin
    wasdone = done;
    sdodelayed = hashcaptured[286];
  end

  // when done is first asserted, shift out msb before clock edge
  assign sdo = (done & !wasdone) ? hashAndNonce[287] : sdodelayed;
endmodule

module uPcoin_loadStoreMessage(input logic          clk,
                               input logic [511:0]  message,
                               input logic          writeEnabled,
                               input logic [31:0]   numberOfCurrentBlock,
                               output logic [511:0] loadedMessage);
    
    logic [511:0] RAM [127:0];
    always_ff @(posedge clk)
    begin
        if(writeEnabled) RAM[numberOfCurrentBlock] <= message;
        loadedMessage <= RAM[numberOfCurrentBlock];
    end
endmodule


/*
    uPcoin_modifyMessage modify only the first 32 bits corresponding to the nonce 
    in the first block.
*/
module uPcoin_modifyMessage(input logic             clk,
                            input logic  [31:0]     currentNonce,
                            input logic  [511:0]    loadedMessage,
                            input logic  [31:0]     numberOfCurrentBlock,
                            output logic [511:0]    processedMessage);
    
    always_comb
        if(numberOfCurrentBlock == 0) begin
            processedMessage[511:480] = currentNonce;
            processedMessage[479:0] = loadedMessage[479:0];
        end else begin 
            processedMessage = loadedMessage;
        end
endmodule



module helperCount0_16(input logic [15:0] text,
                       output logic [31:0] numZeros);
    always_comb
        if(text[15])       numZeros = 0;
        else if(text[14])  numZeros = 1;
        else if(text[13])  numZeros = 2;
        else if(text[12])  numZeros = 3;
        else if(text[11])  numZeros = 4;
        else if(text[10])  numZeros = 5;
        else if(text[9])   numZeros = 6;
        else if(text[8])   numZeros = 7;
        else if(text[7])   numZeros = 8;
        else if(text[6])   numZeros = 9;
        else if(text[5])   numZeros = 10;
        else if(text[4])   numZeros = 11;
        else if(text[3])   numZeros = 12;
        else if(text[2])   numZeros = 13;
        else if(text[1])   numZeros = 14;
        else if(text[0])   numZeros = 15;
        else               numZeros = 16;
endmodule
module helperCount0_255(input logic [255:0] text,
                        output logic [31:0] numZeros);
    logic [31:0] tmpOutput [15:0];
    helperCount0_16 a(text[255:240], tmpOutput[15]);
    helperCount0_16 b(text[239:224], tmpOutput[14]);
    helperCount0_16 c(text[223:208], tmpOutput[13]);
    helperCount0_16 d(text[207:192], tmpOutput[12]);
    helperCount0_16 e(text[191:176], tmpOutput[11]);
    helperCount0_16 f(text[175:160], tmpOutput[10]);
    helperCount0_16 g(text[159:144], tmpOutput[ 9]);
    helperCount0_16 h(text[143:128], tmpOutput[ 8]);
    helperCount0_16 i(text[127:112], tmpOutput[ 7]);
    helperCount0_16 j(text[111: 96], tmpOutput[ 6]);
    helperCount0_16 k(text[ 95: 80], tmpOutput[ 5]);
    helperCount0_16 l(text[ 79: 64], tmpOutput[ 4]);
    helperCount0_16 m(text[ 63: 48], tmpOutput[ 3]);
    helperCount0_16 n(text[ 47: 32], tmpOutput[ 2]);
    helperCount0_16 o(text[ 31: 16], tmpOutput[ 1]);
    helperCount0_16 p(text[ 15:  0], tmpOutput[ 0]);
    always_comb
        if(tmpOutput[15] < 16)      numZeros = tmpOutput[15];
        else if(tmpOutput[14] < 16) numZeros = 16  + tmpOutput[14];
        else if(tmpOutput[13] < 16) numZeros = 32  + tmpOutput[13];
        else if(tmpOutput[12] < 16) numZeros = 48  + tmpOutput[12];
        else if(tmpOutput[11] < 16) numZeros = 64  + tmpOutput[11];
        else if(tmpOutput[10] < 16) numZeros = 80  + tmpOutput[10];
        else if(tmpOutput[ 9] < 16) numZeros = 96  + tmpOutput[ 9];
        else if(tmpOutput[ 8] < 16) numZeros = 112 + tmpOutput[ 8];
        else if(tmpOutput[ 7] < 16) numZeros = 128 + tmpOutput[ 7];
        else if(tmpOutput[ 6] < 16) numZeros = 144 + tmpOutput[ 6];
        else if(tmpOutput[ 5] < 16) numZeros = 160 + tmpOutput[ 5];
        else if(tmpOutput[ 4] < 16) numZeros = 176 + tmpOutput[ 4];
        else if(tmpOutput[ 3] < 16) numZeros = 192 + tmpOutput[ 3];
        else if(tmpOutput[ 2] < 16) numZeros = 208 + tmpOutput[ 2];
        else if(tmpOutput[ 1] < 16) numZeros = 224 + tmpOutput[ 1];
        else if(tmpOutput[ 0] < 16) numZeros = 240 + tmpOutput[ 0];
        else                        numZeros = 256;
endmodule
module uPcoin_computeDifficulty(input logic [255:0] hash,
                                input logic         doneSHA256,
                                output logic [31:0] blockDifficulty);
    logic [31:0] tmpDifficulty;
    helperCount0_255 counter(hash, tmpDifficulty);
    always_comb 
        if(doneSHA256) blockDifficulty = tmpDifficulty;
        else           blockDifficulty = 32'hffffffff;
endmodule


module uPcoin_checkDifficulty(input logic [31:0] blockDifficulty,
                              input logic [31:0] blockchainDifficulty,
                              output logic checkedDifficulty);
    always_comb
        if(blockDifficulty > blockchainDifficulty) checkedDifficulty = 1;
        else checkedDifficulty = 0;
endmodule



/*  
 *  uPcoin_core function 
 *  Generates a hash from a set of 512 bit message blocks
 *
 */
module uPcoin_core(input logic clk, 
						 input logic block_load,
						 input logic [31:0] numberOfBlocks, 
						 input logic [31:0] numberOfCurrentBlock,
                   input logic [511:0] block,
						 input logic [255:0] previousHash,
                   output logic doneSHA256,
                   output logic [255:0] hash); 
							 
	
  // Set falling/rising block and message signals;
  logic falling_edge_block;
  // Set up the round numbers and counter
  logic [5:0] roundNumber, messageScheduleCounter;
  // Set up counters for preparing the message schedule
  logic [3:0] counter3, counter2, next14, next6, next1, next15;
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
  always_ff @(posedge clk)
    if (block_load) begin 
    state <= preProcessing;
  end
  else begin
    state <= nextstate;
    if(state == preProcessing || nextstate == intermediateStep) begin
		intermediate_hash <= previousHash;
    end else if(state == intermediateStep && nextstate == thirdStep) begin
      intermediate_hash <= intermediate_hash;
    end else if(state == waiting && (nextstate == doneHashing || nextstate == intermediateStep)) begin
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
  else              falling_edge_block <= 0;

  // Increase counters for the number of rounds in 6.2.2
  // Set up the intermediate values for the intermediate steps
  always_ff @(posedge clk)
    begin
      if (state == intermediateStep)      roundNumber <=0;
      else                        roundNumber <= roundNumber + 1;

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
        if(roundNumber < 15) W <= W;
        else                 W[counter3] <= newW;
      end
    else W <= W;
      
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
    // Fix this, only set the initial hash value on the first block. Another Counter? 
    else if(nextstate == intermediateStep) begin
      {a,b,c,d,e,f,g,h} <= previousHash;
    end
    end

  // Set up the next state logic, which depends on the roundNumber and the
  // falling edges of the blocks and full message
  always_comb
    case(state) 
      preProcessing:
        if(falling_edge_block)                    nextstate = intermediateStep;
        else                                      nextstate = preProcessing;
      intermediateStep:                           nextstate = thirdStep;
      thirdStep:
        if(roundNumber == 63)                     nextstate = waiting;
        else                                      nextstate = thirdStep;
      waiting:                                    nextstate = doneHashing;
      doneHashing:                                nextstate = doneHashing;      
    endcase



  // Prepare the message using newW in 6.2.2.1
  // Generate the K value for each round in 6.2.2.3
  // Apply the transformations in 6.2.2.3
  prepareMessage ppM(W[next1], W[next6], W[next14], W[next15], newW);
  getConstant kHelper(roundNumber, K);
  thirdComp  thirdComputation(a,b,c,d,e,f,g,h,W[counter2],K, new_a, new_b, new_c, new_d, new_e, new_f, new_g, new_h);


  // Increase the counters to match up with 6.2.2.3
  assign counter3 = counter2+1;
  assign next1 = counter2 - 1;
  assign next6 = counter2 - 6;
  assign next14 = counter2 - 14;
  assign next15 = counter2 - 15;
  
  // Assign final values for completion
  assign doneSHA256 = (state==doneHashing);
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
