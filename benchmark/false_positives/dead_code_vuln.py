# GROUND_TRUTH: SAFE
"""
Dead code containing a vulnerability. The function is NEVER CALLED.
Should be suppressed by DeadCodeDetector.
"""
import hashlib

def vulnerable_hash(password):
    """
    VULNERABLE CODE (but dead) - Uses MD5 for password hashing.
    This function has NO callers anywhere in the codebase.
    """
    # Weak crypto - MD5 is broken, but this code is never executed
    md5_hasher = hashlib.md5()
    md5_hasher.update(password.encode())
    return md5_hasher.hexdigest()

def also_unused_function(x):
    """Another unused function."""
    return x ** 2

# Only this function is actually used
def helper_function():
    """Called by other parts of the app."""
    return "I am used somewhere"
