import os
import secrets
import time
import threading
import requests
import socket
import logging
import json
from pathlib import Path
from enum import Enum, auto
from flask import Flask, request, jsonify

class EasyHTTP():
    def __init__(self, debug=False, port=5000, config_file=None):
        self.debug = debug
        self.port = port
        if config_file:
            self.config_file = config_file
        else:
            import sys
            if getattr(sys, 'frozen', False):
                base_dir = os.path.dirname(sys.executable)
            else:
                # Для python скриптов
                base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
            
            self.config_file = os.path.join(base_dir, "easyhttp_device.json")

        self.id = None
        self.callbacks = {
            'on_get': None,
            'on_data_response': None,
            'on_ping': None
            #'on_pull': None
        }
        self.devices = {}
        self.app = Flask(__name__)
        self.app.route('/easyhttp/api', methods=['POST'])(self.api_handler)
        self._load_config() 

    class commands(Enum):
        DISCOVERY = auto() # Reserved for future updates
        DISCOVERY_RESPONSE = auto() # Reserved for future updates
        PING = auto()
        PING_OK = auto()
        GET = auto()
        DATA_RESPONSE = auto()
        #PULL = auto() 
        #PULL_CONFIRM = auto()
        #PULL_ERROR = auto()

    def _load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    self.id = data.get('device_id')
                    
                if self.debug and self.id:
                    print(f"[CONFIG] Loaded ID: {self.id} from {self.config_file}")
        except Exception as e:
            if self.debug:
                print(f"[CONFIG] Error loading config: {e}")
    
    def _save_config(self):
        try:
            config = {
                'device_id': self.id,
                'port': self.port,
                'version': '0.1.0'
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            if self.debug:
                print(f"[CONFIG] Saved ID to {self.config_file}")
        except Exception as e:
            if self.debug:
                print(f"[CONFIG] Error saving config: {e}")

    def _generate_id(self, length=6):
        alphabet = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"
        self.id = ''.join(secrets.choice(alphabet) for _ in range(length))
        self._save_config()

    def add_device(self, device_id, device_ip, device_port):
        if len(device_id) != 6:
            raise ValueError("Device ID must be 6 characters")
    
        self.devices[device_id] = {
            'ip': device_ip,
            'port': int(device_port),
            'last_seen': time.time(),
            'added_manually': True
        }
    
        if self.debug:
            print(f"[DEBUG] Added device {device_id}: {device_ip}:{device_port}")

    def start(self):
        if not self.id:
            self._generate_id()
    
        try:
            self.server_thread = threading.Thread(
                target=self.app.run,
                kwargs={
                    'host': '0.0.0.0',
                    'port': self.port,
                    'debug': False,
                    'use_reloader': False
                },
                daemon=True
            )
            self.server_thread.start()
            logging.getLogger('werkzeug').disabled = True
            time.sleep(2)
        
            if self.debug:
                print(f"[DEBUG] Device's ID: {self.id}")
                print(f"[DEBUG] EasyHTTP started on port {self.port}")
                local_ip = socket.gethostbyname(socket.gethostname())
                print(f"[DEBUG] API: http://{local_ip}:{self.port}/easyhttp/api")
            
        except Exception as e:
            print(f"\033[31m[ERROR] Failed to start server: {e}\033[0m")
            raise

    def on(self, event, callback_func):
        if event in self.callbacks:
            self.callbacks[event] = callback_func
        else:
            raise ValueError(f"Unknown event: {event}")

    def api_handler(self):
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data"}), 400
            
        command_type = data.get('type')
        header = data.get('header', {})
        sender_id = header.get('sender_id')

        if sender_id and sender_id not in self.devices:
            self.devices[sender_id] = {
                'ip': request.remote_addr,
                'port': header.get('port', self.port),
                'last_seen': time.time()
            }

        if command_type == self.commands.PING.value:
            if self.callbacks.get('on_ping'):
                self.callbacks['on_ping'](sender_id)
                
            return jsonify({
                "type": self.commands.PING_OK.value,
                "header": {
                    "sender_id": self.id,
                    "recipient_id": sender_id,
                    "timestamp": int(time.time())
                }
            })

        elif command_type == self.commands.GET.value:
            if self.callbacks['on_get']:
                response_data = self.callbacks['on_get'](
                    sender_id=sender_id,
                    timestamp=header.get('timestamp')
                )
                if response_data:
                    return jsonify({
                        "type": self.commands.DATA_RESPONSE.value,
                        "header": {
                            "sender_id": self.id,
                            "recipient_id": sender_id,
                            "timestamp": int(time.time())
                        },
                        "data": response_data
                    })
            return jsonify({"status": "get_received"})

        elif command_type == self.commands.DATA_RESPONSE.value:
            if self.callbacks['on_data_response']:
                self.callbacks['on_data_response'](
                    sender_id=sender_id,
                    data=data.get('data'),
                    timestamp=header.get('timestamp')
                )
            return jsonify({"status": "data_received"})

        return jsonify({"error": "Unknown command"}), 400

    def send(self, device_id, command_type, data=None):
        if device_id not in self.devices:
            if self.debug:
                print(f"\033[31m[ERROR] Device {device_id} not found in devices cache\033[0m")
            return None
    
        packet = {
            'type': command_type.value if isinstance(command_type, self.commands) else command_type,
            'header': {
                'sender_id': self.id, 
                'recver_id': device_id, 
                'timestamp': int(time.time())
            }
        }
    
        if data:
            packet['data'] = data
    
        recver_url = f"http://{self.devices[device_id]['ip']}:{self.devices[device_id]['port']}/easyhttp/api"
    
        try:
            response = requests.post(recver_url, json=packet, timeout=3)
            return response.json() if response.status_code == 200 else None
            
        except Exception as e:
            if self.debug:
                print(f'\033[31m[ERROR] Failed to send to {device_id}: {e}\033[0m')
            return None

    def ping(self, device_id):
        response = self.send(device_id, self.commands.PING)
    
        if response and response.get('type') == self.commands.PING_OK.value:
            if self.debug:
                print(f"[PING] {device_id} is online")
            if device_id in self.devices:
                self.devices[device_id]['last_seen'] = time.time()
            return True
        else:
            if self.debug:
                print(f"[PING] {device_id} is offline or not responding")
            return False

    def get(self, device_id, query=None):
        response = self.send(device_id, self.commands.GET, query)
        return response
        