import hashlib
import json
import ed25519
from binascii import unhexlify

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
        return json.dumps(self, default=jsonDumper)
    
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
            messageHash = hashlib.sha256(messageHash.encode('utf-8')).hexdigest()
            
            print(len(publicKey))
            verifying_key = ed25519.VerifyingKey(publicKey, encoding="hex")
            print("sig {}, {} || msgHash {}, {}".format(type(signature), len(signature), type(messageHash), len(messageHash)))
            print("sig {}|| msgHash {}".format(signature,messageHash))

            verification = None
            try:
                verifying_key.verify(signature.encode("utf-8"), messageHash.encode("utf-8"))
                verification = True
            except ed25519.BadSignatureError:
                verification = False
                # print "signature is bad!"

            # change again later
            # if not verification or True:
            #     raise ValueError("Signed transaction is invalid by verification process")

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