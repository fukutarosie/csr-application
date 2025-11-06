"""
Quick Test Runner for Login Tests
Run this script to execute all TDD login tests
"""
import subprocess
import sys

print("=" * 60)
print("🧪 RUNNING TDD LOGIN TESTS")
print("=" * 60)
print()

# Run pytest
result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/test_login.py", "-v", "--tb=short"],
    capture_output=False
)

print()
print("=" * 60)
if result.returncode == 0:
    print("✅ ALL TESTS PASSED!")
else:
    print("❌ SOME TESTS FAILED")
print("=" * 60)

sys.exit(result.returncode)
