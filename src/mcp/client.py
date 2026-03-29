import subprocess
import json
import logging
import shlex
from typing import Any

logger = logging.getLogger(__name__)

class MCPClientError(Exception):
    pass

class MCPConnectionError(MCPClientError):
    pass

class MCPClient:
    
    def __init__(self, server_command:str):
        self.server_command = server_command
        self.process: subprocess.Popen | None = None
        self._request_id = 0
    
    def is_running(self) -> bool:
        return self.process is not None and self.process.poll() is None
    
    def start(self):
        logger.info(f"Starting MCP server: {self.server_command}")

        try:

            command_list = shlex.split(self.server_command)
       

            self.process = subprocess.Popen(
                command_list,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
        except FileNotFoundError:
            raise MCPConnectionError(f"MCP server not found: {self.server_command}")
        except Exception as e:
            raise MCPConnectionError(f"Failed to start MCP server: {e}")
    
    def stop(self) -> None:
        if self.process:
            logger.info("Stopping MCP server")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning("MCP server didn't stop gracefully, killing")
                self.process.kill()
            self.process = None

    def _send(self, message: dict):
        if not self.process or not self.process.stdin:
            raise RuntimeError("MCP server not running")
        
        json_str = json.dumps(message) + '\n'
        self.process.stdin.write(json_str)
        self.process.stdin.flush()
    
    def _receive(self)-> dict:
        if not self.process or not self.process.stdout:
            raise RuntimeError("MCP server not running")
        
        line = self.process.stdout.readline()
        if not line:
            raise RuntimeError("MCP server closed the connection")
        
        return json.loads(line)
    
    def _get_next_id(self) -> int:
        self._request_id += 1
        return self._request_id
    
    def initialize(self):
        request = {
            "jsonrpc": "2.0",
            "id" : self._get_next_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "pelosi-tracker",
                    "version": "1.0.0"
                }
            }
        }
        self._send(request)

        response = self._receive()
        if "error" in response:
            raise MCPConnectionError(f"Initialization failed: {response['error']}")
        
        notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }
        self._send(notification)

        logger.info("MCP server initialized successfully")

    def call_tool(self, tool_name: str, arguments: dict=None) -> Any:
        if arguments is None:
            arguments = {}
        
        request = {
            "jsonrpc": "2.0",
            "id": self._get_next_id(),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }

        self._send(request)
        
        response = self._receive()

        if "error" in response:
            raise MCPClientError(f"Tool call failed: {response['error']}")
        
        if "result" in response:
            return response["result"]
        
        return None


