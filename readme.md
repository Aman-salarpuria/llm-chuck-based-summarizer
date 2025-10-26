LLM Chunk-Based Summarizer

A Python-based text summarization tool that uses large language models (LLMs) to summarize long documents, PDFs, or chat logs efficiently by processing them in manageable chunks.

Features

Summarizes large text files or chat logs that exceed typical LLM input limits.

Processes text in chunks, then generates coherent summaries.

Output is saved automatically to a separate file for easy access.

Customizable chunk sizes and prompt templates for better summarization results.

Getting Started
1. Add Your Input File

Place the original text file you want to summarize in the project folder.

Update the file name in the code (summarizer.py) if necessary.

2. Run the Summarizer
python summarizer.py

3. View Output

The summarized text will be saved in the output file specified in the script.

4. Customize for Your Needs

Chunk Size: Adjust the chunk_size variable in the code depending on your file length and type.

Prompts: Modify the summarization prompt to change how the LLM summarizes content.

Requirements

Python 3.9+

Required packages: openai, PyPDF2 (if processing PDFs), tiktoken (optional, for token management)

pip install openai PyPDF2 tiktoken

Usage Example
# Inside summarizer.py
input_file = "input.txt"  # Change to your file
chunk_size = 2000  # Adjust depending on document length
output_file = "output.txt"

Notes

Best used for large documents where normal LLM summarization fails due to token limits.

Make sure to edit chunk sizes and prompts based on document type (PDF, chat logs, or plain text).
