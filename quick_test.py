"""Quick test runner to see results"""
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/test_login.py", "-v", "--tb=no", "-q"],
    capture_output=True,
    text=True
)

print(result.stdout)
print(result.stderr)
print(f"\n{'='*60}")
if result.returncode == 0:
    print("✅ ALL TESTS PASSED!")
else:
    print(f"⚠️  Some tests failed (Exit code: {result.returncode})")
print(f"{'='*60}")
