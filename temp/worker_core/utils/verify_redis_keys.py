#!/usr/bin/env python3
"""
Redis Key Verification Utility

Verifies all expected Redis keys exist for a given scan_id.
Usage: python verify_redis_keys.py <scan_id>
"""

import sys
import json
import os

# Add parent directories to path for imports (for standalone usage)
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from redis_client import redis_client, REDIS_AVAILABLE


def check_key(scan_id: str, key_suffix: str) -> tuple:
    """
    Check if a key exists in Redis and return its status and size.
    
    Returns: (exists: bool, size_bytes: int, data: any)
    """
    full_key = f"{scan_id}{key_suffix}"
    try:
        data = redis_client.get(full_key)
        if data:
            return (True, len(data.encode('utf-8')), data)
        return (False, 0, None)
    except Exception as e:
        print(f"  Error checking {full_key}: {e}")
        return (False, 0, None)


def main():
    if len(sys.argv) < 2:
        print("Usage: python verify_redis_keys.py <scan_id>")
        sys.exit(1)

    scan_id = sys.argv[1]

    if not REDIS_AVAILABLE:
        print("ERROR: Redis is not available!")
        sys.exit(1)

    print(f"\n🔍 Checking Redis keys for scan_id: {scan_id}\n")

    # Define all expected keys
    keys_to_check = [
        ("", "ProjectIndexer"),
        (":deepwiki_index", "DeepWiki"),
        (":file_deps", "FileDependencyMapper"),
        (":call_graph", "FunctionCallMapper"),
        (":sanitizer_registry", "SanitizerRegistry"),
        (":dead_code_map", "DeadCodeDetector"),
    ]

    all_exist = True

    for suffix, description in keys_to_check:
        exists, size, data = check_key(scan_id, suffix)
        status = "✅ EXISTS" if exists else "❌ MISSING"
        print(f"{status}  {description:25} (key: {scan_id}{suffix})")
        if exists:
            print(f"       Size: {size} bytes")
        print()
        if not exists:
            all_exist = False

    # Pretty print sanitizer_registry if it exists
    sanitizer_exists, _, sanitizer_data = check_key(scan_id, ":sanitizer_registry")
    if sanitizer_exists and sanitizer_data:
        print("\n📋 Sanitizer Registry Content:")
        print("-" * 50)
        try:
            registry = json.loads(sanitizer_data)
            print(json.dumps(registry, indent=2))
        except json.JSONDecodeError:
            print("  (raw data, not JSON)")
            print(f"  {sanitizer_data[:500]}...")
        print("-" * 50)

    # Print dead functions from dead_code_map
    dead_code_exists, _, dead_code_data = check_key(scan_id, ":dead_code_map")
    if dead_code_exists and dead_code_data:
        print("\n💀 Dead/Test Functions (is_dead=true or is_test_only=true):")
        print("-" * 50)
        try:
            dead_map = json.loads(dead_code_data)
            dead_functions = [
                (k, v) for k, v in dead_map.items()
                if v.get("is_dead") or v.get("is_test_only")
            ]
            if dead_functions:
                for func_key, data in dead_functions[:20]:  # Limit to 20
                    is_dead = data.get("is_dead", False)
                    is_test = data.get("is_test_only", False)
                    call_count = data.get("inbound_call_count", -1)
                    markers = []
                    if is_dead:
                        markers.append("DEAD")
                    if is_test:
                        markers.append("TEST-ONLY")
                    print(f"  {func_key}")
                    print(f"    Call count: {call_count}, Markers: {', '.join(markers)}")
            else:
                print("  No dead or test-only functions found.")
        except json.JSONDecodeError:
            print("  (unable to parse dead_code_map)")
        print("-" * 50)

    # Summary
    print(f"\n📊 Summary:")
    if all_exist:
        print("✅ All expected Redis keys are present!")
    else:
        print("⚠️  Some Redis keys are missing. Index phase may have failed.")

    return 0 if all_exist else 1


if __name__ == "__main__":
    import os  # Import here to avoid issues with path setup
    sys.exit(main())
