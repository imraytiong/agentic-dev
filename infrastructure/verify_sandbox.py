import socket
import urllib.request
import os
import sys

def check_tcp(host, port):
    print(f"Checking TCP connection to {host}:{port}...")
    try:
        with socket.create_connection((host, port), timeout=2):
            print(f"SUCCESS: Connected to {host}:{port}")
            return True
    except Exception as e:
        print(f"FAILURE: Could not connect to {host}:{port}: {e}")
        return False

def check_https(url):
    print(f"Checking HTTPS connection to {url}...")
    try:
        # Use a common API endpoint or search engine
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            print(f"SUCCESS: Connected to {url} (Status: {response.status})")
            return True
    except Exception as e:
        print(f"FAILURE: Could not connect to {url}: {e}")
        return False

def check_file_write(path):
    print(f"Checking Write access to {path}...")
    try:
        # Create directory if it doesn't exist for the test (though .data and tmp should exist)
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
            
        test_file = os.path.join(path, "sandbox_test.txt")
        with open(test_file, "w") as f:
            f.write("sandbox test")
        os.remove(test_file)
        print(f"SUCCESS: Write access to {path} confirmed")
        return True
    except Exception as e:
        print(f"FAILURE: No write access to {path}: {e}")
        return False

if __name__ == "__main__":
    print("--- Sandbox Validation Script (CTO Mandate) ---")
    
    # Get current working directory for logging
    print(f"Working Directory: {os.getcwd()}")
    print(f"Environment ADK_ENV: {os.getenv('ADK_ENV')}")
    
    # 1. Network Checks
    # Note: These will only pass if the containers are UP
    pg_ok = check_tcp("localhost", 5432)
    redis_ok = check_tcp("localhost", 6379)
    https_ok = check_https("https://www.google.com")
    
    # 2. Filesystem Checks
    data_ok = check_file_write(".data")
    tmp_ok = check_file_write("tmp")
    
    # Root write should be blocked if Seatbelt profile is working as intended (Read-Only root)
    root_write_ok = check_file_write(".")
    
    print("\n--- Summary ---")
    print(f"Postgres (5432):     {'PASS' if pg_ok else 'FAIL'}")
    print(f"Redis (6379):        {'PASS' if redis_ok else 'FAIL'}")
    print(f"HTTPS (443):         {'PASS' if https_ok else 'FAIL'}")
    print(f"Write .data:         {'PASS' if data_ok else 'FAIL'}")
    print(f"Write tmp:           {'PASS' if tmp_ok else 'FAIL'}")
    print(f"Root Write Allowed:  {'YES (Unexpected if sandboxed)' if root_write_ok else 'NO (Expected)'}")

    # Exit with error if critical checks fail (except PG/Redis which might be down)
    if not https_ok or not data_ok or not tmp_ok:
        sys.exit(1)
    sys.exit(0)
