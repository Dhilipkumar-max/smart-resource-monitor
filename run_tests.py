import unittest
import sys
import os

# Add current directory to path so modules can be imported
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, base_dir)

if __name__ == "__main__":
    loader = unittest.TestLoader()
    test_dir = os.path.join(base_dir, 'tests')
    suite = loader.discover(test_dir)
    print(f"Running {suite.countTestCases()} tests...")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if not result.wasSuccessful():
        sys.exit(1)
