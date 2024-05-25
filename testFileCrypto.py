from FileCrypto import FileCrypto
import lorem

n = 1000

with open("asd.txt", "w") as out:
    for i in range(n):
        out.write(lorem.paragraph())

file = FileCrypto("asd.txt")

file.encrypt(500)

file2 = FileCrypto("asd_encrypted.txt")

file2.decrypt("final.txt")


with open("final.txt","r") as final, open("asd.txt", "r") as original:
    for i in range(len(lorem.paragraph())*n):
        if final.read(1) != original.read(1):
            print("\nnot ")
            break
        
    print("ok")