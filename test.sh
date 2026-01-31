#!/bin/bash

# Run all tests using unittest discovery
# This will automatically find all test_*.py files in the src directory and subdirectories
python3 -m unittest discover -s src -p "test_*.py" -v
