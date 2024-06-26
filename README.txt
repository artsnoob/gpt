**************************************************************************************************************

Simple ChatGPT CLI script for back and forth communication with the GPT API.

Enter your own ChatGPT API key.

**************************************************************************************************************
26/06/2024:

Added vision capabilities to the gtpwelcome script with GPT-4o.
Type 'image: /path/to/image' to analyze an image.

Added history to the script.
Type "history" to see the history.

22/06/2024:

Added a welcome ASCII design to gptwelcome.py

Added the ability to save the previous response:
Type 'save: /path/to/file' to save the last response to a file.

25/05/2024: 

- Added the ability to add arguments in the CLI to gptsyntaxbeta.py.
For example, when gpt is set as an alias in ~./zshrc to run "python3 ~/gpt.py", you can just type: "gpt how are you today".

- Added the ability to send files to the API by adding a file switch:
For example: "gpt -f /path/to/file what does this script do".

- Also added the ability to add a file to the chat in interactive mode.
When in interactive mode type: "file: /path/to/file" to add a file to the chat.

22/05/2024: 

- Added gptsyntaxbeta.py. CLI GPT chat with GPT-4o, with added syntax highlighting in the terminal.

20/05/2024: 

- Updated chatgpt.py to use the GPT-4o model.
