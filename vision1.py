import ollama
import sys

inputImageFile = sys.argv[1]

response = ollama.chat(
    model='llama3.2-vision:11b',
    messages=[{
        'role': 'user',
        'content': 'What is in this image?',
        'images': [inputImageFile]
    }]
)

print(response)
