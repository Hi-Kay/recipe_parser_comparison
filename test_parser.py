import os
import json
import argparse
from pathlib import Path
from parsers import regex_parser, llm_parser

def load_receipt(filepath):
    """Load receipt text from a file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def compare_parsers(filepath, verbose=True):
    """Compare both parsers on the same receipt"""
    
    if verbose:
        print("\n" + "=" * 70)
        print(f"📄 Testing: {filepath}")
        print("=" * 70)
    
    # Load receipt
    receipt_text = load_receipt(filepath)
    
    if verbose:
        print("\n📝 Original Receipt:")
        print("-" * 70)
        preview = receipt_text[:150] + "..." if len(receipt_text) > 150 else receipt_text
        print(preview)
        print("-" * 70)
    
    results = {}
    
    # Test Regex Parser
    if verbose:
        print("\n🔧 REGEX PARSER:")
        print("-" * 70)
    
    try:
        result_regex = regex_parser.parse_receipt(receipt_text)
        total = result_regex.get('total', None)
        items_count = len(result_regex.get('items', []))
        
        if verbose:
            print(f"✅ Success")
            print(f"   Merchant: {result_regex.get('merchant', 'N/A')}")
            print(f"   Items: {items_count}")
            if total is not None:
                print(f"   💰 Total: ${total:.2f}")
            else:
                print(f"   💰 Total: N/A")
        
        results['regex'] = {'success': True, 'data': result_regex}
    except Exception as e:
        if verbose:
            print(f"❌ Failed: {e}")
        results['regex'] = {'success': False, 'error': str(e)}
    
    # Test LLM Parser
    if verbose:
        print("\n🤖 LLM PARSER:")
        print("-" * 70)
    
    try:
        result_llm, usage = llm_parser.parse_receipt(receipt_text)
        total = result_llm.get('total', None)
        items_count = len(result_llm.get('items', []))
        
        if verbose:
            print(f"✅ Success")
            print(f"   Merchant: {result_llm.get('merchant', 'N/A')}")
            print(f"   Items: {items_count}")
            if total is not None:
                print(f"   💰 Total: ${total:.2f}")
            else:
                print(f"   💰 Total: N/A")
        
        results['llm'] = {
            'success': True, 
            'data': result_llm,
            'usage': usage
        }
    except Exception as e:
        if verbose:
            print(f"❌ Failed: {e}")
        results['llm'] = {'success': False, 'error': str(e)}
    
    # Comparison Summary
    if verbose:
        print("\n📊 COMPARISON:")
        print("-" * 70)
        
        if results['regex']['success'] and results['llm']['success']:
            regex_data = results['regex']['data']
            llm_data = results['llm']['data']
            
            merchant_match = regex_data.get('merchant') == llm_data.get('merchant')
            total_match = regex_data.get('total') == llm_data.get('total')
            items_match = len(regex_data.get('items', [])) == len(llm_data.get('items', []))
            
            print(f"Merchant: {'✅ Match' if merchant_match else '⚠️  Different'}")
            print(f"Total: {'✅ Match' if total_match else '⚠️  Different'}")
            if not total_match:
                regex_total = regex_data.get('total')
                llm_total = llm_data.get('total')
                
                regex_str = f"${regex_total:.2f}" if regex_total is not None else "N/A"
                llm_str = f"${llm_total:.2f}" if llm_total is not None else "N/A"
                print(f"  Regex: {regex_str}, LLM: {llm_str}")
            print(f"Items count: {'✅ Match' if items_match else '⚠️  Different'} (Regex={len(regex_data.get('items', []))}, LLM={len(llm_data.get('items', []))})")
            
        elif results['regex']['success']:
            print("⚠️  Only Regex succeeded")
        elif results['llm']['success']:
            print("💡 Only LLM succeeded (Regex failed on format)")
        else:
            print("❌ Both parsers failed")
        
        print("=" * 70)
    
    return results

def list_test_files(test_data_dir="test_data"):
    """List all available test files"""
    test_data_path = Path(test_data_dir)
    files = sorted(test_data_path.rglob("*.txt"))
    
    print("\n📁 Available test files:")
    print("-" * 70)
    for i, filepath in enumerate(files, 1):
        print(f"{i}. {filepath}")
    print("-" * 70)
    
    return files

def run_tests(files=None, test_data_dir="test_data", verbose=True):
    """Run tests on specified files or all files"""
    
    test_data_path = Path(test_data_dir)
    
    if files:
        test_files = [Path(f) for f in files]
    else:
        test_files = list(test_data_path.rglob("*.txt"))
    
    if not test_files:
        print("❌ No test files found!")
        return
    
    print(f"\n🚀 Running tests on {len(test_files)} file(s)...\n")
    
    summary = {
        'total': len(test_files),
        'regex_success': 0,
        'llm_success': 0,
        'both_success': 0,
        'both_failed': 0,
        'total_receipt_amount': 0.0
    }
    
    for filepath in test_files:
        results = compare_parsers(filepath, verbose=verbose)
        
        # Update summary
        if results['regex']['success']:
            summary['regex_success'] += 1
        if results['llm']['success']:
            summary['llm_success'] += 1
            # Add receipt total if available
            llm_total = results['llm']['data'].get('total')
            if llm_total:
                summary['total_receipt_amount'] += llm_total
        if results['regex']['success'] and results['llm']['success']:
            summary['both_success'] += 1
        if not results['regex']['success'] and not results['llm']['success']:
            summary['both_failed'] += 1
    
    # Final Summary
    print("\n" + "=" * 70)
    print("📈 FINAL SUMMARY")
    print("=" * 70)
    print(f"Total files tested: {summary['total']}")
    print(f"Regex successes: {summary['regex_success']} ({summary['regex_success']/summary['total']*100:.0f}%)")
    print(f"LLM successes: {summary['llm_success']} ({summary['llm_success']/summary['total']*100:.0f}%)")
    print(f"Both succeeded: {summary['both_success']}")
    print(f"Both failed: {summary['both_failed']}")
    print("-" * 70)
    print(f"💵 RECEIPT TOTALS:")
    print(f"Combined total of all receipts: ${summary['total_receipt_amount']:.2f}")
    if summary['llm_success'] > 0:
        print(f"Average receipt amount: ${summary['total_receipt_amount']/summary['llm_success']:.2f}")
    print("=" * 70)
    
    # Insights
    llm_only = summary['llm_success'] - summary['both_success']
    if llm_only > 0:
        print(f"\n💡 LLM handled {llm_only} receipt(s) that Regex couldn't!")
    
    print()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test receipt parsers')
    parser.add_argument('files', nargs='*', help='Specific files to test (optional)')
    parser.add_argument('--list', '-l', action='store_true', help='List all test files')
    parser.add_argument('--all', '-a', action='store_true', help='Test all files')
    parser.add_argument('--quiet', '-q', action='store_true', help='Minimal output (summary only)')
    
    args = parser.parse_args()
    
    if args.list:
        list_test_files()
    elif args.all or not args.files:
        run_tests(verbose=not args.quiet)
    else:
        run_tests(args.files, verbose=not args.quiet)