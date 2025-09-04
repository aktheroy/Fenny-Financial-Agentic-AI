import os
import platform
from pathlib import Path
from llama_cpp import Llama
from typing import Dict, Any, List, Optional
import logging

# Set Metal support for Apple Silicon before importing llama_cpp
if platform.system() == "Darwin":
    os.environ["LLAMA_METAL"] = "1"  # Enable Metal backend

from llama_cpp import Llama  # Import after setting env vars

logger = logging.getLogger(__name__)



class FinanceLLM:
    """Interface for the finance-specific LLM using GGUF format"""

    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the LLM with the finance-chat model

        Args:
            model_path: Path to the GGUF model file. If None, will use default location
        """
        self.model = None
        self.model_path = model_path

        # Try to find the model if path not provided
        if not self.model_path:
            # CHANGED FROM Q5_K_S TO Q4_K_M IN ALL PATHS
            possible_paths = [
                "data/models/finance-chat.Q4_K_M.gguf",
                "data/models/.cache/huggingface/finance-chat.Q4_K_M.gguf",
                "data/models/finance-chat.Q4_K_M.gguf",
            ]

            for path in possible_paths:
                if os.path.exists(path):
                    self.model_path = path
                    break

        # Download model if not found
        if not self.model_path or not os.path.exists(self.model_path):
            try:
                from .download_model import download_finance_model
                self.model_path = download_finance_model()
            except Exception as e:
                logger.error(f"Failed to download model: {str(e)}")
                raise RuntimeError(
                    "Could not initialize LLM: Model not found and download failed"
                ) from e

        # Initialize the model with Apple Silicon optimizations
        self._initialize_model()

    def _initialize_model(self):
        """Initialize the Llama model with Apple Silicon optimizations"""
        logger.info(f"Loading finance model from {self.model_path}")

        try:
            # Apple Silicon optimizations:
            # - n_gpu_layers: Offload as many layers as possible to GPU (Metal)
            # - n_ctx: Context window size (2048 is safe for most financial conversations)
            # - n_threads: Use all available CPU cores
            # CHANGED: Increased GPU layers for better Apple Silicon performance with Q4 quantization
            self.model = Llama(
                model_path=self.model_path,
                n_gpu_layers=35,
                n_ctx=4096,
                n_threads=os.cpu_count(),
                verbose=False,
            )
            logger.info("Finance LLM initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {str(e)}")
            raise

    def generate_response(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.95,
        stream: bool = False,
    ) -> str:
        """
        Generate a response from the LLM

        Args:
            prompt: Input prompt for the model
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            stream: Whether to stream tokens (not used in this implementation)

        Returns:
            Generated response text
        """
        if not self.model:
            raise RuntimeError("LLM not initialized")

        logger.debug(f"Generating response with prompt: {prompt[:100]}...")

        try:
            # Generate response
            response = self.model(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                echo=False,
                stop=["</s>", "User:", "Assistant:"],
            )

            # Extract generated text
            generated_text = response["choices"][0]["text"].strip()

            logger.debug(f"Generated response: {generated_text[:100]}...")
            return generated_text

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "I encountered an error while processing your request. Please try again."

    def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 512,
        temperature: float = 0.7,
    ) -> str:
        """
        Chat interface following the finance-chat model's expected format

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            Generated response text
        """
        # Format messages according to finance-chat template
        prompt = self.format_prompt(messages)
        return self.generate_response(
            prompt, max_tokens=max_tokens, temperature=temperature
        )

    def format_prompt(self, messages: List[Dict[str, str]]) -> str:
        """
        Format messages into the prompt template expected by finance-chat

        Expected format:
        [INST] <<SYS>>
        You are a financial expert. You are helpful and harmless.
        <</SYS>>

        {user_input} [/INST]
        """
        system_message = "You are a financial expert assistant named Fenny. You provide accurate, helpful information about finance, investing, and financial documents. Be concise and professional."

        # Start with system message
        prompt = f"[INST] <<SYS>>\n{system_message}\n<</SYS>>\n\n"

        # Process messages
        for i, msg in enumerate(messages):
            if msg["role"] == "user":
                # User message
                prompt += f"{msg['content']} [/INST]\n"
            elif msg["role"] == "assistant":
                # Assistant response
                prompt += f"{msg['content']}\n"
                # Add separator for next user message if not last message
                if i < len(messages) - 1:
                    prompt += "<s>[INST] "

        return prompt
