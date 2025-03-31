
# set up a virtual environment using 
# use this for 32 bit
#         C:\Users\Gregory\AppData\Local\Programs\Python\Python313-32\python.exe -m venv fingerprint_env

# Activate the virtual environment
#       Windows: fingerprint_env\Scripts\activate
#       macOS/Linux: source fingerprint_env/bin/activate

# installed the following
#       pip install -r requirements.txt
#        pip install websockets requests pyinstaller

# Optionally installed: pip install pywin32 (for COM object integration)
# Optionally installed: pip install pyarmor (for code obfuscation)

# Build the Executable
#    pyinstaller --onefile --hidden-import=win32timezone src/fingerprint_connector.py --add-data "dll/uareu4500.dll;."
# # Basic compilation
# pyinstaller --onefile fingerprint_connector.py
# pyinstaller --onefile fingerprint_connector.py

# Optional obfuscation
# pyarmor pack -e "--onefile" fingerprint_connector.py

# donloadded the Windows binary from libusb.info and copy libusb-1.0.dll to C:\Windows\System32.

# Configure Driver with Zadig: Use Zadig 

