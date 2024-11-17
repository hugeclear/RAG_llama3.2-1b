from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from typing import Optional
import os
from huggingface_hub import login
import accelerate  # 追加

class LlamaModel:
    def __init__(self):
        self.model_id = "meta-llama/Llama-3.2-1b"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.tokenizer = None
        print(f"Initializing LlamaModel with device: {self.device}")
        print(f"Accelerate version: {accelerate.__version__}")

    def load_model(self) -> bool:
        """Load the model and tokenizer"""
        try:
            print("Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_id,
                token=True
            )

            print("Loading model...")
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_id,
                device_map="auto",
                torch_dtype=torch.float16,
                token=True,
                low_cpu_mem_usage=True  # 追加
            )

            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                print("Set pad_token to eos_token")

            print("Model loaded successfully!")
            return True

        except Exception as e:
            print(f"Error loading model: {str(e)}")
            print("\nPlease ensure you have:")
            print("1. Valid HuggingFace credentials")
            print("2. Access to the LLaMA model")
            print("3. Sufficient GPU memory")
            print(f"4. Current device: {self.device}")
            print(f"5. Available GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB") if torch.cuda.is_available() else None
            return False

    def generate(self, prompt: str, max_length: int = 100) -> Optional[str]:
        if not self.model or not self.tokenizer:
            print("Model not loaded")
            return None

        try:
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                pad_token_id=self.tokenizer.pad_token_id,
                do_sample=True,
                temperature=0.7,
                top_p=0.9
            )
            return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        except Exception as e:
            print(f"Error generating text: {str(e)}")
            return None