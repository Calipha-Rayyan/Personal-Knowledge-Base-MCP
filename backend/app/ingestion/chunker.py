import re
from typing import List, Dict, Any

def chunk_text(
    text: str,
    chunk_size: int = 500,      # Approximate words per chunk
    overlap: int = 50           # Words overlapping between chunks
) -> List[Dict[str, Any]]:
    """
    Splits long text into overlapping chunks.
    Each chunk gets a dict with 'text' and 'index'.
    """
    # Split text by double newlines (paragraphs)
    paragraphs = re.split(r'\n\s*\n', text)
    chunks = []
    current_chunk = []
    current_word_count = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        para_words = para.split()
        para_word_count = len(para_words)

        # If adding this paragraph makes it too big, save the current chunk
        if current_word_count + para_word_count > chunk_size and current_chunk:
            chunks.append({
                "text": " ".join(current_chunk),
                "index": len(chunks)
            })
            # Keep the last 'overlap' words for the next chunk
            overlap_words = current_chunk[-overlap:] if overlap > 0 else []
            current_chunk = overlap_words.copy()
            current_word_count = len(overlap_words)

        current_chunk.extend(para_words)
        current_word_count += para_word_count

    # Add the last remaining chunk
    if current_chunk:
        chunks.append({
            "text": " ".join(current_chunk),
            "index": len(chunks)
        })

    return chunks