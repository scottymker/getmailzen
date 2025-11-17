"""
Token Encryption Service
Encrypts and decrypts sensitive OAuth tokens using Fernet symmetric encryption
"""
import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()


class TokenEncryption:
    """Handles encryption and decryption of OAuth tokens"""

    def __init__(self):
        """
        Initialize encryption service
        Uses ENCRYPTION_KEY from environment variable
        If not set, generates a new key (only for development!)
        """
        self.encryption_key = os.getenv('ENCRYPTION_KEY')

        if not self.encryption_key:
            # Generate new key (only for development - in production this must be set in .env)
            print("WARNING: ENCRYPTION_KEY not set. Generating new key for development.")
            print("In production, set ENCRYPTION_KEY in your .env file!")
            self.encryption_key = Fernet.generate_key().decode()
            print(f"Generated key: {self.encryption_key}")

        # Convert to bytes if it's a string
        if isinstance(self.encryption_key, str):
            self.encryption_key = self.encryption_key.encode()

        self.cipher = Fernet(self.encryption_key)

    def encrypt(self, plaintext):
        """
        Encrypt a plaintext string

        Args:
            plaintext (str): The text to encrypt

        Returns:
            str: Encrypted string (base64 encoded)
        """
        if not plaintext:
            return None

        # Convert string to bytes
        plaintext_bytes = plaintext.encode()

        # Encrypt
        encrypted_bytes = self.cipher.encrypt(plaintext_bytes)

        # Return as base64 string
        return encrypted_bytes.decode()

    def decrypt(self, encrypted_text):
        """
        Decrypt an encrypted string

        Args:
            encrypted_text (str): The encrypted text (base64 encoded)

        Returns:
            str: Decrypted plaintext string
        """
        if not encrypted_text:
            return None

        # Convert string to bytes
        encrypted_bytes = encrypted_text.encode()

        # Decrypt
        decrypted_bytes = self.cipher.decrypt(encrypted_bytes)

        # Return as string
        return decrypted_bytes.decode()

    @staticmethod
    def generate_key():
        """
        Generate a new encryption key

        Returns:
            str: New Fernet encryption key
        """
        return Fernet.generate_key().decode()


# Global encryption service instance
encryption_service = TokenEncryption()


def encrypt_token(token):
    """Helper function to encrypt a token"""
    return encryption_service.encrypt(token)


def decrypt_token(encrypted_token):
    """Helper function to decrypt a token"""
    return encryption_service.decrypt(encrypted_token)


if __name__ == '__main__':
    # Test encryption
    print("Testing encryption service...")

    # Generate a key
    key = TokenEncryption.generate_key()
    print(f"Generated encryption key: {key}")

    # Test encrypt/decrypt
    service = TokenEncryption()
    original = "my-secret-oauth-token-12345"
    encrypted = service.encrypt(original)
    decrypted = service.decrypt(encrypted)

    print(f"\nOriginal:  {original}")
    print(f"Encrypted: {encrypted}")
    print(f"Decrypted: {decrypted}")
    print(f"Match: {original == decrypted}")
