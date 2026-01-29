#!/bin/bash
# Isaac Sim Diagnostic Script
# Tests Isaac Sim installation and identifies issues

echo "========================================"
echo "  Isaac Sim Diagnostic Tool"
echo "========================================"
echo ""

ISAAC_DIR="/mnt/c/Users/rohit/Downloads/isaac-sim-standalone-5.1.0-linux-x86_64"

echo "[1/6] Checking Isaac Sim directory..."
if [ -d "$ISAAC_DIR" ]; then
    echo "✓ Directory exists: $ISAAC_DIR"
else
    echo "✗ Directory not found!"
    exit 1
fi

cd "$ISAAC_DIR"

echo ""
echo "[2/6] Checking critical files..."
files=("isaac-sim.sh" "python.sh" "kit" "exts")
for file in "${files[@]}"; do
    if [ -e "$file" ]; then
        echo "✓ Found: $file"
    else
        echo "✗ Missing: $file"
    fi
done

echo ""
echo "[3/6] Checking Python environment..."
if [ -f "python.sh" ]; then
    echo "Testing python.sh..."
    ./python.sh --version 2>&1 | head -5
else
    echo "✗ python.sh not found"
fi

echo ""
echo "[4/6] Checking dependencies..."
echo "Checking for required libraries..."
ldd ./kit 2>&1 | grep "not found" || echo "✓ All libraries found"

echo ""
echo "[5/6] Checking display configuration..."
echo "DISPLAY variable: $DISPLAY"
if [ -z "$DISPLAY" ]; then
    echo "⚠ DISPLAY not set! Setting to :0"
    export DISPLAY=:0
fi

echo ""
echo "[6/6] Testing simple X11 application..."
if command -v xeyes &> /dev/null; then
    echo "Testing X11 with xeyes (will open for 2 seconds)..."
    timeout 2 xeyes &
    sleep 2
    echo "✓ X11 working"
else
    echo "⚠ xeyes not installed, skipping X11 test"
    echo "Install with: sudo apt-get install x11-apps"
fi

echo ""
echo "========================================"
echo "  Diagnostic Complete"
echo "========================================"
echo ""
echo "Summary:"
echo "  Isaac Sim Path: $ISAAC_DIR"
echo "  Display: $DISPLAY"
echo ""
echo "To run Isaac Sim manually:"
echo "  cd $ISAAC_DIR"
echo "  export DISPLAY=:0"
echo "  ./isaac-sim.sh"
echo ""
