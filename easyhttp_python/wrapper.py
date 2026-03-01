"""EasyHTTP - Simple HTTP-based P2P framework for IoT."""

import asyncio
from typing import Optional, Any, Callable
from .core import EasyHTTPAsync, __version__

class EasyHTTP:
    """Simple HTTP-based P2P framework with asynchronous core for IoT."""
    
    def __init__(self, debug: bool = False, port: int = 5000, config_file: Optional[str] = None):
        """Initialize the EasyHTTP instance.

        Args:
            debug: Enable debug output. Defaults to False.
            port: Port to run the HTTP server on. Defaults to 5000.
        """

        self._core = EasyHTTPAsync(debug=debug, port=port, config_file=config_file)
        self._loop = None
        self._running = False
        
        self.commands = self._core.commands
        self.__version__ = __version__
        
    def _ensure_loop(self):
        """Ensure event loop is running."""
        if not self._loop:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
    
    def on(self, event: str, callback_func: Callable) -> None:
        """Register a callback function for a specific event.

        Args:
            event: Event name ('on_ping', 'on_fetch', etc.).
            callback_func: Function to call when the event occurs.

        Raises:
            ValueError: If the event is unknown.
        """
        self._core.on(event, callback_func)
    
    def add(self, device_id: str, device_ip: str, device_port: int) -> None:
        """Manually add a device to the local devices cache.

        Args:
            device_id: 6-character device identifier.
            device_ip: IP address of the device.
            device_port: Port number of the device.

        Raises:
            ValueError: If device_id is not 6 characters.
        """
        self._core.add(device_id, device_ip, device_port)

    def start(self) -> None:
        """Start the HTTP server and generate a device ID if not set."""
        self._ensure_loop()
        self._loop.run_until_complete(self._core.start())
        self._running = True
        
    def stop(self) -> None:
        """Gracefully stop the HTTP server and cancel the server task."""
        if self._running:
            self._loop.run_until_complete(self._core.stop())
            self._running = False
    
    def send(self, device_id: str, command_type: Any, data: Optional[Any] = None) -> Optional[dict]:
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
        if not self._loop:
            self._ensure_loop()
        return self._loop.run_until_complete(
            self._core.send(device_id, command_type, data)
        )
    
    def ping(self, device_id: str) -> bool:
        """Send a PING request to a device and check if it's online.

        Args:
            device_id: ID of the device to ping.

        Returns:
            True if device responded with PONG, False otherwise.
        """
        return self._loop.run_until_complete(
            self._core.ping(device_id)
        )
    
    def fetch(self, device_id: str, query: Optional[Any] = None) -> Optional[dict]:
        """Send a FETCH request to another device and return the response.

        Args:
            device_id: ID of the target device.
            query: Query data to send with the FETCH request.

        Returns: 
            Response data from the device, or None if failed.
            The dict typically contains 'type', 'header', and 'data' fields.
        """
        return self._loop.run_until_complete(
            self._core.fetch(device_id, query)
        )
    
    def push(self, device_id: str, data: Optional[Any] = None) -> bool:
        """Send data to another device using PUSH command.

        Args:
            device_id: ID of the target device.
            data: JSON-serializable data to send.

        Returns:
            True if data was successfully sent and acknowledged, False otherwise.

        Raises:
            TypeError: If data is not JSON-serializable.
        """
        return self._loop.run_until_complete(
            self._core.push(device_id, data)
        )

    # Context manager support
    def __enter__(self):
        """Enter the sync context manager."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the sync context manager."""
        self.stop()
    
    # Property accessors
    @property
    def id(self) -> str:
        """Get device ID."""
        return self._core.id
    
    @property
    def devices(self) -> dict:
        """Get devices cache."""
        return self._core.devices