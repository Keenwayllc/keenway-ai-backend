from fastapi import FastAPI
from pydantic import BaseModel
import openai
import os

# 1️⃣ Import CORS middleware
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 2️⃣ Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can replace ["*"] with ["https://www.gokeenway.com"] for more security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

# Load OpenAI API Key from Environment Variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Ensure the API key is set
if not OPENAI_API_KEY:
    raise ValueError("Missing OpenAI API key! Set OPENAI_API_KEY in environment variables.")

# Create OpenAI client (new format)
client = openai.OpenAI(api_key=OPENAI_API_KEY)

@app.post("/chatbot")
def chatbot(request: ChatRequest):
    try:
        print("Received message:", request.message)  # Debug log

        # Generate response using the new OpenAI format
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Change to "gpt-4" if needed
            messages=[{"role": "user", "content": request.message}]
        )

        print("Response from OpenAI:", response)  # Debug log
        return {"response": response.choices[0].message.content}

    except openai.AuthenticationError:
        print("❌ Invalid OpenAI API Key!")
        return {"error": "Invalid OpenAI API Key. Check your API key."}

    except openai.OpenAIError as e:
        print("❌ OpenAI API Error:", str(e))
        return {"error": f"OpenAI API error: {str(e)}"}

    except Exception as e:
        print("❌ Server Error:", str(e))
        return {"error": "Something went wrong on the server. Check logs."}
