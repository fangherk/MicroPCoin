import ed25519
import os
import binascii

############### TEST 1

signing_key, verifying_key = ed25519.create_keypair(entropy=os.urandom)
print("signing  key  = ", binascii.hexlify(signing_key.to_bytes()))
print("verifying key = ", binascii.hexlify(verifying_key.to_bytes()))

computed_verifying_key = signing_key.get_verifying_key()
print("computed vkey = ", binascii.hexlify(computed_verifying_key.to_bytes()))

message = "hello world".encode('utf-8')
signature = signing_key.sign(message)
print("signature = ", binascii.hexlify(signature))

print(verifying_key.verify(signature, message))
print(computed_verifying_key.verify(signature, message))

print()
print()
print()


##################### TEST 2
seed = "1"*32
seed = seed.encode('utf-8')
print("seed = ", seed, len(seed))

signing_key = ed25519.SigningKey(seed)
print("signing  key  = ", (signing_key.to_bytes()))
verify_key = signing_key.get_verifying_key()
print("verify key    =", verify_key.to_bytes())

message = "hello world".encode('utf-8')
signature = signing_key.sign(message)
print("signature = ", binascii.hexlify(signature))

print(verify_key.verify(signature, message))
print()
print()
print()

##################### TEST 3
seed = "6c510044e67931f3e9f0ee793a33b60d7249f951ad53e73c88ceb64eb4f031e6"
seed = binascii.a2b_hex(seed)
print("seed = ", seed, len(seed))

signing_key = ed25519.SigningKey(seed)
print("signing  key  = ", binascii.hexlify((signing_key.to_bytes())), len(signing_key.to_bytes()))
verify_key = signing_key.get_verifying_key()
print("verify key    =", binascii.hexlify(verify_key.to_bytes()))


message = "hello world".encode('utf-8')
signature = signing_key.sign(message)
print("signature = ", binascii.hexlify(signature))

print(verify_key.verify(signature, message))
print()
print()
print()

################################# TEST4
tmp = 'b846d4fde3cb0a611b29cea421743b72fbd0800bdd4236aa36d8dbc4147b1caf'
verify_key = ed25519.VerifyingKey(binascii.a2b_hex(tmp))
signature = '27c0eeaa4c79d8b96baec2326b2103618cf00daa735767d9fa5107b60d141f2a386e3a2773a3820c623fac09ca3506ce413b00955ff8909834984febeb3a5b0c'
signature = binascii.a2b_hex(signature)

print(verify_key.verify(signature, message))