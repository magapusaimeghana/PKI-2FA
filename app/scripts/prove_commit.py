import sys
import subprocess
from pathlib import Path

# -------------------------------------------------
# Fix Python path so utils_crypto can be imported
# -------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT / "app"))

from utils_crypto import (
    load_private_key,
    load_public_key,
    sign_message_rsa_pss,
    encrypt_with_public_key,
)

# -------------------------------------------------
# Key paths (relative to repo root)
# -------------------------------------------------
STUDENT_PRIVATE_KEY = "app/student_private.pem"
INSTRUCTOR_PUBLIC_KEY = "app/instructor_public.pem"


def get_commit_hash():
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"]
    ).decode().strip()


if __name__ == "__main__":
    print("\n--- PKI 2FA Commit Proof Generator ---\n")

    repo_url = subprocess.check_output(
        ["git", "config", "--get", "remote.origin.url"]
    ).decode().strip()

    commit_hash = get_commit_hash()

    print("Repo URL:", repo_url)
    print("Commit Hash:", commit_hash)

    # Message to sign (IMPORTANT: repo|commit)
    message = f"{repo_url}|{commit_hash}".encode()

    # Load keys
    private_key = load_private_key(STUDENT_PRIVATE_KEY)
    public_key = load_public_key(INSTRUCTOR_PUBLIC_KEY)

    # Sign commit
    signature_b64 = sign_message_rsa_pss(private_key, message)

    # Get decrypted seed from user
    seed = input("Enter decrypted seed: ").strip()

    # Encrypt seed for instructor
    encrypted_seed_b64 = encrypt_with_public_key(public_key, seed.encode())

    print("\n--- SUBMIT THESE ---")
    print("Repo URL:", repo_url)
    print("Commit Hash:", commit_hash)
    print("Encrypted Signature:", signature_b64)
    print("Encrypted Seed:", encrypted_seed_b64)