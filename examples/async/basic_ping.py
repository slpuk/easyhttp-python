# Simple ping script with EasyHTTPAsync & context manager
import asyncio
from easyhttp import EasyHTTPAsync

async def main():
    # Async context manager whuch initializing EasyHTTPAsync
    async with EasyHTTPAsync(debug=True, port=5000) as easy:
        try:
            # Manually adding other device (Auto-discovery is in progress!)
            easy.add("ABC123", "192.168.1.100", 5000)

            # Pinging device by ID once every 3 seconds
            while True:
                # Bool: True if device is online(sended PONG command)
                if await easy.ping("ABC123"):
                    print(f"Device ABC123 is online")
                else:
                    print(f"Device ABC123 is offline")

                await asyncio.sleep(3)

        except KeyboardInterrupt:
            # Stopping
            await easy.stop()
        except Exception as e:
            print(e)
    
if __name__ == '__main__':
    asyncio.run(main())