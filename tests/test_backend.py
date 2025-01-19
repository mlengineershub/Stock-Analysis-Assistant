import sys
sys.path.append("../src")
from src.backend import process_query


def test_investment_queries():
    """Test different types of investment queries."""

    # Test cases
    queries = [
        "Should I invest in AAPL based on their latest quarterly results?",
        "What do you think about MSFT's recent performance?",
        "Is NVDA a good investment right now?",
        "Tell me about AMZN's latest financial results"
    ]

    print("Testing Investment Query Processing System\n")
    print("=" * 50)

    for query in queries:
        print(f"\nQuery: {query}")
        print("-" * 50)
        try:
            result = process_query(query, debug=True)
            print(f"Recommendation: {result}")
        except Exception as e:
            print(f"Error processing query: {str(e)}")
        print("=" * 50)


if __name__ == "__main__":
    test_investment_queries()
