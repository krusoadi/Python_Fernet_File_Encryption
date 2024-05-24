from os import path
from math import floor

# ! FileCrypto unfinished skeleton

class FileCrypto:
    def __init__(self, fileName:str, keyFileName:str = "secret.key") -> None:
        self.fileName, self.fileExtension = path.splitext(fileName)
        self.keyFileName, self.keyFileExtension = path.splitext(fileName)
        self.size = None
        self.last_size = None

    def encrypt(self) -> None:
        pass
    
    def decrypt(self) -> None:
        pass
    
    def _getKeyData():
        pass
    
    def _readData():
        pass
    
    def _readLastData():
        pass 
