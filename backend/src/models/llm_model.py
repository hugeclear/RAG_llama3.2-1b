from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from typing import Optional
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class LLMConfig:
    max_length: int = 512
    temperature: float = 0.7
    top_p: float = 0.9
    repetition_penalty: float = 1.2
    do_sample: bool = True

class LlamaModel:
    def __init__(self):
        self.model_id = "meta-llama/Llama-3.2-1b"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.tokenizer = None
        print(f"Initializing LlamaModel with device: {self.device}")

    def load_model(self) -> bool:
        """モデルのロード"""
        try:
            print("Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_id,
                token=True
            )
            
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            print("Loading model...")
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_id,
                device_map="auto",
                torch_dtype=torch.float16,
                token=True,
                low_cpu_mem_usage=True
            )
            
            print("Model loaded successfully!")
            return True
            
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            return False
    
    async def generate_response(
        self,
        prompt: str,
        max_length: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9
    ) -> Optional[str]:
        """応答の生成"""
        if not self.model or not self.tokenizer:
            if not self.load_model():
                return None

        try:
            print(f"\nGenerating response for prompt:\n{prompt}\n")
            
            # 入力の準備
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=max_length//2
            ).to(self.device)
            
            # 生成パラメータ
            generation_config = {
                "max_length": max_length,
                "min_length": 50,  # 最小長さを設定
                "temperature": temperature,
                "top_p": top_p,
                "do_sample": True,
                "pad_token_id": self.tokenizer.pad_token_id,
                "eos_token_id": self.tokenizer.eos_token_id,
                "repetition_penalty": 1.2,
                "no_repeat_ngram_size": 3,
                "num_return_sequences": 1,
                "early_stopping": True
            }
            
            # 生成
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    **generation_config
                )
            
            # デコード
            full_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # プロンプト部分を除去してレスポンスを取得
            response = full_text[len(prompt):].strip()
            print(f"Generated response:\n{response}\n")
            
            return response if response else "申し訳ありません。適切な回答を生成できませんでした。"
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "エラーが発生しました。もう一度お試しください。"

    def __del__(self):
        """クリーンアップ"""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            print("GPU memory cleared")