"""
Categorizer Module - AI-powered merchant categorization using Gemini
"""

import os
from typing import Optional
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_valid_categories() -> list:
    """
    Return list of valid transaction categories
    
    Returns:
        List of category strings
    """
    return [
        "Food and Drinks",
        "Groceries",
        "Shopping",
        "Entertainment",
        "Travel and Transport",
        "Bills and Utilities",
        "Healthcare",
        "Education",
        "Investments",
        "Personal Care",
        "Subscriptions",
        "Others"
    ]


def categorize_merchant(merchant_name: str) -> str:
    """
    Use Gemini AI to categorize a merchant into predefined categories
    
    Args:
        merchant_name: Name of the merchant/store
    
    Returns:
        Category string (falls back to "Others" on error)
    """
    try:
        # Get API key from environment
        api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            print("⚠️ WARNING: GEMINI_API_KEY not found in .env, using fallback categorization")
            return categorize_merchant_fallback(merchant_name)
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Create prompt
        valid_categories = get_valid_categories()
        categories_str = ", ".join(valid_categories)
        
        prompt = f"""Categorize this merchant into ONE category from the following list:
{categories_str}

Merchant: {merchant_name}

Return ONLY the category name, nothing else. Choose the most appropriate category."""
        
        # Generate response
        response = model.generate_content(prompt)
        category = response.text.strip()
        
        # Validate response is in valid categories
        if category in valid_categories:
            return category
        
        # Try to find a partial match
        for valid_cat in valid_categories:
            if valid_cat.lower() in category.lower() or category.lower() in valid_cat.lower():
                return valid_cat
        
        # If no match, use fallback
        print(f"⚠️ Gemini returned invalid category '{category}', using fallback")
        return categorize_merchant_fallback(merchant_name)
        
    except Exception as e:
        print(f"⚠️ Error calling Gemini API: {e}")
        print(f"   Using fallback categorization for: {merchant_name}")
        return categorize_merchant_fallback(merchant_name)


def categorize_merchant_fallback(merchant_name: str) -> str:
    """
    Fallback categorization using keyword matching
    
    Args:
        merchant_name: Name of the merchant/store
    
    Returns:
        Category string
    """
    merchant_lower = merchant_name.lower()
    
    # Food and Drinks keywords (restaurants, cafes, food delivery)
    if any(keyword in merchant_lower for keyword in [
        'restaurant', 'cafe', 'coffee', 'pizza', 'burger', 'food',
        'domino', 'mcdonald', 'kfc', 'subway', 'starbucks',
        'swiggy', 'zomato', 'ubereats', 'dining', 'kitchen',
        'biryani', 'dhaba', 'bar', 'pub', 'drinks',
        'bakery', 'tea', 'juice', 'ice cream', 'dunkin'
    ]):
        return "Food and Drinks"
    
    # Groceries keywords (supermarkets, fresh produce)
    if any(keyword in merchant_lower for keyword in [
        'grocery', 'supermarket', 'blinkit', 'bigbasket', 'grofers',
        'instamart', 'dunzo', 'fresh', 'vegetables', 'fruits',
        'dmart', 'reliance fresh', 'more megastore', 'nature\'s basket',
        'spencer', 'star bazaar', 'jiomart'
    ]):
        return "Groceries"
    
    # Shopping keywords (e-commerce, retail, fashion)
    if any(keyword in merchant_lower for keyword in [
        'amazon', 'flipkart', 'myntra', 'ajio', 'meesho',
        'shop', 'store', 'mart', 'bazaar', 'mall', 'retail',
        'fashion', 'clothing', 'electronics', 'apparel',
        'furniture', 'decor', 'snapdeal', 'nykaa', 'lenskart',
        'vijay sales', 'croma', 'reliance digital'
    ]):
        return "Shopping"
    
    # Entertainment keywords (streaming, movies, events)
    if any(keyword in merchant_lower for keyword in [
        'netflix', 'prime', 'hotstar', 'spotify', 'youtube',
        'movie', 'cinema', 'theater', 'theatre', 'pvr', 'inox',
        'game', 'entertainment', 'music', 'concert', 'event',
        'bookmyshow', 'paytm insider', 'sony liv', 'zee5',
        'disney', 'voot', 'mx player'
    ]):
        return "Entertainment"
    
    # Travel and Transport keywords (cabs, flights, hotels, fuel)
    if any(keyword in merchant_lower for keyword in [
        'uber', 'ola', 'rapido', 'taxi', 'cab', 'metro',
        'bus', 'train', 'flight', 'airline', 'fuel', 'petrol',
        'transport', 'travel', 'hotel', 'resort', 'booking',
        'airbnb', 'makemytrip', 'goibibo', 'cleartrip', 'irctc',
        'indigo', 'spicejet', 'vistara', 'air india', 'diesel',
        'parking', 'toll', 'oyo'
    ]):
        return "Travel and Transport"
    
    # Bills and Utilities keywords (electricity, water, internet, phone)
    if any(keyword in merchant_lower for keyword in [
        'electricity', 'water', 'gas', 'bill', 'utility',
        'broadband', 'internet', 'wifi', 'recharge', 'mobile',
        'airtel', 'jio', 'vodafone', 'bsnl', 'tata', 'adani',
        'reliance', 'postpaid', 'prepaid', 'tata sky', 'dish tv',
        'sun direct', 'airtel digital', 'dth'
    ]):
        return "Bills and Utilities"
    
    # Healthcare keywords (hospitals, pharmacy, medical)
    if any(keyword in merchant_lower for keyword in [
        'hospital', 'clinic', 'doctor', 'medical', 'health',
        'pharmacy', 'apollo', 'medplus', 'netmeds', '1mg',
        'pharmeasy', 'medicine', 'diagnostic', 'lab', 'test',
        'fortis', 'max', 'manipal', 'narayana', 'dental',
        'physiotherapy', 'ayurveda'
    ]):
        return "Healthcare"
    
    # Education keywords (courses, books, tuition)
    if any(keyword in merchant_lower for keyword in [
        'education', 'school', 'college', 'university', 'course',
        'tuition', 'coaching', 'udemy', 'coursera', 'upgrad',
        'byju', 'unacademy', 'vedantu', 'toppr', 'book',
        'library', 'stationery', 'exam', 'fees', 'admission'
    ]):
        return "Education"
    
    # Investments keywords (mutual funds, stocks, insurance)
    if any(keyword in merchant_lower for keyword in [
        'investment', 'mutual fund', 'stock', 'sip', 'insurance',
        'zerodha', 'groww', 'upstox', 'angel', 'paytm money',
        'lic', 'hdfc life', 'icici prudential', 'sbi life',
        'policy', 'premium', 'fd', 'fixed deposit', 'recurring'
    ]):
        return "Investments"
    
    # Personal Care keywords (salon, spa, beauty, gym)
    if any(keyword in merchant_lower for keyword in [
        'salon', 'spa', 'beauty', 'parlour', 'gym', 'fitness',
        'yoga', 'massage', 'wellness', 'hair', 'skin',
        'cult.fit', 'urban company', 'lakme', 'vlcc',
        'grooming', 'cosmetics', 'makeup'
    ]):
        return "Personal Care"
    
    # Subscriptions keywords (recurring services)
    if any(keyword in merchant_lower for keyword in [
        'subscription', 'monthly', 'annual', 'membership',
        'amazon prime', 'youtube premium', 'linkedin premium',
        'office 365', 'adobe', 'microsoft', 'apple',
        'google one', 'icloud', 'dropbox', 'canva pro'
    ]):
        return "Subscriptions"
    
    # Default to Others
    return "Others"


# Example usage and testing
if __name__ == "__main__":
    print("🧪 Testing merchant categorization...\n")
    
    test_merchants = [
        "Domino's Pizza",
        "Amazon India",
        "Netflix",
        "Uber",
        "Apollo Pharmacy",
        "Airtel Recharge",
        "Starbucks",
        "Unknown Merchant XYZ"
    ]
    
    for merchant in test_merchants:
        category = categorize_merchant(merchant)
        print(f"{merchant:30} → {category}")
