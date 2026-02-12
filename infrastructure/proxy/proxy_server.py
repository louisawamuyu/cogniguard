"""
CogniGuard Proxy Server

This sits between clients and AI services, intercepting and protecting all traffic.

Usage:
    python proxy_server.py

Then configure your AI client to use:
    http://localhost:8000/v1/chat/completions
    
instead of:
    https://api.openai.com/v1/chat/completions
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from fastapi import FastAPI, Request, HTTPException
from fastapi