import os
import sys
import torch
from typing import List

# プロジェクトのルートディレクトリをパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from src.models.llm_model import LlamaModel

def print_system_info():
    """システム情報の表示"""
    print(f"Python version: {sys.version}")
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"CUDA device: {torch.cuda.get_device_name(0)}")
        print(f"Available GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")

def test_generation(model: LlamaModel, prompts: List[str]):
    """テスト用の文章生成"""
    for prompt in prompts:
        print(f"\n質問: {prompt}")
        result = model.generate(
            prompt,
            max_length=300,
            temperature=0.6
        )
        if result:
            print(f"回答: {result}")
        else:
            print("Error: Failed to generate response")
        print("-" * 50)

def main():
    # システム情報の表示
    print_system_info()

    print("\nInitializing model...")
    model = LlamaModel()
    
    print("\nLoading model...")
    if model.load_model():
        print("\nTesting generation...")
        
        # テスト用のプロンプト
        test_prompts = [
            "Pythonプログラミング言語の主な特徴と利点について、具体例を挙げて説明してください。",
            "機械学習の基本的な概念と応用例について説明してください。",
            "あなたは質問応答システムとして、どのようなサポートができますか？"
        ]
        
        # テスト実行
        test_generation(model, test_prompts)
    else:
        print("Failed to load model")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nError during test: {str(e)}")
    finally:
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            print("\nGPU memory cleared")