# Simple ping script with EasyHTTP & context manager
import time
from easyhttp_python import EasyHTTP

def main():
    # Async context manager whuch initializing EasyHTTP
    with EasyHTTP(debug=True, port=5000) as easy:
        try:
            # Pinging device by ID once every 3 seconds
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