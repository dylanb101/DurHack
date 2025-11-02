# main.py
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import List
from datetime import datetime
import shutil
import httpx
import os
import base64

load_dotenv()
app = FastAPI()

UPLOAD_DIR = "uploads"
IMAGES_DIR = "full_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextToSpeechRequest(BaseModel):
    text: str

class TextToSpeechResponse(BaseModel):
    audio: str  # base64 encoded audio

@app.post("/api/text-to-speech", response_model=TextToSpeechResponse)
async def text_to_speech(request: TextToSpeechRequest):
    """
    Convert text to speech using ElevenLabs API
    """
    api_key = os.getenv("ELEVENLABS_API_KEY")
    
    if not api_key:
        raise HTTPException(status_code=500, detail="API key not configured")
    
    # Default voice ID
    voice_id = "EXAVITQu4vr4xnSDxMaL"
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    
    headers = {
        "Accept": "audio/mpeg",
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    data = {
        "text": request.text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, headers=headers, timeout=30.0)
            response.raise_for_status()
            
            # Convert audio to base64
            audio_base64 = base64.b64encode(response.content).decode('utf-8')
            
            return TextToSpeechResponse(audio=audio_base64)
            
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"ElevenLabs API error: {str(e)}")



@app.post("/api/images-upload")
async def upload_images(files: List[UploadFile] = File(...)):
    """
    Upload multiple images to this endpoint.
    Each batch is in their own folder.
    """

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    session_dir = os.path.join(UPLOAD_DIR, f"session_{timestamp}")
    os.makedirs(session_dir, exist_ok=True)

    file_details = []

    for file in files:
        file_path = os.path.join(session_dir, file.filename)

        # Save file to disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_details.append({
            "filename": file.filename,
            "content_type": file.content_type,
            "size": os.path.getsize(file_path)
        })

    return {"uploaded_files": file_details, "timestamp": timestamp}

class PostImagesRequest(BaseModel):
    session: str

@app.post("/api/get-images-base64")
async def list_images_base64(request: PostImagesRequest):
    images_data = []
    SESSION_DIR = os.path.join(UPLOAD_DIR, f"session_{request.session}")

    for filename in os.listdir(SESSION_DIR):
        file_path = os.path.join(SESSION_DIR, filename)
        if os.path.isfile(file_path):
            with open(file_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
            images_data.append({
                "filename": filename,
                "data": f"data:image/jpeg;base64,{encoded}"
            })

    return {"images": images_data}

@app.get("/api/images/latest-base64")
async def get_latest_image_base64():
    # Get all image files from the upload directory
    image_files = [
        os.path.join(IMAGES_DIR, f)
        for f in os.listdir(IMAGES_DIR)
        if os.path.isfile(os.path.join(IMAGES_DIR, f))
           and f.lower().endswith((".png", ".jpg", ".jpeg"))
    ]

    if not image_files:
        return {"error": "No images found"}

    # Find the most recently modified image
    latest_file = max(image_files, key=os.path.getmtime)
    filename = os.path.basename(latest_file)

    # Read and encode as base64
    with open(latest_file, "rb") as f:
        encoded_string = base64.b64encode(f.read()).decode("utf-8")

    # Guess MIME type from file extension
    if filename.lower().endswith(".png"):
        mime = "image/png"
    else:
        mime = "image/jpeg"

    # Return as JSON
    return {
        "filename": filename,
        "data": f"data:{mime};base64,{encoded_string}"
    }