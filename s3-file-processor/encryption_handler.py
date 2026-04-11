import os
from cryptography.fernet import Fernet


def generate_key():
    return Fernet.generate_key()


def save_key(key, key_path='secret.key'):
    with open(key_path, 'wb') as key_file:
        key_file.write(key)
    print(f"Encryption key saved to: {key_path}")


def load_key(key_path='secret.key'):
    with open(key_path, 'rb') as key_file:
        return key_file.read()


def get_or_create_key(key_path='secret.key'):
    if os.path.exists(key_path):
        print("Loading existing encryption key...")
        return load_key(key_path)
    else:
        print("Generating new encryption key...")
        key = generate_key()
        save_key(key, key_path)
        return key


def encrypt_data(data_bytes, key):
    cipher = Fernet(key)
    return cipher.encrypt(data_bytes)


def decrypt_data(encrypted_bytes, key):
    cipher = Fernet(key)
    return cipher.decrypt(encrypted_bytes)


def encrypt_file(input_path, output_path, key):
    with open(input_path, 'rb') as f:
        original_data = f.read()
    
    encrypted_data = encrypt_data(original_data, key)
    
    with open(output_path, 'wb') as f:
        f.write(encrypted_data)
    
    print(f"Encrypted: {input_path} → {output_path}")
    return encrypted_data


def decrypt_file(input_path, output_path, key):
    with open(input_path, 'rb') as f:
        encrypted_data = f.read()
    
    decrypted_data = decrypt_data(encrypted_data, key)
    
    with open(output_path, 'wb') as f:
        f.write(decrypted_data)
    
    print(f"Decrypted: {input_path} → {output_path}")
    return decrypted_data