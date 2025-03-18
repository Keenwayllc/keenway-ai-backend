from fastapi import FastAPI
from pydantic import BaseModel
import openai
import os

app = FastAPI()

class ChatRequest(BaseModel):
    message: str

# Load OpenAI API Key from Environment Variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("❌ OpenAI API Key is missing! Set it in your environment variables.")

# Set OpenAI API Key
openai.api_key = OPENAI_API_KEY

@app.post("/chatbot")
async def chatbot(request: ChatRequest):
    try:
        print("✅ Received message:", request.message)  # Debugging log

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use GPT-4 if available
            messages=[{"role": "user", "content": request.message}]
        )

        print("✅ Response from OpenAI:", response)  # Debugging log
        return {"response": response["choices"][0]["message"]["content"]}

    except openai.error.AuthenticationError:
        print("❌ Invalid OpenAI API Key!")
        return {"error": "Invalid OpenAI API Key. Check your API key."}

    except openai.error.OpenAIError as e:
        print("❌ OpenAI API Error:", str(e))
        return {"error": f"OpenAI API error: {str(e)}"}

    except Exception as e:
        print("❌ Server Error:", str(e))
        return {"error": "Something went wrong on the server. Check logs."}
