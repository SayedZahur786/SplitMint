"""
Test script to demonstrate the enhanced categorization system
"""

from SplitMint.backend.categorizer import categorize_merchant, get_valid_categories

def test_categorization():
    print("=" * 80)
    print("SPLITMINT - ENHANCED CATEGORIZATION SYSTEM")
    print("=" * 80)
    
    # Show all categories
    print("\n📋 All Available Categories:")
    print("-" * 80)
    categories = get_valid_categories()
    for i, cat in enumerate(categories, 1):
        print(f"{i:2}. {cat}")
    
    print(f"\n✅ Total Categories: {len(categories)}")
    
    # Comprehensive test cases for each category
    print("\n\n🧪 Testing Categorization with Real Merchants:")
    print("=" * 80)
    
    test_cases = {
        "Food and Drinks": [
            "Domino's Pizza India",
            "Starbucks Coffee",
            "Swiggy",
            "Zomato",
            "McDonald's"
        ],
        "Groceries": [
            "BigBasket",
            "Blinkit",
            "DMart",
            "Reliance Fresh",
            "JioMart"
        ],
        "Shopping": [
            "Amazon India",
            "Flipkart",
            "Myntra",
            "Croma Electronics",
            "Lenskart"
        ],
        "Entertainment": [
            "Netflix",
            "BookMyShow",
            "PVR Cinemas",
            "Spotify",
            "Disney+ Hotstar"
        ],
        "Travel and Transport": [
            "Uber India",
            "Ola Cabs",
            "IndiGo Airlines",
            "MakeMyTrip",
            "Indian Oil Petrol Pump"
        ],
        "Bills and Utilities": [
            "Airtel Recharge",
            "Jio Prepaid",
            "BSES Electricity Bill",
            "Tata Sky DTH",
            "Broadband Bill"
        ],
        "Healthcare": [
            "Apollo Pharmacy",
            "1mg",
            "Fortis Hospital",
            "Medplus",
            "PharmEasy"
        ],
        "Education": [
            "Byju's",
            "Unacademy",
            "Udemy",
            "School Fees Payment",
            "Crossword Bookstore"
        ],
        "Investments": [
            "Zerodha",
            "Groww",
            "HDFC Life Insurance",
            "SBI Mutual Fund",
            "LIC Premium"
        ],
        "Personal Care": [
            "Cult.fit Membership",
            "Urban Company",
            "Lakme Salon",
            "Gold's Gym",
            "Nykaa Beauty"
        ],
        "Subscriptions": [
            "Amazon Prime Subscription",
            "YouTube Premium",
            "Microsoft Office 365",
            "LinkedIn Premium",
            "Adobe Creative Cloud"
        ],
        "Others": [
            "Unknown Merchant XYZ",
            "Random Store 123",
            "Miscellaneous Payment"
        ]
    }
    
    # Test each category
    total_tests = 0
    correct_predictions = 0
    
    for expected_category, merchants in test_cases.items():
        print(f"\n{expected_category}")
        print("-" * 80)
        
        for merchant in merchants:
            predicted_category = categorize_merchant(merchant)
            total_tests += 1
            
            # Check if prediction matches expected
            is_correct = predicted_category == expected_category
            if is_correct:
                correct_predictions += 1
                status = "✅"
            else:
                status = "❌"
            
            print(f"{status} {merchant:45s} -> {predicted_category}")
    
    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {total_tests}")
    print(f"Correct Predictions: {correct_predictions}")
    print(f"Accuracy: {(correct_predictions/total_tests)*100:.1f}%")
    print(f"\nNote: Using Gemini AI (gemini-2.0-flash-exp) with keyword fallback")
    print("=" * 80)


if __name__ == "__main__":
    test_categorization()
