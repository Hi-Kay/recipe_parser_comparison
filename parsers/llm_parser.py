import anthropic
import json
import os
import re
from dotenv import load_dotenv
from typing import Dict, Any, Tuple

load_dotenv()

def parse_receipt(receipt_text: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Parse receipt using Claude AI.
    
    Returns:
        Tuple of (parsed_data, usage_stats)
    """
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found!")
    
    client = anthropic.Anthropic(api_key=api_key)
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"""Extract structured data from this receipt and return ONLY valid JSON.

Required fields:
- merchant: string
- date: string (YYYY-MM-DD format if possible)
- invoice_number: string or null
- items: array of objects with description and amount
- subtotal: number or null
- tax: number or null
- total: number

Receipt text:
{receipt_text}

Important: Return ONLY the JSON object, no markdown, no explanations."""
            }
        ]
    )
    
    response_text = message.content[0].text.strip()
    
    # Remove markdown code blocks if present
    if response_text.startswith("```"):
        match = re.search(r'```(?:json)?\s*\n(.*?)\n```', response_text, re.DOTALL)
        if match:
            response_text = match.group(1)
    
    result = json.loads(response_text)
    result["parser_used"] = "llm"
    
    # Extract usage stats
    usage = {
        "input_tokens": message.usage.input_tokens,
        "output_tokens": message.usage.output_tokens,
        "total_tokens": message.usage.input_tokens + message.usage.output_tokens
    }
    
    return result, usage
  