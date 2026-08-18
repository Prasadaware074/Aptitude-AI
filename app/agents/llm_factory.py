import os
import logging
from typing import Optional, Any
from app.config.settings import settings

logger = logging.getLogger(__name__)

def get_llm(temperature: Optional[float] = None, structured_output_schema: Optional[Any] = None) -> Any:
    """Get ChatGoogleGenerativeAI model instance or fallback handler if API key is not configured."""
    temp = temperature if temperature is not None else settings.TEMPERATURE
    api_key = settings.GOOGLE_API_KEY or os.getenv("GOOGLE_API_KEY", "")

    if api_key:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            llm = ChatGoogleGenerativeAI(
                model=settings.MODEL_NAME,
                google_api_key=api_key,
                temperature=temp,
                max_retries=settings.MAX_RETRIES
            )
            if structured_output_schema:
                return llm.with_structured_output(structured_output_schema)
            return llm
        except Exception as e:
            logger.warning(f"Could not initialize ChatGoogleGenerativeAI: {e}. Operating in deterministic fallback mode.")
    
    return None
