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
    num_beams: int = 5  # ビームサーチのパラメータを追加

class LlamaModel:
    def __init__(self):
        self.model_id = "meta-llama/Llama-3.2-1b"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.tokenizer = None
        self.config = LLMConfig()
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
        max_length: int = 2048,
        temperature: float = 0.7,
        top_p: float = 0.9
    ) -> Optional[str]:
        """Generate a response"""
        if not self.model or not self.tokenizer:
            if not self.load_model():
                return None

        try:
            logger.info(f"Processing prompt:\n{prompt}")
            
            # プロンプトにanswer:を追加して、回答の開始位置を明確にする
            complete_prompt = f"{prompt}\nanswer:"
            
            # 入力の準備
            inputs = self.tokenizer(
                complete_prompt,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=max_length//2
            ).to(self.device)
            
            # 生成
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                temperature=temperature,
                top_p=top_p,
                do_sample=True,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                repetition_penalty=1.1
            )
            
            # デコードして応答を取得
            full_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # "answer:"以降の部分のみを抽出
            try:
                response = full_text.split("Answer:")[-1].strip()
            except:
                response = None
            
            logger.info(f"Generated response:\n{response}")
            
            if not response:
                logger.warning("Empty response generated")
                return None
                
            return response
            
        except Exception as e:
            logger.error(f"Error in generation: {str(e)}")
            logger.exception(e)
            return None

    def __del__(self):
        """クリーンアップ"""
        try:
            if hasattr(self, 'model'):
                del self.model
            if hasattr(self, 'tokenizer'):
                del self.tokenizer
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                print("GPU memory cleared")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")


class CodeLlamaModel(BaseLLM):
    def __init__(self, device: str = None):
        super().__init__(device)
        self.model_id = "tyson0420/codellama-7B-instruct-slerp"
        self.model = None
        self.tokenizer = None
        print(f"Initializing CodeLlamaModel with device: {self.device}")

    def load_model(self) -> bool:
        try:
            print("Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_id,
                token=True,
            )
            
            print("Loading model...")
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_id,
                device_map="auto",
                torch_dtype=torch.float16,
                token=True,
                low_cpu_mem_usage=True
            )
            
            print("CodeLlama model loaded successfully!")
            return True
            
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            return False

    async def generate_response(
        self,
        prompt: str,
        max_length: int = 2048,
        temperature: float = 0.7,
        top_p: float = 0.9
    ) -> Optional[str]:
        if not self.model or not self.tokenizer:
            if not self.load_model():
                return None

        try:
            # CodeLLaMa用のプロンプトフォーマット
            formatted_prompt = f"[INST] {prompt} [/INST]"
            
            inputs = self.tokenizer(
                formatted_prompt,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=max_length//2
            ).to(self.device)
            
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                temperature=temperature,
                top_p=top_p,
                do_sample=True,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                repetition_penalty=1.1
            )
            
            full_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # [INST]タグの後の部分を抽出
            try:
                response = full_text.split("[/INST]")[-1].strip()
            except:
                response = full_text[len(formatted_prompt):].strip()
            
            return response

        except Exception as e:
            logger.error(f"Error in CodeLLaMa generation: {str(e)}")
            logger.exception(e)
            return None

    def __del__(self):
        if hasattr(self, 'model'):
            del self.model
        if hasattr(self, 'tokenizer'):
            del self.tokenizer
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            print("GPU memory cleared for CodeLLaMa")