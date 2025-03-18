from fastapi import FastAPI
from pydantic import BaseModel
import openai
import os

app = FastAPI()

class ChatRequest(BaseModel):
    message: str

# Load OpenAI API Key from Environment Variables
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.post("/chatbot")
def chatbot(request: ChatRequest):
    try:
        print("Received message:", request.message)  # Debugging log

        # Ensure the API key is loaded
        if not openai.api_key:
            print("❌ OpenAI API Key is missing!")
            return {"error": "OpenAI API Key is not set."}

        # Send request to OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": request.message}]
        )

        print("Response from OpenAI:", response)  # Debugging log
        return {"response": response["choices"][0]["message"]["content"]}

    except openai.error.AuthenticationError:
        print("❌ Invalid OpenAI API Key!")
        return {"error": "Invalid OpenAI API Key. Check your API key."}

    except openai.error.OpenAIError as e:
        print("❌ OpenAI API Error:", str(e))
        return {"error": "OpenAI API error. Check logs."}

    except Exception as e:
        print("❌ Server Error:", str(e))
        return {"error": "Something went wrong on the server. Check the logs."}
