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
        """ Change the from address of the transaction""" 
        self.listOfUTXO = listOfUTXO
        return self

    def to(self, address, amount):
        """ Change the outputAddress and total amount of the transaction""" 
        self.outputAddress = address
        self.totalAmount = amount
        return self

    def change(self, changeAddress):
        """ Change the changeAddress """ 
        self.changeAddress = changeAddress
        return self

    def fee(self, amount):
        """ Change the fee of the transaction"""
        self.feeAmount = amount
        return self

    def sign(self, secretKey):
        """ Change secret key of the transaction""" 
        self.secretKey = secretKey
        return self

    def type(self, typeT):
        """ Change the type of the transaction """ 
        self.typeW = typeT

    def build(self):
        """ Build a transaction from the internal parameters"""

        # check for valid transactions by checking
        if self.listOfUTXO == None:
            raise ValueError(" Unspent Output Transactions ")
        elif self.outputAddress == None:
            raise ValueError(" No Output Address ") 
        elif self.totalAmount == None:
            raise ValueError(" No Total Amount ")

        # Add up all the amounts from the utxo
        totalAmountOfUTXO = 0
        for output in self.listOfUTXO:
            totalAmountOfUTXO += output["amount"]

        # Remove the transaction amount from the total utxo amounts
        changeAmount =  int(totalAmountOfUTXO) - int(self.totalAmount) - int(self.feeAmount)

        # Generate the inputs 
        inputs = [] 
        for utxo in self.listOfUTXO:
            # Generate the transaction input and calculate the hash/sign the data
            inputStr  = str(utxo["transaction"]) + str(utxo["index"]) + str(utxo["address"])
            hexed = hashlib.sha256(inputStr.encode('utf-8')).digest()
            txiHash = hexed

            # Create a signing key from secretkey
            # print("Pause --------------")
            # print("alert!--------------")
            # signing_key = ed25519.SigningKey(self.secretKey.encode("utf-8"))
            # sig = signing_key.sign(txiHash, encoding="base64")
            # verifying_key = signing_key.get_verifying_key()
            # verifying_key.verify(sig, txiHash, encoding="base64")
            # print("alert!--------------")

            # Generate the signing key to sign the transaction
            signing_key, verify_key = self.generateKeyPair(self.secretKey)
            # # Sign the transaction using the signing key
            # print("alert!--------------")
            # sig = signing_key.sign(txiHash, encoding="base64")
            # verify_key.verify(sig, txiHash, encoding="base64")
            # print("alert!--------------")

            utxo["signature"] =  signing_key.sign(txiHash, encoding="hex").decode("utf-8")
            # print("messageHashV", hexed)
            # print("signatureV", utxo["signature"])

            # # print("verify key", verify_key.to_ascii(encoding="hex").decode("ascii"))
            # strig = '3432626566663236633432393134343066636161663266383062396462646631'
            # verifier = ed25519.VerifyingKey(strig.encode("ascii"), encoding="hex")
            # print("\n\n\n\nDoes this work? ")
            # abc = verifier.verify(signing_key.sign(txiHash, encoding="hex"), txiHash, encoding="hex")
            # print(abc) 
            # print("\n\n\n\n-----------")
            # print("\n\n stop \n\n")
            inputs.append(utxo)

        # Generate the outputs
        outputs = []
        outputs.append({"amount":   self.totalAmount,
                        "address":  self.outputAddress})

        if changeAmount > 0:
            outputs.append({"amount":   changeAmount,
                            "address":  self.changeAddress})
        else:
            raise ValueError("Sender does not have enough money to  send transaction")

        # return a dictionary of all the values to the create transaction function in Transaction 
        buildData = {}
        buildData["id"] = secrets.token_hex(32)
        buildData["hash"] = None
        buildData["type"] = self.typeW
        inOut = {} 
        inOut["inputs"] = inputs
        inOut["outputs"] = outputs
        buildData["data"] = inOut
        
        return Transaction.createTransaction(buildData)
        


    def generateKeyPair(self, seed):
            """ 
            Generate Key Public and Private Key Pairs using the EdDSA algorithm library
            """
            keys = {} 
            signing_key = ed25519.SigningKey(seed.encode('utf-8'))

            # Obtain the verify key for a given signing key
            verify_key = signing_key.get_verifying_key()

            return signing_key, verify_key
