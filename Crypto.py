from cryptography.fernet import Fernet

#! Untested Sketch

class Crypto:
    def __init__(self) -> None:
        self.key = None
        self.cryptor = None
        
    def _generateKey(self) -> None:
        """Private method, generates a key using Fernet.generate_key()."""
        self.key = Fernet.generate_key()
             
    def _setCryptor(self) -> None:
        """Private method sets the Fernet Client, with our key."""
        if self.key != None:
            self.cryptor = Fernet(key=self.key)
        
    def reset(self) -> None:
        """Resets the variables of the object. (for reuse)"""
        self.key = None
        self.cryptor = None
        
    def prepareDecrypt(self, key:bytes) -> None:
        """Should be used before the decrypt, it ensures that the decryption will hapen with our key."""
        self.key = key
        self.cryptor = Fernet(key=self.key)

    def prepareEncrypt(self) -> None:
        """Generates a key, and sets Fernet Client to this key."""
        self._generateKey()
        self._setCryptor()
            
    def getKey(self) ->bytes:
        """Returns the key which we used in bytes."""
        return self.key
        
    def encrypt(self, input:bytes) -> bytes:
        """Encrypts the given bytes using our previously set key and returns them."""
        if self.key == None:
            self.prepareEncrypt()
            
        return self.cryptor.encrypt(input)
        
    def decrypt(self, input:bytes) -> bytes:
        """Decrypts the given bytes using our previously set key and returns them in bytes."""
        if self.key != None:
            return self.cryptor.decrypt(input)