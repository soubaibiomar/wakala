import os
import sys
from pathlib import Path

# Add project root to path for absolute imports
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "data_pipeline" / "kafka" / "producers"))
