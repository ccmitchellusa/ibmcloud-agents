#!/bin/bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  📝 IBMCloud Static Docs Site - Base file to check deps and init env.
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# Author: Maxim Shelepov
# Description: Initializes local env for docs site.

echo "Checking node.js installation..."
if command -v node &> /dev/null; then
    echo "✅ node.js installation found"
else
    echo "❌ node.js installation not found. Please install node.js."
    exit 1
fi

# Install deps.
echo "Installing docs site deps..."
npm i
echo "✅ deps installed."
