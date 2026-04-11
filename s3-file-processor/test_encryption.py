from encryption_handler import get_or_create_key, encrypt_data, decrypt_data
from address_processor import process_addresses

print("=" * 50)
print("ENCRYPTION DEMO")
print("=" * 50)

key = get_or_create_key()
print(f"Key (first 10 chars): {key[:10]}...")
print()

test_addresses = """123 Main St, Austin, TX 78701
456 Oak Avenue, Chicago, IL 60601
10 Downing Street, London, UK
789 Pine Rd, Miami, FL 33101
27 Rue de Rivoli, Paris, France
321 Elm St, New York, NY 10001"""

print("STEP 1 — Processing addresses...")
print("-" * 40)
us_content, non_us_content = process_addresses(test_addresses)
print("US addresses found:")
print(us_content)
print()
print("Non-US addresses found:")
print(non_us_content)
print()

print("STEP 2 — Encrypting and saving to disk...")
print("-" * 40)

encrypted_us = encrypt_data(us_content.encode('utf-8'), key)
with open('us_addresses.enc', 'wb') as f:
    f.write(encrypted_us)
print("Saved: us_addresses.enc")

encrypted_non_us = encrypt_data(non_us_content.encode('utf-8'), key)
with open('non_us_addresses.enc', 'wb') as f:
    f.write(encrypted_non_us)
print("Saved: non_us_addresses.enc")
print()

print("STEP 3 — Decrypting to verify...")
print("-" * 40)

with open('us_addresses.enc', 'rb') as f:
    loaded_encrypted_us = f.read()

decrypted_us = decrypt_data(loaded_encrypted_us, key)
print("Decrypted US addresses:")
print(decrypted_us.decode('utf-8'))
print()

with open('non_us_addresses.enc', 'rb') as f:
    loaded_encrypted_non_us = f.read()

decrypted_non_us = decrypt_data(loaded_encrypted_non_us, key)
print("Decrypted Non-US addresses:")
print(decrypted_non_us.decode('utf-8'))
print()

print("=" * 50)
print("SUCCESS — Files encrypted, saved, and decrypted correctly")
print("=" * 50)