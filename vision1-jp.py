import ollama
import sys

inputImageFile = sys.argv[1]

response = ollama.chat(
    model='llama3.2-vision',
    messages=[{
        'role': 'user',
        'content': 'これはなんの画像ですか?',
        'images': [inputImageFile]
    }]
)

print(response)
