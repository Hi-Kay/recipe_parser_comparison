# Receipt Parser Comparison

A Python project that compares two approaches for parsing receipt data:

1. **Regex Parser** - Uses regular expressions to extract structured data from receipts
2. **LLM Parser** - Uses Claude AI to extract structured data from receipts

## Purpose

This project demonstrates the trade-offs between traditional regex-based parsing and LLM-based parsing:

- **Regex Parser**: Fast and free, but only works with structured English receipts that follow a specific format
- **LLM Parser**: More flexible and handles various formats/languages, but requires API calls

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file with your Anthropic API key:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```

## Usage

Run all tests:
```bash
python test_parser.py
```

List available test files:
```bash
python test_parser.py --list
```

Test specific files:
```bash
python test_parser.py test_data/english/receipt1.txt
```

Run with minimal output (summary only):
```bash
python test_parser.py --quiet
```

## Project Structure

```
parser_comparison/
├── parsers/
│   ├── __init__.py
│   ├── regex_parser.py    # Regex-based receipt parser
│   └── llm_parser.py      # Claude AI-based receipt parser
├── test_data/
│   ├── english/           # English receipt samples
│   ├── german/            # German receipt samples
│   └── spanish/           # Spanish receipt samples
├── test_parser.py         # Main comparison script
├── test_env.py            # API key configuration test
├── test_llm.py            # Simple LLM parser test
├── requirements.txt
└── README.md
```

## Output Format

Both parsers return structured data with the following fields:

- `merchant`: Store/business name
- `date`: Transaction date
- `invoice_number`: Invoice/receipt number (if available)
- `items`: List of items with description and amount
- `subtotal`: Subtotal before tax
- `tax`: Tax amount
- `total`: Final total

## Requirements

- Python 3.8+
- Anthropic API key (for LLM parser)
