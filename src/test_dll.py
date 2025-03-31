# test_dll.py
import ctypes
try:
    dll = ctypes.CDLL(r'C:\Users\Gregory\Desktop\project\Biometric-Captured-system\connector\src\dll\uareu4500.dll', winmode=0)
    print("DLL loaded successfully!")
except OSError as e:
    print(f"Error: {e}")