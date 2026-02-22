from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
import os
class LLMFactory():
    @staticmethod
    def create_llm(model_name: str = "gemini-2.5-flash-lite", temp: float = 0.3, max_retries: int = 3):
        GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
        if model_name.startswith("gemini"):
            return ChatGoogleGenerativeAI(model=model_name, temperature=temp, api_key=GEMINI_API_KEY, max_retries=max_retries)
        else:
            raise ValueError(f"Unsupported model: {model_name}")
