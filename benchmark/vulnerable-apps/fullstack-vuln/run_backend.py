#!/usr/bin/env python
import sys
import os
root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, root)
from backend.app import app
app.run(host="0.0.0.0", port=5010, debug=True)
