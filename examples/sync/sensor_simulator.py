import time
from easyhttp import EasyHTTP

# Callback function on FETCH
def handle_fetch(sender_id):
    print(f"FETCH request from {sender_id}")
    return {
        "temperature": 24.5,
        "humidity": 60
    }

def main():
    # Initializing
    easy = EasyHTTP(debug=True, port=5000)

    # Manually adding other device (Auto-discovery is in progress!)
    easy.add("ABC123", "192.168.1.100", 5000)

    # Setting up callback function
    easy.on("on_fetch", handle_fetch)

    # Starting
    easy.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Stopping
        easy.stop()
    except Exception as e:
        print(e)
    
if __name__ == '__main__':
    main()