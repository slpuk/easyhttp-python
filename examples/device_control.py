from easyhttp import EasyHTTP
import time

# PULL request callback
def handle_pull(sender_id, data, timestamp):
    print(f"[CONTROL] Command from {sender_id}: {data}")
    
    # Validation and command processing
    if data and data.get("command") == "led":
        state = data.get("state")
        print(f"[CONTROL] Turning LED {state}")
        # Here you can add real GPIO control
        return True  # Command was successfully executed
    elif data and data.get("command") == "reboot":
        print("[CONTROL] Scheduling reboot...")
        # You can schedule a reboot here
        return True
    else:
        print(f"[CONTROL] Unknown command: {data}")
        return False  # Неизвестная команда

def main():
    # Initializing
    easy = EasyHTTP(debug=True, port=5000)
    easy.add_device("7H8G2K", "192.168.1.100", 5000)
    
    # Setting up callback-functions
    easy.on("on_pull", handle_pull)
    
    # Starting
    easy.start()
    
    print(f"[INFO] Device {easy.id} started on port 5000")
    print("[INFO] Waiting for control commands...")
    print("[INFO] Press Ctrl+C to stop")
    
    # An example of sending test commands (if you need to test two-way communication)
    # Uncomment if you want this device to also send commands
    """
    try:
        while True:
            # Example of sending a command to turn on an LED
            success = easy.pull("7H8G2K", {
                "command": "led",
                "state": "on",
                "brightness": 80
            })
            
            if success:
                print("[SEND] Command executed successfully!")
            else:
                print("[SEND] Device rejected the command")
            
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n[INFO] Stopping...")
    """
    
    # Just waiting for incoming commands
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] Stopping device...")

if __name__ == '__main__':
    main()