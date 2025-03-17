from fastapi import FastAPI
from pydantic import BaseModel
import openai
import os  # Import os to read environment variables

app = FastAPI()

# Define request structure
class ChatRequest(BaseModel):
    message: str

# Load OpenAI API Key from Environment Variables
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.post("/chatbot")
def chatbot(request: ChatRequest):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # You can use GPT-4 if available
        messages=[{"role": "user", "content": request.message}]
    )
    return {"response": response["choices"][0]["message"]["content"]}
