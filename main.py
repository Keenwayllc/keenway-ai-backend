from fastapi import FastAPI
from pydantic import BaseModel
import openai
import os
import requests
from bs4 import BeautifulSoup
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Let your website talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # replace "*" with "https://www.gokeenway.com" for more security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

# Load the secret key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Missing OpenAI API key! Set OPENAI_API_KEY in environment variables.")

# Tell OpenAI which key to use
openai.api_key = OPENAI_API_KEY

# A system prompt telling GPT-4 how to behave
KEENWAY_CONTEXT = """
You are Hauler, the friendly AI assistant for Keenway, a final-mile delivery service in Los Angeles. 
Answer questions clearly and concisely about Keenway's services, such as fast and reliable delivery 
of auto parts, retail items, and healthcare supplies. Avoid repeating information. 
Keep your responses engaging and helpful.
"""

def scrape_keenway():
    """Scrape the Keenway website in real-time for updated info."""
    url = "https://www.gokeenway.com"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            text = " ".join([p.get_text() for p in soup.find_all("p")])
            return text if text else "Keenway provides final-mile delivery in Los Angeles. See gokeenway.com."
        else:
            return "Keenway provides final-mile delivery in Los Angeles. See gokeenway.com."
    except Exception as e:
        print("Error scraping Keenway website:", str(e))
        return "Keenway provides final-mile delivery in Los Angeles. See gokeenway.com."

@app.post("/chatbot")
def chatbot(request: ChatRequest):
    """Chatbot endpoint: receives a user message, scrapes Keenway site, and asks GPT-4 for an answer."""
    try:
        print("Received message:", request.message)
        
        # Grab updated Keenway info
        live_info = scrape_keenway()
        
        # Combine system instructions + website content
        full_context = f"{KEENWAY_CONTEXT}\n\nKeenway Website Info: {live_info}"
        
        # Ask GPT-4 using the stable approach in openai==0.27.2
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": full_context},
                {"role": "user", "content": request.message}
            ]
        )
        
        # GPT-4's text answer
        answer = response.choices[0].message.content
        print("GPT-4 Response:", answer)
        
        return {"response": answer}
    
    except Exception as e:
        # Catch any error, show it in logs, and return a simple message
        print("Server Error:", str(e))
        return {"error": f"Server error: {str(e)}"}
