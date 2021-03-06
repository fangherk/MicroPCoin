# wallet.py
# HMC E85 8 December 2017
# hfang@hmc.edu, mjenrungrot@hmc.edu

import hashlib, binascii
import ed25519 # API Documentation is available at: https://github.com/warner/python-ed25519
import json

class Wallet:
    def __init__(self, wallet_id, passwordHash, secret=None, keypairs=None):
        """ 
        Wallet Constructor
        - Initialization of Basic Parameters 
        """
        self.id = wallet_id 
        self.passwordHash = passwordHash
        self.secret = secret
        self.keypairs = []  

    def __repr__(self):
        # jsonDumper is used for recursively converting an object to correct JSON output format
        def jsonDumper(obj):
            return obj.__dict__
        return json.dumps(self, default=jsonDumper)

    def generateAddress(self, walletId):
        """ 
        Generate an Address based on the secret 
        """ 
        if self.secret == None:
            self.generateSecret(self.passwordHash + walletId, wallet_pass=True)

        # Last set of keypairs
        last_key_pair = None
        if not self.keypairs:
            last_key_pair = None
        else:
            last_key_pair = self.keypairs[-1]

        # Set the next seed based on the 1st seed or the last key pair's public key
        if last_key_pair is None:
            seed = self.secret
        else:            
            temp_secret = last_key_pair["public_key"]
            seed = self.generateSecret(temp_secret)

        key_pair = self.generateKeyPair(seed) 
        new_key_pair = {"index":        len(self.keypairs) +  1,
                        "secret_key":   key_pair["secret_key"],
                        "public_key":   key_pair["public_key"]}

        self.keypairs.append(new_key_pair)
        return new_key_pair["public_key"]


    def generateKeyPair(self, seed):
        """ 
        Generate Key Public and Private Key Pairs using the EdDSA algorithm library
        """
        keys = {}

        # Note that seed is expected to be 64 hexadecimal characters
        # Convert 64 hexadecimal characters to 32 bytes
        seed_bytes = binascii.a2b_hex(seed)

        # Create a signing key from 32 bytes
        signing_key = ed25519.SigningKey(seed_bytes)

        # Obtain the verify key for a given signing key
        verify_key = signing_key.get_verifying_key()

        # Store secret key of length 128 hexadecimal characters (64 bytes)
        keys["secret_key"] = binascii.hexlify(signing_key.to_bytes()).decode('utf-8')
        
        # Store public key of length 64 hexadecimal characters (32 bytes)
        keys["public_key"] = binascii.hexlify(verify_key.to_bytes()).decode('utf-8')
        
        return keys

    def generateSecret(self, secret, wallet_pass=False):
        """ 
        Create a secret using a password hash based on PBKDF2.
        """
        # secretX = hashlib.pbkdf2_hmac('sha256', secret.encode('utf-8'), b'salt', 100000)
        # hexed  = binascii.hexlify(secretX)
        # Hash the secret 
        hexed = hashlib.sha256(secret.encode('utf-8')).hexdigest()

        if wallet_pass: 
            self.secret = hexed
            return
        else:
            return hexed


    def getPublicKeyByAddress(self, index):
        """ 
        Gather the address by its index 
        """
        for wallet in self.keypairs:
            if wallet["index"] == index:
                return wallet["public_key"]
        
    def getAddressByPublicKey(self, public_key):
        #TODO: Throw error
        for wallet in self.keypairs:
            if wallet["public_key"] == public_key:
                return wallet["public_key"]

    def getSecretKeyByAddress(self, address):
        """
        Gather the secret key from the address 
        """
        for wallet in self.keypairs:
            if wallet["public_key"] == address:
                return wallet["secret_key"]

    def getAddresses(self):
        """ 
        Get all of the addresses 
        """
        return [wallet["public_key"] for wallet in self.keypairs]  
