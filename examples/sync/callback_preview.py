import time
# Import synchronous wrapper of EasyHTTP
from easyhttp import EasyHTTP

'''
Callback functions
'''
# Callback function for PING
def handle_ping(sender_id):
    print(f"PING from device {sender_id}")

# Callback function for PONG
def handle_pong(sender_id):
    print(f"PONG from device {sender_id}")

# Callback function for FETCH
def handle_fetch(sender_id, query, timestamp):
    print(f"FETCH request from {sender_id} on {timestamp} with {query}")

    # Returning data
    return {
        "message": "Hello EasyHTTP!"
    }

# Callback function for DATA
def handle_data(sender_id, data, timestamp):
    print(f"DATA from device {sender_id}: {data}")

# Callback function for PUSH
def handle_push(sender_id, data, timestamp):
    print(f"PUSH from device {sender_id}: {data}")

    # Returning True to confirm
    # You can return False to reject
    return True

'''Main process'''
def main():
    try:
        # Initializing
        easy = EasyHTTP(debug=True, port=5000)

        # Setting up callback functions
        easy.on('on_ping', handle_ping)     # Handle PING
        easy.on('on_pong', handle_pong)     # Handle PONG
        easy.on('on_fetch', handle_fetch)   # Handle FETCH
        easy.on('on_data', handle_data)     # Handle DATA
        easy.on('on_push', handle_push)     # Handle PUSH

        # Manually adding other device (Auto-discovery is in progress!)
        easy.add("ABC123", "192.168.1.100", 5000)

        # Starting API
        easy.start()

        while True:
            time.sleep(5)

    except KeyboardInterrupt:
        # Gracefully stopping API
        easy.stop()

    except Exception as e:
        pass

if __name__ == '__main__':
    main()