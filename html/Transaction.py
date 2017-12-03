import hashlib
import json
import ed25519
import binascii

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
        # jsonDumper is used for recursively converting an object to correct JSON output format
        def jsonDumper(obj):
            return obj.__dict__
        return str(json.dumps(self, default=jsonDumper))
    
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
            

            # Generate the Message Hash from the transaction hash, index, and address
            messageHash = str(transactionHash) + str(index) + str(address)
            messageHashed = hashlib.sha256(messageHash.encode('utf-8')).digest()

            # Generate the verifying key from the public key
            verifying_key = ed25519.VerifyingKey(binascii.a2b_hex(publicKey))

            # Check if the the signature of the transaction is valid by checking if we can verify the messageHash
            # by the signature.
            verification = None
            try:
                verifying_key.verify(binascii.a2b_hex(signature), messageHashed)
                verification = True
                print("signature is good!")
            except ed25519.BadSignatureError:
                verification = False
                print("signature is bad!")

            # Verify the signed transaction
            if not verification:
                raise ValueError("Signed transaction is invalid by verification process")

        # Check if the sum of input transactions are enough for the sum of output transactions
        # plus fee.
        if self.type == "regular":
            sumOfInputsAmount = 0
            sumOfOutputsAmount = 0
            
            for inputTransaction in self.data["inputs"]:
                sumOfInputsAmount += int(inputTransaction["amount"])
            for outputTransaction in self.data["outputs"]:
                sumOfOutputsAmount += int(outputTransaction["amount"])

            if(sumOfInputsAmount < sumOfOutputsAmount):
                raise ValueError("Input amount is less than output amount")

            if((sumOfInputsAmount - sumOfOutputsAmount) < FEE_PER_TRANSACTION):
                raise ValueError("Not enough fee")

        return True

def createTransaction(data):
    """
    Create a transaction from dictionary.
    """
    transaction = Transaction()
    # print(data)
    # print(data["id"])
    # print(transaction.id)
    transaction.id = data["id"]
    transaction.type = data["type"]
    transaction.data = data["data"]
    transaction.hash = transaction.toHash()
    return transaction


def createTransactionObject(data):
    """
    Create a transaction from transaction.
    """
    transaction = Transaction()
    transaction.id = data.id
    transaction.type = data.type
    transaction.data = data.data
    transaction.hash = transaction.toHash()
    return transaction
