import asyncio
from easyhttp import EasyHTTPAsync

# Callback function on FETCH
async def handle_fetch(sender_id, query, timestamp):
    print(f"FETCH request from {sender_id} on {timestamp} with {query}")
    return {
        "response": "Hello EasyHTTP!"
    }

# Callback function on DATA
async def handle_data(sender_id, data):
    print(f"Received from {sender_id}: {data}")

async def main():
    # Initializing
    easy = EasyHTTPAsync(debug=True, port=5000)
    easy.add("ABC123", "192.168.1.100", 5000)

    # Setting up callback functions
    easy.on("on_fetch", handle_fetch)
    easy.on("on_data", handle_data)

    # Starting
    await easy.start()

    # Getting data by ID once every 3 seconds
    try:
        while True:
            await easy.fetch("ABC123")
            await asyncio.sleep(3)
    except KeyboardInterrupt:
        # Gracefully stopping API
        await easy.stop()
    except Exception as e:
        print(e)
    
if __name__ == '__main__':
    asyncio.run(main())