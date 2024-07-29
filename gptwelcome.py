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
from colorama import init, Fore, Back, Style
import shutil

# Initialize colorama
init(autoreset=True)

# Set your OpenAI API key here
api_key = 'xxx'

# Initialize the OpenAI API client
openai.api_key = api_key

# Global variables for conversation history and user questions
conversation_history = []
user_questions = []
coding_mode = False  # New global variable to track coding mode

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
            print(f"{Fore.RED}Error loading history file. Starting with empty history.{Style.RESET_ALL}")

def save_history():
    try:
        with open(HISTORY_FILE, 'w') as f:
            json.dump({
                'conversation_history': conversation_history,
                'user_questions': user_questions
            }, f)
    except Exception as e:
        print(f"{Fore.RED}Error saving history: {e}{Style.RESET_ALL}")

def extract_code_blocks(text):
    code_pattern = re.compile(r'```(?:\w+)?\n(.*?)```', re.DOTALL)
    return code_pattern.findall(text)

def save_code_blocks(response):
    code_blocks = extract_code_blocks(response)
    if not code_blocks:
        print(f"{Fore.YELLOW}No code blocks found in the response.{Style.RESET_ALL}")
        return

    for i, block in enumerate(code_blocks, 1):
        print(f"{Fore.CYAN}Code Block {i}:{Style.RESET_ALL}")
        print(block)
        print()

    while True:
        choice = input(f"{Fore.YELLOW}Enter the number of the code block to save (or 'a' for all, 'c' to cancel): {Style.RESET_ALL}")
        if choice.lower() == 'c':
            return
        elif choice.lower() == 'a':
            save_path = input(f"{Fore.YELLOW}Enter the path to save all code blocks: {Style.RESET_ALL}")
            save_path = os.path.expanduser(save_path)
            try:
                with open(save_path, 'w') as file:
                    for block in code_blocks:
                        file.write(block + '\n\n')
                print(f"{Fore.GREEN}All code blocks saved to {save_path}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}Error writing to file: {e}{Style.RESET_ALL}")
            return
        try:
            index = int(choice) - 1
            if 0 <= index < len(code_blocks):
                save_path = input(f"{Fore.YELLOW}Enter the path to save the code block: {Style.RESET_ALL}")
                save_path = os.path.expanduser(save_path)
                try:
                    with open(save_path, 'w') as file:
                        file.write(code_blocks[index])
                    print(f"{Fore.GREEN}Code block saved to {save_path}{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED}Error writing to file: {e}{Style.RESET_ALL}")
                return
            else:
                print(f"{Fore.RED}Invalid number. Please try again.{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}Invalid input. Please enter a number, 'a', or 'c' to cancel.{Style.RESET_ALL}")

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
        model="gpt-4o-mini",  # Use the vision-capable model
        messages=messages,
        max_tokens=1000,
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
            # Normal text
            print(f"{Fore.WHITE}{part}", end='')
        else:
            # Code block
            print(f"{Fore.BLACK}{Back.WHITE}")
            for line in part.split('\n'):
                print(f"{Fore.BLACK}{Back.WHITE}{line.ljust(shutil.get_terminal_size().columns)}")
            print(Style.RESET_ALL, end='')

def show_history():
    if not user_questions:
        print(f"{Fore.YELLOW}No history available.{Style.RESET_ALL}")
        return None

    print(f"{Fore.CYAN}Recent questions:{Style.RESET_ALL}")
    for i, question in enumerate(user_questions[-10:], 1):
        print(f"{Fore.WHITE}{i}. {question}{Style.RESET_ALL}")
    
    while True:
        choice = input(f"{Fore.YELLOW}Enter the number of the question to reuse (or 'c' to cancel): {Fore.RESET}")
        if choice.lower() == 'c':
            return None
        try:
            index = int(choice) - 1
            if 0 <= index < len(user_questions[-10:]):
                return user_questions[-10:][index]
            else:
                print(f"{Fore.RED}Invalid number. Please try again.{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}Invalid input. Please enter a number or 'c' to cancel.{Style.RESET_ALL}")

def print_startup_screen():
    # Set background color
    print(Back.BLACK + Fore.RESET + Style.BRIGHT, end="")
    
    # Print decorative border
    border = "╔" + "═" * (shutil.get_terminal_size().columns - 2) + "╗"
    print(Fore.BLUE + border)

    # ASCII art with gradient
    ascii_art = r'''
 $$$$$$\  $$$$$$$\ $$$$$$$$\       $$$$$$\  $$\       $$$$$$\ 
$$  __$$\ $$  __$$\\__$$  __|     $$  __$$\ $$ |      \_$$  _|
$$ /  \__|$$ |  $$ |  $$ |        $$ /  \__|$$ |        $$ |  
$$ |$$$$\ $$$$$$$  |  $$ |$$$$$$\ $$ |      $$ |        $$ |  
$$ |\_$$ |$$  ____/   $$ |\______|$$ |      $$ |        $$ |  
$$ |  $$ |$$ |        $$ |        $$ |  $$\ $$ |        $$ |  
\$$$$$$  |$$ |        $$ |        \$$$$$$  |$$$$$$$$\ $$$$$$\ 
 \______/ \__|        \__|         \______/ \________|\______|
    '''
    
    lines = ascii_art.split('\n')
    for i, line in enumerate(lines):
        color = int(255 - (i / len(lines)) * 155)
        print(f"\033[38;2;0;{color};255m{line}")

    # Welcome message
    print(Fore.LIGHTCYAN_EX + "\nWelcome to the GPT-4 Vision API.")
    print()

    # Instructions
    instructions = [
        "Type 'file: /path/to/file' to add a file to the chat.",
        "Type 'save: /path/to/file' to save the last response to a file.",
        "Type 'image: /path/to/image' to analyze an image.",
        "Type 'history' to view and reuse previous questions.",
        "Type 'coding' to toggle coding mode (enables/disables code block saving).",
        "Type 'exit' to end the chat."
    ]

    for instruction in instructions:
        print(Fore.LIGHTYELLOW_EX + instruction)

    # Print bottom border
    print(Fore.BLUE + "╚" + "═" * (shutil.get_terminal_size().columns - 2) + "╝")
    print(Style.RESET_ALL)

def main():
    global coding_mode
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
            print(f"{Fore.RED}Error reading file: {e}{Style.RESET_ALL}")
            return

    if args.message or file_content or args.image:
        user_input = ' '.join(args.message) if args.message else ""
        if file_content:
            user_input = f"{file_content}\n\n{user_input}"
        
        if args.image:
            image_path = os.path.expanduser(args.image)
            if not os.path.exists(image_path):
                print(f"{Fore.RED}Error: Image file not found at {image_path}{Style.RESET_ALL}")
                return
            user_input = f"Analyze this image: {user_input}"
            response = chat_with_gpt(user_input, image_path)
        else:
            response = chat_with_gpt(user_input)
        
        sys.stdout.write(f"{Fore.GREEN}ChatGPT: {Fore.RESET}")
        sys.stdout.flush()
        print_with_highlighting(response)
        print()
        
        # Offer to save code blocks after the response
        save_code_blocks(response)
    else:
        # Interactive mode
        print_startup_screen()
        
        # Prompt for coding mode
        coding_mode_input = input(f"{Fore.YELLOW}Do you want to enter coding mode? (yes/no): {Fore.RESET}").lower()
        coding_mode = coding_mode_input.startswith('y')
        
        if coding_mode:
            print(f"{Fore.GREEN}Coding mode activated. Code block saving will be available.{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}Regular mode. Code block saving will not be available.{Style.RESET_ALL}")
        
        last_response = ""
        while True:
            user_input = input(f"{Fore.YELLOW}You: {Fore.RESET}")
            print()
            if user_input.lower() == 'exit':
                print(f"{Fore.YELLOW}Exiting the chat. Goodbye!{Style.RESET_ALL}")
                save_history()  # Save history before exiting
                break

            if user_input.lower() == 'coding':
                coding_mode = not coding_mode
                print(f"{Fore.GREEN}Coding mode {'activated' if coding_mode else 'deactivated'}.{Style.RESET_ALL}")
                continue

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
                    print(f"{Fore.GREEN}Response saved to {save_path}{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED}Error writing to file: {e}{Style.RESET_ALL}")
                continue

            file_content = ""
            image_path = None

            if user_input.lower().startswith('file:'):
                file_path = user_input[5:].strip()
                file_path = os.path.expanduser(file_path)
                try:
                    with open(file_path, 'r') as file:
                        file_content = file.read()
                    print(f"{Fore.GREEN}File content from {file_path} included in the conversation.{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED}Error reading file: {e}{Style.RESET_ALL}")
                    continue
                user_input = input(f"{Fore.YELLOW}You (your message): {Fore.RESET}")
            elif user_input.lower().startswith('image:'):
                image_path = user_input[6:].strip()
                image_path = os.path.expanduser(image_path)
                if not os.path.exists(image_path):
                    print(f"{Fore.RED}Error: Image file not found at {image_path}{Style.RESET_ALL}")
                    continue
                print(f"{Fore.GREEN}Image from {image_path} will be analyzed.{Style.RESET_ALL}")
                user_input = input(f"{Fore.YELLOW}You (describe what to analyze in the image): {Fore.RESET}")

            combined_input = f"{file_content}\n\n{user_input}" if file_content else user_input
            user_questions.append(combined_input)
            last_response = chat_with_gpt(combined_input, image_path)
        
            sys.stdout.write(f"{Fore.GREEN}ChatGPT: {Fore.RESET}")
            sys.stdout.flush()
            print_with_highlighting(last_response)
            print()

            # Only offer to save code blocks if in coding mode
            if coding_mode:
                save_code_blocks(last_response)

            print()

if __name__ == "__main__":
    main()
