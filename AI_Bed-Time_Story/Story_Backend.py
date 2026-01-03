from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import httpx
import random

app = FastAPI()

# Enable CORS so your HTML can call this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (fine for local projects)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = "<ADD HERE>"
BASE_URL = "<ADD HERE>"

# Story themes and characters for variety
THEMES = [
    "a magical forest adventure",
    "a journey to a candy kingdom",
    "a friendly dragon's day",
    "underwater sea adventures",
    "a trip to the moon",
    "talking animals in the garden",
    "a little wizard's first spell",
    "a teddy bear comes to life"
]

CHARACTERS = [
    "a brave little bunny",
    "a curious kitten",
    "a friendly bear cub",
    "a wise owl",
    "a playful puppy",
    "a kind elephant",
    "a silly monkey",
    "a gentle deer"
]

class StoryRequest(BaseModel):
    child_name: str = "little one"
    age: int = 5

@app.post("/generate-story")
async def generate_story(request: StoryRequest):
    """Generate a bedtime story with AI"""
    try:
        # Randomly select theme and character
        theme = random.choice(THEMES)
        character = random.choice(CHARACTERS)
        
        # Create a child-friendly story prompt
        story_prompt = f"""Create a short, gentle bedtime story (about 150-200 words) for a {request.age}-year-old child named {request.child_name}.

Theme: {theme}
Main character: {character}

The story should be:
- Calming and peaceful, perfect for bedtime
- Have a gentle lesson about kindness, friendship, or bravery
- End with the character going to sleep or finding peace
- Use simple, age-appropriate language
- Be wholesome and sweet

Write the complete story now."""

        async with httpx.AsyncClient(timeout=60.0) as client:
            # Generate story text
            story_response = await client.post(
                BASE_URL,
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "claude-sonnet-4-5-20250929",
                    "messages": [
                        {"role": "user", "content": story_prompt}
                    ],
                    "temperature": 0.8,
                    "max_tokens": 1000
                }
            )

            story_data = story_response.json()
            
            if story_response.status_code != 200:
                raise HTTPException(status_code=story_response.status_code, detail=story_data)

            story_text = story_data["choices"][0]["message"]["content"]

            # Generate image prompt based on the story
            image_prompt = f"A cute, colorful children's book illustration of {character} in {theme}. Soft, warm colors. Gentle, friendly style. Suitable for young children. Dreamy bedtime atmosphere."

            # Generate image
            image_response = await client.post(
                BASE_URL,
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "claude-sonnet-4-5-20250929",
                    "messages": [
                        {
                            "role": "user", 
                            "content": f"Generate an image: {image_prompt}"
                        }
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1000
                }
            )

            image_data = image_response.json()

            return {
                "story": story_text,
                "theme": theme,
                "character": character,
                "image_prompt": image_prompt,
                "status": "success"
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(request: dict):
    """General chat endpoint for interactive storytelling"""
    try: 
        messages = request.get("messages", [])

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                BASE_URL,
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "claude-sonnet-4-5-20250929",
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
            )

            data = response.json()

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=data)

            return {"reply": data["choices"][0]["message"]["content"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Bedtime Story Generator Backend is running! 🌙✨"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)