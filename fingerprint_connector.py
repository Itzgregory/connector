import asyncio
import websockets
import requests
import json

class FingerprintConnector:
    def __init__(self, websocket_port=8080):
        self.websocket_port = websocket_port
        self.service_url = None

    async def detect_service_endpoint(self):
        """Detect the fingerprint service endpoint from DpHostW.exe"""
        try:
            response = requests.get(
                "https://127.0.0.1:52181/get_connection",
                verify=False,
                timeout=5
            )
            response.raise_for_status()
            data = response.json()
            if "endpoint" not in data:
                raise Exception("No endpoint in response; scanner may not be connected")
            self.service_url = data["endpoint"].split("?")[0]
            print(f"Detected service URL: {self.service_url}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Service endpoint detection error: {str(e)}")
            return False

    async def capture_fingerprint(self):
        """Capture fingerprint data via HTTP"""
        try:
            if not self.service_url and not await self.detect_service_endpoint():
                raise Exception("Service endpoint not detected; ensure scanner is connected")
            response = requests.get(
                f"{self.service_url}/Capture",  # Adjust after confirming endpoint
                verify=False,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            sample = data.get("samples", "mock-fingerprint-data")
            if sample == "mock-fingerprint-data":
                print("No sample in response; using mock data")
            return sample
        except Exception as e:
            print(f"Fingerprint capture error: {str(e)}")
            return None

    async def handle_connection(self, websocket):
        """Handle WebSocket connection and messages"""
        print("Frontend connected")
        try:
            async for message in websocket:
                if message == "startCapture":
                    sample = await self.capture_fingerprint()
                    if sample:
                        await websocket.send(json.dumps({
                            "status": "captured",
                            "sample": sample
                        }))
                    else:
                        await websocket.send(json.dumps({
                            "status": "error",
                            "message": "Fingerprint capture failed; ensure scanner is connected"
                        }))
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket connection closed")

    async def start_server(self):
        """Start WebSocket server"""
        async with websockets.serve(
            self.handle_connection,
            "localhost",
            self.websocket_port
        ):
            print(f"WebSocket server running on ws://localhost:{self.websocket_port}")
            await asyncio.Future()

def main():
    connector = FingerprintConnector()
    asyncio.run(connector.start_server())

if __name__ == "__main__":
    main()