import ollama
import sys
import json
from datetime import datetime, timedelta, timezone

# Get the input image file from command-line arguments
input_image_file = sys.argv[1]

# Analyze the image and get the response
response = ollama.chat(
    model='llama3.2-vision:11b',
    messages=[{
        'role': 'user',
        'content': '''
        You are a program specialized in recognizing Mahjong tiles from images. 
        Your task is to analyze the provided image and identify the Mahjong tiles visible in front of the player.

        **Instructions**:
        1. Focus only on the Mahjong tiles in the player's hand and exclude all other elements in the image (e.g., background, labels, or text).
        2. Always output exactly 13 tiles in total, listed in order from left to right as they appear in the image. If you are unsure about a tile, provide a description of its appearance (e.g., "A tile with a blue character that looks like a '3'").
        3. Identify tiles using the following naming conventions:
           - Numeric tiles: Specify the number and suit (e.g., "3 of Bamboo", "7 of Circles", "6 of Characters").
           - Wind tiles: Use their standard names (e.g., "East Wind", "South Wind").
           - Dragon tiles: Use their standard names (e.g., "Red Dragon", "White Dragon").
        4. Ensure that the output is consistent and formatted as a list of 13 items, even if some tiles are unclear.

        **Output Format**:
        - List exactly 13 tiles in English, using the format: ["Tile 1", "Tile 2", ..., "Tile 13"].
        - Example: ["3 of Bamboo", "Red Dragon", "7 of Circles", "East Wind", "6 of Characters", "5 of Circles", "White Dragon", "9 of Bamboo", "2 of Characters", "North Wind", "8 of Circles", "4 of Bamboo", "Green Dragon"]

        **Important Notes**:
        - Avoid repeating the example tiles; analyze and describe the actual tiles visible in the provided image.
        - If any tiles are unclear, describe them briefly instead of guessing.
        - Do not list fewer or more than 13 tiles under any circumstances.

        Please analyze the image carefully and provide the most accurate output possible.
        ''',
        'images': [input_image_file]
    }]
)

# Display the response details
print("Response Details:")
try:
    # Output the recognized Mahjong tiles
    content = response['message']['content']
    print("\nRecognized Tiles:")
    print(content)

except json.JSONDecodeError:
    print("\nError: Failed to parse 'content' as JSON.")
    print(f"Raw Content: {response['message']['content']}")
except KeyError as e:
    print(f"\nError: Missing key in response: {e}")
except Exception as e:
    print(f"\nUnexpected Error: {e}")
