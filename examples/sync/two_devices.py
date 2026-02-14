import time
from easyhttp import EasyHTTP

# Callback function on FETCH
def handle_fetch(sender_id, query, timestamp):
    print(f"FETCH request from {sender_id} on {timestamp} with {query}")
    return {
        "response": "Hello EasyHTTP!"
    }

# Callback function on DATA
def handle_data(sender_id, data):
    print(f"Received from {sender_id}: {data}")

def main():
    # Initializing
    easy = EasyHTTP(debug=True, port=5000)
    easy.add("ABC123", "192.168.1.100", 5000)

    # Setting up callback functions
    easy.on("on_fetch", handle_fetch)
    easy.on("on_data", handle_data)

    # Starting
    easy.start()

    # Getting data by ID once every 3 seconds
    try:
        while True:
            easy.fetch("ABC123")
            time.sleep(3)
    except KeyboardInterrupt:
        # Gracefully stopping API
        easy.stop()
    except Exception as e:
        print(e)
    
if __name__ == '__main__':
    main()