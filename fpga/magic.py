import subprocess
ITER = 9

def get_spi():
   
    block = "abcdefghbcdefghicdefghijdefghijkefghijklfghijklmghijklmnhijklmnoijklmnopjklmnopqklmnopqrlmnopqrsmnopqrstnopqrstu"
    with open("input_message.txt", "w") as f:
        f.write(block)

    hashes = []
    
    for i in range(ITER):
        subprocess.run(["sudo", "./call_spi"], timeout=2)
        # subprocess.run(["sudo", "./call_spi"], timeout=2)
        # subprocess.call(["sudo", "./call_spi"])
        print("Block {:} is done".format(i))

        with open("output.txt", "r") as f2:
            output = f2.read()

        hashes.append(output)
        
        f2.close()

    print("The hash is: \n\n")
    print("\n")
    print(hashes)
    print(max(set(hashes), key =hashes.count))

def main():
    get_spi()

if __name__  == "__main__":
    main()





