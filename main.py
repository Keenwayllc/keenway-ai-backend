from fastapi import FastAPI
from pydantic import BaseModel
import openai
import os
import requests
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

# Load OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Missing OpenAI API key! Set OPENAI_API_KEY in environment variables.")

openai.api_key = OPENAI_API_KEY

# Chatbot system instructions
KEENWAY_CONTEXT = """
You are Keenway AI Assistant, a smart chatbot for final-mile delivery services. 
Answer questions accurately and concisely, keeping responses clear and helpful.
Do **not** display full URLs. Use:
  - **[Login](https://gokeenway.tookan.in/page/login)**
  - **[Sign Up](https://gokeenway.tookan.in/page/register)**
  - **[Book A Delivery](https://gokeenway.tookan.in/page/order)**
"""

# Optimized Chat Endpoint
@app.post("/chatbot")
def chatbot(request: ChatRequest):
    try:
        print("Received message:", request.message)

        # Reduce response time with streaming
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": KEENWAY_CONTEXT},
                {"role": "user", "content": request.message}
            ],
            stream=True  # Enables real-time response
        )

        collected_response = ""
        for chunk in response:
            if "choices" in chunk and chunk["choices"]:
                collected_response += chunk["choices"][0]["delta"].get("content", "")

        print("Response:", collected_response)
        return {"response": collected_response}

    except Exception as e:
        print("Server Error:", str(e))
        return {"error": f"Server error: {str(e)}"}
