import time
from easyhttp import EasyHTTP

# Callback-function on GET
def handle_get(sender_id, timestamp):
    print(f"GET request from {sender_id} on {timestamp}")
    return {
        "response": "Hello EasyHTTP!"
    }

# Callback-function on DATA_RESPONSE
def handle_data_response(sender_id, data):
    print(f"Received from {sender_id}: {data}")

def main():
    # Initializing
    easy = EasyHTTP(debug=True, port=5000)
    easy.add_device("7H8G2K", "192.168.1.100", 5000)

    # Setting up callback-functions
    easy.on("on_get", handle_get)
    easy.on("on_data_response", handle_data_response)

    # Starting
    easy.start()

    # Getting data by ID once every 3 seconds
    try:
        while True:
            easy.get("7H8G2K")
            time.sleep(3)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(e)
    
if __name__ == '__main__':
    main()