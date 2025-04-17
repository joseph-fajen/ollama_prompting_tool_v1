import requests
import json
from typing import Dict, List, Any, Optional, Union, Tuple, Generator
from abc import ABC, abstractmethod
from conversation_manager import Message

class LLMAdapter(ABC):
    """Abstract base class for LLM API adapters"""
    
    @abstractmethod
    def generate(self, model: str, messages: List[Dict[str, str]], 
                 stream: bool = False, **kwargs) -> Union[str, Generator[str, None, None]]:
        """Generate a response from the model"""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get a list of available models"""
        pass

class OllamaAdapter(LLMAdapter):
    """Adapter for Ollama API"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def generate(self, model: str, messages: List[Dict[str, str]], 
                 stream: bool = False, **kwargs) -> Union[str, Generator[str, None, None]]:
        """Generate a response using Ollama API"""
        # For chat mode
        if len(messages) > 1:
            return self._generate_chat(model, messages, stream, **kwargs)
        # For completion mode (traditional)
        else:
            prompt = messages[0]["content"] if messages else ""
            return self._generate_completion(model, prompt, stream, **kwargs)
    
    def _generate_chat(self, model: str, messages: List[Dict[str, str]], 
                      stream: bool = False, **kwargs) -> Union[str, Generator[str, None, None]]:
        """Generate a response using Ollama chat API"""
        url = f"{self.base_url}/api/chat"
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
            "options": kwargs.get("options", {})
        }
        
        if stream:
            return self._stream_response(url, payload)
        else:
            response = self.session.post(url, json=payload, timeout=kwargs.get("timeout", 600))
            response.raise_for_status()
            response_json = response.json()
            
            if "message" in response_json:
                return response_json["message"]["content"]
            return ""
    
    def _generate_completion(self, model: str, prompt: str, 
                           stream: bool = False, **kwargs) -> Union[str, Generator[str, None, None]]:
        """Generate a response using Ollama completion API"""
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            "options": kwargs.get("options", {})
        }
        
        if stream:
            return self._stream_response(url, payload)
        else:
            response = self.session.post(url, json=payload, timeout=kwargs.get("timeout", 600))
            response.raise_for_status()
            response_json = response.json()
            return response_json.get("response", "")
    
    def _stream_response(self, url: str, payload: Dict[str, Any]) -> Generator[str, None, None]:
        """Stream response tokens"""
        with self.session.post(url, json=payload, stream=True) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if line:
                    response_json = json.loads(line)
                    if "message" in response_json:  # Chat API
                        chunk = response_json["message"].get("content", "")
                    else:  # Generate API
                        chunk = response_json.get("response", "")
                    yield chunk
    
    def get_available_models(self) -> List[str]:
        """Get list of available Ollama models"""
        try:
            url = f"{self.base_url}/api/tags"
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            models = [model["name"] for model in data.get("models", []) 
                     if "embed" not in model["name"].lower()]
            return models
        except:
            # Fall back to command line
            import subprocess
            try:
                result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
                lines = result.stdout.strip().split('\n')
                
                # Skip the header line
                if len(lines) > 1:
                    models = []
                    for line in lines[1:]:  # Skip header row
                        parts = line.split()
                        if len(parts) >= 1:
                            model_name = parts[0]
                            # Skip embedding models
                            if "embed" not in model_name.lower():
                                models.append(model_name)
                    return models
            except:
                pass
            return []

class OpenAIAdapter(LLMAdapter):
    """Adapter for OpenAI-compatible APIs"""
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })
    
    def generate(self, model: str, messages: List[Dict[str, str]], 
                 stream: bool = False, **kwargs) -> Union[str, Generator[str, None, None]]:
        """Generate a response using OpenAI-compatible API"""
        url = f"{self.base_url}/v1/chat/completions"
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 1024)
        }
        
        if stream:
            return self._stream_response(url, payload)
        else:
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            response_json = response.json()
            
            if "choices" in response_json and len(response_json["choices"]) > 0:
                return response_json["choices"][0]["message"]["content"]
            return ""
    
    def _stream_response(self, url: str, payload: Dict[str, Any]) -> Generator[str, None, None]:
        """Stream response tokens from OpenAI API"""
        with self.session.post(url, json=payload, stream=True) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if line:
                    line = line.decode("utf-8")
                    if line.startswith("data: ") and line != "data: [DONE]":
                        data = json.loads(line[6:])
                        if "choices" in data and len(data["choices"]) > 0:
                            delta = data["choices"][0].get("delta", {})
                            if "content" in delta:
                                yield delta["content"]
    
    def get_available_models(self) -> List[str]:
        """Get list of available models from OpenAI API"""
        try:
            url = f"{self.base_url}/v1/models"
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            return [model["id"] for model in data.get("data", [])]
        except:
            return []

class HuggingFaceAdapter(LLMAdapter):
    """Adapter for Hugging Face Inference API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api-inference.huggingface.co/models"
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })
    
    def generate(self, model: str, messages: List[Dict[str, str]], 
                 stream: bool = False, **kwargs) -> Union[str, Generator[str, None, None]]:
        """Generate a response using Hugging Face API"""
        url = f"{self.base_url}/{model}"
        
        # Convert messages to prompt that HF understands
        prompt = self._messages_to_prompt(messages)
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": kwargs.get("max_tokens", 1024),
                "temperature": kwargs.get("temperature", 0.7),
                "return_full_text": kwargs.get("return_full_text", False)
            }
        }
        
        # HF API doesn't support true streaming, so ignore stream parameter
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        response_json = response.json()
        
        if isinstance(response_json, list) and len(response_json) > 0:
            return response_json[0].get("generated_text", "")
        return ""
    
    def _messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert a list of messages to a prompt string for HF models"""
        result = ""
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            
            if role == "system":
                result += f"<|system|>\n{content}\n"
            elif role == "user":
                result += f"<|user|>\n{content}\n"
            elif role == "assistant":
                result += f"<|assistant|>\n{content}\n"
        
        # Add final assistant marker for generation
        if result and not result.endswith("<|assistant|>\n"):
            result += "<|assistant|>\n"
            
        return result
    
    def get_available_models(self) -> List[str]:
        """Get available models (only returns a predefined list as HF has thousands)"""
        # HF has thousands of models, so we just return popular ones
        # In a real implementation, you might want to allow specifying a model directly
        return [
            "mistralai/Mistral-7B-Instruct-v0.1",
            "meta-llama/Llama-2-7b-chat-hf",
            "gpt2",
            "bigcode/starcoder",
            "bigscience/bloom"
        ]

class LLMAdapterFactory:
    """Factory for creating API adapters"""
    
    @staticmethod
    def create_adapter(provider: str, **kwargs) -> LLMAdapter:
        """Create an adapter for the specified provider"""
        if provider == "ollama":
            base_url = kwargs.get("base_url", "http://localhost:11434")
            return OllamaAdapter(base_url)
        elif provider == "openai":
            base_url = kwargs.get("base_url", "https://api.openai.com")
            api_key = kwargs.get("api_key")
            if not api_key:
                raise ValueError("API key is required for OpenAI adapter")
            return OpenAIAdapter(base_url, api_key)
        elif provider == "huggingface":
            api_key = kwargs.get("api_key")
            if not api_key:
                raise ValueError("API key is required for HuggingFace adapter")
            return HuggingFaceAdapter(api_key)
        else:
            raise ValueError(f"Unsupported provider: {provider}")