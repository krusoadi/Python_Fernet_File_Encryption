from FileCrypto import FileCrypto
import lorem

with open("asd.txt", "w") as out:
    for i in range(1000):
        out.write(lorem.paragraph())

file = FileCrypto("asd.txt")

file.encrypt(500)

file2 = FileCrypto("asd_encrypted.txt")

file2.decrypt("final.txt")