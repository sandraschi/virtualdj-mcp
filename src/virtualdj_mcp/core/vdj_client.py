"""
VirtualDJ Client - CLI and REST API wrapper
"""

import asyncio
import subprocess
import json
import aiohttp
from typing import Optional, Dict, Any, Union
from pathlib import Path


class VDJError(Exception):
    """VirtualDJ operation error"""
    pass


class VirtualDJClient:
    """VirtualDJ CLI and REST API client wrapper"""
    
    def __init__(self, config):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self._vdj_process: Optional[subprocess.Popen] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        if self.config.rest_api_enabled:
            self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def start_virtualdj(self) -> bool:
        """Start VirtualDJ application if not running"""
        try:
            # Check if VirtualDJ is already running
            if await self.is_running():
                return True
            
            # Start VirtualDJ with API enabled
            cmd = [
                self.config.virtualdj_path,
                "-api", str(self.config.rest_api_port)
            ]
            
            self._vdj_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # Wait for startup
            await asyncio.sleep(3)
            
            return await self.is_running()
            
        except Exception as e:
            raise VDJError(f"Failed to start VirtualDJ: {e}")
    
    async def is_running(self) -> bool:
        """Check if VirtualDJ is running and responsive"""
        if not self.config.rest_api_enabled:
            return True  # Assume CLI-only mode works
        
        try:
            async with self.session.get(
                f"{self.config.rest_api_url}/status",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                return response.status == 200
        except:
            return False
    
    async def send_command(self, command: str) -> Dict[str, Any]:
        """Send command to VirtualDJ via REST API or CLI"""
        if self.config.rest_api_enabled and self.session:
            return await self._send_rest_command(command)
        elif self.config.cli_enabled:
            return await self._send_cli_command(command)
        else:
            raise VDJError("No communication method enabled")
    
    async def _send_rest_command(self, command: str) -> Dict[str, Any]:
        """Send command via REST API"""
        try:
            payload = {"cmd": command}
            async with self.session.post(
                f"{self.config.rest_api_url}/command",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=self.config.cli_timeout)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return {"status": "success", "result": result}
                else:
                    error_text = await response.text()
                    return {"status": "error", "error": error_text}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def _send_cli_command(self, command: str) -> Dict[str, Any]:
        """Send command via CLI"""
        try:
            cmd = [self.config.virtualdj_path, "-cmd", command]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self.config.cli_timeout
            )
            
            if process.returncode == 0:
                output = stdout.decode().strip()
                return {"status": "success", "result": output}
            else:
                error = stderr.decode().strip()
                return {"status": "error", "error": error}
                
        except asyncio.TimeoutError:
            return {"status": "error", "error": "Command timeout"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def get_status(self) -> Dict[str, Any]:
        """Get VirtualDJ status"""
        if self.config.rest_api_enabled and self.session:
            try:
                async with self.session.get(
                    f"{self.config.rest_api_url}/status"
                ) as response:
                    if response.status == 200:
                        return await response.json()
            except Exception as e:
                raise VDJError(f"Failed to get status: {e}")
        
        # Fallback to CLI status commands
        result = await self.send_command("get_var 'status'")
        if result["status"] == "success":
            return {"status": "running", "details": result["result"]}
        else:
            raise VDJError(f"Failed to get status: {result.get('error', 'Unknown error')}")
    
    async def stop_virtualdj(self):
        """Stop VirtualDJ application"""
        try:
            await self.send_command("quit")
            if self._vdj_process:
                self._vdj_process.terminate()
                self._vdj_process = None
        except Exception as e:
            raise VDJError(f"Failed to stop VirtualDJ: {e}")
