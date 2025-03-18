from fastapi import FastAPI
from pydantic import BaseModel
import openai
import os
import requests
from bs4 import BeautifulSoup
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# This helps our website talk to our API from any place.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can change "*" to your domain later for more security.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# This is the structure of the message our API expects.
class ChatRequest(BaseModel):
    message: str

# Get our secret OpenAI key from the environment (so we don't show it in the code).
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Missing OpenAI API key! Set it in environment variables.")

# Set the key for OpenAI.
openai.api_key = OPENAI_API_KEY

# This tells GPT-4 how to behave: be friendly, professional, and talk about Keenway.
KEENWAY_CONTEXT = """
You are Hauler, the friendly AI assistant for Keenway, a final-mile delivery service in Los Angeles. 
Answer questions clearly and helpfully. Focus on Keenway's services, such as fast and reliable delivery of auto parts, retail items, healthcare supplies, and more. 
Do not repeat yourself and always provide accurate information based on www.gokeenway.com.
"""

# This function fetches the latest text from the Keenway website in real-time.
def scrape_keenway():
    url = "https://www.gokeenway.com"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            text = " ".join([p.get_text() for p in soup.find_all("p")])
            return text if text else "Keenway provides final-mile delivery services in Los Angeles. Visit www.gokeenway.com for details."
        else:
            return "Keenway provides final-mile delivery services in Los Angeles. Visit www.gokeenway.com for details."
    except Exception as e:
        print(f"Error fetching Keenway website: {str(e)}")
        return "Keenway provides final-mile delivery services in Los Angeles. Visit www.gokeenway.com for details."

# This is our chatbot endpoint.
@app.post("/chatbot")
def chatbot(request: ChatRequest):
    try:
        print("Received message:", request.message)
        # Get the latest info from the website.
        live_keenway_info = scrape_keenway()
        # Combine our custom instructions and the live website info.
        full_context = f"{KEENWAY_CONTEXT}\nKeenway website info: {live_keenway_info}"
        
        # Ask GPT-4 to answer using our instructions and the user's message.
        response = openai.ChatCompletion.create(
            model="gpt-4",  # We are using GPT-4 now.
            messages=[
                {"role": "system", "content": full_context},
                {"role": "user", "content": request.message}
            ]
        )
        
        print("Response from OpenAI:", response)
        # Return the answer from GPT-4.
        return {"response": response["choices"][0]["message"]["content"]}
    
    except openai.error.AuthenticationError:
        print("Invalid OpenAI API Key!")
        return {"error": "Invalid OpenAI API Key. Check your API key."}
    
    except openai.error.OpenAIError as e:
        print("OpenAI API Error:", str(e))
        return {"error": f"OpenAI API error: {str(e)}"}
    
    except Exception as e:
        print("Server Error:", str(e))
        return {"error": "Something went wrong on the server. Check logs."}
