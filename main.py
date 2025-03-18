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

# Load OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Missing OpenAI API key! Set OPENAI_API_KEY in environment variables.")

openai.api_key = OPENAI_API_KEY

# System prompt that instructs GPT-4 how to behave
KEENWAY_CONTEXT = """
You are Keenway AI Assistant, the friendly AI helper for Keenway, a final-mile delivery service in Los Angeles. 
Answer questions clearly and concisely about Keenway's services, such as fast and reliable delivery of auto parts, 
retail items, and healthcare supplies.

### Important:
- Do **not** display raw URLs.
- Always format links correctly, like this:
  - **[Login](https://gokeenway.tookan.in/page/login)**
  - **[Sign Up](https://gokeenway.tookan.in/page/register)**
  - **[Get Started](https://gokeenway.tookan.in/page/register)**
  - **[Book A Delivery](https://gokeenway.tookan.in/page/order)**

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

# Function to format links properly
def format_links(response_text):
    """Replace raw URLs with clickable text."""
    replacements = {
        "https://gokeenway.tookan.in/page/login": "**[Login](https://gokeenway.tookan.in/page/login)**",
        "https://gokeenway.tookan.in/page/register": "**[Sign Up](https://gokeenway.tookan.in/page/register)**",
        "https://gokeenway.tookan.in/page/order": "**[Book A Delivery](https://gokeenway.tookan.in/page/order)**"
    }

    for url, markdown_link in replacements.items():
        response_text = response_text.replace(url, markdown_link)
    
    return response_text

@app.post("/chatbot")
def chatbot(request: ChatRequest):
    try:
        print("Received message:", request.message)
        
        # Get the latest website info in real-time
        live_info = scrape_keenway()
        
        # Combine instructions with real-time website data
        full_context = f"{KEENWAY_CONTEXT}\n\nKeenway Website Info: {live_info}"

        # Generate response using GPT-4
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": full_context},
                {"role": "user", "content": request.message}
            ]
        )

        raw_answer = response["choices"][0]["message"]["content"]
        formatted_answer = format_links(raw_answer)  # Ensure links are properly formatted

        print("Response from OpenAI:", formatted_answer)
        return {"response": formatted_answer}

    except Exception as e:
        print("Server Error:", str(e))
        return {"error": f"Server error: {str(e)}"}
