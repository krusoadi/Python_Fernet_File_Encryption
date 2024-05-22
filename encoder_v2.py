from cryptography.fernet import Fernet
from os import path
import gc   #Garbage collector
from math import floor

# TODO : Make a Tkinter UI for the script
# TODO : Rewrite and refactor to make it more readable and efficient with OOP principles
# TODO : Check if garbage collector has any effect on the performance, and safety of the script
# TODO : Segment it into smaller functions, and more files for better readability

def encrypt(filename:str) -> None:
    name, ext = path.splitext(filename)

    #Generating a fernet key.
    key = Fernet.generate_key()
    fernet = Fernet(key=key)

    #File opening
    with open(filename, "rb") as in_file, open(f"{name}_encrypted{ext}", "wb") as out_file, open(f"{name}_fk.key", "wb") as keyfile:
        size = path.getsize(filename)
        reading_unit = 3145728    #3MB which is divisible by three therefore its easier to calculate/debug with this. I didn't want to use more, because of the memory.
        iterations = floor(size / reading_unit) -1 #To get the numbers of iterations with the reading unit
        last_size = size - (iterations * reading_unit) #The last size, the remainder, which is smaller than 3MB
        
        if size <= reading_unit:  #If the size is <= than 3MB it's way easier to read the whole file and encrypt it.
            original = in_file.read()
            encrypted = fernet.encrypt(original)
            out_file.write(encrypted)
            encrypted_chunksize = len(encrypted).to_bytes(4, "big") #Important because the algorithm (explained later. line 47)
            encrypted_chunksize2 = len(encrypted).to_bytes(4, "big") #We need 2 size to be written out, because decrypting excpects 2 Int32 values
            keyfile.write(encrypted_chunksize)
            keyfile.write(encrypted_chunksize2)

            del(encrypted_chunksize) #freeing memory
            del(encrypted_chunksize2)
            del(original)
            del(encrypted)
            gc.collect()

        else:
            encrypted_chunk = fernet.encrypt(in_file.read(reading_unit))
            out_file.write(encrypted_chunk)

            encrypted_chunksize = len(encrypted_chunk).to_bytes(4, "big") #So basically after every 3072 original bytes fernet spits out 4196 encoded bytes 
            keyfile.write(encrypted_chunksize)                            #and encrypts it. But if you do not read back the original amount of encoded bytes fernet won't be able to
            del(encrypted_chunk)                                          #to decrypt it. Thats why we write the last reading units size and the reading unit size to the key file in bytes.
            del(encrypted_chunksize)

            for i in range(iterations + 1):
                if i == iterations: # The last reading (remainder)
                    original = in_file.read((last_size))
                    encrypted = fernet.encrypt(original)
                    encrypted_chunksize = len(encrypted).to_bytes(4, "big") #Last reading unit size in 4 bytes (Int32)
                    keyfile.write(encrypted_chunksize)
                    out_file.write(encrypted)
                    del(encrypted_chunksize)
                    del(original)
                    del(encrypted)

                else:
                    original = in_file.read(reading_unit)
                    encrypted = fernet.encrypt(original)
                    out_file.write(encrypted)
                    del(original)
                    del(encrypted)
                gc.collect()

        keyfile.write(key) #The key is the last in the .key file so it makes easier to read it back 


def decrypt(filename:str, key: str) -> None:

    fullname, ext = path.splitext(filename)
    name = fullname.split("_encr")[0]
    safe = True

    if key != f"{name}_fk.key": #It's to make sure we don't switch up keys accidentally
        safe = False
        
    if safe == True:
        with open(key, "rb") as key_file, open(filename, "rb") as in_file, open(f"{name}{ext}", "wb") as out_file: 
            
            keyfile_size = path.getsize(key) - 8                        #We need to get the keys size withouth the reading unit bytes
            reading_unit = int.from_bytes(key_file.read(4), "big")      #First reading unit
            last_reading_unit = int.from_bytes(key_file.read(4), "big") #Last reading unit
            key_from_file = key_file.read(keyfile_size)                 #The Fernet key

            fernet = Fernet(key= key_from_file)
            size = path.getsize(filename)
            
            iterations = floor(size / reading_unit)     #Here we don't need to decrease it by one because the sample was in the reading units size
            
        
            if size == reading_unit:
                encrypted = in_file.read(size)
                decrypted = fernet.decrypt(encrypted)
                out_file.write(decrypted)
                del(encrypted)
                del(decrypted)
                gc.collect()

            else:
                for i in range(iterations + 1):
                    if i == iterations:
                        encrypted = in_file.read(last_reading_unit)
                        decrypted_ = fernet.decrypt(encrypted)
                        out_file.write(decrypted_)
                        del(encrypted)
                        del(decrypted_)
                    
                    else:
                        encrypted = in_file.read(reading_unit)
                        decrypted = fernet.decrypt(encrypted)
                        out_file.write(decrypted)
                        del(encrypted)
                        del(decrypted)
                    gc.collect()

    else:
        print("Unsafe key")

#I'm really thinking about making a Tkinter UI to be less sketchy, but for now it gets the job done. 


runtime = True

while runtime == True:

    print("\nMade by: Adam Krusoczki\n")

    answer = input("Would you like to encrypt or decrypt? (encrypt/decrypt/exit) >")

    if answer == "exit":
        break

    elif answer == "encrypt":
        print("\nThe file should be in this folder. Please write the whole filename (e.g.: secret.txt)")
        print("The script will make an encypted and a key file. Please hide they key file, because the file is unlockable with it.")
        print("Delete the original and it is best to put the key on a USB stick, etc. You can keep the encrypted file.\n")
        print("Please test the decription for making sure problems won't occur!\n")
        filename = input("Type the filename (please read the instructions) > ")

        encrypt(filename)
        print("The file is encrypted succesfuly.")
    
    elif answer == "decrypt":
        print("To decrypt the file you should use the original key and file.\n")
        filename = input("Type the filename > ")
        print("\n")
        keyfile = input("Type the keyfiles name > ")
        decrypt(filename=filename, key=keyfile)
        print("File is decrypted succesfully.")


