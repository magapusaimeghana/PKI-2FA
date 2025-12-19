from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

from utils_crypto import decrypt_seed, generate_2fa_code, verify_2fa_code

app = FastAPI()

DATA_DIR = "/data"
SEED_FILE = f"{DATA_DIR}/seed.txt"

class SeedRequest(BaseModel):
    encrypted_seed: str

class VerifyRequest(BaseModel):
    code: str

@app.get("/")
def root():
    return {"message": "PKI 2FA student service running"}

# -----------------------------
# Decrypt Seed
# -----------------------------
@app.post("/decrypt-seed")
def decrypt_seed_endpoint(req: SeedRequest):
    try:
        seed = decrypt_seed(req.encrypted_seed)

        os.makedirs(DATA_DIR, exist_ok=True)
        with open(SEED_FILE, "w") as f:
            f.write(seed)

        return {"status": "seed stored"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# -----------------------------
# Generate 2FA
# -----------------------------
@app.get("/generate-2fa")
def generate_2fa():
    try:
        with open(SEED_FILE, "r") as f:
            seed = f.read().strip()

        return {"code": generate_2fa_code(seed)}

    except FileNotFoundError:
        raise HTTPException(status_code=400, detail="Seed not initialized")

# -----------------------------
# Verify 2FA
# -----------------------------
@app.post("/verify-2fa")
def verify_2fa(req: VerifyRequest):
    try:
        with open(SEED_FILE, "r") as f:
            seed = f.read().strip()

        return {"valid": verify_2fa_code(seed, req.code)}

    except FileNotFoundError:
        raise HTTPException(status_code=400, detail="Seed not initialized")