#!/usr/bin/env python3
"""
Centralized model configuration for MCPxA2AxAgentic-RAG system.
Uses Google Gemini for LLM and HuggingFace for embeddings.
"""

import os
import sys

# Ensure UTF-8 output encoding on Windows consoles
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from dotenv import load_dotenv, find_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
# from langchain_huggingface import HuggingFaceEmbeddings


# Load environment variables, overriding any existing OS placeholder variables
_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(_env_path):
    load_dotenv(dotenv_path=_env_path, override=True)
else:
    load_dotenv(find_dotenv(usecwd=True), override=True)

def extract_response_text(response) -> str:
    """Extract string text from an LLM response or response.content, safely handling strings and part lists."""
    content = getattr(response, "content", response)
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, str):
                parts.append(part)
            elif isinstance(part, dict) and "text" in part:
                parts.append(str(part["text"]))
            elif hasattr(part, "text"):
                parts.append(str(part.text))
            else:
                parts.append(str(part))
        return "".join(parts).strip()
    return str(content).strip()

def get_llm_model(temperature: float = 0):
    """Get LLM model name string for Google ADK LlmAgent."""
    print("[INFO] Using Google Gemini model")
    return "gemini-3.1-flash-lite"

def get_llm_model_instance(temperature: float = 0):
    """Get actual LLM model instance for direct use."""
    print("[INFO] Creating Google Gemini model instance")
    return ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite",
        temperature=temperature,
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        convert_system_message_to_human=True
    )

def get_embedding_model(use_huggingface: bool = True):
    """Get embedding model with safer Google Generative AI embeddings"""
    # Use Google embeddings (more stable)
    print("[INFO] Using Google Generative AI embeddings")
    return GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )

def get_safe_embedding_model():
    """
    Get the global embedding model instance using Google Generative AI API.
    """

    try:
        return GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
    except Exception as e:
        print(f"[WARN] gemini-embedding-001 failed: {e}")
        print("[INFO] Falling back to Google gemini-embedding-2...")
        # Ultimate fallback 
        return GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-2",
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )

# Global model instances (lazy initialization)
llm_model = None
embed_model = None

# Legacy compatibility functions for existing imports
def get_llm_model_legacy():
    """Get the global LLM model instance, creating it if needed."""
    global llm_model
    if llm_model is None:
        llm_model = get_llm_model_instance()
        print(f"[CONFIG] Created LLM model instance: {MODEL_INFO['llm_model']}")
    return llm_model

def get_embed_model_instance():
    """Get the global embedding model instance, creating it if needed."""
    global embed_model
    if embed_model is None:
        # Try the safe embedding model first, but with even more safety
        try:
            embed_model = GoogleGenerativeAIEmbeddings(
                model="models/gemini-embedding-001",
                google_api_key=os.getenv("GOOGLE_API_KEY")
            )
            print(f"[CONFIG] Created embedding model instance: {MODEL_INFO['embed_model']}")
        except Exception as e:
            print(f"[WARN] gemini-embedding-001 failed: {e}")
            print("[INFO] Falling back to Google gemini-embedding-2...")
            # Ultimate fallback 
            embed_model = GoogleGenerativeAIEmbeddings(
                model="models/gemini-embedding-2",
                google_api_key=os.getenv("GOOGLE_API_KEY")
            )
            print("[CONFIG] Created Google embedding model as fallback")
    return embed_model

# MODEL_INFO for backward compatibility (dynamic evaluation)
def get_model_info():
    """Get current model information."""
    return {
        "model2use": "google",
        "llm_model": "Google Gemini",
        "embed_model": "Google gemini-embedding-001 with fallback model gemini-embedding-2",
        "llm_provider": "Google Generative AI",
        "embed_provider": "Google"
    }

# For backward compatibility, create a property-like access
class ModelInfoDict(dict):
    def __getitem__(self, key):
        return get_model_info()[key]
    
    def get(self, key, default=None):
        return get_model_info().get(key, default)
    
    def items(self):
        return get_model_info().items()
    
    def keys(self):
        return get_model_info().keys()
    
    def values(self):
        return get_model_info().values()

MODEL_INFO = ModelInfoDict()

if __name__ == "__main__":
    print("Current model selection: google")
    model_info = get_model_info()
    print(f"LLM Model: {model_info['llm_model']}")
    print(f"Embedding Model: {model_info['embed_model']}")
    print("[SUCCESS] Models configured successfully!")
    
    # Test lazy loading
    print("\n[TEST] Testing lazy model loading:")
    test_llm = get_llm_model_legacy()
    test_embed = get_embed_model_instance()
    
    print("\n[SUMMARY] Model Usage Summary:")
    print("* Gemini: Used for LLM operations (agents and RAG)")
    print("* Google embedding model : Used for embedding operations (document processing)")