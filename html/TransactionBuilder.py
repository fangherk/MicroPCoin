import secrets
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

    def from(self, listOfUTXO):
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

        changeAmount =  totalAmountofUTXO - self.totalAmount - self.feeAmount

        inputs = [] 
        for utxo in self.listOfUTXO:
            inputStr  = str(utxo.transaction) + str(utxo.index) + str(utxo.address)
            # secretX = hashlib.pbkdf2_hmac('sha256', inputStr.encode('utf-8'), b'salt', 100000)
            # hexed  = binascii.hexlify(secretX)
            hexed = hashlib.sha256(inputStr.encode('utf-8')).hexdigest()
            txiHash = hexed

            # Create a signing key from secretkey
            signing_key = ed25519.SigningKey(sefl.secretkey)

            # Sign the transaction using the signing key
            utxo.signature =  signing_key.sign(txiHash, encoding="hex")

            inputs.append(utxo)

        outputs = []
        outputs.append({"amount":   self.totalAmount,
                        "address":  self.outputAddress})

        if changeAmount > 0:
            outputs.append({"amount":   changeAmount,
                            "address":  self.outputAddress})
        else:
            raise ValueError("Sender does not have enough money to  send transaction"0

        return Transaction.createTransaction({  "id": secrets.token_hex(32) , 
                                                "hash": None, 
                                                "type": self.typeW, 
                                                "data": {   "inputs": inputs, 
                                                            "outputs" :outputs}
                                                })
        


