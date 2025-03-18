from fastapi import FastAPI
from pydantic import BaseModel
import openai
import os
import requests
from bs4 import BeautifulSoup
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow your website to talk to this API (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change "*" to "https://www.gokeenway.com" for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

# Get your OpenAI API key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Missing OpenAI API key! Set OPENAI_API_KEY in environment variables.")

# Set the API key for the new OpenAI usage
openai.api_key = OPENAI_API_KEY

# System prompt to guide GPT-4
KEENWAY_CONTEXT = """
You are Hauler, the friendly AI assistant for Keenway, a final-mile delivery service in Los Angeles. 
Answer questions clearly and concisely about Keenway's services, such as fast and reliable delivery 
of auto parts, retail items, and healthcare supplies. Avoid repeating information. 
Keep your responses engaging and helpful.
"""

# Function to scrape Keenway site in real time
def scrape_keenway():
    url = "https://www.gokeenway.com"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            # Extract all paragraph text
            text = " ".join([p.get_text() for p in soup.find_all("p")])
            return text if text else "Keenway provides final-mile delivery in Los Angeles. See gokeenway.com."
        else:
            return "Keenway provides final-mile delivery in Los Angeles. See gokeenway.com."
    except Exception as e:
        print(f"Error scraping Keenway website: {str(e)}")
        return "Keenway provides final-mile delivery in Los Angeles. See gokeenway.com."

@app.post("/chatbot")
def chatbot(request: ChatRequest):
    try:
        print("Received message:", request.message)

        # Grab the latest Keenway info
        live_info = scrape_keenway()

        # Combine system instructions + website content
        full_context = f"{KEENWAY_CONTEXT}\n\nKeenway Website Info: {live_info}"

        # Use the new openai.chat.completions.create approach (not openai.ChatCompletion)
        response = openai.chat.completions.create(
            model="gpt-4",  # GPT-4 for better quality
            messages=[
                {"role": "system", "content": full_context},
                {"role": "user", "content": request.message}
            ]
        )

        print("Response from OpenAI:", response)
        return {"response": response["choices"][0]["message"]["content"]}

    except Exception as e:
        # Catch any errors, including OpenAI or scraping issues
        print("Server Error:", str(e))
        return {"error": f"Server error: {str(e)}"}
