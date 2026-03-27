#!/usr/bin/env python3
"""
Unified test runner for Prusa Connect Webcam Uploader

This script provides a comprehensive testing solution that combines:
- Code quality checks (linting, type checking, formatting)
- Test execution with coverage
- Performance testing
- Security checks

Usage:
    python run_tests.py                    # Run all checks
    python run_tests.py --quick           # Skip slow tests
    python run_tests.py --coverage        # Generate coverage report
    python run_tests.py --lint-only       # Only run linting
    python run_tests.py --help           # Show all options
"""

import subprocess
import sys
import argparse
import os
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output."""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    NC = '\033[0m'  # No Color


class TestRunner:
    """Unified test runner with comprehensive checks."""
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.project_root = Path(__file__).parent
        self.main_module = "prusa_webcam_uploader"
        
    def print_status(self, message, color=Colors.BLUE):
        """Print status message with color."""
        print(f"{color}[INFO]{Colors.NC} {message}")
        
    def print_success(self, message):
        """Print success message."""
        print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}")
        
    def print_warning(self, message):
        """Print warning message."""
        print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")
        
    def print_error(self, message):
        """Print error message."""
        print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")
        
    def run_command(self, command, description, required=True):
        """Run a command and handle results."""
        self.print_status(f"{description}...")
        
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                check=True, 
                capture_output=True, 
                text=True,
                cwd=self.project_root
            )
            
            if self.verbose and result.stdout:
                print(result.stdout)
                
            self.print_success(f"{description} completed")
            return True
            
        except subprocess.CalledProcessError as e:
            if required:
                self.print_error(f"{description} failed")
                if e.stdout:
                    print("STDOUT:", e.stdout)
                if e.stderr:
                    print("STDERR:", e.stderr)
                return False
            else:
                self.print_warning(f"{description} had issues (non-critical)")
                if self.verbose and e.stderr:
                    print("STDERR:", e.stderr)
                return True
                
    def check_dependencies(self):
        """Check if required dependencies are available."""
        self.print_status("Checking dependencies...")
        
        # Check if main module exists
        if not (self.project_root / f"{self.main_module}.py").exists():
            self.print_error(f"Main module {self.main_module}.py not found")
            return False
            
        # Check if test directory exists
        if not (self.project_root / "tests").exists():
            self.print_error("Tests directory not found")
            return False
            
        return True
        
    def run_linting(self):
        """Run code linting with flake8."""
        cmd = f"flake8 {self.main_module}.py --max-line-length=100 --ignore=E501,W503,E203"
        return self.run_command(cmd, "Code linting (flake8)")
        
    def run_type_checking(self):
        """Run type checking with mypy."""
        cmd = f"mypy {self.main_module}.py --ignore-missing-imports --no-strict-optional"
        return self.run_command(cmd, "Type checking (mypy)", required=False)
        
    def run_formatting(self):
        """Run code formatting with black."""
        cmd = f"black {self.main_module}.py --line-length 100 --check"
        return self.run_command(cmd, "Code formatting (black)", required=False)
        
    def run_security_check(self):
        """Run security check with bandit."""
        cmd = f"bandit -r {self.main_module}.py -q"
        return self.run_command(cmd, "Security check (bandit)", required=False)
        
    def run_tests(self, quick=False, coverage=False):
        """Run the test suite."""
        cmd = "pytest"
        
        if quick:
            cmd += " -m 'not slow'"
            
        if coverage:
            cmd += " --cov=prusa_webcam_uploader --cov-report=html --cov-report=term-missing"
            
        if self.verbose:
            cmd += " -v"
            
        return self.run_command(cmd, "Test suite (pytest)")
        
    def run_performance_tests(self, quick=False):
        """Run performance tests."""
        cmd = "pytest tests/test_performance.py"
        
        if quick:
            cmd += " -m 'not slow'"
            
        if self.verbose:
            cmd += " -v"
            
        return self.run_command(cmd, "Performance tests")
        
    def run_all_checks(self, quick=False, coverage=False, lint_only=False, 
                      type_only=False, perf_only=False):
        """Run all quality checks and tests."""
        
        print(f"{Colors.CYAN}{'='*60}{Colors.NC}")
        print(f"{Colors.WHITE}🧪 Prusa Connect Webcam Uploader Test Suite{Colors.NC}")
        print(f"{Colors.CYAN}{'='*60}{Colors.NC}")
        
        if not self.check_dependencies():
            return False
            
        success = True
        
        # Run specific checks based on flags
        if lint_only:
            success &= self.run_linting()
        elif type_only:
            success &= self.run_type_checking()
        elif perf_only:
            success &= self.run_performance_tests(quick)
        else:
            # Run all checks
            success &= self.run_linting()
            success &= self.run_type_checking()
            success &= self.run_formatting()
            success &= self.run_security_check()
            success &= self.run_tests(quick, coverage)
            
        # Final result
        print(f"\n{Colors.CYAN}{'='*60}{Colors.NC}")
        if success:
            self.print_success("🎉 All checks passed!")
            if coverage:
                self.print_status("📊 Coverage report: htmlcov/index.html")
        else:
            self.print_error("💥 Some checks failed!")
            
        return success


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Unified test runner for Prusa Connect Webcam Uploader",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                    # Run all checks
  python run_tests.py --quick           # Skip slow tests
  python run_tests.py --coverage        # Generate coverage report
  python run_tests.py --lint-only       # Only run linting
  python run_tests.py --type-only       # Only run type checking
  python run_tests.py --perf-only       # Only run performance tests
        """
    )
    
    parser.add_argument("--quick", "-q", action="store_true", 
                       help="Skip slow tests")
    parser.add_argument("--coverage", "-c", action="store_true", 
                       help="Generate coverage report")
    parser.add_argument("--lint-only", "-l", action="store_true", 
                       help="Only run linting")
    parser.add_argument("--type-only", "-t", action="store_true", 
                       help="Only run type checking")
    parser.add_argument("--perf-only", "-p", action="store_true", 
                       help="Only run performance tests")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Verbose output")
    
    args = parser.parse_args()
    
    runner = TestRunner(verbose=args.verbose)
    success = runner.run_all_checks(
        quick=args.quick,
        coverage=args.coverage,
        lint_only=args.lint_only,
        type_only=args.type_only,
        perf_only=args.perf_only
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
