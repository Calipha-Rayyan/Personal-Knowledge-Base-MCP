"""
Manual smoke test for the ingestion pipeline (loader -> chunker -> embedder -> Qdrant).

Run from the backend/ directory:
    python tests/test_seperate.py
"""
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.ingestion.processor import process_document, search_vectors  # noqa: E402


def run_test():
    print("=" * 50)
    print("RUNNING INGESTION SMOKE TEST")
    print("=" * 50)

    file_path = os.path.join(os.path.dirname(__file__), "sample.txt")

    if not os.path.exists(file_path):
        print(f"ERROR: Cannot find '{file_path}'")
        return

    print(f"Found file: {file_path}")

    user_id = "test_user_123"
    doc_id = "my_doc_456"
    filename = "sample.txt"

    print("\nProcessing document...")
    try:
        chunk_ids = process_document(file_path, user_id, doc_id, filename)
        print(f"Stored {len(chunk_ids)} chunks.")
    except Exception as e:
        print(f"Error: {e}")
        return

    print("\nSearching for: 'What is my favorite color?'")
    results = search_vectors(user_id, "What is my favorite color?", top_k=3)

    if results:
        print("\nTEST PASSED")
        for idx, res in enumerate(results, 1):
            print(f"\nResult #{idx}:")
            print(f"  File: {res['filename']}")
            print(f"  Score: {res['score']:.4f}")
            print(f"  Text: {res['chunk_text'].strip()}")
    else:
        print("\nNo results found (check score threshold / embeddings).")

    # Isolation check: a different user must see nothing for this document.
    other_user_results = search_vectors("someone_else", "favorite color", top_k=3)
    other_user_hits = [r for r in other_user_results if r["document_id"] == doc_id]
    assert not other_user_hits, "User isolation violated: another user saw this document!"
    print("\nUser isolation check passed: other users cannot see this document.")

    print("\n" + "=" * 50)
    print("Test finished.")


if __name__ == "__main__":
    run_test()
