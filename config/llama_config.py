#!/usr/bin/env python3
"""
Llama 3.2 Configuration
======================

Configuration settings for Llama 3.2 LLM integration.
Supports multiple deployment options.
"""

import os
from typing import Dict, Any

class LlamaConfig:
    """Configuration for Llama 3.2 LLM integration"""
    
    # Deployment Types
    DEPLOYMENT_OLLAMA = "ollama"
    DEPLOYMENT_VLLM = "vllm"
    DEPLOYMENT_TRANSFORMERS = "transformers"
    DEPLOYMENT_API = "api"
    
    # Default Configuration
    DEFAULT_DEPLOYMENT = DEPLOYMENT_OLLAMA
    DEFAULT_MODEL = "llama3.2"
    DEFAULT_TEMPERATURE = 0.1
    DEFAULT_MAX_TOKENS = 2000
    DEFAULT_TIMEOUT = 30
    
    # Ollama Configuration
    OLLAMA_BASE_URL = "http://localhost:11434"
    OLLAMA_CHAT_ENDPOINT = f"{OLLAMA_BASE_URL}/api/chat"
    OLLAMA_GENERATE_ENDPOINT = f"{OLLAMA_BASE_URL}/api/generate"
    OLLAMA_TAGS_ENDPOINT = f"{OLLAMA_BASE_URL}/api/tags"
    
    # vLLM Configuration
    VLLM_BASE_URL = "http://localhost:8000"
    VLLM_CHAT_ENDPOINT = f"{VLLM_BASE_URL}/v1/chat/completions"
    
    # Model Options
    AVAILABLE_MODELS = {
        "llama3.2": "meta-llama/Llama-3.2-3B-Instruct",
        "llama3.2-1b": "meta-llama/Llama-3.2-1B-Instruct",
        "llama3.2-3b": "meta-llama/Llama-3.2-3B-Instruct",
        "llama3.2-11b": "meta-llama/Llama-3.2-11B-Vision-Instruct",
        "llama3.2-90b": "meta-llama/Llama-3.2-90B-Vision-Instruct"
    }
    
    # Generation Parameters
    GENERATION_PARAMS = {
        "temperature": DEFAULT_TEMPERATURE,
        "top_p": 0.9,
        "top_k": 40,
        "repeat_penalty": 1.1,
        "max_tokens": DEFAULT_MAX_TOKENS
    }
    
    # System Prompts
    SYSTEM_PROMPT = """You are an expert at converting natural language queries into structured API filter payloads for an IT Service Management (ITSM) system.

Your task is to analyze user queries and generate precise JSON qualification payloads that can be used to filter IT service requests.

Key principles:
1. Return ONLY valid JSON, no explanations or markdown
2. Use exact field keys and operators as specified
3. Map text values to their corresponding IDs when available
4. Use appropriate operators: "in" for ID fields, "contains" for text fields
5. If unsure about a value, omit that filter rather than guess

Always respond with a JSON object in this exact format:
{
  "qualDetails": {
    "type": "FlatQualificationRest",
    "quals": [...]
  }
}"""

    @classmethod
    def get_deployment_config(cls, deployment_type: str = None) -> Dict[str, Any]:
        """Get configuration for specific deployment type"""
        deployment_type = deployment_type or cls.DEFAULT_DEPLOYMENT
        
        configs = {
            cls.DEPLOYMENT_OLLAMA: {
                "api_endpoint": cls.OLLAMA_CHAT_ENDPOINT,
                "generate_endpoint": cls.OLLAMA_GENERATE_ENDPOINT,
                "tags_endpoint": cls.OLLAMA_TAGS_ENDPOINT,
                "requires_auth": False,
                "timeout": cls.DEFAULT_TIMEOUT
            },
            cls.DEPLOYMENT_VLLM: {
                "api_endpoint": cls.VLLM_CHAT_ENDPOINT,
                "requires_auth": False,
                "timeout": cls.DEFAULT_TIMEOUT
            },
            cls.DEPLOYMENT_TRANSFORMERS: {
                "requires_gpu": True,
                "memory_requirement": "8GB+",
                "timeout": 60
            },
            cls.DEPLOYMENT_API: {
                "api_endpoint": None,  # Must be provided
                "requires_auth": True,
                "timeout": cls.DEFAULT_TIMEOUT
            }
        }
        
        return configs.get(deployment_type, configs[cls.DEFAULT_DEPLOYMENT])
    
    @classmethod
    def get_model_path(cls, model_name: str) -> str:
        """Get full model path for given model name"""
        return cls.AVAILABLE_MODELS.get(model_name, model_name)
    
    @classmethod
    def validate_deployment(cls, deployment_type: str) -> bool:
        """Validate deployment type"""
        valid_types = [cls.DEPLOYMENT_OLLAMA, cls.DEPLOYMENT_VLLM, 
                      cls.DEPLOYMENT_TRANSFORMERS, cls.DEPLOYMENT_API]
        return deployment_type in valid_types
    
    @classmethod
    def get_environment_config(cls) -> Dict[str, Any]:
        """Get configuration from environment variables"""
        return {
            "deployment_type": os.getenv("LLAMA_DEPLOYMENT", cls.DEFAULT_DEPLOYMENT),
            "model_name": os.getenv("LLAMA_MODEL", cls.DEFAULT_MODEL),
            "api_endpoint": os.getenv("LLAMA_ENDPOINT"),
            "api_key": os.getenv("LLAMA_API_KEY"),
            "temperature": float(os.getenv("LLAMA_TEMPERATURE", cls.DEFAULT_TEMPERATURE)),
            "max_tokens": int(os.getenv("LLAMA_MAX_TOKENS", cls.DEFAULT_MAX_TOKENS)),
            "timeout": int(os.getenv("LLAMA_TIMEOUT", cls.DEFAULT_TIMEOUT))
        }

# Installation and Setup Instructions
SETUP_INSTRUCTIONS = {
    "ollama": {
        "description": "Local Ollama deployment (Recommended)",
        "requirements": [
            "Install Ollama: https://ollama.ai/download",
            "Pull Llama 3.2 model: ollama pull llama3.2",
            "Start Ollama service: ollama serve"
        ],
        "test_command": "curl http://localhost:11434/api/tags",
        "pros": ["Local deployment", "No API costs", "Fast inference", "Privacy"],
        "cons": ["Requires local resources", "Model download size"]
    },
    "vllm": {
        "description": "vLLM high-performance inference server",
        "requirements": [
            "Install vLLM: pip install vllm",
            "Start server: python -m vllm.entrypoints.openai.api_server --model meta-llama/Llama-3.2-3B-Instruct",
            "Requires GPU for optimal performance"
        ],
        "test_command": "curl http://localhost:8000/v1/models",
        "pros": ["High performance", "OpenAI-compatible API", "Batch processing"],
        "cons": ["Requires GPU", "More complex setup"]
    },
    "transformers": {
        "description": "Direct Hugging Face Transformers integration",
        "requirements": [
            "Install transformers: pip install transformers torch",
            "Requires significant GPU memory (8GB+)",
            "Model will be downloaded automatically"
        ],
        "test_command": "python -c 'from transformers import AutoTokenizer; print(\"OK\")'",
        "pros": ["Direct integration", "No external services", "Full control"],
        "cons": ["High memory usage", "Slower inference", "Complex setup"]
    },
    "api": {
        "description": "External API endpoint (Hugging Face, Replicate, etc.)",
        "requirements": [
            "API endpoint URL",
            "API key (if required)",
            "OpenAI-compatible format preferred"
        ],
        "test_command": "curl -X POST [YOUR_ENDPOINT] -H 'Authorization: Bearer [API_KEY]'",
        "pros": ["No local resources", "Managed service", "Scalable"],
        "cons": ["API costs", "Internet dependency", "Latency"]
    }
}

def print_setup_guide():
    """Print setup guide for Llama 3.2 integration"""
    print("🦙 Llama 3.2 Setup Guide")
    print("=" * 50)
    
    for deployment, info in SETUP_INSTRUCTIONS.items():
        print(f"\n📋 {deployment.upper()}: {info['description']}")
        print("Requirements:")
        for req in info['requirements']:
            print(f"  • {req}")
        print(f"Test: {info['test_command']}")
        print(f"Pros: {', '.join(info['pros'])}")
        print(f"Cons: {', '.join(info['cons'])}")
    
    print("\n🚀 Quick Start (Ollama - Recommended):")
    print("1. curl -fsSL https://ollama.ai/install.sh | sh")
    print("2. ollama pull llama3.2")
    print("3. ollama serve")
    print("4. Set environment: export LLAMA_DEPLOYMENT=ollama")
    print("5. Restart the API server")

if __name__ == "__main__":
    print_setup_guide()
