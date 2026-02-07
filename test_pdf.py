"""Test PDF loading to debug the issue"""
import sys
import traceback

print("Step 1: Testing imports...")
try:
    from langchain_community.document_loaders import PyPDFLoader
    print("✓ PyPDFLoader imported successfully")
except Exception as e:
    print(f"✗ Failed to import PyPDFLoader: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\nStep 2: Creating loader...")
try:
    loader = PyPDFLoader('uploads/iphone17.pdf')
    print("✓ Loader created successfully")
except Exception as e:
    print(f"✗ Failed to create loader: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\nStep 3: Loading PDF...")
try:
    docs = loader.load()
    print(f"✓ Successfully loaded {len(docs)} pages")
    if docs:
        print(f"  First page preview: {docs[0].page_content[:200]}...")
except Exception as e:
    print(f"✗ Failed to load PDF: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n✅ All tests passed!")
