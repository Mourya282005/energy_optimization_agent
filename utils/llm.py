import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()


def get_llm(temperature: float = 0.3):
    """Returns a configured GROQ LLM client."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not found. Create a .env file (copy .env.example) "
            "and add your key from https://console.groq.com/keys"
        )
    return ChatGroq(
        api_key=api_key,
        model="llama-3.3-70b-versatile",
        temperature=temperature,
    )
