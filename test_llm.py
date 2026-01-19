from parsers.llm_parser import parse_receipt

receipt = """
ACME Office Supplies
Date: 2024-01-15
Total: $71.81
"""

try:
    result, usage = parse_receipt(receipt)
    print("✅ LLM parser works!")
    print(result)
except Exception as e:
    print(f"❌ Error: {e}")
