from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from app import models, utils
from app.database import get_db
import shutil

router = APIRouter(prefix="/ops", tags=["Ops User"])

@router.post("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email, models.User.role == "ops").first()
    if not user or not utils.verify_password(password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return {"access_token": utils.create_access_token({"user_id": user.id}), "token_type": "bearer"}

@router.post("/upload-file")
def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    allowed_types = ["application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                     "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                     "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    db_file = models.File(filename=file.filename, file_path=file_path, uploaded_by=1)  # Replace with actual user ID
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return {"message": "File uploaded successfully", "file": db_file}
