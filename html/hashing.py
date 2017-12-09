# hashing.py
# HMC E85 8 December 2017
# hfang@hmc.edu, mjenrungrot@hmc.edu

import subprocess
import time
ITER = 15 



def get_spi(input_msg=None, difficulty=0):
    """Get the SPI output by running the C algorithm """
    # Set the input message
    if input_msg is not None:
        with open("input_message.txt", "wb") as f:
            f.write(input_msg)

    hashes = []
    previousHash = None
    i = 0
    counter = 0

    # Run the hashing process several times to gather the correct hash output from the C program
    while i  < ITER:
        # Run the C modules
        try:
            subprocess.run(["sudo", "./call_spi", str(difficulty)], timeout=2)
        except subprocess.TimeoutExpired: 
            pass 
        
        time.sleep(0.2)

        # Read the output from the C program
        with open("output.txt", "r") as f2:
            outputNonce = int(f2.readline())
            outputHash = f2.readline()

        # Wait until we have three of the same values to break
        if outputHash == previousHash:
            counter += 1
        else:
            counter = 0

        if counter == 3: 
            print("Final Hash: {:}    nonce = {:}".format(outputHash, outputNonce))
            return outputHash, outputNonce

        hashes.append((outputHash, outputNonce))
        previousHash = outputHash

        f2.close()
        i += 1

    # Return the actual hash and nonce from what the most common ones before
    (actual_hash, actual_nonce) = max(set(hashes), key =hashes.count)
   
    return  (actual_hash, actual_nonce)






