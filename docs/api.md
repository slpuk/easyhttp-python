## 🔧 API Reference

> Core Methods

### `EasyHTTP(debug=False, port=5000, config_file=None)`
Initialize a new EasyHTTP device.

**Parameters:**
- `debug` (bool): Enable debug output (default: False)
- `port` (int): HTTP server port (default: 5000)
- `config_file` (str, optional): Custom config file path. If `None`, uses `easyhttp_device.json` in current directory (default: None)

### `start()`
Start the HTTP server and generate device ID if not already set.

### `add_device(device_id, ip, port)`
Manually add a device to the device cache.

**Parameters:**
- `device_id` (str): 6-character device ID
- `ip` (str): IP address of the device
- `port` (int): Port number of the device's HTTP server

**Example:**
```python
device.add_device("7H8G2K", "192.168.1.100", 5000)
device.add_device("ABC123", "localhost", 5001)
```

### `send(device_id, command_type, data=None)`
Manually sends command and data if available.

**Parameters:**
- `device_id` (str): 6-character device ID
- `command_type` (EasyHTTP.commands): Command to send
- `data` (optional): Data to send (default: None)

**Returns:** Response dictionary (parsed JSON) if successful, `None` if failed.

**Example:**
```python
# Send a PING command
response = device.send("7H8G2K", EasyHTTP.commands.PING)
if response and response.get('type') == EasyHTTP.commands.PING_OK.value:
    print("PING successful!")

# Send custom data with GET command
response = device.send("7H8G2K", EasyHTTP.commands.GET, {"query": "temperature"})
if response:
    print(f"Received: {response}")
```

### Available Commands

| Command | Value | Description |
|---------|-------|-------------|
| `PING` | 3 | Check device availability |
| `PING_OK` | 4 | Response to ping |
| `GET` | 5 | Request data from device |
| `DATA_RESPONSE` | 6 | Send data in response to GET |

### `ping(device_id)`
Check if a device is online.

**Parameters:**
- `device_id` (str): ID of the device to ping

**Returns:** `True` if device responds, `False` otherwise.

**Example:**
```python
if device.ping("7H8G2K"):
    print("Device is online!")
```

### `get(device_id, query=None)`
Request data from a device.

**Parameters:**
- `device_id` (str): ID of the device to query
- `query` (dict, optional): Additional query parameters

**Returns:** Response dictionary or `None` if failed.

**Example:**
```python
response = device.get("7H8G2K", {"sensor": "temperature"})
if response and 'data' in response:
    print(f"Temperature: {response['data']['temperature']}°C")
```

### `on(event, callback)`
Register a callback function for an event.

**Available events:**
- `on_get`: Triggered when a GET request is received from another device
- `on_data_response`: Triggered when data is received from another device
- `on_ping`: Triggered when PING is received from another device (Automatically sends PING_OK)

**Example:**
```python
def my_data_handler(sender_id, data, timestamp):
    print(f"Received from {sender_id}: {data}")

device.on('on_data_response', my_data_handler)
```