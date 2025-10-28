"""
Transaction Parser Module - Extract transaction details from email text
Uses regex patterns to identify merchant, amount, and date
"""

import re
from datetime import datetime
from typing import Optional, Dict, List


def get_regex_patterns() -> List[Dict[str, re.Pattern]]:
    """
    Return list of compiled regex patterns for transaction extraction
    
    Returns:
        List of pattern dictionaries with 'amount' and 'merchant' patterns
    """
    patterns = [
        # Pattern 1: "Rs. 450 spent at Domino's" or "₹450 spent at Amazon"
        {
            'name': 'spent_at',
            'amount': re.compile(r'(?:Rs\.?\s*|₹|Rupees\s+)\s*(\d+(?:,\d+)*(?:\.\d{2})?)', re.IGNORECASE),
            'merchant': re.compile(r'(?:spent at|paid to|at)\s+([A-Za-z0-9\s&\'-]+?)(?:\s+(?:at|on|dated)|\.|$)', re.IGNORECASE)
        },
        
        # Pattern 2: "₹1299 debited to Amazon" or "Rs 1299 debited to Flipkart"
        {
            'name': 'debited_to',
            'amount': re.compile(r'(?:Rs\.?\s*|₹|Rupees\s+)\s*(\d+(?:,\d+)*(?:\.\d{2})?)', re.IGNORECASE),
            'merchant': re.compile(r'(?:debited to|credited to|to)\s+([A-Za-z0-9\s&\'-]+?)(?:\s+(?:at|on|dated)|\.|$)', re.IGNORECASE)
        },
        
        # Pattern 3: "sent 100 Rupees to Domino's" or "sent Rs 100 to Amazon"
        {
            'name': 'sent_to',
            'amount': re.compile(r'(?:sent|transferred)\s+(?:Rs\.?\s*|₹|Rupees\s+)?\s*(\d+(?:,\d+)*(?:\.\d{2})?)\s+(?:Rs\.?|₹|Rupees)?', re.IGNORECASE),
            'merchant': re.compile(r'(?:to|at)\s+([A-Za-z0-9\s&\'-]+?)(?:\s+(?:at|on|dated)|\.|$)', re.IGNORECASE)
        },
        
        # Pattern 4: "Amount: ₹180 Payment to Uber"
        {
            'name': 'amount_payment',
            'amount': re.compile(r'(?:Amount|Amt)[:\s]*(?:Rs\.?\s*|₹|Rupees\s+)\s*(\d+(?:,\d+)*(?:\.\d{2})?)', re.IGNORECASE),
            'merchant': re.compile(r'(?:payment to|paid to)\s+([A-Za-z0-9\s&\'-]+?)(?:\s+(?:at|on|dated)|\.|$)', re.IGNORECASE)
        },
        
        # Pattern 5: "₹649 to Netflix" or "Rs 649 at Starbucks"
        {
            'name': 'simple_to_at',
            'amount': re.compile(r'(?:Rs\.?\s*|₹|Rupees\s+)\s*(\d+(?:,\d+)*(?:\.\d{2})?)', re.IGNORECASE),
            'merchant': re.compile(r'(?:to|at|from)\s+([A-Za-z0-9\s&\'-]+?)(?:\s+(?:at|on|dated)|\.|$)', re.IGNORECASE)
        },
        
        # Pattern 6: "Transaction of Rs 500 at Dominos" or "Payment of ₹1200 to Amazon"
        {
            'name': 'transaction_of',
            'amount': re.compile(r'(?:transaction|payment)\s+of\s+(?:Rs\.?\s*|₹|Rupees\s+)\s*(\d+(?:,\d+)*(?:\.\d{2})?)', re.IGNORECASE),
            'merchant': re.compile(r'(?:at|to|from)\s+([A-Za-z0-9\s&\'-]+?)(?:\s+(?:at|on|dated)|\.|$)', re.IGNORECASE)
        },
        
        # Pattern 7: Generic "Rs 500" or "₹500" or "Rupees 500" with merchant nearby
        {
            'name': 'generic',
            'amount': re.compile(r'(?:Rs\.?\s*|₹|Rupees\s+)\s*(\d+(?:,\d+)*(?:\.\d{2})?)', re.IGNORECASE),
            'merchant': re.compile(r'([A-Z][A-Za-z0-9\s&\'-]{2,30}?)(?:\s+(?:on|dated|transaction|at)|\.|$)', re.IGNORECASE)
        }
    ]
    
    return patterns


def extract_date_from_text(text: str) -> str:
    """
    Extract date from email text, or return today's date
    
    Args:
        text: Email body or subject text
    
    Returns:
        Date string in YYYY-MM-DD format
    """
    # Common date patterns
    date_patterns = [
        r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',  # DD/MM/YYYY or DD-MM-YYYY
        r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',  # YYYY/MM/DD or YYYY-MM-DD
        r'(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{4})',  # DD Month YYYY
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                groups = match.groups()
                
                # Handle different formats
                if len(groups) == 3:
                    if groups[0].isdigit() and len(groups[0]) == 4:
                        # YYYY-MM-DD format
                        year, month, day = groups
                        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                    elif groups[1].isdigit():
                        # DD-MM-YYYY format
                        day, month, year = groups
                        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                    else:
                        # DD Month YYYY format
                        months = {
                            'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
                            'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
                            'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
                        }
                        day, month_name, year = groups
                        month = months.get(month_name.lower()[:3], '01')
                        return f"{year}-{month}-{day.zfill(2)}"
            except:
                pass
    
    # Default to today's date
    return datetime.now().strftime('%Y-%m-%d')


def parse_transaction_from_email(subject: str, body: str) -> Optional[Dict[str, any]]:
    """
    Extract transaction details from email subject and body
    
    Args:
        subject: Email subject line
        body: Email body text
    
    Returns:
        Dictionary with merchant, amount, date or None if no transaction found
    """
    # Combine subject and body for parsing
    full_text = f"{subject} {body}"
    
    patterns = get_regex_patterns()
    
    merchant = None
    amount = None
    
    # Try each pattern until we find a match
    for pattern_set in patterns:
        # Extract amount
        amount_match = pattern_set['amount'].search(full_text)
        if amount_match:
            amount_str = amount_match.group(1).replace(',', '')
            try:
                amount = float(amount_str)
            except ValueError:
                continue
            
            # Extract merchant
            merchant_match = pattern_set['merchant'].search(full_text)
            if merchant_match:
                merchant = merchant_match.group(1).strip()
                
                # Clean up merchant name
                merchant = re.sub(r'\s+', ' ', merchant)  # Remove extra spaces
                merchant = merchant.strip('.,;:-')  # Remove trailing punctuation
                
                # If we found both, we're done
                if merchant and amount:
                    break
    
    # If no transaction found, return None
    if not merchant or not amount:
        return None
    
    # Extract date
    date_str = extract_date_from_text(full_text)
    
    return {
        'merchant': merchant,
        'amount': amount,
        'date': date_str
    }


# Example usage and testing
if __name__ == "__main__":
    # Test cases
    test_emails = [
        {"subject": "Payment Alert", "body": "Rs. 450 spent at Domino's Pizza on 15 Oct 2025"},
        {"subject": "Transaction Alert", "body": "₹1299 debited to Amazon on 18/10/2025"},
        {"subject": "Bank Alert", "body": "Amount: ₹180 Payment to Uber dated 20-10-2025"},
        {"subject": "Payment Confirmation", "body": "₹649 to Netflix subscription"},
        {"subject": "Purchase Alert", "body": "Transaction of Rs 2500 at Big Bazaar"},
    ]
    
    print("🧪 Testing transaction parser...\n")
    for i, email in enumerate(test_emails, 1):
        result = parse_transaction_from_email(email['subject'], email['body'])
        print(f"Test {i}:")
        print(f"  Subject: {email['subject']}")
        print(f"  Body: {email['body']}")
        print(f"  Result: {result}")
        print()
