import openai
import sys
import re
import argparse
import os
import base64
import json
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import TerminalFormatter

# Set your OpenAI API key here
api_key = 'xx'

# Initialize the OpenAI API client
openai.api_key = api_key

# Global variables for conversation history and user questions
conversation_history = []
user_questions = []

# File to store history
HISTORY_FILE = os.path.expanduser('~/.gptcli_history.json')

def load_history():
    global conversation_history, user_questions
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                data = json.load(f)
                conversation_history = data.get('conversation_history', [])
                user_questions = data.get('user_questions', [])
        except json.JSONDecodeError:
            print("Error loading history file. Starting with empty history.")

def save_history():
    try:
        with open(HISTORY_FILE, 'w') as f:
            json.dump({
                'conversation_history': conversation_history,
                'user_questions': user_questions
            }, f)
    except Exception as e:
        print(f"Error saving history: {e}")

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def chat_with_gpt(message, image_path=None):
    global conversation_history

    messages = conversation_history.copy()
    
    if image_path:
        base64_image = encode_image(image_path)
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": message},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        })
    else:
        messages.append({"role": "user", "content": message})

    # Call the OpenAI API to get a response from ChatGPT
    response = openai.ChatCompletion.create(
        model="gpt-4o",  # Use the vision-capable model
        messages=messages,
        max_tokens=300,
    )

    # Extract the response content
    gpt_response = response.choices[0].message['content'].strip()

    # Append GPT's response to the conversation history
    conversation_history.append({"role": "assistant", "content": gpt_response})

    # Save history after each interaction
    save_history()

    return gpt_response

def print_with_highlighting(text):
    code_pattern = re.compile(r'```(.*?)```', re.DOTALL)
    matches = code_pattern.split(text)
    
    for i, part in enumerate(matches):
        if i % 2 == 0:
            # This is normal text
            sys.stdout.write(part)
            sys.stdout.flush()
        else:
            # This is code, apply syntax highlighting
            highlighted_code = highlight(part, PythonLexer(), TerminalFormatter())
            sys.stdout.write(highlighted_code)
            sys.stdout.flush()

def show_history():
    if not user_questions:
        print("No history available.")
        return None

    print("Recent questions:")
    for i, question in enumerate(user_questions[-10:], 1):
        print(f"{i}. {question}")
    
    while True:
        choice = input("Enter the number of the question to reuse (or 'c' to cancel): ")
        if choice.lower() == 'c':
            return None
        try:
            index = int(choice) - 1
            if 0 <= index < len(user_questions[-10:]):
                return user_questions[-10:][index]
            else:
                print("Invalid number. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number or 'c' to cancel.")

def main():
    # Load history at the start of the program
    load_history()

    parser = argparse.ArgumentParser(description="Chat with GPT-4 from the command line")
    parser.add_argument('message', nargs='*', help="Message to send to GPT-4")
    parser.add_argument('-f', '--file', type=str, help="Path to a text file to include in the conversation")
    parser.add_argument('-i', '--image', type=str, help="Path to an image file to analyze")
    args = parser.parse_args()

    file_content = ""
    if args.file:
        file_path = os.path.expanduser(args.file)
        try:
            with open(file_path, 'r') as file:
                file_content = file.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            return

    if args.message or file_content or args.image:
        user_input = ' '.join(args.message) if args.message else ""
        if file_content:
            user_input = f"{file_content}\n\n{user_input}"
        
        if args.image:
            image_path = os.path.expanduser(args.image)
            if not os.path.exists(image_path):
                print(f"Error: Image file not found at {image_path}")
                return
            user_input = f"Analyze this image: {user_input}"
            response = chat_with_gpt(user_input, image_path)
        else:
            response = chat_with_gpt(user_input)
        
        sys.stdout.write("ChatGPT: ")
        sys.stdout.flush()
        print_with_highlighting(response)
        print()
    else:
        # Interactive mode
        print(r''' 
  /$$$$$$  /$$       /$$$$$$                      /$$$$$$  /$$$$$$$  /$$$$$$$$
 /$$__  $$| $$      |_  $$_/                     /$$__  $$| $$__  $$|__  $$__/
| $$  \__/| $$        | $$                      | $$  \__/| $$  \ $$   | $$   
| $$      | $$        | $$         /$$$$$$      | $$ /$$$$| $$$$$$$/   | $$   
| $$      | $$        | $$        |______/      | $$|_  $$| $$____/    | $$   
| $$    $$| $$        | $$                      | $$  \ $$| $$         | $$   
|  $$$$$$/| $$$$$$$$ /$$$$$$                    |  $$$$$$/| $$         | $$   
\______/ |________/|______/                     \______/ |__/         |__/   
''')
        print("Welcome to the GPT-4 Vision API.")
        print()
        print("Type 'file: /path/to/file' to add a file to the chat.")
        print("Type 'save: /path/to/file' to save the last response to a file.")
        print("Type 'image: /path/to/image' to analyze an image.")
        print("Type 'history' to view and reuse previous questions.")
        print()
        print("Type 'exit' to end the chat.")
        print()
        
        last_response = ""
        while True:
            user_input = input("You: ")
            print()
            if user_input.lower() == 'exit':
                print("Exiting the chat. Goodbye!")
                save_history()  # Save history before exiting
                break

            if user_input.lower() == 'history':
                selected_question = show_history()
                if selected_question:
                    user_input = selected_question
                else:
                    continue

            if user_input.lower().startswith('save:'):
                save_path = user_input[5:].strip()
                save_path = os.path.expanduser(save_path)
                try:
                    with open(save_path, 'w') as file:
                        file.write(last_response)
                    print(f"Response saved to {save_path}")
                except Exception as e:
                    print(f"Error writing to file: {e}")
                continue

            file_content = ""
            image_path = None

            if user_input.lower().startswith('file:'):
                file_path = user_input[5:].strip()
                file_path = os.path.expanduser(file_path)
                try:
                    with open(file_path, 'r') as file:
                        file_content = file.read()
                    print(f"File content from {file_path} included in the conversation.")
                except Exception as e:
                    print(f"Error reading file: {e}")
                    continue
                user_input = input("You (your message): ")
            elif user_input.lower().startswith('image:'):
                image_path = user_input[6:].strip()
                image_path = os.path.expanduser(image_path)
                if not os.path.exists(image_path):
                    print(f"Error: Image file not found at {image_path}")
                    continue
                print(f"Image from {image_path} will be analyzed.")
                user_input = input("You (describe what to analyze in the image): ")

            combined_input = f"{file_content}\n\n{user_input}" if file_content else user_input
            user_questions.append(combined_input)
            last_response = chat_with_gpt(combined_input, image_path)
            
            sys.stdout.write("ChatGPT: ")
            sys.stdout.flush()
            print_with_highlighting(last_response)
            print()
            print()

if __name__ == "__main__":
    main()
