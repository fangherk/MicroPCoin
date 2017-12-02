import subprocess
import time
ITER = 15 


def get_spi(input_msg=None, difficulty=0):
    if input_msg is not None:
        with open("input_message.txt", "wb") as f:
            f.write(input_msg)

    hashes = []
    previousHash = None
    i = 0
    counter = 0
    while i  < ITER:
        try:
            subprocess.run(["sudo", "./call_spi", str(difficulty)], timeout=2)
        except subprocess.TimeoutExpired: 
            pass 
        # print("Block {:} is done".format(i))
        time.sleep(0.2)
        with open("output.txt", "r") as f2:
            outputNonce = int(f2.readline())
            outputHash = f2.readline()

        print(outputNonce)  
        print(outputHash)
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

    (actual_hash, actual_nonce) = max(set(hashes), key =hashes.count)
    print("Actual Hash: {:}    nonce = {:}".format(outputHash, outputNonce))
    return  (actual_hash, actual_nonce)

def main():
    get_spi()

if __name__  == "__main__":
    main()





