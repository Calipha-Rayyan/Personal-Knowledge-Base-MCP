import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.ingestion.processor import process_document, search_vectors

os.environ["QDRANT_HOST"] = "localhost"
os.environ["QDRANT_PORT"] = "6333"

def run_test():
    print("=" * 50)
    print("🧪 RUNNING FINAL TEST")
    print("=" * 50)

    file_path = os.path.join(os.path.dirname(__file__), "sample.txt")
    
    if not os.path.exists(file_path):
        print(f"❌ ERROR: Cannot find 'tests/sample.txt'!")
        return

    print(f"✅ Found your file: {file_path}")

    user_id = "test_user_123"
    doc_id = "my_doc_456"
    filename = "sample.txt"

    print("\n⚙️ Processing your document...")
    try:
        chunk_ids = process_document(file_path, user_id, doc_id, filename)
        print(f"✅ SUCCESS! Stored {len(chunk_ids)} chunks!")
    except Exception as e:
        print(f"❌ Error: {e}")
        return

    print("\n🔍 Searching for: 'What is my favorite color?'")
    results = search_vectors(user_id, "What is my favorite color?", top_k=3)

    if results:
        print("\n" + "=" * 50)
        print("🎉🎉🎉 TEST PASSED! YOUR MODULE WORKS PERFECTLY! 🎉🎉🎉")
        print("=" * 50)
        for idx, res in enumerate(results, 1):
            print(f"\nResult #{idx}:")
            print(f"  📄 File: {res['filename']}")
            print(f"  📊 Score: {res['score']:.4f}")
            print(f"  📝 Text: {res['chunk_text'].strip()}")
    else:
        print("\n❌ No results found.")

    print("\n" + "=" * 50)
    print("🏁 Test finished!")

if __name__ == "__main__":
    run_test()