from os import path
from math import floor
from cryptography.fernet import Fernet
from typing import BinaryIO


class FileCrypto:
    """FileCrypto is a class for encrypting files using Fernet continuously, with a given reading unit.\n
    Unfortunately Fernet is only capable of decrypting files if we use the same chunk size which it encrypted our
    reading units to. This class manages these problems automatically with saving the encrypted chunks sizes and
    decrypting it with them."""
    def __init__(self, file_name: str, key_file: str = "secret.key") -> None:
        self.fileName, self.fileExtension = path.splitext(file_name)
        self.keyFileName: str = key_file
        self.size: int = path.getsize(file_name)  # Normal file reading size
        self.last_size: int | None = None  # Normal file reading remainder size

        self.reading_unit: int | None = None

        self.Fernet: Fernet | None = None
        self.key: bytes | None = None

        self.encryptedChunkSize: int | None = None  # Encrypted file write size
        self.lastEncryptedChunkSize: int | None = None  # Encrypted file write size

        self.progress = 0  # for the UI progressbar
        self.progressMax = 1

    def _generate_key(self) -> None:
        """Private method for generating a Fernet key"""  # TODO check if it's random enough
        self.key = Fernet.generate_key()

    def _set_generator(self) -> None:
        """Private method for constructing the Fernet Client with the chosen key."""
        self.Fernet = Fernet(key=self.key)

    def _retrieve_key_file_data(self):
        """Private method for opening the chosen key file for reading in the key, and the chunk sizes."""
        with open(self.keyFileName, "rb") as key_file:
            key_size = path.getsize(self.keyFileName) - 8
            self.encryptedChunkSize = int.from_bytes(key_file.read(4), "big")
            self.lastEncryptedChunkSize = int.from_bytes(key_file.read(4), "big")
            self.key = key_file.read(key_size)

    def _write_key_file_data(self):
        """Private method for saving the key and the chunk sizes in the key file."""
        with open(self.keyFileName, "wb") as key_file:
            key_file.write(self.encryptedChunkSize.to_bytes(4, "big"))
            key_file.write(self.lastEncryptedChunkSize.to_bytes(4, "big"))
            key_file.write(self.key)

    def _read_data(self, buffer: BinaryIO) -> bytes:
        """Private Wrapper method for reading data from a given file with the reading_unit."""
        return buffer.read(self.reading_unit)

    def _read_last_data(self, buffer: BinaryIO) -> bytes:
        """Private Wrapper method for reading the last data from a given file."""
        return buffer.read(self.last_size)

    def _read_encrypted_data(self, buffer: BinaryIO) -> bytes:
        """Private Wrapper method for reading encrypted data chunks from a given file."""
        return buffer.read(self.encryptedChunkSize)

    def _read_last_encrypted_data(self, buffer: BinaryIO) -> bytes:
        """Private Wrapper method for reading the last encrypted data chunks from a given file."""
        return buffer.read(self.lastEncryptedChunkSize)

    @staticmethod
    def _write_data(data: bytes, buffer: BinaryIO) -> None:
        """Private Wrapper method for writing data to a file."""
        buffer.write(data)

    def _fetch_decrypt_and_throw(self, i_buffer: BinaryIO, o_buffer: BinaryIO, last: bool) -> None:
        """This private method reads data from the given input file (i_buffer), decrypts it and writes out to the given
        output (o_buffer)"""
        if last:
            data = self._read_last_encrypted_data(i_buffer)
        else:
            data = self._read_encrypted_data(i_buffer)
        decrypted = self.Fernet.decrypt(data)
        self._write_data(decrypted, o_buffer)

    def _fetch_encrypt_and_throw(self, i_buffer: BinaryIO, o_buffer: BinaryIO, last: bool) -> None:
        """This private method reads in raw data from the input (i_buffer), encrypts it, and writes out to the output
        (o_buffer), and saves the encrypted chunk size for the key file"""
        if last:
            data = self._read_last_data(i_buffer)
            encrypted = self.Fernet.encrypt(data)
            self.lastEncryptedChunkSize = len(encrypted)
        else:
            data = self._read_data(i_buffer)
            encrypted = self.Fernet.encrypt(data)
            self.encryptedChunkSize = len(encrypted)

        self._write_data(encrypted, o_buffer)

    def encrypt(self, reading_unit: int) -> None:
        """Public method for continuously encrypting a file, with the given reading_unit."""

        self._generate_key()
        self._set_generator()
        self.reading_unit = reading_unit

        with open(self.fileName + self.fileExtension, "rb") as rawFile, open(
                self.fileName + "_encrypted" + self.fileExtension, "wb") as out:
            iterations = floor(self.size / reading_unit)
            self.last_size = self.size - (iterations * reading_unit)
            self.progressMax = iterations - 1

            if self.size < reading_unit:
                self.progressMax = 1
                self._fetch_encrypt_and_throw(rawFile, out, True)
                self.encryptedChunkSize = self.lastEncryptedChunkSize
                self.progress += 1

            else:
                for i in range(iterations + 1):
                    self._fetch_encrypt_and_throw(rawFile, out, i == iterations)
                    self.progress += 1

            self._write_key_file_data()

    def decrypt(self, new_name: str) -> None:
        """Public method for continuously decrypting a file and saving the data in the new_name file."""
        self._retrieve_key_file_data()
        self._set_generator()
        self.reading_unit = self.encryptedChunkSize

        iterations = floor(self.size / self.reading_unit)

        self.progressMax = iterations - 1

        with open(self.fileName + self.fileExtension, "rb") as encrypted, open(new_name, "wb") as rawFile:
            if self.size == self.reading_unit:
                self.progressMax = 1
                self._fetch_decrypt_and_throw(encrypted, rawFile, True)

            else:
                for i in range(iterations + 1):
                    self._fetch_decrypt_and_throw(encrypted, rawFile, i == iterations)
                    self.progress += 1
