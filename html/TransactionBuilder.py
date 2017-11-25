import secrets
import Transaction
import json
import hashlib
import ed25519 # API Documentation is available at: https://github.com/warner/python-ed25519

class TransactionBuilder:
    def __init__(self):
        self.listOfUTXO = None
        self.outputAddresses = None
        self.totalAmount = None
        self.changeAddress = None
        self.feeAmount = 0
        self.secretKey = None
        self.typeW = 'regular'

    def __repr__(self):
        """
        String representation for a transaction
        """
        # jsonDumper is used for recursively converting an object to correct JSON output format
        def jsonDumper(obj):
            return obj.__dict__
        return json.dumps(self, default=jsonDumper)

    def fromAddress(self, listOfUTXO):
        self.listOfUTXO = listOfUTXO
        return self

    def to(self, address, amount):
        self.outputAddress = address
        self.totalAmount = amount
        return self

    def change(self, changeAddress):
        self.changeAddress = changeAddress
        return self

    def fee(self, amount):
        self.feeAmount = amount
        return self

    def sign(self, secretKey):
        self.secretKey = secretKey
        return self

    def type(self, typeT):
        self.typeW = typeT

    def build(self):
        if self.listOfUTXO == None:
            raise ValueError(" Unspent Output Transactions ")
        elif self.outputAddress == None:
            raise ValueError(" No Output Address ") 
        elif self.totalAmount == None:
            raise ValueError(" No Total Amount ")

        totalAmountOfUTXO = 0
        for output in self.listOfUTXO:
            totalAmountOfUTXO += output["amount"]

        changeAmount =  int(totalAmountOfUTXO) - int(self.totalAmount) - int(self.feeAmount)

        inputs = [] 
        for utxo in self.listOfUTXO:
            inputStr  = str(utxo["transaction"]) + str(utxo["index"]) + str(utxo["address"])
            hexed = hashlib.sha256(inputStr.encode('utf-8')).digest()
            txiHash = hexed

            # Create a signing key from secretkey
            signing_key = ed25519.SigningKey(utxo["address"].encode('utf-8'))
            print("utxo address", utxo["address"])
            print("signing signature encode: {}\ninputHash: {}\n".format(utxo["address"].encode('utf-8'),  hexed))
            # Sign the transaction using the signing key
            print("signature sign: ", signing_key.sign(txiHash, encoding="hex"))
            utxo["signature"] =  signing_key.sign(txiHash, encoding="hex").decode("utf-8")


            inputs.append(utxo)

        outputs = []
        outputs.append({"amount":   self.totalAmount,
                        "address":  self.outputAddress})

        if changeAmount > 0:
            outputs.append({"amount":   changeAmount,
                            "address":  self.outputAddress})
        else:
            raise ValueError("Sender does not have enough money to  send transaction")

        buildData = {}
        buildData["id"] = secrets.token_hex(32)
        buildData["hash"] = None
        buildData["type"] = self.typeW
        inOut = {} 
        inOut["inputs"] = inputs
        inOut["outputs"] = outputs
        buildData["data"] = inOut
        
        return Transaction.createTransaction(buildData)
        


