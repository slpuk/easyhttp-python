import asyncio
from easyhttp import EasyHTTPAsync

# Callback function on FETCH
async def handle_fetch(sender_id):
    print(f"FETCH request from {sender_id}")
    return {
        "temperature": 24.5,
        "humidity": 60
    }

async def main():
    # Initializing
    easy = EasyHTTPAsync(debug=True, port=5000)

    # Manually adding other device (Auto-discovery is in progress!)
    easy.add("ABC123", "192.168.1.100", 5000)

    # Setting up callback function
    easy.on("on_fetch", handle_fetch)

    # Starting
    await easy.start()

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        # Stopping
        await easy.stop()
    except Exception as e:
        print(e)
    
if __name__ == '__main__':
    asyncio.run(main())