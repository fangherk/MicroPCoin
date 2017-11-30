import subprocess
import time
import pprint
ITER = 1000

def get_spi(input_msg):
   
    block = input_msg
    with open("input_message.txt", "w") as f:
        f.write(block)

    hashes = []
    
    for i in range(ITER):
        try:
            subprocess.run(["sudo", "./call_spi"], timeout=1)
        except subprocess.TimeoutExpired: 
            raise subprocess.TimeoutExpired
            pass 
        # print("Block {:} is done".format(i))
        with open("output.txt", "r") as f2:
            output = f2.read()

        print(output)
        time.sleep(1)
        hashes.append(output)
        
        f2.close()

    #print("The hash is: \n\n")
    # print("\n")
    pprint.pprint((hashes))
    actual_hash = max(set(hashes), key =hashes.count)
    # print(actual_hash)
    return actual_hash

def main():
    strInput = input()
    get_spi(strInput)

if __name__  == "__main__":
    main()





