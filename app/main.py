from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
import time

# Import crypto functions from your utils file
from app.utils_crypto import (
    load_private_key,
    decrypt_seed,
    generate_totp_code,
    verify_totp_code
)

DATA_DIR = Path("/data")
SEED_FILE = DATA_DIR / "seed.txt"
PRIVATE_KEY_PATH = Path("student_private.pem")

app = FastAPI()

# Request Models
class DecryptRequest(BaseModel):
    encrypted_seed: str

class VerifyRequest(BaseModel):
    code: str


# -----------------------------
#  /decrypt-seed  (POST)
# -----------------------------
@app.post("/decrypt-seed")
async def decrypt_seed_endpoint(req: DecryptRequest):
    # Load private key
    try:
        private_key = load_private_key(PRIVATE_KEY_PATH)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load private key: {e}")

    # Decrypt seed
    try:
        hex_seed = decrypt_seed(req.encrypted_seed, private_key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Decryption failed: {e}")

    # Save to persistent storage
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(SEED_FILE, "w") as f:
        f.write(hex_seed)

    return {"status": "ok"}


# -----------------------------
#  /generate-2fa  (GET)
# -----------------------------
@app.get("/generate-2fa")
async def generate_2fa():
    if not SEED_FILE.exists():
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

    hex_seed = SEED_FILE.read_text().strip()

    # Generate code
    try:
        code = generate_totp_code(hex_seed)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TOTP generation failed: {e}")

    # Remaining validity
    valid_for = 30 - (int(time.time()) % 30)

    return {"code": code, "valid_for": valid_for}


# -----------------------------
#  /verify-2fa  (POST)
# -----------------------------
@app.post("/verify-2fa")
async def verify_2fa(req: VerifyRequest):

    if not req.code:
        raise HTTPException(status_code=400, detail="Missing code")

    if not SEED_FILE.exists():
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

    hex_seed = SEED_FILE.read_text().strip()

    # Verify with ±1 time window
    try:
        valid = verify_totp_code(hex_seed, req.code, valid_window=1)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification failed: {e}")

    return {"valid": bool(valid)}
