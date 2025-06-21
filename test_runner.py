#!/usr/bin/env python3
"""
Quick test runner for development

This script provides a simple way to run tests during development
with common configurations and options.
"""

import subprocess
import sys
import argparse
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Run tests for Prusa Connect Webcam Uploader")
    parser.add_argument("--quick", "-q", action="store_true", help="Run only quick tests")
    parser.add_argument("--coverage", "-c", action="store_true", help="Run with coverage")
    parser.add_argument("--performance", "-p", action="store_true", help="Run performance tests")
    parser.add_argument("--lint", "-l", action="store_true", help="Run linting only")
    parser.add_argument("--type-check", "-t", action="store_true", help="Run type checking only")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Check if we're in the right directory
    if not Path("prusa_webcam_uploader.py").exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    success = True
    
    # Run linting
    if args.lint or not any([args.quick, args.coverage, args.performance, args.type_check]):
        if not run_command("flake8 prusa_webcam_uploader.py --max-line-length=100 --ignore=E501,W503", "Linting"):
            success = False
    
    # Run type checking
    if args.type_check or not any([args.quick, args.coverage, args.performance, args.lint]):
        if not run_command("mypy prusa_webcam_uploader.py --ignore-missing-imports", "Type checking"):
            success = False
    
    # Determine pytest command
    pytest_cmd = "pytest"
    if args.verbose:
        pytest_cmd += " -v"
    
    if args.coverage:
        pytest_cmd += " --cov=prusa_webcam_uploader --cov-report=html --cov-report=term-missing"
    
    # Run main tests
    if not args.performance and not args.lint and not args.type_check:
        test_file = "test_prusa_webcam_uploader.py"
        if args.quick:
            pytest_cmd += " -m 'not slow'"
        
        if not run_command(f"{pytest_cmd} {test_file}", "Unit tests"):
            success = False
    
    # Run performance tests
    if args.performance:
        perf_cmd = pytest_cmd + " test_performance.py"
        if args.quick:
            perf_cmd += " -m 'not slow'"
        
        if not run_command(perf_cmd, "Performance tests"):
            success = False
    
    # Final result
    if success:
        print("\n🎉 All tests passed!")
        if args.coverage:
            print("📊 Coverage report: htmlcov/index.html")
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
