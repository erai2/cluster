import os
import sys

# Ensure the project root is importable when running pytest as a script.
# Some CI environments execute `pytest` directly which doesn't add the
# current working directory to ``sys.path``.  Without this, importing the
# top-level ``saju_database`` module fails.
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
