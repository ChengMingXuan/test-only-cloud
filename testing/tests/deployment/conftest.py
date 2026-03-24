"""deployment 级别的 conftest。"""

import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HELM_DIR = os.path.join(PROJECT_ROOT, "Configuration2.0", "helm", "jgsy-agi")
