import pickle
from pathlib import Path

def check_texts():
    # 加载保存的文本数据
    texts_file = Path("data/vectors/faiss_index/texts.pkl")
    print(f"正在读取文件: {texts_file}")
    
    with open(texts_file, "rb") as f:
        texts = pickle.load(f)
    
    print(f"\n总共加载了 {len(texts)} 条文本")
    print("\n前两条文本的内容:")
    for i, text in enumerate(texts[:2]):
        print(f"\n--- 文本 {i+1} ---")
        print(text)

if __name__ == "__main__":
    check_texts() 