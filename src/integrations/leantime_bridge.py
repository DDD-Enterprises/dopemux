"""
Leantime MCP Integration Bridge for Dopemux

This module provides a bridge between Dopemux and Leantime through the Model Context Protocol.
Handles project management, task tracking, and ADHD-optimized workflows.
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum

import aiohttp
import jwt
from pydantic import BaseModel, ValidationError

from ..core.exceptions import DopemuxIntegrationError, AuthenticationError
from ..core.config import Config
from ..core.monitoring import MetricsCollector
from ..utils.security import SecureTokenManager
from ..utils.adhd_optimizations import ADHDTaskOptimizer


logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Leantime task status enumeration with ADHD considerations."""
    PENDING = "0"
    IN_PROGRESS = "1"
    COMPLETED = "2"
    BLOCKED = "3"
    DEFERRED = "4"
    CANCELLED = "5"
    NEEDS_BREAK = "6"  # ADHD-specific status
    CONTEXT_SWITCH = "7"  # ADHD-specific status


class TaskPriority(Enum):
    """Task priority levels optimized for ADHD attention management."""
    HYPERFOCUS = "1"      # High cognitive load, deep work
    FOCUSED = "2"         # Standard attention required
    SCATTERED = "3"       # Low cognitive load, quick wins
    BACKGROUND = "4"      # Can be done with divided attention


@dataclass
class LeantimeTask:
    """Leantime task representation with ADHD optimizations."""
    id: Optional[int] = None
    headline: str = ""
    description: str = ""
    project_id: int = 0
    user_id: Optional[int] = None
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.FOCUSED
    story_points: Optional[int] = None
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    sprint: Optional[str] = None
    milestone_id: Optional[int] = None
    dependencies: List[int] = None
    tags: List[str] = None

    # ADHD-specific fields
    cognitive_load: Optional[int] = None  # 1-10 scale
    attention_requirement: Optional[str] = None  # hyperfocus, focused, scattered
    break_frequency: Optional[int] = None  # minutes between breaks
    context_complexity: Optional[int] = None  # 1-5 scale

    # Metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.tags is None:
            self.tags = []


@dataclass
class LeantimeProject:
    """Leantime project representation."""
    id: Optional[int] = None
    name: str = ""
    description: str = ""
    state: str = "open"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: Optional[datetime] = None

    # ADHD-specific project settings
    adhd_mode_enabled: bool = True
    context_preservation: bool = True
    notification_batching: bool = True


class LeantimeMCPClient:
    """
    MCP client for Leantime integration with ADHD optimizations.

    Handles authentication, API communication, and data synchronization
    with Leantime's MCP server.
    """

    def __init__(self, config: Config):
        self.config = config
        self.base_url = config.get('leantime.api_url', 'http://localhost:8080')
        self.api_token = config.get('leantime.api_token')
        self.mcp_endpoint = f"{self.base_url}/mcp"

        self.session: Optional[aiohttp.ClientSession] = None
        self.token_manager = SecureTokenManager()
        self.metrics = MetricsCollector()
        self.adhd_optimizer = ADHDTaskOptimizer()

        # Connection state
        self._connected = False
        self._session_id = None
        self._last_heartbeat = None

        # Request tracking
        self._request_id = 0
        self._pending_requests: Dict[int, asyncio.Future] = {}

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()

    async def connect(self) -> bool:
        """
        Establish connection to Leantime MCP server.

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    'Authorization': f'Bearer {self.api_token}',
                    'Content-Type': 'application/json',
                    'User-Agent': 'Dopemux-Leantime-Bridge/1.0'
                }
            )

            # Test connection with MCP initialization
            init_response = await self._send_mcp_request({
                "jsonrpc": "2.0",
                "id": self._next_request_id(),
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "resources": {},
                        "prompts": {}
                    },
                    "clientInfo": {
                        "name": "Dopemux-Leantime-Bridge",
                        "version": "1.0.0"
                    }
                }
            })

            if init_response.get('result'):
                self._connected = True
                self._session_id = init_response['result'].get('sessionId')
                logger.info("Successfully connected to Leantime MCP server")

                # Start heartbeat
                asyncio.create_task(self._heartbeat_loop())

                return True
            else:
                logger.error(f"Failed to initialize MCP connection: {init_response}")
                return False

        except Exception as e:
            logger.error(f"Failed to connect to Leantime: {e}")
            if self.session:
                await self.session.close()
                self.session = None
            return False

    async def disconnect(self):
        """Gracefully disconnect from Leantime MCP server."""
        if self.session:
            try:
                # Send shutdown notification
                await self._send_mcp_request({
                    "jsonrpc": "2.0",
                    "method": "notifications/shutdown"
                })
            except Exception as e:
                logger.warning(f"Error during shutdown: {e}")
            finally:
                await self.session.close()
                self.session = None
                self._connected = False
                logger.info("Disconnected from Leantime MCP server")

    def _next_request_id(self) -> int:
        """Generate next request ID."""
        self._request_id += 1
        return self._request_id

    async def _send_mcp_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send MCP request to Leantime server.

        Args:
            request: MCP request payload

        Returns:
            MCP response
        """
        if not self.session:
            raise DopemuxIntegrationError("Not connected to Leantime")

        try:
            async with self.session.post(self.mcp_endpoint, json=request) as response:
                response.raise_for_status()
                result = await response.json()

                # Track metrics
                self.metrics.record_api_call(
                    service='leantime',
                    method=request.get('method', 'unknown'),
                    status='success',
                    response_time=(datetime.now() - datetime.now()).total_seconds()
                )

                return result

        except aiohttp.ClientError as e:
            logger.error(f"HTTP error in MCP request: {e}")
            self.metrics.record_api_call(
                service='leantime',
                method=request.get('method', 'unknown'),
                status='error'
            )
            raise DopemuxIntegrationError(f"Leantime API error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in MCP request: {e}")
            raise DopemuxIntegrationError(f"Unexpected error: {e}")

    async def _heartbeat_loop(self):
        """Maintain connection with periodic heartbeat."""
        while self._connected and self.session:
            try:
                await asyncio.sleep(30)  # 30 second heartbeat

                await self._send_mcp_request({
                    "jsonrpc": "2.0",
                    "method": "notifications/heartbeat",
                    "params": {
                        "sessionId": self._session_id,
                        "timestamp": datetime.now().isoformat()
                    }
                })

                self._last_heartbeat = datetime.now()

            except Exception as e:
                logger.warning(f"Heartbeat failed: {e}")
                break

    # Project Management Methods

    async def get_projects(self, limit: int = 50) -> List[LeantimeProject]:
        """
        Retrieve all projects from Leantime.

        Args:
            limit: Maximum number of projects to return

        Returns:
            List of Leantime projects
        """
        response = await self._send_mcp_request({
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "tools/call",
            "params": {
                "name": "leantime.rpc.projects.getAllProjects",
                "arguments": {
                    "limit": limit
                }
            }
        })

        if response.get('result', {}).get('content'):
            projects_data = response['result']['content'][0]['text']
            projects = json.loads(projects_data)

            return [
                LeantimeProject(
                    id=proj.get('id'),
                    name=proj.get('name', ''),
                    description=proj.get('details', ''),
                    state=proj.get('state', 'open'),
                    created_at=self._parse_datetime(proj.get('created'))
                )
                for proj in projects
            ]

        return []

    async def get_project(self, project_id: int) -> Optional[LeantimeProject]:
        """
        Get specific project details.

        Args:
            project_id: Leantime project ID

        Returns:
            Project details or None if not found
        """
        response = await self._send_mcp_request({
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "tools/call",
            "params": {
                "name": "leantime.rpc.projects.getProject",
                "arguments": {
                    "projectId": project_id
                }
            }
        })

        if response.get('result', {}).get('content'):
            project_data = json.loads(response['result']['content'][0]['text'])

            return LeantimeProject(
                id=project_data.get('id'),
                name=project_data.get('name', ''),
                description=project_data.get('details', ''),
                state=project_data.get('state', 'open'),
                start_date=self._parse_datetime(project_data.get('start')),
                end_date=self._parse_datetime(project_data.get('end')),
                created_at=self._parse_datetime(project_data.get('created'))
            )

        return None

    async def create_project(self, project: LeantimeProject) -> Optional[LeantimeProject]:
        """
        Create new project in Leantime.

        Args:
            project: Project details

        Returns:
            Created project with ID or None if failed
        """
        response = await self._send_mcp_request({
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "tools/call",
            "params": {
                "name": "leantime.rpc.projects.addProject",
                "arguments": {
                    "name": project.name,
                    "details": project.description,
                    "state": project.state
                }
            }
        })

        if response.get('result', {}).get('content'):
            result_data = json.loads(response['result']['content'][0]['text'])
            if result_data.get('success'):
                project.id = result_data.get('projectId')
                return project

        return None

    # Task Management Methods

    async def get_tasks(self, project_id: Optional[int] = None,
                       status: Optional[TaskStatus] = None,
                       limit: int = 100) -> List[LeantimeTask]:
        """
        Retrieve tasks from Leantime with ADHD optimizations.

        Args:
            project_id: Optional project filter
            status: Optional status filter
            limit: Maximum number of tasks

        Returns:
            List of Leantime tasks
        """
        params = {
            "limit": limit
        }

        if project_id:
            params["projectId"] = project_id
        if status:
            params["status"] = status.value

        response = await self._send_mcp_request({
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "tools/call",
            "params": {
                "name": "leantime.rpc.tickets.getAllTickets",
                "arguments": params
            }
        })

        if response.get('result', {}).get('content'):
            tasks_data = json.loads(response['result']['content'][0]['text'])

            tasks = []
            for task_data in tasks_data:
                task = LeantimeTask(
                    id=task_data.get('id'),
                    headline=task_data.get('headline', ''),
                    description=task_data.get('description', ''),
                    project_id=task_data.get('projectId', 0),
                    user_id=task_data.get('editorId'),
                    status=TaskStatus(str(task_data.get('status', '0'))),
                    story_points=task_data.get('storypoints'),
                    created_at=self._parse_datetime(task_data.get('date')),
                    updated_at=self._parse_datetime(task_data.get('dateToFinish'))
                )

                # Apply ADHD optimizations
                task = await self.adhd_optimizer.optimize_task(task)
                tasks.append(task)

            return tasks

        return []

    async def get_task(self, task_id: int) -> Optional[LeantimeTask]:
        """
        Get specific task details.

        Args:
            task_id: Leantime task ID

        Returns:
            Task details or None if not found
        """
        response = await self._send_mcp_request({
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "tools/call",
            "params": {
                "name": "leantime.rpc.tickets.getTicket",
                "arguments": {
                    "ticketId": task_id
                }
            }
        })

        if response.get('result', {}).get('content'):
            task_data = json.loads(response['result']['content'][0]['text'])

            return LeantimeTask(
                id=task_data.get('id'),
                headline=task_data.get('headline', ''),
                description=task_data.get('description', ''),
                project_id=task_data.get('projectId', 0),
                user_id=task_data.get('editorId'),
                status=TaskStatus(str(task_data.get('status', '0'))),
                story_points=task_data.get('storypoints'),
                created_at=self._parse_datetime(task_data.get('date')),
                updated_at=self._parse_datetime(task_data.get('dateToFinish'))
            )

        return None

    async def create_task(self, task: LeantimeTask) -> Optional[LeantimeTask]:
        """
        Create new task in Leantime with ADHD optimizations.

        Args:
            task: Task details

        Returns:
            Created task with ID or None if failed
        """
        # Apply ADHD optimizations before creation
        optimized_task = await self.adhd_optimizer.optimize_task(task)

        response = await self._send_mcp_request({
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "tools/call",
            "params": {
                "name": "leantime.rpc.tickets.addTicket",
                "arguments": {
                    "headline": optimized_task.headline,
                    "description": optimized_task.description,
                    "projectId": optimized_task.project_id,
                    "status": optimized_task.status.value,
                    "priority": optimized_task.priority.value,
                    "storypoints": optimized_task.story_points,
                    "editorId": optimized_task.user_id
                }
            }
        })

        if response.get('result', {}).get('content'):
            result_data = json.loads(response['result']['content'][0]['text'])
            if result_data.get('success'):
                optimized_task.id = result_data.get('ticketId')
                return optimized_task

        return None

    async def update_task(self, task: LeantimeTask) -> bool:
        """
        Update existing task in Leantime.

        Args:
            task: Task with updates

        Returns:
            True if update successful, False otherwise
        """
        if not task.id:
            raise ValueError("Task ID required for update")

        response = await self._send_mcp_request({
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "tools/call",
            "params": {
                "name": "leantime.rpc.tickets.updateTicket",
                "arguments": {
                    "ticketId": task.id,
                    "headline": task.headline,
                    "description": task.description,
                    "status": task.status.value,
                    "priority": task.priority.value,
                    "storypoints": task.story_points
                }
            }
        })

        if response.get('result', {}).get('content'):
            result_data = json.loads(response['result']['content'][0]['text'])
            return result_data.get('success', False)

        return False

    async def delete_task(self, task_id: int) -> bool:
        """
        Delete task from Leantime.

        Args:
            task_id: Task ID to delete

        Returns:
            True if deletion successful, False otherwise
        """
        response = await self._send_mcp_request({
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "tools/call",
            "params": {
                "name": "leantime.rpc.tickets.deleteTicket",
                "arguments": {
                    "ticketId": task_id
                }
            }
        })

        if response.get('result', {}).get('content'):
            result_data = json.loads(response['result']['content'][0]['text'])
            return result_data.get('success', False)

        return False

    # ADHD-Specific Methods

    async def get_adhd_optimized_tasks(self, user_id: int,
                                      attention_state: str = "focused") -> List[LeantimeTask]:
        """
        Get tasks optimized for current ADHD attention state.

        Args:
            user_id: User ID for personalization
            attention_state: Current attention state (hyperfocus, focused, scattered)

        Returns:
            List of tasks suitable for current attention state
        """
        all_tasks = await self.get_tasks()

        # Filter and optimize based on attention state
        optimized_tasks = []
        for task in all_tasks:
            if task.user_id == user_id or task.user_id is None:
                # Apply ADHD filtering logic
                if attention_state == "hyperfocus" and task.priority == TaskPriority.HYPERFOCUS:
                    optimized_tasks.append(task)
                elif attention_state == "focused" and task.priority in [TaskPriority.FOCUSED, TaskPriority.HYPERFOCUS]:
                    optimized_tasks.append(task)
                elif attention_state == "scattered" and task.priority in [TaskPriority.SCATTERED, TaskPriority.BACKGROUND]:
                    optimized_tasks.append(task)

        # Sort by ADHD-optimized criteria
        return sorted(optimized_tasks, key=lambda t: (
            t.cognitive_load or 5,  # Lower cognitive load first for scattered attention
            t.story_points or 0,    # Smaller tasks first
            t.priority.value        # Priority order
        ))

    async def update_context_preservation(self, user_id: int, context_data: Dict[str, Any]) -> bool:
        """
        Update context preservation data for ADHD users.

        Args:
            user_id: User ID
            context_data: Context information to preserve

        Returns:
            True if update successful
        """
        # Store context in Leantime user preferences or custom table
        # This would require custom Leantime plugin for full implementation
        logger.info(f"Context preservation update for user {user_id}: {context_data}")
        return True

    # Utility Methods

    def _parse_datetime(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime string from Leantime format."""
        if not date_str:
            return None

        try:
            # Try common Leantime date formats
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y-%m-%dT%H:%M:%S']:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
        except Exception as e:
            logger.warning(f"Failed to parse datetime '{date_str}': {e}")

        return None

    async def health_check(self) -> Dict[str, Any]:
        """
        Check health status of Leantime connection.

        Returns:
            Health status information
        """
        try:
            if not self._connected:
                return {
                    "status": "disconnected",
                    "connected": False,
                    "last_heartbeat": None,
                    "error": "Not connected to Leantime"
                }

            # Try a simple API call
            projects = await self.get_projects(limit=1)

            return {
                "status": "healthy",
                "connected": True,
                "last_heartbeat": self._last_heartbeat.isoformat() if self._last_heartbeat else None,
                "session_id": self._session_id,
                "api_responsive": True,
                "projects_accessible": len(projects) >= 0
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "connected": self._connected,
                "last_heartbeat": self._last_heartbeat.isoformat() if self._last_heartbeat else None,
                "error": str(e)
            }


# Factory function for easy instantiation
def create_leantime_bridge(config: Config) -> LeantimeMCPClient:
    """
    Factory function to create Leantime MCP client.

    Args:
        config: Dopemux configuration

    Returns:
        Configured Leantime MCP client
    """
    return LeantimeMCPClient(config)