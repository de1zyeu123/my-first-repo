#!/bin/bash

# Hello World Test Script

echo "Running Hello World Test..."

# Test function
hello_world() {
    echo "Hello World"
}

# Run the test
output=$(hello_world)
expected="Hello World"

if [ "$output" == "$expected" ]; then
    echo "✓ Test passed: Output matches expected value"
    echo "  Expected: '$expected'"
    echo "  Got:      '$output'"
    exit 0
else
    echo "✗ Test failed: Output does not match expected value"
    echo "  Expected: '$expected'"
    echo "  Got:      '$output'"
    exit 1
fi
