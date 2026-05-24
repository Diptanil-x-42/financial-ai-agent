# Centralized path setup - ensures `src/agents` is importable as `agents`
# without sys.path hacks in every individual file.
import os
import sys

_src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src')
if _src_path not in sys.path:
    sys.path.insert(0, _src_path)
