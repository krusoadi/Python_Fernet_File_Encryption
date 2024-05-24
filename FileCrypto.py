from os import path
from math import floor
from cryptography.fernet import Fernet
from io import BufferedReader
from io import BufferedWriter
from ttkbootstrap import DoubleVar

class FileCrypto:
    def __init__(self, fileNameIn:str, keyFileName:str = "secret.key") -> None:
        self.fileName, self.fileExtension = path.splitext(fileNameIn)
        self.keyFileName:str = keyFileName
        self.size: int = path.getsize(fileNameIn) # Normal file reading size
        self.last_size:int = None # Normal file reading remainder size
        
        self.reading_unit:int = None
        
        self.Fernet:Fernet = None
        self.key:bytes = None
        
        self.encryptedChunkSize:int = None # Encrypted file write size
        self.lastEncryptedChunkSize:int = None #Encrypted file write size
        
        self.progress = 0 # for the UI progressbar
        self.progressMax = 1 
        

    def _generateKey(self) -> None:
        self.key = Fernet.generate_key()
    
    def _setGenerator(self) ->None:
        self.Fernet = Fernet(key=self.key)
    
    def _retrieveKeyFileData(self):
        with open(self.keyFileName, "rb") as kfile:
            keysize = path.getsize(self.keyFileName) - 8
            self.encryptedChunkSize = int.from_bytes(kfile.read(4), "big")
            self.lastEncryptedChunkSize = int.from_bytes(kfile.read(4), "big")
            self.key = kfile.read(keysize)

    def _writeKeyFileData(self):
        with open(self.keyFileName, "wb") as kfile:
            kfile.write(self.encryptedChunkSize.to_bytes(4, "big"))
            kfile.write(self.lastEncryptedChunkSize.to_bytes(4, "big"))
            kfile.write(self.key)            

    def _readData(self, buffer: BufferedReader) ->bytes:
        return buffer.read(self.reading_unit)
            
    def _readLastData(self, buffer: BufferedReader) -> bytes:
        return buffer.read(self.last_size)

    def _readEncryptedData(self, buffer: BufferedReader) -> bytes:
        return buffer.read(self.encryptedChunkSize)

    def _readLastEncryptedData(self, buffer: BufferedReader) -> bytes:
        return buffer.read(self.lastEncryptedChunkSize)

    def _writeData(self, data:bytes , buffer: BufferedWriter) -> None:
        buffer.write(data)
        
    def _fetchDecryptAndThrow(self, ibuffer: BufferedReader, obuffer:BufferedWriter, last:bool) -> None:
        if last:
            data = self._readLastEncryptedData(ibuffer) 
        else:
            data = self._readEncryptedData(ibuffer)
        decrypted = self.Fernet.decrypt(data)
        self._writeData(decrypted, obuffer)
    
    def _fetchEncryptAndThrow(self, ibuffer: BufferedReader, obuffer:BufferedWriter, last :bool) -> None:
        if last:
            data = self._readLastData(ibuffer) 
            encrypted = self.Fernet.encrypt(data)    
            self.lastEncryptedChunkSize = len(encrypted)
        else:
            data = self._readData(ibuffer)
            encrypted = self.Fernet.encrypt(data)
            self.encryptedChunkSize = len(encrypted)
    
        self._writeData(encrypted, obuffer)
        
    def encrypt(self, reading_unit:int) -> None:
        self._generateKey()
        self._setGenerator()
        self.reading_unit = reading_unit
        
        
        with open(self.fileName+self.fileExtension, "rb") as rawFile, open(self.fileName+"_encrypted"+self.fileExtension, "wb") as out:
            iterations = floor(self.size / reading_unit)
            self.last_size = self.size - (iterations * reading_unit)
            
            self.progressMax = iterations
            
            if self.size < reading_unit:
                self.progressMax = 1
                self._fetchEncryptAndThrow(rawFile, out, True)
                self.encryptedChunkSize = self.lastEncryptedChunkSize
                self.progress += 1
                    
            else:
                for i in range(iterations + 1):
                    self._fetchEncryptAndThrow(rawFile, out, i == iterations)
                    self.progress += 1
            
            self._writeKeyFileData()
                   
    def decrypt(self, newName:str, progressBar:DoubleVar = None) -> None:
        self._retrieveKeyFileData()
        self._setGenerator()
        self.reading_unit = self.encryptedChunkSize
        
        iterations = floor(self.size / self.reading_unit)
        
        self.progressMax = iterations
        
        with open(self.fileName+self.fileExtension, "rb") as encrypted, open(newName, "wb") as rawFile:
            if self.size == self.reading_unit:
                self.progressMax = 1
                self._fetchDecryptAndThrow(encrypted, rawFile, True)
                if progressBar != None:
                    self.progress += 1
                    self.update_progress(progressBar)
            
            else:
                for i in range(iterations):
                    self._fetchDecryptAndThrow(encrypted, rawFile, i==iterations-1)
                    
                    if progressBar != None:
                        self.progress += 1
                        self.update_progress(progressBar)
            