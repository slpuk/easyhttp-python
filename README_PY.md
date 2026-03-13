# EasyHTTP

[![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)](https://github.com/slpuk/easyhttp-python)
![Protocol Version](https://img.shields.io/badge/version-0.4.0-blue?style=for-the-badge)
![Development Status](https://img.shields.io/badge/status-alpha-red?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3.7+-blue?style=for-the-badge&logo=python&logoColor=white)

> **A lightweight HTTP-based P2P framework for IoT and device-to-device communication**

## 🛠️ Changelog
- Added UDP multicast discovery
- Fixed some bugs

## 📖 About

**EasyHTTP** is a simple yet powerful framework with asynchronous core that enables P2P (peer-to-peer) communication between devices using plain HTTP.

### Key Features:
- **🔄 P2P Architecture** - No central server required
- **🧩 Dual API:** `EasyHTTP` (synchronous) and `EasyHTTPAsync` (asynchronous) with the same methods
- **📡 Event-Driven Communication** - Callback-based architecture
- **🆔 Human-Readable Device IDs** - Base32 identifiers instead of IP addresses
- **✅ Easy to Use** - Simple API with minimal setup
- **🚀 Performance** - Asynchronous code and lightweight libraries(FastAPI/aiohttp)
- **⚙️ Auto-detect** - Devices automatically find each other

## 🏗️ Architecture

### Device Identification
Instead of using hard-to-remember IP addresses, each device in the EasyHTTP network has a unique 6-character identifier:

- **Format**: 6 characters from Base32 alphabet (without ambiguous characters)
- **Alphabet**: `23456789ABCDEFGHJKLMNPQRSTUVWXYZ`
- **Examples**: `7H8G2K`, `AB3F9Z`, `X4R7T2`
- **Generation**: Randomly generated on first boot, stored in device configuration

### Command System
EasyHTTP uses a simple JSON-based command system:

| Command | Value | Description |
|---------|-------|-------------|
| `PING` | 1 | Check if another device is reachable |
| `PONG` | 2 | Response to ping request |
| `FETCH` | 3 | Request data from a device |
| `DATA` | 4 | Send data or answer to FETCH |
| `PUSH` | 5 | Request to write/execute on remote device |
| `ACK` | 6 | Success/confirmation |
| `NACK` | 7 | Error/reject |

### Basic Example with Callbacks (synchronous)
```python
import time
from easyhttp_python import EasyHTTP

# Callback function
def handle_data(sender_id, data, timestamp):
    # Callback for incoming DATA responses
    print(f"From {sender_id}: {data}")

def handle_fetch(sender_id, query, timestamp):
    # Callback for FETCH requests - returns data when someone requests it
    print(f"FETCH request from {sender_id}")
    return {
        "temperature": 23.5,
        "humidity": 45,
        "status": "normal",
        "timestamp": timestamp
    }

def handle_push(sender_id, data, timestamp):
    # Callback for PUSH requests - handle control commands
    print(f"Control from {sender_id}: {data}")
    if data and data.get("command") == "led":
        state = data.get("state", "off")
        print(f"[CONTROL] Turning LED {state}")
        # Here you can add real GPIO control
        return True  # Successful → ACK
    return False  # Error → NACK

def main():
    # Initializing EasyHTTP - sync wrapper of EasyHTTPAsync
    easy = EasyHTTP(debug=True, port=5000)
    
    # Setting up callback functions
    easy.on('on_ping', handle_ping)
    easy.on('on_pong', handle_pong)
    easy.on('on_fetch', handle_fetch)
    easy.on('on_data', handle_data)
    easy.on('on_push', handle_push)
    
    easy.start()  # Starting server
    print(f"Device {easy.id} is running on port 5000!")
    
    # Monitoring device's status
    try:
        while True:
            if easy.ping("ABC123"):
                print("Device ABC123 is online")
            else:
                print("Device ABC123 is offline")
            
            time.sleep(5)
    
    except KeyboardInterrupt:
        print("\nStopping device...")
        easy.stop()  # Stopping server

# Starting main process
if __name__ == "__main__":
    main()
```
## 📦 Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.4.0 | 2026-13-03 | UDP Discovery, auto-detect |
| 0.3.3 | 2026-03-01 | Fixed imports, renamed to easyhttp_python |
| 0.3.2 | 2026-02-14 | Context managers |

**More examples available on [GitHub](https://github.com/slpuk/easyhttp-python)**