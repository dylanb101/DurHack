from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


app = FastAPI()

# Enable CORS so the React app can make requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "API is running!"}


class TextInput(BaseModel):
    text: str

@app.post("/api/echo")
async def echo_text(input_data: TextInput):
    """
    Endpoint that returns whatever text was sent to it
    """
    return {
        "message": "Text received successfully",
        "received_text": input_data.text
    }

# To run: uvicorn filename:app --reload