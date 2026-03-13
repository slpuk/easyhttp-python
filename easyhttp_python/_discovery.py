"""UDP multicast discovery module for EasyHTTP."""

import asyncio
import socket
import struct
import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .core import EasyHTTPAsync

from loggity import Logger, Colors, LoggerConfig
log_config = LoggerConfig(
    colored = True,
    timestamps = False,
    timeformat = None,
    file = None
)
log = Logger(config = log_config)

class Discovery:
    """Manages UDP multicast discovery for EasyHTTP devices."""

    def __init__(
        self,
        parent: "EasyHTTPAsync",
        multicast_group: str = "224.0.0.106",
        multicast_port: int = 37020,
    ):
        self.parent = parent
        self.version = self.parent.__version__
        self.multicast_group = multicast_group
        self.multicast_port = multicast_port
        self.discovery_task: asyncio.Task | None = None
        self.enabled = False

    async def start(self):
        """Start discovery listener and broadcaster."""
        self.enabled = True
        self.discovery_task = asyncio.create_task(self._discovery_loop())

    async def stop(self):
        """Stop discovery tasks."""
        if self.discovery_task:
            self.discovery_task.cancel()
            try:
                await self.discovery_task
            except asyncio.CancelledError:
                pass
            self.discovery_task = None

    async def _discovery_loop(self):
        """Run listener and broadcaster concurrently."""
        listener = asyncio.create_task(self._listen_multicast())
        broadcaster = asyncio.create_task(self._broadcast_presence())
        await asyncio.gather(listener, broadcaster)

    async def _listen_multicast(self):
        """Listen for DISCOVERY messages from other devices."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("", self.multicast_port))

        mreq = struct.pack(
            "4sl", socket.inet_aton(self.multicast_group), socket.INADDR_ANY
        )
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        sock.setblocking(False)

        loop = asyncio.get_event_loop()
        while True:
            try:
                data, addr = await loop.sock_recvfrom(sock, 1024)
                await self._handle_discovery_message(data, addr)
            except asyncio.CancelledError:
                break
            except Exception as e:
                if self.parent.debug:
                    log.custom("DISCOVERY", Colors.RED, e)

    async def _broadcast_presence(self):
        """Periodically broadcast DISCOVERY messages."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

        while True:
            try:
                packet = {
                    "version": self.version,
                    "type": self.parent.commands.DISCOVERY.value,
                    "id": self.parent.id,
                    "port": self.parent.port,
                }
                sock.sendto(
                    json.dumps(packet).encode(),
                    (self.multicast_group, self.multicast_port),
                )
                await asyncio.sleep(30)
            except asyncio.CancelledError:
                break
            except Exception as e:
                if self.parent.debug:
                    log.custom("DISCOVERY", Colors.RED, e)

    async def _handle_discovery_message(self, data: bytes, addr: tuple):
        """Process incoming discovery messages."""
        try:
            message = json.loads(data.decode())
            cmd_type = message.get("type")

            # Received DISCOVERY -> send DISCOVERY_ACK
            if cmd_type == self.parent.commands.DISCOVERY.value:
                device_id = message.get("id")
                device_port = message.get("port")

                if device_id and device_id != self.parent.id:
                    ack_packet = {
                        "version": self.version,
                        "type": self.parent.commands.DISCOVERY_ACK.value,
                        "id": self.parent.id,
                        "port": self.parent.port,
                    }
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.sendto(
                        json.dumps(ack_packet).encode(),
                        (addr[0], self.multicast_port),
                    )
                    if self.parent.debug:
                        log.custom("DISCOVERY", Colors.GREEN, f"Responded to {device_id} at {addr[0]}")

            # Received DISCOVERY_ACK -> add device
            elif cmd_type == self.parent.commands.DISCOVERY_ACK.value:
                device_id = message.get("id")
                device_port = message.get("port")

                if device_id and device_id != self.parent.id:
                    if device_id not in self.parent.devices:
                        self.parent.add(device_id, addr[0], device_port)
                        if self.parent.debug:
                            log.custom("DISCOVERY", Colors.GREEN, f"Found device {device_id} at {addr[0]}")
                        asyncio.create_task(self.parent.ping(device_id))

        except Exception as e:
            if self.parent.debug:
                log.custom("DISCOVERY", Colors.RED, e)
