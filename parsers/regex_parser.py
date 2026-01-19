import re
from typing import Dict, Any

def parse_receipt(receipt_text: str) -> Dict[str, Any]:
    """
    Parse receipt using regex patterns.
    Only works for structured English receipts!
    """
    
    result = {
        "merchant": None,
        "date": None,
        "invoice_number": None,
        "items": [],
        "subtotal": None,
        "tax": None,
        "total": None,
        "parser_used": "regex"  # Track which parser was used
    }
    
    lines = receipt_text.strip().split('\n')
    
    # Extract merchant (first non-empty line)
    for line in lines:
        if line.strip():
            result["merchant"] = line.strip()
            break
    
    # Extract date
    date_match = re.search(r"Date:\s*(.+)", receipt_text)
    if date_match:
        result["date"] = date_match.group(1).strip()
    
    # Extract invoice number
    invoice_match = re.search(r"Invoice #:\s*(.+)", receipt_text)
    if invoice_match:
        result["invoice_number"] = invoice_match.group(1).strip()
    
    # Extract total
    total_match = re.search(r"TOTAL:\s*\$(\d+\.\d+)", receipt_text)
    if total_match:
        result["total"] = float(total_match.group(1))
    
    # Extract subtotal
    subtotal_match = re.search(r"Subtotal:\s*\$(\d+\.\d+)", receipt_text)
    if subtotal_match:
        result["subtotal"] = float(subtotal_match.group(1))
    
    # Extract tax
    tax_match = re.search(r"Tax.*?:\s*\$(\d+\.\d+)", receipt_text)
    if tax_match:
        result["tax"] = float(tax_match.group(1))
    
    # Extract line items
    for line in lines:
        if line.strip().startswith('-'):
            item_match = re.search(r'-\s*(.+?)\s*\.\.\.\s*\$(\d+\.\d+)', line)
            if item_match:
                description = item_match.group(1).strip()
                amount = float(item_match.group(2))
                result["items"].append({
                    "description": description,
                    "amount": amount
                })
    
    return result


# # Test data
# receipt_text_1 = """
# ACME Office Supplies
# 123 Business St, New York
# Date: 2024-01-15
# Invoice #: INV-2024-001

# Items:
# - Paper (A4, 5 reams) ... $45.00
# - Pens (Blue, pack of 12) ... $8.50
# - Stapler ... $12.99

# Subtotal: $66.49
# Tax (8%): $5.32
# TOTAL: $71.81

# Thank you for your business!
# """

# # Test your function
# if __name__ == "__main__":
#     result = parse_receipt(receipt_text_1)
    
#     print("=" * 50)
#     print("PARSED RECEIPT:")
#     print("=" * 50)
#     print(f"Merchant: {result['merchant']}")
#     print(f"Date: {result['date']}")
#     print(f"Invoice #: {result['invoice_number']}")
#     print(f"\nItems:")
#     for item in result['items']:
#         print(f"  - {item['description']}: ${item['amount']}")
#     print(f"\nSubtotal: ${result['subtotal']}")
#     print(f"Tax: ${result['tax']}")
#     print(f"Total: ${result['total']}")
#     print("=" * 50)
    
#     # Validation
#     assert result["merchant"] == "ACME Office Supplies", "Merchant parsing failed"
#     assert result["total"] == 71.81, "Total parsing failed"
#     assert len(result["items"]) == 3, "Items parsing failed"
#     print("\n✅ All tests passed!")