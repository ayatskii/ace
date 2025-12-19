from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.core.security import get_current_user
from app.models import User
import os
import uuid
from pathlib import Path

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
(UPLOAD_DIR / "audio").mkdir(exist_ok=True)
(UPLOAD_DIR / "images").mkdir(exist_ok=True)

@router.post("/audio")
async def upload_audio(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload audio file for speaking section"""
    # Validate file type
    if not file.content_type.startswith("audio/"):
        raise HTTPException(400, "File must be audio")
    
    # Generate unique filename
    ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = UPLOAD_DIR / "audio" / filename
    
    # Save file
    with open(filepath, "wb") as f:
        content = await file.read()
        f.write(content)
    
    return {"url": f"/uploads/audio/{filename}"}

@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload image for writing task"""
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "File must be image")
    
    ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = UPLOAD_DIR / "images" / filename
    
    with open(filepath, "wb") as f:
        content = await file.read()
        f.write(content)
    
    
    return {"url": f"/uploads/images/{filename}"}

@router.get("/files")
async def get_files(
    type: str = "all",  # all, audio, images
    current_user: User = Depends(get_current_user)
):
    """List uploaded files"""
    files = []
    
    if type in ["all", "audio"]:
        audio_dir = UPLOAD_DIR / "audio"
        if audio_dir.exists():
            for f in audio_dir.iterdir():
                if f.is_file():
                    files.append({
                        "name": f.name,
                        "type": "audio",
                        "url": f"/uploads/audio/{f.name}",
                        "size": f.stat().st_size,
                        "created_at": f.stat().st_ctime
                    })
    
    if type in ["all", "images"]:
        image_dir = UPLOAD_DIR / "images"
        if image_dir.exists():
            for f in image_dir.iterdir():
                if f.is_file():
                    files.append({
                        "name": f.name,
                        "type": "image",
                        "url": f"/uploads/images/{f.name}",
                        "size": f.stat().st_size,
                        "created_at": f.stat().st_ctime
                    })
    
    # Sort by created_at desc
    files.sort(key=lambda x: x["created_at"], reverse=True)
    return files

@router.delete("/files/{file_type}/{filename}")
async def delete_file(
    file_type: str,
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a file"""
    if file_type not in ["audio", "images"]:
        raise HTTPException(400, "Invalid file type")
        
    filepath = UPLOAD_DIR / file_type / filename
    
    if not filepath.exists():
        raise HTTPException(404, "File not found")
        
    try:
        os.remove(filepath)
    except Exception as e:
        raise HTTPException(500, f"Failed to delete file: {str(e)}")
        
    return {"message": "File deleted"}
