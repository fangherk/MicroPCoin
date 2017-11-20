import hashlib, binascii
import nacl.encoding, nacl.signing

class Wallet:
    def __init__(self, wallet_id, passwordHash, secret=None, keypairs=None):
        """ Wallet Initialization of Basic Parameters """
        self.id = wallet_id 
        self.passwordHash = passwordHash
        self.secret = secret
        self.keypairs = []

    def generateAddress(self):
        """ Generate an Address based on the secret """ 
        if self.secret == None:
            self.generateSecret(self.passwordHash, wallet_pass=True)

        # Last set of keypairs
        if not self.keypairs:
            last_key_pair = None
        else:
            last_key_pair == self.keypairs[-1]

        # Set the next set based on the 1st seed or the last key pair
        if last_key_pair == None:
            seed = self.secret
        else:
            # TODO: Add Key Pair Property
            temp_secret = secret
            seed = self.generateSecret(temp_secret)

        key_pair = self.generateKeyPair(seed) 
        new_key_pair = {index: len(self.keypairs) +  1,
                      secret_key: key_pair["secret_key"],
                      public_key: key_pair["public_key"]}

        self.keyPairs.append(newKeyPair)
        return new_key_pair["public_key"]


    def generateKeyPair(self, seed):
        """ Generate Key Public and Private Key Pairs using the EdDSA algorithm library"""
        keys = {} 
        signing_key = nacl.signing.SigningKey.generate(seed)

        # Obtain the verify key for a given signing key
        verify_key = signing_key.verify_key

        # Serialize the verify key to send it to a third party
        verify_key_hex = verify_key.encode(encoder=nacl.encoding.HexEncoder)

        keys["secret_key"] = signing_key
        keys["public_key"] = verify_key_hex

        return keys

    def generateSecret(self, secret, wallet_pass=False):
        """ Create a secret using a password hash based on PBKDF2."""
        secretX = hashlib.pbkdf2_hmac('sha256', secret.encode('utf-8'), b'salt', 100000)
        hexed  = binascii.hexlify(secretX)
        if wallet_pass: 
            self.secret = hexed
            return
        else:
            return hexed


    def getPublicKeyByAddress(self, index):
        """ Gather the address by its index """
        for wallet in self.keypairs:
            if wallet["index"] == index:
                return wallet["public_key"]
        
    def getAddressByPublicKey(self, public_key):
        #TODO: Throw error
        for wallet in self.keypairs:
            if wallet["public_key"] == public_key:
                return wallet["public_key"]

    def getSecretKeyByAddress(self, address):
        """ Gather the secret key from the address """
        for wallet in self.keypairs:
            if wallet["public_key"] == address:
                return wallet["secret_key"]

    def getAddresses(self):
        """ Get all of the addresses """
        return [wallet["public_key"] for wallet in self.keypairs]  
