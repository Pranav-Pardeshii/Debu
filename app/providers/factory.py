from app.providers.gemini_provider import GeminiProvider, LLMProvider

def get_provider(model_name: str) -> LLMProvider:
    if model_name.startswith("gemini"):
        return GeminiProvider()
    raise ValueError(f"Unknown model: {model_name}")