import sys
from pathlib import Path

# Adiciona a raiz e a pasta src ao sys.path
root_dir = Path(__file__).resolve().parent
src_dir = root_dir / "src"
for p in (str(root_dir), str(src_dir)):
    if p not in sys.path:
        sys.path.insert(0, p)

from src.main import main

if __name__ == "__main__":
    main()
