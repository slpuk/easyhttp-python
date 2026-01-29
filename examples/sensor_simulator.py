import time
from easyhttp import EasyHTTP

# Callback-function on GET
def handle_get(sender_id):
    print(f"GET request from {sender_id}")
    return {
        "temperature": 24.5,
        "humidity": 60
    }

def main():
    # Initializing
    easy = EasyHTTP(debug=True, port=5000)
    easy.add_device("7H8G2K", "192.168.1.100", 5000)

    # Setting up callback-function
    easy.on("on_get", handle_get)

    # Starting
    easy.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(e)
    
if __name__ == '__main__':
    main()