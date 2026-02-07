"""EasyHTTP - Simple HTTP-based P2P framework for IoT."""

import os
import secrets
import time
import logging
import json
from pathlib import Path
from enum import Enum, auto
from typing import Optional, Union, Dict, Any, Callable

# API libraries
import aiohttp
import asyncio
import socket
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

__version__ = "0.3.0-alpha"

class EasyHTTPAsync:
    """Simple asynchronous HTTP-based core of P2P framework for IoT."""
    
    class commands(Enum):
        """Enumeration of available command types."""

        PING = auto()   # Ping another device
        PONG = auto()   # Anwser for PING
        FETCH = auto()  # Request data from another device
        DATA = auto()   # Response containing data
        PUSH = auto()   # Send data to another device
        ACK = auto()    # Acknowledge successful command
        NACK = auto()   # Indicate an error occurred

    def __init__(self, debug: bool = False, port: int = 5000, config_file=None):
        """Initialize the EasyHTTPAsync instance.

        Args:
            debug: Enable debug output. Defaults to False.
            port: Port to run the HTTP server on. Defaults to 5000.
        """

        self.debug = debug
        self.port = port

        if config_file:
            self.config_file = config_file
        else:
            import sys
            if getattr(sys, 'frozen', False):
                base_dir = os.path.dirname(sys.executable)
            else:
                base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
            self.config_file = os.path.join(base_dir, "easyhttp_device.json")

        self.id = None
        self.callbacks = {
            'on_ping': None,
            'on_pong': None,
            'on_fetch': None,
            'on_data': None,
            'on_push': None
        }
        self.devices = {}
        self.app = FastAPI(title="EasyHTTP API")
        self.app.post('/easyhttp/api')(self.api_handler)
        self.server_task = None
        self._load_config()

    def _load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    self.id = data.get('device_id')
                    
                if self.debug and self.id:
                    print(f"\033[32mINFO\033[0m:\t Loaded ID: {self.id} from {self.config_file}")
        except Exception as e:
            if self.debug:
                print(f"\033[31mERROR\033[0m:\t Error loading config: {e}")
    
    def _save_config(self):
        try:
            config = {
                'device_id': self.id,
                'port': self.port,
                'version': __version__
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            if self.debug:
                print(f"\033[32mINFO\033[0m:\t Saved ID to {self.config_file}")
        except Exception as e:
            if self.debug:
                print(f"\033[31mERROR\033[0m:\t Error saving config: {e}")

    def _get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            try:
                return socket.gethostbyname(socket.gethostname())
            except:
                return "127.0.0.1"

    def _generate_id(self, length: int = 6) -> str:
        """Generate a unique device ID with a custom alphabet.

        Args:
            length: Length of the generated ID.

        Returns:
            The generated unique ID.
        """

        alphabet = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"
        self.id = ''.join(secrets.choice(alphabet) for _ in range(length))
        self._save_config()

    def on(self, event: str, callback_func: Callable) -> None:
        """Register a callback function for a specific event.

        Args:
            event: Event name ('on_ping', 'on_fetch', etc.).
            callback_func: Function to call when the event occurs.

        Raises:
            ValueError: If the event is unknown.
        """

        if event in self.callbacks:
            self.callbacks[event] = callback_func
        else:
            raise ValueError(f"Unknown event: {event}")

    def add(self, device_id: str, device_ip: str, device_port: int) -> None:
        """Manually add a device to the local devices cache.

        Args:
            device_id: 6-character device identifier.
            device_ip: IP address of the device.
            device_port: Port number of the device.

        Raises:
            ValueError: If device_id is not 6 characters.
        """

        if len(device_id) != 6:
            raise ValueError("Device ID must be 6 characters")
    
        if device_id not in self.devices:
            self.devices[device_id] = {
                'ip': device_ip,
                'port': int(device_port),
                'last_seen': time.time(),
                'added_manually': True
            }
            if self.debug:
                print(f"DEBUG:\t Added device {device_id}: {device_ip}:{device_port}")
        else:
            print(f"DEBUG:\t Device already exists")

    async def start(self) -> None:
        """Start the HTTP server and generate a device ID if not set."""

        if not self.id:
            self._generate_id()

        try:
            config = uvicorn.Config(
                self.app, 
                host="0.0.0.0", 
                port=self.port,
                log_level="info" if self.debug else "warning"
            )
            
            server = uvicorn.Server(config)
            self.server_task = asyncio.create_task(server.serve())

            logging.getLogger('werkzeug').disabled = True
            logging.getLogger('uvicorn.error').propagate = False
            logging.getLogger('uvicorn.access').propagate = False

            await asyncio.sleep(2)  # Give server time to start

            if self.debug:
                print(f"\033[32mINFO\033[0m:\t \033[32m\033[1mEasyHTTP \033[37m{__version__}\033[0m has been started!")
                print(f"\033[32mINFO\033[0m:\t Device's ID: {self.id}")
                print(f"\033[32mINFO\033[0m:\t EasyHTTP starting on port {self.port}")
                print(f"\033[32mINFO\033[0m:\t API running on \033[1mhttp://{self._get_local_ip()}:{self.port}/easyhttp/api\033[0m")
            
        except Exception as e:
            print(f"\033[31mERROR\033[0m:\t Failed to start server: {e}")
            raise

    async def stop(self) -> None:
        """Gracefully stop the HTTP server and cancel the server task."""

        if self.server_task:
            self.server_task.cancel()
            try:
                await self.server_task
            except asyncio.CancelledError:
                pass

    async def send(self, device_id: str, command_type: Union[int, 'commands'], data: Optional[Any] = None) -> Optional[dict]:
        """Send a JSON-formatted command to another device.

        Args:
            device_id: ID of the target device (must be 6 characters).
            command_type: Command type (commands enum member) or its integer value.
            data: JSON-serializable data to send (dict, list, str, or None).

        Returns:
            Response JSON dict if successful, None otherwise.
            Response typically contains 'type', 'header', and optionally 'data' fields.

        Note:
            The device must be added to the devices cache before sending.
        """

        if device_id not in self.devices:
            if self.debug:
                print(f"\033[31mERROR\033[0m:\t Device {device_id} not found in devices cache")
            return None
    
        packet = {
            "version": __version__,
            "type": command_type if isinstance(command_type, self.commands) else command_type,
            "header": {
                "sender_id": self.id, 
                "sender_port": self.port,
                "recipient_id": device_id, 
                "timestamp": int(time.time())
            }
        }
    
        if data:
            packet['data'] = data
    
        recipient_url = f"http://{self.devices[device_id]['ip']}:{self.devices[device_id]['port']}/easyhttp/api"
    
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(recipient_url, json=packet, timeout=3) as response:
                    if response.status == 200:
                        return await response.json()
                    return None
            
        except Exception as e:
            if self.debug:
                print(f'\033[31mERROR\033[0m:\t Failed to send to {device_id}: {e}')
            return None

    async def ping(self, device_id: str) -> bool:
        """Send a PING request to a device and check if it's online.

        Args:
            device_id: ID of the device to ping.

        Returns:
            True if device responded with PONG, False otherwise.
        """

        response = await self.send(device_id, self.commands.PING.value)
    
        if response and response.get('type') == self.commands.PONG.value:
            if self.debug:
                print(f"\033[32mPING\033[0m:\t {device_id} is online")
            if device_id in self.devices:
                self.devices[device_id]['last_seen'] = time.time()
            return True
        else:
            if self.debug:
                print(f"\033[31mPING\033[0m:\t {device_id} is offline or not responding")
            return False

    async def fetch(self, device_id: str, query: Optional[Any] = None) -> Optional[dict]:
        """Send a FETCH request to another device and return the response.

        Args:
            device_id: ID of the target device.
            query: Query data to send with the FETCH request.

        Returns: 
            Response data from the device, or None if failed.
            The dict typically contains 'type', 'header', and 'data' fields.
        """

        response = await self.send(device_id, self.commands.FETCH.value, query)
        return response

    async def push(self, device_id: str, data: Optional[Any] = None) -> bool:
        """Send data to another device using PUSH command.

        Args:
            device_id: ID of the target device.
            data: JSON-serializable data to send.

        Returns:
            True if data was successfully sent and acknowledged, False otherwise.

        Raises:
            TypeError: If data is not JSON-serializable.
        """

        if data is not None and not isinstance(data, (dict, list, str)):
            raise TypeError("Data must be JSON-serializable (dict, list, str)")
        
        response = await self.send(device_id, self.commands.PUSH, data)

        if response and response.get('type') == self.commands.ACK.value:
            if self.debug:
                print(f"\033[32mPUSH\033[0m:\t Successfully wrote to {device_id}")
            return True
        else:
            if self.debug:
                print(f"\033[31mPUSH\033[0m:\t Error writing to {device_id}")
            return False

    async def api_handler(self, request: Request) -> JSONResponse:
        """Handle incoming API requests and route commands to callbacks.

        Args:
            request: FastAPI request object.

        Returns:
            JSONResponse: Response to the client.
        """
        
        try:
            data = await request.json()
        except:
            return JSONResponse({"error": "Invalid JSON data"}, status_code=400)
            
        if not data:
            return JSONResponse({"error": "No JSON data"}, status_code=400)
            
        command_type = data.get('type')
        header = data.get('header', {})
        sender_id = header.get('sender_id')
        
        client_ip = request.client.host if request.client else "0.0.0.0"

        if sender_id and sender_id != self.id and sender_id not in self.devices:
            self.devices[sender_id] = {
                'ip': client_ip,
                'port': header.get('sender_port', self.port),
                'last_seen': int(time.time())
            }

        # Handle PING response
        if command_type == self.commands.PING.value:
            if self.callbacks['on_ping']:
                callback = self.callbacks['on_ping']
                if asyncio.iscoroutinefunction(callback):
                    await callback(sender_id)
                else:
                    callback(sender_id)
                
            return JSONResponse({
                "version": __version__,
                "type": self.commands.PONG.value,
                "header": {
                    "sender_id": self.id,
                    "sender_port": self.port,
                    "recipient_id": sender_id,
                    "timestamp": int(time.time())
                }
            })

        # Handle PONG answer
        elif command_type == self.commands.PONG.value:
            if self.callbacks['on_pong']:
                callback = self.callbacks['on_pong']
                if asyncio.iscoroutinefunction(callback):
                    await callback(sender_id)
                else:
                    callback(sender_id)

            if self.debug:
                print(f"\033[32mPONG\033[0m:\t Received from {sender_id}")
            if sender_id in self.devices:
                self.devices[sender_id]['last_seen'] = time.time()
            return JSONResponse({"status": "pong_received"})

        # Handle FETCH response
        elif command_type == self.commands.FETCH.value:
            if self.callbacks['on_fetch']:
                response_data = self.callbacks['on_fetch']
                if asyncio.iscoroutinefunction(response_data):
                    await response_data(
                        sender_id=sender_id,
                        query=data.get('data'),
                        timestamp=header.get('timestamp')
                    )
                else:
                    response_data(
                        sender_id=sender_id,
                        query=data.get('data'),
                        timestamp=header.get('timestamp')
                    )
                if response_data:
                    return JSONResponse({
                        "version": __version__,
                        "type": self.commands.DATA.value,
                        "header": {
                            "sender_id": self.id,
                            "sender_port": self.port,
                            "recipient_id": sender_id,
                            "timestamp": int(time.time())
                        },
                        "data": response_data
                    })
            return JSONResponse({"status": "fetch_handled"})

        # Handle PUSH response
        elif command_type == self.commands.PUSH.value:
            if not self.callbacks['on_push']:
                return JSONResponse({
                    "version": __version__,
                    "type": self.commands.NACK.value,
                    "header": {
                        "sender_id": self.id,
                        "sender_port": self.port,
                        "recipient_id": sender_id,
                        "timestamp": int(time.time())
                    },
                }, status_code=400)

            success = self.callbacks['on_push']
            if asyncio.iscoroutinefunction(success):
                await success(
                    sender_id=sender_id,
                    data=data.get('data'),
                    timestamp=header.get('timestamp')
                )
            else:
                success(
                    sender_id=sender_id,
                    data=data.get('data'),
                    timestamp=header.get('timestamp')
                )
            
            if success:
                return JSONResponse({
                    "version": __version__,
                    "type": self.commands.ACK.value,
                    "header": {
                        "sender_id": self.id,
                        "sender_port": self.port,
                        "recipient_id": sender_id,
                        "timestamp": int(time.time())
                    }
                })
            else:
                return JSONResponse({
                    "version": __version__,
                    "type": self.commands.NACK.value,
                    "header": {
                        "sender_id": self.id,
                        "sender_port": self.port,
                        "recipient_id": sender_id,
                        "timestamp": int(time.time())
                    }
                })

        # Handle DATA
        elif command_type == self.commands.DATA.value:
            if self.callbacks['on_data']:
                callback = self.callbacks['on_data']
                if asyncio.iscoroutinefunction(callback):
                    await callback(
                        sender_id=sender_id,
                        data=data.get('data'),
                        timestamp=header.get('timestamp')
                    )
                else:
                    callback(
                        sender_id=sender_id,
                        data=data.get('data'),
                        timestamp=header.get('timestamp')
                    )
            return JSONResponse({"status": "data_received"})
        
        # Handle unknown command types
        return JSONResponse({"error": "Unknown command type"}, status_code=400)
