from fastapi import FastAPI
from pydantic import BaseModel
import openai
import os
import requests
from bs4 import BeautifulSoup
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS for frontend chatbot integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Set to ["https://www.gokeenway.com"] for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

# Load OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Missing OpenAI API key! Set OPENAI_API_KEY in environment variables.")

# Create OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# **Function to Scrape Keenway Website in Real-Time**
def scrape_keenway():
    url = "https://www.gokeenway.com"
    try:
        response = requests.get(url, timeout=10)  # Set timeout to prevent long waits
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            text = " ".join([p.get_text() for p in soup.find_all("p")])  # Extracts text from <p> tags
            return text if text else "Keenway provides final-mile delivery services in Los Angeles. Visit www.gokeenway.com for details."
        else:
            return "Keenway provides final-mile delivery services in Los Angeles. Visit www.gokeenway.com for details."
    except Exception as e:
        print(f"❌ Error fetching Keenway website: {str(e)}")
        return "Keenway provides final-mile delivery services in Los Angeles. Visit www.gokeenway.com for details."

@app.post("/chatbot")
def chatbot(request: ChatRequest):
    try:
        print("Received message:", request.message)

        # **Fetch the latest Keenway info before responding**
        live_keenway_knowledge = scrape_keenway()

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Upgrade to GPT-4 if needed
            messages=[
                {"role": "system", "content": f"Keenway website info: {live_keenway_knowledge}"},
                {"role": "user", "content": request.message}
            ]
        )

        print("Response from OpenAI:", response)
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
