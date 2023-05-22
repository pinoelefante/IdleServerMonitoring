import sys

def is_linux() -> bool:
    return sys.platform.startswith("linux")

def is_windows() -> bool:
    return sys.platform.startswith("win")
    
def is_mac() -> bool:
    return sys.platform.startswith("darwin")