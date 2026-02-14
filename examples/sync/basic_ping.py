import time
from easyhttp import EasyHTTP

def main():
    # Initializing EasyHTTP
    easy = EasyHTTP(debug=True, port=5000)

    # Manually adding other device (Auto-discovery is in progress!)
    easy.add("ABC123", "192.168.1.100", 5000)

    # Starting API
    easy.start()

    # Pinging device by ID once every 3 seconds
    try:
        while True:
            # Bool: True if device is online(sended PONG command)
            if easy.ping("ABC123"):
                print(f"Device ABC123 is online")
            else:
                print(f"Device ABC123 is offline")

            time.sleep(3)
    except KeyboardInterrupt:
        # Stopping
        easy.stop()
    except Exception as e:
        print(e)
    
if __name__ == '__main__':
    main()