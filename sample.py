from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class ModelConfig:
    model_id: str
    device_map: str = "auto"
    torch_dtype: torch.dtype = torch.float16  # 1Bモデルなのでfloat16で十分
    load_in_8bit: bool = False  # 1Bモデルなので8bit量子化は不要


class ModelManager:
    def __init__(self):
        self.models: Dict[str, AutoModelForCausalLM] = {}
        self.tokenizers: Dict[str, AutoTokenizer] = {}

    async def load_model(self, name: str, config: ModelConfig):
        """モデルとトークナイザーをロード"""
        try:
            tokenizer = AutoTokenizer.from_pretrained(
                "meta-llama/Llama-3.2-1b",  # 更新: Llama-3.2-1bを使用
                trust_remote_code=True,
            )
            model = AutoModelForCausalLM.from_pretrained(
                "meta-llama/Llama-3.2-1b",  # 更新: Llama-3.2-1bを使用
                device_map=config.device_map,
                torch_dtype=config.torch_dtype,
                trust_remote_code=True,
            )

            self.models[name] = model
            self.tokenizers[name] = tokenizer

            print(f"Successfully loaded model: {name}")
            return True
        except Exception as e:
            print(f"Error loading model {name}: {str(e)}")
            return False


# システム初期化の例
async def setup_models():
    model_manager = ModelManager()

    # Llama-3.2-1bのロード
    base_config = ModelConfig(
        model_id="meta-llama/Llama-3.2-1b",
        load_in_8bit=False,  # 1Bモデルなので8bit量子化は不要
    )
    await model_manager.load_model("base", base_config)

    return model_manager
