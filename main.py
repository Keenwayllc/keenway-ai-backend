from fastapi import FastAPI
from pydantic import BaseModel
import openai
import os
import requests
from bs4 import BeautifulSoup
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS so other websites can talk to our API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For security, you can change this to your domain later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

# Load our secret API key from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Missing OpenAI API key! Set OPENAI_API_KEY in environment variables.")

openai.api_key = OPENAI_API_KEY

# System prompt that instructs GPT-4 how to behave
KEENWAY_CONTEXT = """
You are Hauler, the friendly AI assistant for Keenway, a final-mile delivery service in Los Angeles. 
Answer questions clearly and concisely about Keenway's services, such as fast and reliable delivery of auto parts, 
retail items, and healthcare supplies. Always include a note that customers can create an account by clicking "Get Started" 
at https://gokeenway.tookan.in/page/register, or if they already have an account, they can log in at https://gokeenway.tookan.in/page/login. 
Do not repeat information unnecessarily. Keep your responses engaging and helpful.
"""

# Function to scrape the Keenway website for real-time info
def scrape_keenway():
    url = "https://www.gokeenway.com"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            text = " ".join([p.get_text() for p in soup.find_all("p")])
            return text if text else "Keenway provides final-mile delivery services in Los Angeles. Visit gokeenway.com for details."
        else:
            return "Keenway provides final-mile delivery services in Los Angeles. Visit gokeenway.com for details."
    except Exception as e:
        print("Error scraping Keenway website:", str(e))
        return "Keenway provides final-mile delivery services in Los Angeles. Visit gokeenway.com for details."

@app.post("/chatbot")
def chatbot(request: ChatRequest):
    try:
        print("Received message:", request.message)
        # Get the latest website info in real-time
        live_info = scrape_keenway()
        # Combine our system instructions with the live info
        full_context = f"{KEENWAY_CONTEXT}\n\nKeenway Website Info: {live_info}"

        # Corrected OpenAI API call
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": full_context},
                {"role": "user", "content": request.message}
            ]
        )

        answer = response["choices"][0]["message"]["content"]
        print("Response from OpenAI:", answer)
        return {"response": answer}

    except Exception as e:
        print("Server Error:", str(e))
        return {"error": f"Server error: {str(e)}"}
