# fig11_04.py
import random
import secrets

random.seed(1)
primero = random.random()
random.seed(1)
segundo = random.random()
print("random con la misma semilla:", primero == segundo)

token = secrets.token_hex(16)
print("secrets, largo del token:", len(token))
