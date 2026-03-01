# EasyHTTP
[EN README](README.md) | [RU README](README_RU.md)
> **A lightweight HTTP-based P2P framework for IoT and device-to-device communication**

![Protocol Version](https://img.shields.io/badge/version-0.3.3-blue?style=for-the-badge)
![Development Status](https://img.shields.io/badge/status-beta-orange?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3.7+-blue?style=for-the-badge&logo=python&logoColor=white)

> [!WARNING]
> **Breaking Changes from 0.3.2**
> 
> ### API Changes
> ```python
> # 0.3.2 (OLD)
> from easyhttp import ...
>
> # 0.3.3 (NEW)
> from easyhttp_python import ...
>```

## 🚀 Quick Start

### Installation

```bash
# Install by PyPI
pip install easyhttp-python

# Or from GitHub
pip install git+https://github.com/slpuk/easyhttp-python.git
```

### Basic Usage (synchronous)
Syntax with context managers and full code is supported

```python
from easyhttp_python import EasyHTTP

def main():
    # Initialize a device with context manager
    with EasyHTTP(debug=True, port=5000) as easy:
        print(f"Device ID: {easy.id}")
    
        # Manually add another device
        easy.add("ABC123", "192.168.1.100", 5000)
    
        # Ping to check if device is online
        if easy.ping("ABC123"):
            print("Device is online!")
    
        # Request data from device
        response = easy.fetch("ABC123")
        if response:
            print(f"Received: {response.get('data')}")
    
        # Push data to device
        success = easy.push("ABC123", {"led": "on"})
        if success:
            print("Command executed successfully")

# Starting main process
if __name__ == "__main__":
    main()
```

### Or asynchronous

```python
import asyncio
from easyhttp_python import EasyHTTPAsync

async def main():
    # Initialize a device
    easy = EasyHTTPAsync(debug=True, port=5000)
    await easy.start()
    
    print(f"Device ID: {easy.id}")
    
    # Manually add another device
    easy.add("ABC123", "192.168.1.100", 5000)
    
    # Ping to check if device is online
    if await easy.ping("ABC123"):
        print("Device is online!")
    
    # Request data from device
    response = await easy.fetch("ABC123")
    if response:
        print(f"Received: {response.get('data')}")
    
    # Push data to device
    success = await easy.push("ABC123", {"led": "on"})
    if success:
        print("Command executed successfully")

# Starting main process
if __name__ == "__main__":
    asyncio.run(main())
```
---

## 📖 About

**EasyHTTP** is a simple yet powerful framework with asynchronous core that enables P2P (peer-to-peer) communication between devices using plain HTTP.

### Key Features:
- **🔄 P2P Architecture** - No central server required
- **🧩 Dual API:** `EasyHTTP` (synchronous) and `EasyHTTPAsync` (asynchronous) with the same methods
- **📡 Event-Driven Communication** - Callback-based architecture
- **🆔 Human-Readable Device IDs** - Base32 identifiers instead of IP addresses
- **✅ Easy to Use** - Simple API with minimal setup
- **🚀 Performance** - Asynchronous code and lightweight libraries(FastAPI/aiohttp)

## Project Structure
```
easyhttp-python/
├── docs/
│   ├── EasyHTTP.md      # Sync API reference
│   └── EasyHTTPAsync.md # Async API reference
├── easyhttp_python/
│   ├── __init__.py
│   ├── core.py     # Main framework file/core
│   └── wrapper.py  # Synchronous wrapper
├── examples/
│   ├── async/       # Asynchronous examples
│   │   ├── basic_ping.py
│   │   ├── callback_preview.py
│   │   ├── device_control.py
│   │   ├── sensor_simulator.py
│   │   └── two_devices.py
│   └── sync/      # Synchronous examples
│       ├── basic_ping.py
│       ├── callback_preview.py
│       ├── device_control.py
│       ├── sensor_simulator.py
│       └── two_devices.py
├── .gitignore
├── LICENSE             # MIT license
├── pyproject.toml      # Project config
├── README_PY.md        # Documentation for PyPI
├── README_RU.md        # Russian documentation
├── README.md           # This file
└── requirements.txt    # Project dependencies
```

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

### Communication Flow
```mermaid
sequenceDiagram
    participant DeviceA
    participant DeviceB
    
    DeviceA->>DeviceB: PING
    DeviceB-->>DeviceA: PONG
    
    DeviceA->>DeviceB: FETCH
    DeviceB-->>DeviceA: DATA
    
    DeviceA->>DeviceB: PUSH
    DeviceB-->>DeviceA: ACK/NACK
```

## 📦 Installation & Setup

### Installation

```bash
# Install from PyPI
pip install easyhttp-python

# Or from GitHub
pip install git+https://github.com/slpuk/easyhttp-python.git
```

### Basic Example with Callbacks(Synchronous)
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
    
    # Adding device
    easy.add("ABC123", "192.168.1.100", 5000)
    print("Added device ABC123")
    
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

## 📚 Examples

Check the [`examples/`](examples/) directory for more:
<br> (synchronous examples below; check [`examples/async/`](examples/async/) for asynchronous versions)

- [`basic_ping.py`](examples/sync/basic_ping.py) - Basic device communication using context manager
- [`callback_preview.py`](examples/sync/callback_preview.py) - Callback events demo
- [`two_devices.py`](examples/sync/two_devices.py) - Two devices exchanging data
- [`sensor_simulator.py`](examples/sync/sensor_simulator.py) - Simulated IoT sensor
- [`device_control.py`](examples/sync/device_control.py) - Remote device control

## 🔧 API Reference

Check the directories for functions documentation:
- Synchronous wrapper: [`docs/EasyHTTP.md`](docs/EasyHTTP.md)
- Asynchronous core: [`docs/EasyHTTPAsync.md`](docs/EasyHTTPAsync.md)
