import hashlib
import json
import ed25519

FEE_PER_TRANSACTION = 1

class Transaction:
    def __init__(self):
        """
        Constructor for a transaction.
        """
        self.id = None
        self.hash = None
        self.type = None
        self.data = {
            "inputs": [],
            "outputs": []
        }

    def __repr__(self):
        """
        String representation for a transaction
        """
        return json.dumps(self.__dict__)
    
    def toHash(self):
        """
        Compute hash for the transaction
        """
        strInput = str(self.id) + str(self.type) + str(self.data)
        return hashlib.sha256(strInput.encode('utf-8')).hexdigest()

    def check(self):
        """
        Check that the transaction is valid, e.g. signed by the correct 
        individual.
        """

        # Check if the computed hash matches the transaction's hash.
        transactionHash = self.toHash()
        if(transactionHash != self.hash):
            raise ValueError("hash value of transaction error")

        # Check if the signature of all input transactions are correct.
        for inputTransaction in self.data["inputs"]:
            transactionHash = inputTransaction["transaction"]
            index = inputTransaction["index"]
            amount = inputTransaction["amount"]
            address = inputTransaction["address"]
            signature = inputTransaction["signature"]

            publicKey = address
            messageHash = str(transactionHash) + str(index) + str(address)

            verifying_key = VerifyingKey(publicKey, encoding="hex")
            verification = verifying_key.verify(signature, messageHash)
            if(not verification):
                raise ValueError("Signed transaction is invalid by verification process")

        # Check if the sum of input transactions are enough for the sum of output transactions
        # plus fee.
        if self.type == "regular":
            sumOfInputsAmount = 0
            sumOfOutputsAmount = 0
            
            for inputTransaction in self.data["inputs"]:
                sumOfInputsAmount += inputTransaction["amount"]
            for outputTransaction in self.data["outputs"]:
                sumOfOutputsAmount += outputTransaction["amount"]

            if(sumOfInputsAmount < sumOfOutputsAmount):
                raise ValueError("Input amount is less than output amount")

            if((sumOfInputsAmount - sumOfOutputsAmount) < FEE_PER_TRANSACTION):
                raise ValueError("Not enough fee")

        return True

def createTransaction(data):
    """
    Create a transaction from JSON object.
    """
    transaction = Transaction()
    transaction.id = data["id"]
    transaction.type = data["type"]
    transaction.data = data["data"]
    transaction.hash = transaction.toHash()
    return transaction