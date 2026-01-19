from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Literal
import traceback

from parsers import regex_parser, llm_parser

# Create FastAPI app
app = FastAPI(
    title="Receipt Parser API",
    description="Parse receipts using regex or LLM",
    version="1.0.0"
)

# Request model
class ReceiptRequest(BaseModel):
    receipt_text: str
    parser: Literal["llm", "regex", "auto"] = "auto"
    
    class Config:
        json_schema_extra = {
            "example": {
                "receipt_text": "ACME Office Supplies\nDate: 2024-01-15\nTotal: $71.81",
                "parser": "auto"
            }
        }

# Response model
class ReceiptResponse(BaseModel):
    success: bool
    parser_used: str
    data: Optional[dict] = None
    error: Optional[str] = None
    usage: Optional[dict] = None

# Health check endpoint
@app.get("/")
def health_check():
    """Check if API is running"""
    return {
        "status": "healthy",
        "service": "Receipt Parser API",
        "version": "1.0.0"
    }

# Parse receipt endpoint
@app.post("/parse", response_model=ReceiptResponse)
def parse_receipt(request: ReceiptRequest):
    """
    Parse a receipt using the specified parser
    
    - **receipt_text**: The raw text from the receipt
    - **parser**: Which parser to use (llm, regex, or auto)
        - auto: tries LLM first, falls back to regex if it fails
    """
    
    if not request.receipt_text.strip():
        raise HTTPException(status_code=400, detail="receipt_text cannot be empty")
    
    # Auto mode: try LLM first, fallback to regex
    if request.parser == "auto":
        try:
            result, usage = llm_parser.parse_receipt(request.receipt_text)
            return ReceiptResponse(
                success=True,
                parser_used="llm",
                data=result,
                usage=usage
            )
        except Exception as llm_error:
            print(f"LLM failed, falling back to regex: {llm_error}")
            try:
                result = regex_parser.parse_receipt(request.receipt_text)
                return ReceiptResponse(
                    success=True,
                    parser_used="regex_fallback",
                    data=result
                )
            except Exception as regex_error:
                raise HTTPException(
                    status_code=500,
                    detail=f"Both parsers failed. LLM: {str(llm_error)}, Regex: {str(regex_error)}"
                )
    
    # LLM mode
    elif request.parser == "llm":
        try:
            result, usage = llm_parser.parse_receipt(request.receipt_text)
            return ReceiptResponse(
                success=True,
                parser_used="llm",
                data=result,
                usage=usage
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"LLM parsing failed: {str(e)}"
            )
    
    # Regex mode
    elif request.parser == "regex":
        try:
            result = regex_parser.parse_receipt(request.receipt_text)
            return ReceiptResponse(
                success=True,
                parser_used="regex",
                data=result
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Regex parsing failed: {str(e)}"
            )

# Compare parsers endpoint
@app.post("/compare")
def compare_parsers(request: ReceiptRequest):
    """
    Compare results from both parsers
    """
    
    if not request.receipt_text.strip():
        raise HTTPException(status_code=400, detail="receipt_text cannot be empty")
    
    results = {}
    
    # Try LLM
    try:
        llm_result, usage = llm_parser.parse_receipt(request.receipt_text)
        results["llm"] = {
            "success": True,
            "data": llm_result,
            "usage": usage
        }
    except Exception as e:
        results["llm"] = {
            "success": False,
            "error": str(e)
        }
    
    # Try Regex
    try:
        regex_result = regex_parser.parse_receipt(request.receipt_text)
        results["regex"] = {
            "success": True,
            "data": regex_result
        }
    except Exception as e:
        results["regex"] = {
            "success": False,
            "error": str(e)
        }
    
    # Compare if both succeeded
    if results["llm"]["success"] and results["regex"]["success"]:
        llm_data = results["llm"]["data"]
        regex_data = results["regex"]["data"]
        
        results["comparison"] = {
            "merchant_match": llm_data.get("merchant") == regex_data.get("merchant"),
            "total_match": llm_data.get("total") == regex_data.get("total"),
            "items_count": {
                "llm": len(llm_data.get("items", [])),
                "regex": len(regex_data.get("items", []))
            }
        }
    
    return results

# Get parser info
@app.get("/parsers")
def get_parsers_info():
    """Get information about available parsers"""
    return {
        "parsers": [
            {
                "name": "llm",
                "description": "Uses Claude AI - handles any language/format",
                "pros": ["Multi-language", "Flexible", "High accuracy"],
                "cons": ["Costs money", "Requires API", "Slower"]
            },
            {
                "name": "regex",
                "description": "Pattern matching - fast but limited",
                "pros": ["Free", "Fast", "No API needed"],
                "cons": ["English only", "Strict format", "Brittle"]
            },
            {
                "name": "auto",
                "description": "Tries LLM first, falls back to regex",
                "pros": ["Best of both worlds", "Resilient"],
                "cons": ["Costs money when LLM is used"]
            }
        ]
    }