import time
from easyhttp import EasyHTTP

# PUSH request callback
def handle_push(sender_id, data, timestamp):
    print(f"PUSH command from {sender_id}: {data}")
    
    # Validation and command processing
    if data and data.get("command") == "led":
        state = data.get("state")
        print(f"Turning LED {state}")
        # Here you can add real GPIO control
        return True  # Command was successfully executed
    elif data and data.get("command") == "reboot":
        print("Scheduling reboot...")
        # You can schedule a reboot here
        return True
    else:
        print(f"Unknown command: {data}")
        return False  # Unknown command

def main():
    # Initializing
    easy = EasyHTTP(debug=True, port=5000)

    # Manually adding other device (Auto-discovery is in progress!)
    easy.add("ABC123", "192.168.1.100", 5000)
    
    # Setting up callback functions
    easy.on("on_push", handle_push)
    
    # Starting API
    easy.start()
    
    # An example of sending test commands (if you need to test two-way communication)
    # Uncomment if you want this device to also send commands
    """
    try:
        while True:
            # Example of sending a command to turn on an LED
            success = easy.push("ABC123", {
                "command": "led",
                "state": "on",
                "brightness": 80
            })
            
            if success:
                print("Command executed successfully!")
            else:
                print("Device rejected the command")
            
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nStopping...")
        easy.stop()
    """
    
    # Just waiting for incoming commands
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping device...")
        # Gracefully stopping API
        easy.stop()

if __name__ == '__main__':
    main()