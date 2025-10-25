#!/usr/bin/env python
"""
CSR App - Pre-flight Check Script
Verifies all dependencies and installations before running the app
"""

import subprocess
import sys
import os
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def run_command(command, description):
    """Run a command and return success status"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)

def check_python():
    """Check if Python is installed"""
    print_header("Checking Python Installation")
    success, output, _ = run_command("python --version", "Python version check")
    
    if success:
        print_success(f"Python is installed: {output}")
        return True
    else:
        print_error("Python is not installed or not in PATH")
        print("  Install from: https://www.python.org/")
        return False

def check_node():
    """Check if Node.js is installed"""
    print_header("Checking Node.js Installation")
    success, output, _ = run_command("node --version", "Node.js version check")
    
    if success:
        print_success(f"Node.js is installed: {output}")
        return True
    else:
        print_error("Node.js is not installed or not in PATH")
        print("  Install from: https://nodejs.org/")
        return False

def check_npm():
    """Check if npm is installed"""
    print_header("Checking npm Installation")
    success, output, _ = run_command("npm --version", "npm version check")
    
    if success:
        print_success(f"npm is installed: {output}")
        return True
    else:
        print_error("npm is not installed or not in PATH")
        return False

def check_venv():
    """Check if virtual environment exists"""
    print_header("Checking Python Virtual Environment")
    venv_path = Path("venv")
    
    if venv_path.exists():
        print_success("Virtual environment already exists")
        return True
    else:
        print_warning("Virtual environment does not exist")
        print("  Creating virtual environment...")
        success, _, _ = run_command("python -m venv venv", "Create venv")
        
        if success:
            print_success("Virtual environment created successfully")
            return True
        else:
            print_error("Failed to create virtual environment")
            return False

def check_pip_packages():
    """Check if required pip packages are installed"""
    print_header("Checking Python Dependencies")
    
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print_error("requirements.txt not found")
        return False
    
    print("Installing Python dependencies...")
    # Activate venv and install requirements
    if sys.platform == "win32":
        cmd = ".\\venv\\Scripts\\activate.bat && pip install -r requirements.txt"
    else:
        cmd = "source venv/bin/activate && pip install -r requirements.txt"
    
    success, output, error = run_command(cmd, "Install pip packages")
    
    if success:
        print_success("All Python dependencies installed successfully")
        return True
    else:
        print_error(f"Failed to install dependencies: {error}")
        return False

def check_npm_packages():
    """Check if node_modules exist"""
    print_header("Checking Node.js Dependencies")
    
    node_modules = Path("node_modules")
    if node_modules.exists():
        print_success("Node modules already installed")
        return True
    else:
        print_warning("node_modules not found")
        print("  Installing Node.js dependencies...")
        success, _, error = run_command("npm install", "Install npm packages")
        
        if success:
            print_success("All Node.js dependencies installed successfully")
            return True
        else:
            print_error(f"Failed to install npm packages: {error}")
            return False

def check_env_file():
    """Check if .env file exists"""
    print_header("Checking Environment Configuration")
    
    env_file = Path(".env")
    if env_file.exists():
        print_success(".env file exists")
        return True
    else:
        print_warning(".env file not found")
        env_example = Path(".env.example")
        if env_example.exists():
            print("  Creating .env from .env.example...")
            # Copy .env.example to .env
            import shutil
            try:
                shutil.copy(".env.example", ".env")
                print_success(".env file created from .env.example")
                return True
            except Exception as e:
                print_error(f"Failed to create .env: {e}")
                return False
        else:
            print_error(".env.example not found")
            return False

def check_directories():
    """Check if required directories exist"""
    print_header("Checking Directory Structure")
    
    required_dirs = ["src", "src/app", "src/config", "src/controller", "src/entity"]
    all_exist = True
    
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print_success(f"{dir_path}/ exists")
        else:
            print_error(f"{dir_path}/ not found")
            all_exist = False
    
    return all_exist

def check_main_files():
    """Check if main files exist"""
    print_header("Checking Main Files")
    
    required_files = ["app.py", "requirements.txt", ".env"]
    all_exist = True
    
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print_success(f"{file_path} exists")
        else:
            print_error(f"{file_path} not found")
            all_exist = False
    
    return all_exist

def test_backend_import():
    """Test if backend can be imported"""
    print_header("Testing Backend Imports")
    
    if sys.platform == "win32":
        cmd = ".\\venv\\Scripts\\activate.bat && python -c \"from src.entity import User, Role; from src.controller.auth.auth_controller import auth_blueprint; print('Backend imports successful')\""
    else:
        cmd = "source venv/bin/activate && python -c \"from src.entity import User, Role; from src.controller.auth.auth_controller import auth_blueprint; print('Backend imports successful')\""
    
    success, output, error = run_command(cmd, "Test imports")
    
    if success:
        print_success(output)
        return True
    else:
        print_error(f"Backend import test failed: {error}")
        return False

def main():
    """Run all checks"""
    print(f"\n{Colors.BLUE}")
    print("  ╔═══════════════════════════════════════════════╗")
    print("  ║   CSR App - Pre-Flight Check Script          ║")
    print("  ║   Verifying Installation & Dependencies      ║")
    print("  ╚═══════════════════════════════════════════════╝")
    print(f"{Colors.END}")
    
    checks = [
        ("Python Installation", check_python),
        ("Node.js Installation", check_node),
        ("npm Installation", check_npm),
        ("Virtual Environment", check_venv),
        ("Python Dependencies", check_pip_packages),
        ("Node.js Dependencies", check_npm_packages),
        ("Environment Configuration", check_env_file),
        ("Directory Structure", check_directories),
        ("Main Files", check_main_files),
        ("Backend Imports", test_backend_import),
    ]
    
    results = {}
    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
        except Exception as e:
            print_error(f"Error during {check_name}: {e}")
            results[check_name] = False
    
    # Summary
    print_header("Installation Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\nResults: {passed}/{total} checks passed\n")
    
    for check_name, result in results.items():
        status = f"{Colors.GREEN}PASS{Colors.END}" if result else f"{Colors.RED}FAIL{Colors.END}"
        print(f"  {check_name}: {status}")
    
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    if passed == total:
        print(f"{Colors.GREEN}✓ All checks passed! You can now run the application.{Colors.END}")
        print(f"\n{Colors.YELLOW}Next steps:{Colors.END}")
        print(f"  1. Run: {Colors.BLUE}run.bat{Colors.END} (Windows CMD)")
        print(f"  2. Or:  {Colors.BLUE}.\\run.ps1{Colors.END} (PowerShell)")
        print(f"  3. Or manually start:")
        print(f"     - Backend: {Colors.BLUE}python app.py{Colors.END}")
        print(f"     - Frontend: {Colors.BLUE}npm run dev{Colors.END}")
        print()
        return 0
    else:
        print(f"{Colors.RED}✗ Some checks failed. Please fix the issues above.{Colors.END}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())