
# set up a virtual environment using 
#         python -m venv fingerprint_env

# Activate the virtual environment
#       Windows: fingerprint_env\Scripts\activate
#       macOS/Linux: source fingerprint_env/bin/activate

# installed the following
#        pip install websockets requests pyinstaller

# Optionally installed: pip install pywin32 (for COM object integration)
# Optionally installed: pip install pyarmor (for code obfuscation)

# # Basic compilation
# pyinstaller --onefile fingerprint_connector.py
# pyinstaller --onefile fingerprint_connector.py

# Optional obfuscation
# pyarmor pack -e "--onefile" fingerprint_connector.py