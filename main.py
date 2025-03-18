from fastapi import FastAPI
from pydantic import BaseModel
import openai
import os

app = FastAPI()

class ChatRequest(BaseModel):
    message: str

# Load OpenAI API Key from Environment Variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

@app.post("/chatbot")
def chatbot(request: ChatRequest):
    try:
        print("Received message:", request.message)  # Debugging log

        # Ensure API key exists
        if not OPENAI_API_KEY:
            print("❌ OpenAI API Key is missing!")
            return {"error": "OpenAI API Key is not set."}

        # Use OpenAI's new function calling structure
        client = openai.OpenAI(api_key=OPENAI_API_KEY)

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Use GPT-4 if available
            messages=[{"role": "user", "content": request.message}]
        )

        print("Response from OpenAI:", response)  # Debugging log
        return {"response": response.choices[0].message.content}

    except openai.AuthenticationError:
        print("❌ Invalid OpenAI API Key!")
        return {"error": "Invalid OpenAI API Key. Check your API key."}

    except openai.OpenAIError as e:
        print("❌ OpenAI API Error:", str(e))
        return {"error": "OpenAI API error. Check logs."}

    except Exception as e:
        print("❌ Server Error:", str(e))
        return {"error": "Something went wrong on the server. Check logs."}
