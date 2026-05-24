
import os
import sys
from pathlib import Path

def check_env():
    print(f"Python executable: {sys.executable}")
    try:
        import openai
        print(f"openai version: {openai.__version__}")
    except ImportError:
        print("openai not installed")
    
    try:
        import textual
        print(f"textual version: {textual.__version__}")
    except ImportError:
        print("textual not installed")

    src_path = Path(__file__).resolve().parent / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    try:
        import agents
        print(f"agents package found: {agents.__file__}")
    except ModuleNotFoundError as exc:
        if exc.name == "agents":
            print("agents package NOT found")
        else:
            print(f"agents package found, but dependency is missing: {exc.name}")
    except ImportError as exc:
        print(f"agents package import failed: {exc}")

    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        print("OPENAI_API_KEY is set")
    else:
        print("OPENAI_API_KEY is NOT set")

if __name__ == "__main__":
    check_env()
