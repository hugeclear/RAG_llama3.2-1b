import os
import sys

# プロジェクトのルートディレクトリをパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.models.llm_model import LlamaModel

def test_llama():
    print("Starting LLaMA model test...")
    
    # モデルの初期化
    llm = LlamaModel()
    if not llm.load_model():
        print("Failed to initialize model")
        return
    
    # 簡単なプロンプトでテスト
    test_prompt = "Pythonプログラミング言語について簡単に説明してください。"
    print(f"\nTesting with prompt: {test_prompt}")
    
    response = llm.generate_response(test_prompt)
    
    if response:
        print("\nSuccess! Response received:")
        print("-" * 50)
        print(response)
        print("-" * 50)
    else:
        print("Failed to generate response")

if __name__ == "__main__":
    test_llama()