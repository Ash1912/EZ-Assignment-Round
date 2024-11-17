from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models, schemas, utils, email_service
from app.database import get_db
from typing import List
from cryptography.fernet import Fernet
from app.config import SECRET_KEY

router = APIRouter(prefix="/client", tags=["Client User"])

# Encryption Key for secure URLs
encryption_key = SECRET_KEY[:32].encode()  # First 32 characters for Fernet
fernet = Fernet(encryption_key)


# --- Sign Up API ---
@router.post("/signup", response_model=schemas.UserResponse)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    hashed_password = utils.hash_password(user.password)
    new_user = models.User(email=user.email, password=hashed_password, role="client")
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Send verification email
    verification_url = f"http://localhost:8000/client/verify-email/{new_user.id}"
    email_service.send_verification_email(new_user.email, verification_url)

    return new_user


# --- Email Verification API ---
@router.get("/verify-email/{user_id}")
def verify_email(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id, models.User.role == "client").first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user.is_verified:
        return {"message": "Email already verified"}

    user.is_verified = True
    db.commit()
    return {"message": "Email verified successfully"}


# --- Login API ---
@router.post("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email, models.User.role == "client").first()
    if not user or not utils.verify_password(password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not user.is_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email not verified")

    token = utils.create_access_token({"user_id": user.id})
    return {"access_token": token, "token_type": "bearer"}


# --- List All Uploaded Files API ---
@router.get("/files", response_model=List[schemas.FileResponse])
def list_files(db: Session = Depends(get_db)):
    files = db.query(models.File).all()
    return files


# --- Download File API ---
@router.get("/download-file/{file_id}")
def download_file(file_id: int, db: Session = Depends(get_db)):
    file = db.query(models.File).filter(models.File.id == file_id).first()
    if not file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    # Encrypt the file path
    encrypted_path = fernet.encrypt(file.file_path.encode()).decode()
    download_url = f"http://localhost:8000/client/access-file/{encrypted_path}"
    return {"download-link": download_url, "message": "success"}


# --- Access Encrypted File API ---
@router.get("/access-file/{encrypted_path}")
def access_file(encrypted_path: str, db: Session = Depends(get_db)):
    try:
        decrypted_path = fernet.decrypt(encrypted_path.encode()).decode()
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid download link")

    return {"file_path": decrypted_path}
