import openai
import time
import sys
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import TerminalFormatter
import re

# Set your OpenAI API key here
api_key = 'xxx'

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
    print("ChatGPT CLI App")
    print("Type 'exit' to end the chat.")
    while True:
        # Read user input
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            print("Exiting the chat. Goodbye!")
            break
        # Get the response from ChatGPT
        response = chat_with_gpt(user_input)
        
        # Print ChatGPT's response with selective syntax highlighting
        sys.stdout.write("ChatGPT: ")
        sys.stdout.flush()
        print_with_highlighting(response)
        print()  # Move to the next line after printing the response

if __name__ == "__main__":
    main()
