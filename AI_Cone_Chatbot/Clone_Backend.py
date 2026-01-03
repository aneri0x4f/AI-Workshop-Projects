from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import httpx

app = FastAPI()

# Enable CORS so your HTML can call this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (fine for local workshop)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = "<ADD HERE>"
BASE_URL = "<ADD HERE>"

class ChatRequest(BaseModel):
    personality: str
    conversation: List[Dict[str, str]]

@app.post("/chat")
async def chat(request: ChatRequest):
    # Endpoint to chat with the AI
    try: 
        messages = [{"role": "system", "content": request.personality}] + request.conversation

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                BASE_URL,
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    # "model":"llama-3.1-8b-instant",
                    "model": "claude-sonnet-4-5-20250929",
                    "messages":messages,
                    "temperature":0.3,
                    "max_tokens":5000
                }
            )

            # string to json conversion
            data = response.json()

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=data)

            return {"reply": data["choices"][0]["message"]["content"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "AI Clone Backend is running! 🚀"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)