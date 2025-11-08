@echo off
REM Run TDD Login Tests

echo ============================================
echo Running TDD Login Tests
echo ============================================
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run pytest
python -m pytest tests/test_login.py -v --tb=short

echo.
echo ============================================
echo Tests Complete!
echo ============================================
pause
