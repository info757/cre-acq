#!/bin/bash
# Run the Bar & Cocoa Chainlit agent
# Uses Python 3.13 venv (Chainlit has Python 3.14 compat issues)
cd "$(dirname "$0")"
.venv13/bin/chainlit run app.py --port 8501 --watch "$@"
