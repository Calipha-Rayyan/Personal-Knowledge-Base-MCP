import re
from typing import List, Dict, Any


def _split_sentences(text: str) -> List[str]:
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z0-9])', text.strip())
    return [s.strip() for s in sentences if s.strip()]


def _split_long_paragraph(
    paragraph: str, chunk_size: int, overlap: int
) -> List[str]:
    """Splits a single paragraph into sentence-level chunks only if it
    exceeds chunk_size. Short paragraphs are returned as a single chunk."""
    word_count = len(paragraph.split())
    if word_count <= chunk_size:
        return [paragraph]

    sentences = _split_sentences(paragraph)
    chunks = []
    current = []
    current_words = 0

    for sentence in sentences:
        w = len(sentence.split())
        if current_words + w > chunk_size and current:
            chunks.append(" ".join(current))
            overlap_words = 0
            overlap_sentences = []
            for s in reversed(current):
                sw = len(s.split())
                if overlap_words + sw > overlap:
                    break
                overlap_sentences.insert(0, s)
                overlap_words += sw
            current = overlap_sentences.copy()
            current_words = overlap_words
        current.append(sentence)
        current_words += w

    if current:
        chunks.append(" ".join(current))

    return chunks


def chunk_text(
    text: str,
    chunk_size: int = 80,   # only used to split an individual paragraph if it's too long
    overlap: int = 15,
) -> List[Dict[str, Any]]:
    """
    Chunks text by PARAGRAPH first (one topic per paragraph, as most
    documents are naturally structured), and only splits a paragraph
    further if it exceeds chunk_size words.

    Crucially, this does NOT merge multiple short paragraphs into one
    chunk. Earlier versions merged unrelated short paragraphs (e.g.
    "favorite color" + "pizza toppings") into a single chunk purely
    because both were short, which diluted the embedding for either
    topic and hurt similarity scores. Respecting existing paragraph
    boundaries keeps each chunk focused on one idea.

    If a document has no paragraph breaks at all (one giant block of
    text), it's treated as a single "paragraph" and split at the
    sentence level instead, so it still gets chunked usefully.
    """
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]

    if not paragraphs:
        return []

    chunks = []
    for paragraph in paragraphs:
        for piece in _split_long_paragraph(paragraph, chunk_size, overlap):
            chunks.append({"text": piece, "index": len(chunks)})

    return chunks