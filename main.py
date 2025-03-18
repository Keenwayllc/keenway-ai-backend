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
        print("Received request:", request.message)  # Debug log
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Or use "gpt-4"
            messages=[{"role": "user", "content": request.message}]
        )
        
        print("Response from OpenAI:", response)  # Debug log
        return {"response": response["choices"][0]["message"]["content"]}
    
    except openai.OpenAIError as e:
        print("OpenAI API Error:", str(e))  # Print API errors
        return {"error": "OpenAI API error. Check logs."}

    except Exception as e:
        print("Server Error:", str(e))  # Print other errors
        return {"error": "Something went wrong on the server. Check the logs."}
