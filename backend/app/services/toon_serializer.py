import json
import os
from typing import Any

def to_toon_string(data: Any) -> str:
    """
    Convert Python object to TOON format string with fallback to JSON.

    TOON (Token-Oriented Object Notation) is a compact data encoding format
    designed for LLM inputs that reduces token usage by 30-60% compared to JSON.

    Args:
        data: Python object (dict, list, etc.) to serialize

    Returns:
        String representation in TOON format, or JSON if TOON encoding fails
    """
    if not should_use_toon():
        return json.dumps(data, indent=2)

    try:
        from toon_format import encode
        result = encode(data)
        return result
    except ImportError:
        print("WARNING: toon_format package not installed, falling back to JSON")
        return json.dumps(data, indent=2)
    except Exception as e:
        print(f"WARNING: TOON encoding failed: {e}, falling back to JSON")
        return json.dumps(data, indent=2)


def from_toon_string(toon_str: str) -> Any:
    """
    Convert TOON format string back to Python object.

    Args:
        toon_str: String in TOON format

    Returns:
        Python object (dict, list, etc.)
    """
    try:
        from toon_format import decode
        return decode(toon_str)
    except ImportError:
        print("WARNING: toon_format package not installed, trying JSON parsing")
        return json.loads(toon_str)
    except Exception as e:
        print(f"WARNING: TOON decoding failed: {e}, trying JSON parsing")
        return json.loads(toon_str)


def should_use_toon() -> bool:
    """
    Check if TOON format should be used based on environment configuration.

    Returns:
        True if TOON should be used, False otherwise
    """
    return os.getenv("USE_TOON_FORMAT", "true").lower() == "true"
