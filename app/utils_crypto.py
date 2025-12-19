import base64
import time
import hmac
import hashlib
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

# -----------------------------
# Load Keys
# -----------------------------
def load_private_key(path: str):
    with open(path, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)

def load_public_key(path: str):
    with open(path, "rb") as f:
        return serialization.load_pem_public_key(f.read())

# -----------------------------
# Decrypt Seed
# -----------------------------
def decrypt_seed(encrypted_seed_b64: str) -> str:
    private_key = load_private_key("/app/student_private.pem")

    encrypted_bytes = base64.b64decode(encrypted_seed_b64)

    seed = private_key.decrypt(
        encrypted_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    return seed.decode()

# -----------------------------
# RSA Sign Commit
# -----------------------------
def sign_message_rsa_pss(private_key, message: bytes) -> str:
    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )
    return base64.b64encode(signature).decode()

# -----------------------------
# Encrypt with Public Key
# -----------------------------
def encrypt_with_public_key(public_key, message: bytes) -> str:
    encrypted = public_key.encrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    return base64.b64encode(encrypted).decode()

# -----------------------------
# 2FA Generation
# -----------------------------
def generate_2fa_code(seed: str) -> str:
    timestep = int(time.time() // 30)
    msg = f"{seed}:{timestep}".encode()
    h = hmac.new(seed.encode(), msg, hashlib.sha256).hexdigest()
    return str(int(h[:6], 16)).zfill(6)

# -----------------------------
# 2FA Verify
# -----------------------------
def verify_2fa_code(seed: str, code: str) -> bool:
    return generate_2fa_code(seed) == code