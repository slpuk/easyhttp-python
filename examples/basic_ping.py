import time
from easyhttp import EasyHTTP

def main():
    # Initializing EasyHTTP
    easy = EasyHTTP(debug=True, port=5000)
    easy.add_device("7H8G2K", "192.168.1.100", 5000)
    easy.start()

    # Pinging device by ID once every 3 seconds
    try:
        while True:
            easy.ping("7H8G2K")
            time.sleep(3)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(e)
    
if __name__ == '__main__':
    main()