from werkzeug.security import check_password_hash
from cryptography.fernet import Fernet
# from Cryptodome.Cipher import AES
# from Cryptodome.Util.Padding import pad, unpad
import os
import uuid

f = Fernet(os.getenv('ANEX_MASTER_KEY'))


class Security:
    @staticmethod
    def fernet_encrypt(data):
        """
        Takes data asthe input, encodes it in UTF-8 format, and encrypts it
        using the Fernet encryption algorithm.

        :param data: The `data` parameter is the string that you want to encrypt using the Fernet encryption
        algorithm
        """
        return f.encrypt(data.encode('utf-8'))

    @staticmethod
    def fernet_decrypt(data):
        """
        Decrypts data using the Fernet encryption algorithm and returns it as
        a UTF-8 encoded string.

        :param data: The `data` parameter is the encrypted data that you want to decrypt
        :return: the decrypted data as a string.
        """
        return f.decrypt(data).decode('utf-8')

    @staticmethod
    def fernet_uuid_encrypt(data):
        """
        Takes in data and encrypts it using the Fernet encryption
        algorithm.

        :param data: The parameter `data` is expected to be an object of type `bytes`
        :return: the encrypted version of the input data.
        """
        return f.encrypt(data.bytes)

    @staticmethod
    def fernet_uuid_decrypt(data):
        """
        Takes in encrypted data and returns a UUID object after
        decrypting it.

        :param data: The `data` parameter is the encrypted data that needs to be decrypted
        :return: a UUID object.
        """
        return uuid.UUID(bytes=f.decrypt(data))

    # @staticmethod
    # def aes_encrypt(date):
    #     uuid_bytes = pad(date.encode(), AES.block_size)
    #     return cipher.encrypt(uuid_bytes)
    #
    # @staticmethod
    # def aes_decrypt(data):
    #     return cipher.decrypt(data).rstrip()

    class User:
        @staticmethod
        def hash_password_compare(hashed, regular):
            """
            Compares a hashed password with a regular password to check if
            they match.

            :param hashed: The hashed parameter is the hashed version of the password.
            :param regular: The regular parameter is the plain text password that you want to compare with the
            hashed password
            :return: the result of the check_password_hash function, which compares a hashed password with a
            regular password and returns True if they match, and False otherwise.
            """
            return check_password_hash(hashed, regular)

    class Network:
        access_key = 0

        @staticmethod
        def init():
            Security.Network.access_key = ((~2496 << 16) & 0xFFFF0000) | 9618
