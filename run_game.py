#!/usr/bin/env python3
"""
Pixel Kombat - A simple 2D fighting game
Run this script to start the game.
"""

import os
import sys

# Add the game directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Run the game
from game.main import main

if __name__ == "__main__":
    main()