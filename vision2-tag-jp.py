import ollama
import sys

inputImageFile = sys.argv[1]

response = ollama.chat(
    model='llama3.2-vision',
    messages=[{
        'role': 'user',
        'content': 'なんの画像かを読み込んで、この画像を表すタグ名を３つカンマ区切りで書いてください。例えば「虎、動物、公園」のような形で',
        'images': [inputImageFile]
    }]
)

print(response)
