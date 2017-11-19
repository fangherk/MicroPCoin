import hashlib

FEE_PER_TRANSACTION = 1

class Transaction:
    def __init__(self):
        self.id = None
        self.hash = None
        self.type = None
        self.data = {
            "inputs": [],
            "outputs": []
        }
    
    def toHash(self):
        strInput = str(self.id) + str(self.type) + str(self.data)
        return hashlib.sha256(strInput.encode('utf-8')).hexdigest()

    def check(self):
        transactionHash = self.toHash()
        if(transactionHash != self.hash):
            raise ValueError("hash value of transaction error")

        # Check if the signature of all input transactions are correct.
        for inputTransaction in self.data["inputs"]
            transactionHash = inputTransaction["transaction"]
            index = inputTransaction["index"]
            amount = inputTransaction["amount"]
            address = inputTransaction["address"]
            signature = inputTransaction["signature"]

            # Verify that 
            publicKey = address
            messageHash = str(transactionHash) + str(index) + str(address)

            # verify(publicKey, signature, messageHash) must be true

        if self.type == "regular":
            sumOfInputsAmount = 0
            sumOfOutputsAmount = 0
            
            for inputTransaction in self.data["inputs"]
                sumOfInputsAmount += inputTransaction["amount"]
            for outputTransaction in self.data["outputs"]
                sumOfOutputsAmount += outputTransaction["amount"]

            if(sumOfInputsAmount < sumOfOutputsAmount):
                raise ValueError("Input amount is less than output amount")

            if((sumOfInputsAmount - sumOfOutputsAmount) < FEE_PER_TRANSACTION):
                raise ValueError("Not enough fee")

        return True
