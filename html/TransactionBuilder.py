import secrets
import Transaction
import json
import hashlib
import binascii
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
            txiHash = hashlib.sha256(inputStr.encode('utf-8')).digest()

            # Generate the signing key to sign the transaction
            signing_key, verify_key = self.generateKeyPair(self.secretKey)
            utxo["signature"] = binascii.hexlify(signing_key.sign(txiHash)).decode("utf-8")

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
            
            # Note that seed is expected to be 64 hexadecimal characters
            # Convert 64 hexadecimal characters to 32 bytes
            seed_bytes = binascii.a2b_hex(seed)

            # Create the signing key from 32 bytes
            signing_key = ed25519.SigningKey(seed_bytes)

            # Obtain the verify key for a given signing key
            verify_key = signing_key.get_verifying_key()

            return signing_key, verify_key
