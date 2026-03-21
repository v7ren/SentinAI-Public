# GROUND_TRUTH: SAFE
"""
Test-only vulnerable code. The vulnerable function is only called from a test function.
Should be suppressed by DeadCodeDetector as test-only.
"""
import sqlite3

def mock_execute(query):
    """
    Mock function that executes raw SQL - only used in tests.
    VULNERABLE but only reachable from test code.
    """
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    cursor.execute(query)  # Would be vulnerable in production
    result = cursor.fetchall()
    conn.close()
    return result

def test_mock_execute():
    """
    Test function - the ONLY caller of mock_execute.
    In production this code path is never reached.
    """
    # Test with safe data
    result = mock_execute("SELECT 1")
    assert result == [(1,)]
    print("Test passed!")

if __name__ == "__main__":
    test_mock_execute()
