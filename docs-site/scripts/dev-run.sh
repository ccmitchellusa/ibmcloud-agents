#!/bin/bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  📝 IBMCloud Static Docs Site - Prod ready view of docs site.
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# Author: Maxim Shelepov
# Description: Builds and serves the docs site as if prod env.
set -x

# Initializing environment.
echo "Initializing env 👈"
script_dir="$(cd "$(dirname "$0")" && pwd)"
chmod +x "$script_dir/base.sh"
"$script_dir/base.sh"
code=$?

if [ $code -ne 0 ]; then
  exit $code
fi

# Building and serving.
echo "Running for local development 👈"
npm run dev
