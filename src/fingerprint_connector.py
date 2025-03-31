import asyncio
import json
import logging
import websockets
import ssl
from cryptography.fernet import Fernet
from src.uareu4500 import getFingerReadingAsBase64String, compareBase64StringWithFingerReading

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('fingerprint_connector.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class FingerprintConnector:
    def __init__(self, ws_url="wss://localhost:8080"):
        self.ws_url = ws_url
        self.websocket = None
        self.running = False
        self.connected = True  
        self.last_error = None
        self.encryption_key = Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)

    async def capture_fingerprint(self):
        """Capture fingerprint using the DLL wrapper."""
        if not self.connected:
            raise RuntimeError("Scanner not initialized")
        try:
            logger.info("Capturing fingerprint...")
            base64_string = getFingerReadingAsBase64String()
            if not base64_string:
                raise RuntimeError("Failed to capture fingerprint")
            encrypted_data = self.cipher.encrypt(base64_string.encode())
            return {"status": "success", "data": encrypted_data.decode()}
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Capture failed: {e}")
            raise

    async def compare_fingerprint(self, base64_string):
        """Compare a base64 string with a new fingerprint scan."""
        if not self.connected:
            raise RuntimeError("Scanner not initialized")
        try:
            decrypted_data = self.cipher.decrypt(base64_string.encode()).decode()
            result = compareBase64StringWithFingerReading(decrypted_data)
            return {"status": "success", "match": bool(result)}
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Comparison failed: {e}")
            raise

    async def send_status(self, websocket):
        """Send current status to the client."""
        await websocket.send(json.dumps({
            "status": "ready" if self.connected else "error",
            "connected": self.connected,
            "scanner_available": self.connected,
            "last_error": self.last_error
        }))

    async def handle_client(self, websocket):
        """Handle WebSocket client requests."""
        self.websocket = websocket
        logger.info("Client connected")
        try:
            await self.send_status(websocket)
            async for message in websocket:
                data = json.loads(message)
                action = data.get("action")
                if action == "capture":
                    try:
                        result = await self.capture_fingerprint()
                        await websocket.send(json.dumps(result))
                    except Exception as e:
                        await websocket.send(json.dumps({"status": "error", "message": str(e)}))
                elif action == "compare":
                    try:
                        base64_string = data.get("base64_string")
                        if not base64_string:
                            raise ValueError("No base64_string provided")
                        result = await self.compare_fingerprint(base64_string)
                        await websocket.send(json.dumps(result))
                    except Exception as e:
                        await websocket.send(json.dumps({"status": "error", "message": str(e)}))
                elif action == "status":
                    await self.send_status(websocket)
                else:
                    await websocket.send(json.dumps({"status": "error", "message": "Invalid action"}))
        except websockets.ConnectionClosed:
            logger.info("Client disconnected")
        except Exception as e:
            logger.error(f"WebSocket error: {e}")

    async def start_websocket(self):
        """Start WebSocket server with reconnection logic."""
        ssl_context = None
        if "wss" in self.ws_url:
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ssl_context.load_cert_chain(certfile="../certs/cert.pem", keyfile="../certs/key.pem")
        while self.running:
            try:
                async with websockets.serve(
                    self.handle_client,
                    "localhost",
                    8080,
                    ssl=ssl_context,
                    ping_interval=20,
                    ping_timeout=20
                ):
                    logger.info(f"WebSocket server running at {self.ws_url}")
                    await asyncio.Future()
            except Exception as e:
                logger.error(f"WebSocket server failed: {e}")
                await asyncio.sleep(5)

    async def run(self):
        """Run the fingerprint connector service."""
        self.running = True
        if self.connected:
            await self.start_websocket()
        else:
            logger.error("Failed to initialize scanner, exiting")

    def stop(self):
        """Stop the service."""
        self.running = False
        if self.websocket:
            self.websocket.close()

if __name__ == "__main__":
    connector = FingerprintConnector()
    try:
        asyncio.run(connector.run())
    except KeyboardInterrupt:
        connector.stop()
        logger.info("Service stopped")