import subprocess
import time
ITER = 15 


def get_spi(input_msg):
   
    block = input_msg
    with open("input_message.txt", "w") as f:
        f.write(block)

    hashes = []
    
    i = 0
    while i  < ITER:
        try:
            subprocess.run(["sudo", "./call_spi"], timeout=1)
        except subprocess.TimeoutExpired: 
            pass 
        # print("Block {:} is done".format(i))
        time.sleep(0.2)
        with open("output.txt", "r") as f2:
            output = f2.read()
        
        print(output)
        if hashes.count(output) == 3: 
            return output
        hashes.append(output)
        
        f2.close()

    #print("The hash is: \n\n")
    # print("\n")
    # print(hashes)
    actual_hash = max(set(hashes), key =hashes.count)
    print(actual_hash)
    return actual_hash

def main():
    get_spi()

if __name__  == "__main__":
    main()





