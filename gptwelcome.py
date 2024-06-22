import openai
import sys
import re
import argparse
import os
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import TerminalFormatter

# Set your OpenAI API key here
api_key = 'xx'

# Initialize the OpenAI API client
openai.api_key = api_key

# Global variable for conversation history
conversation_history = []

def chat_with_gpt(message):
    global conversation_history

    # Append the user's message to the conversation history
    conversation_history.append({"role": "user", "content": message})

    # Call the OpenAI API to get a response from ChatGPT
    response = openai.ChatCompletion.create(
        model="gpt-4o",  # Use the appropriate model name
        messages=conversation_history,
    )

    # Extract the response content
    gpt_response = response.choices[0].message['content'].strip()

    # Append GPT's response to the conversation history
    conversation_history.append({"role": "assistant", "content": gpt_response})

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

def main():
    parser = argparse.ArgumentParser(description="Chat with GPT-4 from the command line")
    parser.add_argument('message', nargs='*', help="Message to send to GPT-4")
    parser.add_argument('-f', '--file', type=str, help="Path to a text file to include in the conversation")
    args = parser.parse_args()

    file_content = ""
    if args.file:
        file_path = os.path.expanduser(args.file)  # Expand ~ to the full home directory path
        try:
            with open(file_path, 'r') as file:
                file_content = file.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            return

    if args.message or file_content:
        # Join the message if provided and include the file content if applicable
        user_input = ' '.join(args.message) if args.message else ""
        if file_content:
            user_input = f"{file_content}\n\n{user_input}"
        
        response = chat_with_gpt(user_input)
        
        sys.stdout.write("ChatGPT: ")
        sys.stdout.flush()
        print_with_highlighting(response)
        print()  # Move to the next line after printing the response
    else:
        # Interactive mode if no message or file is provided
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
        print("Welcome to the GPT-4o API.")
        print()
        print("Type 'file: /path/to/file' to add a file to the chat.")
        print("Type 'save: /path/to/file' to save the last response to a file.")
        print()
        print("Type 'exit' to end the chat.")
        print()
        
        last_response = ""
        while True:
            # Read user input
            user_input = input("You: ")
            print()
            if user_input.lower() == 'exit':
                print("Exiting the chat. Goodbye!")
                break

            # Check if the user wants to save the last response to a file
            if user_input.lower().startswith('save:'):
                save_path = user_input[5:].strip()
                save_path = os.path.expanduser(save_path)  # Expand ~ to the full home directory path
                try:
                    with open(save_path, 'w') as file:
                        file.write(last_response)
                    print(f"Response saved to {save_path}")
                except Exception as e:
                    print(f"Error writing to file: {e}")
                continue

            # Check if the user wants to include a file
            if user_input.lower().startswith('file:'):
                file_path = user_input[5:].strip()
                file_path = os.path.expanduser(file_path)  # Expand ~ to the full home directory path
                try:
                    with open(file_path, 'r') as file:
                        file_content = file.read()
                        print(f"File content from {file_path} included in the conversation.")
                except Exception as e:
                    print(f"Error reading file: {e}")
                    continue
                # Read the next input as the actual message
                user_input = input("You (your message): ")

            # Get the response from ChatGPT
            combined_input = f"{file_content}\n\n{user_input}" if file_content else user_input
            last_response = chat_with_gpt(combined_input)
            
            # Print ChatGPT's response with selective syntax highlighting
            sys.stdout.write("ChatGPT: ")
            sys.stdout.flush()
            print_with_highlighting(last_response)
            print()
            print()  # Move to the next line after printing the response

if __name__ == "__main__":
    main()
