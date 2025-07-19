import os
import requests
from dotenv import load_dotenv

prompt = """You are a high-context memory summarizer. You will be given a long section of a real ChatGPT conversation. Your task is to compress this into a highly detailed, emotionally aware, context-preserving narrative.

This is not a clinical or bullet-only summary. Your goal is to preserve the user’s original voice, thoughts, emotional state, struggles, and goals in a way that would let another AI assistant **truly understand who they are, what they’re going through, and what they’re building** — even after thousands of lines.

GUIDELINES:

1. **Use mostly paragraphs**, but feel free to add bullet points under strategies, goals, or frameworks.
2. **Preserve tone** — include rants, contradictions, spirals, patterns.
3. Use the **user’s original phrasing** when it's revealing.
4. Prioritize **emotional flow and mental state over pure structure**.
5. Don’t just tell what they said — reflect the *how and why* behind their words.
6. Include systems, tools, and next steps — but wrap them in narrative.
7. Organize with section headers like "Identity", "Emotional Landscape", "Projects", "Goals", "Contradictions", "Core Philosophies", "Next Steps", etc., but let **paragraphs do the storytelling**.

SUMMARY OBJECTIVE:
Capture the user's internal world, motivations, behaviors, and contradictions — including:
- Who they are becoming
- What they're building and why
- What’s holding them back
- How they frame progress, power, loneliness, discipline, purpose, addiction, and capital
- What they repeat emotionally or strategically
- What a future AI must never forget about them

Do not compress too tightly.
Do not replace full ideas with only bullets.
Do not discard emotional content.

EXAMPLE OF A PARA
At 18, he's already thinking in leverage stacks, not lecture halls. While most of his peers chase placements or GPA clout, he’s plotting ₹100Cr control through quiet systems—real estate
, software, and debt structuring. He doesn’t want to be rich to impress anyone. He wants control. And maybe freedom. But beneath that ambition is a haunting FOMO—the kind that comes when yo
ur friends are scaling SMMA agencies while your product still has 3 users...


Write this as if you are building a memory file that **another AI would read before continuing this relationship**. It must reflect the full depth of the original 33,000 lines in compressed but truthful, tone-preserving form.

Do not make this generic.
Do not reduce the soul of the conversation.
Compress with care.

BEGIN MEMORY SUMMARY:
"""

def load_text_from_file(file_path):
    """Read text content from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None
    except Exception as e:
        print(f"Error reading file: {str(e)}")
        return None

def save_text_to_file(file_path, text):
    """Save text content to a file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(text)
        print(f"Successfully saved summary to {file_path}")
        return True
    except Exception as e:
        print(f"Error saving file: {str(e)}")
        return False

def chunk_text(text, words_per_chunk=60000):
    """Split text into chunks of approximately words_per_chunk words."""
    # Split text into words
    words = text.split()
    chunks = []
    
    # Split into chunks of approximately words_per_chunk words
    for i in range(0, len(words), words_per_chunk):
        chunk = ' '.join(words[i:i + words_per_chunk])
        chunks.append(chunk)
    
    return chunks

def summarize_text(api_key, text, is_final_summary=False):
    """Send text to OpenRouter API for summarization."""
    if not text:
        print("Error: No text provided for summarization")
        return None
        
    try:
        print("Sending request to OpenRouter API...")
        
        # Use a different prompt for final summary
        if is_final_summary:
            system_message = "You are a helpful assistant that combines multiple summaries into one cohesive summary."
            user_message = f"Combine these summaries into one comprehensive final summary. Maintain the structured format and include all key points:\n\n{text}"
        else:
            system_message = "You are a helpful assistant that summarizes text."
            user_message = f"Please summarize the following text using this format:\n\n{prompt}\n\nText to summarize:\n{text}"
        
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "Text Summarizer"
            },
            json={
                "model": "deepseek/deepseek-chat-v3-0324:free",
                "messages": [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ]
            },
            timeout=120  # Increased timeout for larger summaries
        )
        
        response.raise_for_status()
        result = response.json()
        
        if 'choices' in result and len(result['choices']) > 0:
            return result['choices'][0]['message']['content']
        else:
            print("Unexpected response format from API")
            return None
            
    except requests.exceptions.Timeout:
        print("Error: Request to OpenRouter API timed out (120 seconds)")
        return None
    except requests.exceptions.RequestException as e:
        print(f"API Error: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response content: {e.response.text}")
        return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

def summarize_large_text(api_key, text):
    """Summarize large text by splitting into chunks and combining summaries."""
    # Split text into chunks
    chunks = chunk_text(text)
    
    if not chunks:
        return None
        
    print(f"Processing {len(chunks)} chunks...")
    
    # Summarize each chunk
    chunk_summaries = []
    for i, chunk in enumerate(chunks, 1):
        print(f"Summarizing chunk {i}/{len(chunks)}...")
        summary = summarize_text(api_key, chunk)
        if summary:
            chunk_summaries.append(summary)
            print(f"Chunk {i} summarized successfully!")
        else:
            print(f"Warning: Failed to summarize chunk {i}")
    
    if not chunk_summaries:
        print("No valid summaries were generated from the chunks.")
        return None
    
    # If only one chunk, return its summary
    if len(chunk_summaries) == 1:
        return chunk_summaries[0]
    
    # Combine all chunk summaries and create a final summary
    print("\nCreating final summary from all chunks...")
    combined_summaries = "\n\n--- CHUNK SUMMARY ---\n\n".join(chunk_summaries)
    final_summary = summarize_text(api_key, combined_summaries, is_final_summary=True)
    
    return final_summary

def main():
    # Load environment variables
    load_dotenv('.env.local')
    api_key = os.getenv('OPENROUTER_API_KEY')
    
    if not api_key:
        print("Error: OPENROUTER_API_KEY not found in .env.local")
        return
    
    # Define file paths
    input_file = 'input.txt'
    output_file = 'output.txt'
    
    # Read input text
    print(f"Reading input from {input_file}...")
    input_text = load_text_from_file(input_file)
    
    if not input_text:
        print("No text to summarize. Please check your input file.")
        return
    
    # Generate summary using chunking for large texts
    print("Starting summarization process...")
    summary = summarize_large_text(api_key, input_text)
    
    if summary:
        # Save summary to output file
        save_text_to_file(output_file, summary)
        print("\nSummary generated successfully!")
    else:
        print("Failed to generate summary.")

if __name__ == "__main__":
    main()
