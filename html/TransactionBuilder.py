import secrets
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
            secretX = hashlib.pbkdf2_hmac('sha256', inputStr.encode('utf-8'), b'salt', 100000)
            hexed  = binascii.hexlify(secretX)
            txiHash = hexed
            utxo.signature =  "ttt"
            inputs.append(utxo)

        outputs = []
        outputs.append({"amount":self.totalAmount,"address":self.outputAddress})

        if changeAmount > 0:
            outputs.append({"amount": changeAmount,"address":self.outputAddress})
        else:
            raise ValueError("Sender does not have enough money to  send transaction"0

        return json.dumps({"id": secrets.token_hex(32) , "hash": None, "type": self.typeW, "data": {"inputs": inputs, "outputs" :outputs}})
        


