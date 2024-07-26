# GPT CLI

GPT CLI is a command-line interface tool that allows you to interact with OpenAI's GPT-4 model, including its vision capabilities, directly from your terminal. It supports chat-based interactions, file input, image analysis, and conversation history management.

## Features

- Interactive chat with GPT-4
- Support for analyzing images using GPT-4 Vision
- File input for including text content in conversations
- Conversation history management with the ability to reuse previous questions
- Syntax highlighting for code snippets in responses
- Option to save responses to files

## Prerequisites

- Python 3.6+
- OpenAI API key

## Installation

1. Clone this repository or download the script.
2. Install the required dependencies:

```bash
pip install openai pygments
```

3. Set your OpenAI API key in the script:

```python
api_key = 'your_api_key_here'
```

## Usage

### Command-line Arguments

Run the script with a message:

```bash
python gpt_cli.py "Your message here"
```

Include a file in the conversation:

```bash
python gpt_cli.py -f /path/to/file.txt "Your message here"
```

Analyze an image:

```bash
python gpt_cli.py -i /path/to/image.jpg "Describe what's in this image"
```

### Interactive Mode

Run the script without arguments to enter interactive mode:

```bash
python gpt_cli.py
```

In interactive mode, you can:

- Type messages to chat with GPT-4
- Use `file: /path/to/file` to include file content in the conversation
- Use `image: /path/to/image` to analyze an image
- Use `save: /path/to/file` to save the last response to a file
- Type `history` to view and reuse previous questions
- Type `exit` to end the chat

## History Management

The script automatically saves conversation history to `~/.gptcli_history.json`. This allows you to maintain context across sessions and reuse previous questions.

## Note

This tool uses the GPT-4 model with vision capabilities. Ensure your OpenAI account has access to GPT-4 and the necessary credits for API usage.

## License

[MIT License](https://opensource.org/licenses/MIT)
