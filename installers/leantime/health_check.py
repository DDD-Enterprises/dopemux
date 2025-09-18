#!/usr/bin/env python3
"""
Dopemux Leantime & Task-Master Health Check Utility

Comprehensive health monitoring for Leantime and Task-Master AI integration,
with ADHD-optimized status reporting and automated diagnostics.
"""

import asyncio
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
import click
import aiohttp
import docker
from docker.errors import DockerException

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.config import Config
from src.integrations.leantime_bridge import create_leantime_bridge
from src.integrations.taskmaster_bridge import create_taskmaster_bridge
from src.integrations.sync_manager import create_sync_manager


logger = logging.getLogger(__name__)


class HealthStatus:
    """Health status levels with ADHD-friendly indicators."""
    HEALTHY = "healthy"
    WARNING = "warning"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

    @staticmethod
    def get_emoji(status: str) -> str:
        """Get emoji indicator for status."""
        emoji_map = {
            HealthStatus.HEALTHY: "✅",
            HealthStatus.WARNING: "⚠️",
            HealthStatus.UNHEALTHY: "❌",
            HealthStatus.CRITICAL: "🚨",
            HealthStatus.UNKNOWN: "❓"
        }
        return emoji_map.get(status, "❓")

    @staticmethod
    def get_color(status: str) -> str:
        """Get color code for CLI output."""
        color_map = {
            HealthStatus.HEALTHY: "green",
            HealthStatus.WARNING: "yellow",
            HealthStatus.UNHEALTHY: "red",
            HealthStatus.CRITICAL: "red",
            HealthStatus.UNKNOWN: "white"
        }
        return color_map.get(status, "white")


class DopemuxHealthChecker:
    """Comprehensive health checker for Dopemux Leantime installation."""

    def __init__(self):
        self.config = Config()
        self.installation_dir = Path.cwd()
        self.docker_dir = self.installation_dir / "docker" / "leantime"

        # Health check results
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": HealthStatus.UNKNOWN,
            "components": {},
            "recommendations": [],
            "metrics": {}
        }

    async def run_health_check(self, verbose: bool = False, check_integration: bool = True) -> Dict[str, Any]:
        """
        Run comprehensive health check.

        Args:
            verbose: Include detailed diagnostics
            check_integration: Test MCP integrations

        Returns:
            Health check results
        """
        try:
            logger.info("🔍 Starting Dopemux health check...")

            # System checks
            await self._check_system_requirements()
            await self._check_docker_environment()
            await self._check_leantime_service()
            await self._check_database_connectivity()
            await self._check_taskmaster_installation()

            if check_integration:
                await self._check_mcp_integrations()
                await self._check_sync_functionality()

            # ADHD-specific checks
            await self._check_adhd_optimizations()

            # Performance metrics
            if verbose:
                await self._collect_performance_metrics()

            # Determine overall status
            self._calculate_overall_status()

            # Generate recommendations
            self._generate_recommendations()

            logger.info("✅ Health check completed")

        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            self.results["overall_status"] = HealthStatus.CRITICAL
            self.results["error"] = str(e)

        return self.results

    async def _check_system_requirements(self):
        """Check system requirements and dependencies."""
        component = "system_requirements"
        self.results["components"][component] = {
            "status": HealthStatus.HEALTHY,
            "checks": {},
            "issues": []
        }

        try:
            # Check Docker
            try:
                docker_client = docker.from_env()
                docker_client.ping()
                version_info = docker_client.version()

                self.results["components"][component]["checks"]["docker"] = {
                    "status": HealthStatus.HEALTHY,
                    "version": version_info.get("Version", "unknown"),
                    "api_version": version_info.get("ApiVersion", "unknown")
                }
            except DockerException as e:
                self.results["components"][component]["checks"]["docker"] = {
                    "status": HealthStatus.CRITICAL,
                    "error": str(e)
                }
                self.results["components"][component]["status"] = HealthStatus.CRITICAL
                self.results["components"][component]["issues"].append("Docker not available")

            # Check Docker Compose
            try:
                proc = await asyncio.create_subprocess_exec(
                    "docker-compose", "--version",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await proc.communicate()

                if proc.returncode == 0:
                    self.results["components"][component]["checks"]["docker_compose"] = {
                        "status": HealthStatus.HEALTHY,
                        "version": stdout.decode().strip()
                    }
                else:
                    raise Exception(stderr.decode())

            except Exception as e:
                self.results["components"][component]["checks"]["docker_compose"] = {
                    "status": HealthStatus.CRITICAL,
                    "error": str(e)
                }
                self.results["components"][component]["status"] = HealthStatus.CRITICAL

            # Check Node.js for Task-Master
            try:
                proc = await asyncio.create_subprocess_exec(
                    "node", "--version",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await proc.communicate()

                if proc.returncode == 0:
                    self.results["components"][component]["checks"]["nodejs"] = {
                        "status": HealthStatus.HEALTHY,
                        "version": stdout.decode().strip()
                    }
                else:
                    raise Exception(stderr.decode())

            except Exception as e:
                self.results["components"][component]["checks"]["nodejs"] = {
                    "status": HealthStatus.WARNING,
                    "error": str(e),
                    "note": "Required for Task-Master AI"
                }

        except Exception as e:
            self.results["components"][component]["status"] = HealthStatus.UNHEALTHY
            self.results["components"][component]["error"] = str(e)

    async def _check_docker_environment(self):
        """Check Docker containers and services."""
        component = "docker_environment"
        self.results["components"][component] = {
            "status": HealthStatus.HEALTHY,
            "containers": {},
            "networks": {},
            "volumes": {},
            "issues": []
        }

        try:
            docker_client = docker.from_env()

            # Check containers
            required_containers = {
                "leantime": {"image": "leantime/leantime", "ports": ["80/tcp"]},
                "mysql_leantime": {"image": "mysql", "ports": ["3306/tcp"]},
                "redis_leantime": {"image": "redis", "ports": ["6379/tcp"]}
            }

            containers = docker_client.containers.list(all=True)
            container_map = {c.name: c for c in containers}

            for container_name, requirements in required_containers.items():
                if container_name in container_map:
                    container = container_map[container_name]
                    container_info = {
                        "status": container.status,
                        "image": container.image.tags[0] if container.image.tags else "unknown",
                        "created": container.attrs["Created"],
                        "health": HealthStatus.HEALTHY if container.status == "running" else HealthStatus.UNHEALTHY
                    }

                    # Check health if container has health check
                    if container.status == "running":
                        try:
                            health_info = container.attrs.get("State", {}).get("Health", {})
                            if health_info:
                                health_status = health_info.get("Status", "unknown")
                                container_info["health_check"] = health_status
                                if health_status != "healthy":
                                    container_info["health"] = HealthStatus.WARNING

                        except Exception:
                            pass

                    self.results["components"][component]["containers"][container_name] = container_info

                    if container.status != "running":
                        self.results["components"][component]["issues"].append(
                            f"Container {container_name} is not running"
                        )
                        self.results["components"][component]["status"] = HealthStatus.UNHEALTHY

                else:
                    self.results["components"][component]["containers"][container_name] = {
                        "status": "not_found",
                        "health": HealthStatus.CRITICAL
                    }
                    self.results["components"][component]["issues"].append(
                        f"Required container {container_name} not found"
                    )
                    self.results["components"][component]["status"] = HealthStatus.CRITICAL

            # Check networks
            try:
                networks = docker_client.networks.list(names=["leantime-net"])
                if networks:
                    network = networks[0]
                    self.results["components"][component]["networks"]["leantime-net"] = {
                        "status": HealthStatus.HEALTHY,
                        "driver": network.attrs.get("Driver", "unknown"),
                        "containers": len(network.attrs.get("Containers", {}))
                    }
                else:
                    self.results["components"][component]["networks"]["leantime-net"] = {
                        "status": HealthStatus.CRITICAL
                    }
                    self.results["components"][component]["issues"].append("Leantime network not found")

            except Exception as e:
                self.results["components"][component]["networks"]["error"] = str(e)

        except Exception as e:
            self.results["components"][component]["status"] = HealthStatus.CRITICAL
            self.results["components"][component]["error"] = str(e)

    async def _check_leantime_service(self):
        """Check Leantime web service availability."""
        component = "leantime_service"
        self.results["components"][component] = {
            "status": HealthStatus.HEALTHY,
            "url": "",
            "response_time": 0,
            "issues": []
        }

        try:
            # Determine Leantime URL
            leantime_url = self._get_leantime_url()
            self.results["components"][component]["url"] = leantime_url

            start_time = datetime.now()

            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(
                        leantime_url,
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        response_time = (datetime.now() - start_time).total_seconds()
                        self.results["components"][component]["response_time"] = response_time

                        self.results["components"][component]["http_status"] = response.status

                        if response.status in [200, 302]:  # 302 for redirect to login/install
                            self.results["components"][component]["status"] = HealthStatus.HEALTHY
                        elif response.status in [401, 403]:
                            self.results["components"][component]["status"] = HealthStatus.WARNING
                            self.results["components"][component]["issues"].append("Authentication required")
                        else:
                            self.results["components"][component]["status"] = HealthStatus.UNHEALTHY
                            self.results["components"][component]["issues"].append(
                                f"HTTP {response.status} response"
                            )

                        # Check response headers for additional info
                        server = response.headers.get("Server", "unknown")
                        self.results["components"][component]["server"] = server

                except asyncio.TimeoutError:
                    self.results["components"][component]["status"] = HealthStatus.UNHEALTHY
                    self.results["components"][component]["issues"].append("Request timeout")

                except aiohttp.ClientError as e:
                    self.results["components"][component]["status"] = HealthStatus.UNHEALTHY
                    self.results["components"][component]["issues"].append(f"Connection error: {e}")

        except Exception as e:
            self.results["components"][component]["status"] = HealthStatus.CRITICAL
            self.results["components"][component]["error"] = str(e)

    async def _check_database_connectivity(self):
        """Check database connectivity and health."""
        component = "database"
        self.results["components"][component] = {
            "status": HealthStatus.HEALTHY,
            "connection": {},
            "performance": {},
            "issues": []
        }

        try:
            # Check MySQL container health first
            docker_client = docker.from_env()
            containers = docker_client.containers.list(filters={"name": "mysql_leantime"})

            if not containers:
                self.results["components"][component]["status"] = HealthStatus.CRITICAL
                self.results["components"][component]["issues"].append("MySQL container not found")
                return

            mysql_container = containers[0]

            if mysql_container.status != "running":
                self.results["components"][component]["status"] = HealthStatus.CRITICAL
                self.results["components"][component]["issues"].append("MySQL container not running")
                return

            # Test database connection through container
            try:
                # Execute a simple query to test connectivity
                exec_result = mysql_container.exec_run(
                    "mysql -u root -p${MYSQL_ROOT_PASSWORD} -e 'SELECT 1'"
                )

                if exec_result.exit_code == 0:
                    self.results["components"][component]["connection"]["status"] = HealthStatus.HEALTHY
                    self.results["components"][component]["connection"]["test"] = "basic_query_success"
                else:
                    self.results["components"][component]["connection"]["status"] = HealthStatus.UNHEALTHY
                    self.results["components"][component]["issues"].append("Database query failed")

            except Exception as e:
                self.results["components"][component]["connection"]["status"] = HealthStatus.WARNING
                self.results["components"][component]["connection"]["error"] = str(e)

            # Check database size and tables
            try:
                exec_result = mysql_container.exec_run(
                    "mysql -u root -p${MYSQL_ROOT_PASSWORD} -e 'SHOW DATABASES'"
                )

                if exec_result.exit_code == 0:
                    output = exec_result.output.decode()
                    databases = [line.strip() for line in output.split('\n') if line.strip()]
                    self.results["components"][component]["databases"] = databases

            except Exception:
                pass

        except Exception as e:
            self.results["components"][component]["status"] = HealthStatus.CRITICAL
            self.results["components"][component]["error"] = str(e)

    async def _check_taskmaster_installation(self):
        """Check Task-Master AI installation and configuration."""
        component = "taskmaster"
        self.results["components"][component] = {
            "status": HealthStatus.HEALTHY,
            "installation": {},
            "configuration": {},
            "providers": {},
            "issues": []
        }

        try:
            # Check if task-master-ai is installed
            try:
                proc = await asyncio.create_subprocess_exec(
                    "npx", "-y", "--package=task-master-ai", "task-master-ai", "--version",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await proc.communicate()

                if proc.returncode == 0:
                    self.results["components"][component]["installation"]["status"] = HealthStatus.HEALTHY
                    self.results["components"][component]["installation"]["version"] = stdout.decode().strip()
                else:
                    self.results["components"][component]["installation"]["status"] = HealthStatus.UNHEALTHY
                    self.results["components"][component]["issues"].append("Task-Master AI not accessible")

            except Exception as e:
                self.results["components"][component]["installation"]["status"] = HealthStatus.CRITICAL
                self.results["components"][component]["installation"]["error"] = str(e)

            # Check configuration
            taskmaster_dir = self.installation_dir / ".taskmaster"
            config_file = taskmaster_dir / "config.json"

            if config_file.exists():
                try:
                    with open(config_file, 'r') as f:
                        config_data = json.load(f)

                    self.results["components"][component]["configuration"]["status"] = HealthStatus.HEALTHY
                    self.results["components"][component]["configuration"]["providers_count"] = len(
                        config_data.get("providers", {})
                    )

                    # Check configured providers
                    providers = config_data.get("providers", {})
                    for provider, provider_config in providers.items():
                        has_api_key = bool(provider_config.get("apiKey", "").strip())
                        self.results["components"][component]["providers"][provider] = {
                            "configured": has_api_key,
                            "model": provider_config.get("model", "unknown")
                        }

                    if not providers:
                        self.results["components"][component]["status"] = HealthStatus.WARNING
                        self.results["components"][component]["issues"].append("No AI providers configured")

                except Exception as e:
                    self.results["components"][component]["configuration"]["status"] = HealthStatus.UNHEALTHY
                    self.results["components"][component]["configuration"]["error"] = str(e)

            else:
                self.results["components"][component]["configuration"]["status"] = HealthStatus.WARNING
                self.results["components"][component]["issues"].append("Task-Master configuration not found")

        except Exception as e:
            self.results["components"][component]["status"] = HealthStatus.CRITICAL
            self.results["components"][component]["error"] = str(e)

    async def _check_mcp_integrations(self):
        """Check MCP integration functionality."""
        component = "mcp_integrations"
        self.results["components"][component] = {
            "status": HealthStatus.HEALTHY,
            "leantime_bridge": {},
            "taskmaster_bridge": {},
            "issues": []
        }

        try:
            # Test Leantime MCP bridge
            try:
                leantime_client = create_leantime_bridge(self.config)
                async with leantime_client:
                    health = await leantime_client.health_check()
                    self.results["components"][component]["leantime_bridge"] = health

                    if health.get("status") != "healthy":
                        self.results["components"][component]["issues"].append("Leantime MCP bridge unhealthy")
                        if self.results["components"][component]["status"] == HealthStatus.HEALTHY:
                            self.results["components"][component]["status"] = HealthStatus.WARNING

            except Exception as e:
                self.results["components"][component]["leantime_bridge"]["status"] = "error"
                self.results["components"][component]["leantime_bridge"]["error"] = str(e)
                self.results["components"][component]["issues"].append("Leantime MCP bridge failed")

            # Test Task-Master MCP bridge
            try:
                taskmaster_client = create_taskmaster_bridge(self.config)
                async with taskmaster_client:
                    health = await taskmaster_client.health_check()
                    self.results["components"][component]["taskmaster_bridge"] = health

                    if health.get("status") != "healthy":
                        self.results["components"][component]["issues"].append("Task-Master MCP bridge unhealthy")
                        if self.results["components"][component]["status"] == HealthStatus.HEALTHY:
                            self.results["components"][component]["status"] = HealthStatus.WARNING

            except Exception as e:
                self.results["components"][component]["taskmaster_bridge"]["status"] = "error"
                self.results["components"][component]["taskmaster_bridge"]["error"] = str(e)
                self.results["components"][component]["issues"].append("Task-Master MCP bridge failed")

        except Exception as e:
            self.results["components"][component]["status"] = HealthStatus.CRITICAL
            self.results["components"][component]["error"] = str(e)

    async def _check_sync_functionality(self):
        """Check synchronization between Leantime and Task-Master."""
        component = "sync_functionality"
        self.results["components"][component] = {
            "status": HealthStatus.HEALTHY,
            "sync_manager": {},
            "last_sync": {},
            "issues": []
        }

        try:
            # Test sync manager
            sync_manager = create_sync_manager(self.config)

            # Get sync status
            sync_status = await sync_manager.get_sync_status()
            self.results["components"][component]["sync_manager"] = sync_status

            # Check if sync is functional
            if not sync_status.get("leantime_status", {}).get("connected"):
                self.results["components"][component]["issues"].append("Leantime not connected to sync manager")
                self.results["components"][component]["status"] = HealthStatus.WARNING

            if not sync_status.get("taskmaster_status", {}).get("connected"):
                self.results["components"][component]["issues"].append("Task-Master not connected to sync manager")
                self.results["components"][component]["status"] = HealthStatus.WARNING

        except Exception as e:
            self.results["components"][component]["status"] = HealthStatus.UNHEALTHY
            self.results["components"][component]["error"] = str(e)

    async def _check_adhd_optimizations(self):
        """Check ADHD-specific optimizations and features."""
        component = "adhd_optimizations"
        self.results["components"][component] = {
            "status": HealthStatus.HEALTHY,
            "features": {},
            "issues": []
        }

        try:
            # Check environment configuration
            env_file = self.docker_dir / ".env"
            if env_file.exists():
                with open(env_file, 'r') as f:
                    env_content = f.read()

                adhd_features = {
                    "adhd_mode": "LEAN_ADHD_MODE=true" in env_content,
                    "notification_batching": "LEAN_NOTIFICATION_BATCH=true" in env_content,
                    "context_preservation": "LEAN_CONTEXT_PRESERVATION=true" in env_content
                }

                self.results["components"][component]["features"] = adhd_features

                enabled_features = sum(adhd_features.values())
                if enabled_features == 0:
                    self.results["components"][component]["status"] = HealthStatus.WARNING
                    self.results["components"][component]["issues"].append("No ADHD optimizations enabled")
                elif enabled_features < 3:
                    self.results["components"][component]["status"] = HealthStatus.WARNING
                    self.results["components"][component]["issues"].append("Some ADHD optimizations not enabled")

            else:
                self.results["components"][component]["status"] = HealthStatus.WARNING
                self.results["components"][component]["issues"].append("Environment configuration not found")

        except Exception as e:
            self.results["components"][component]["status"] = HealthStatus.UNHEALTHY
            self.results["components"][component]["error"] = str(e)

    async def _collect_performance_metrics(self):
        """Collect performance and usage metrics."""
        try:
            docker_client = docker.from_env()

            # Container resource usage
            containers = docker_client.containers.list(filters={"name": "*leantime*"})

            for container in containers:
                try:
                    stats = container.stats(stream=False)
                    cpu_usage = self._calculate_cpu_percentage(stats)
                    memory_usage = self._calculate_memory_usage(stats)

                    self.results["metrics"][container.name] = {
                        "cpu_percentage": cpu_usage,
                        "memory_usage_mb": memory_usage,
                        "status": container.status
                    }

                except Exception:
                    pass

            # Disk usage
            try:
                import shutil
                disk_usage = shutil.disk_usage(self.installation_dir)
                self.results["metrics"]["disk"] = {
                    "total_gb": disk_usage.total / (1024**3),
                    "used_gb": (disk_usage.total - disk_usage.free) / (1024**3),
                    "free_gb": disk_usage.free / (1024**3)
                }
            except Exception:
                pass

        except Exception as e:
            logger.warning(f"Failed to collect performance metrics: {e}")

    def _calculate_cpu_percentage(self, stats: Dict) -> float:
        """Calculate CPU usage percentage from Docker stats."""
        try:
            cpu_stats = stats["cpu_stats"]
            precpu_stats = stats["precpu_stats"]

            cpu_usage = cpu_stats["cpu_usage"]["total_usage"] - precpu_stats["cpu_usage"]["total_usage"]
            system_usage = cpu_stats["system_cpu_usage"] - precpu_stats["system_cpu_usage"]

            if system_usage > 0:
                return (cpu_usage / system_usage) * len(cpu_stats["cpu_usage"]["percpu_usage"]) * 100
            return 0.0

        except (KeyError, ZeroDivisionError):
            return 0.0

    def _calculate_memory_usage(self, stats: Dict) -> float:
        """Calculate memory usage in MB from Docker stats."""
        try:
            memory_usage = stats["memory_stats"]["usage"]
            return memory_usage / (1024 * 1024)  # Convert to MB

        except KeyError:
            return 0.0

    def _get_leantime_url(self) -> str:
        """Get Leantime URL from configuration."""
        # Try to read from .env file
        env_file = self.docker_dir / ".env"
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    if line.startswith("LEAN_APP_URL="):
                        return line.split("=", 1)[1].strip()

        # Default fallback
        return "http://localhost:8080"

    def _calculate_overall_status(self):
        """Calculate overall system status based on component statuses."""
        component_statuses = [
            comp["status"] for comp in self.results["components"].values()
        ]

        if HealthStatus.CRITICAL in component_statuses:
            self.results["overall_status"] = HealthStatus.CRITICAL
        elif HealthStatus.UNHEALTHY in component_statuses:
            self.results["overall_status"] = HealthStatus.UNHEALTHY
        elif HealthStatus.WARNING in component_statuses:
            self.results["overall_status"] = HealthStatus.WARNING
        else:
            self.results["overall_status"] = HealthStatus.HEALTHY

    def _generate_recommendations(self):
        """Generate actionable recommendations based on health check results."""
        recommendations = []

        for component_name, component_data in self.results["components"].items():
            status = component_data.get("status")
            issues = component_data.get("issues", [])

            if status == HealthStatus.CRITICAL:
                if component_name == "docker_environment":
                    recommendations.append({
                        "priority": "high",
                        "component": component_name,
                        "action": "Restart Docker services",
                        "command": "cd docker/leantime && docker-compose up -d"
                    })
                elif component_name == "leantime_service":
                    recommendations.append({
                        "priority": "high",
                        "component": component_name,
                        "action": "Check Leantime container logs",
                        "command": "cd docker/leantime && docker-compose logs leantime"
                    })

            elif status == HealthStatus.UNHEALTHY:
                if component_name == "taskmaster" and "not accessible" in str(issues):
                    recommendations.append({
                        "priority": "medium",
                        "component": component_name,
                        "action": "Reinstall Task-Master AI",
                        "command": "npm install -g task-master-ai"
                    })

            elif status == HealthStatus.WARNING:
                if component_name == "adhd_optimizations":
                    recommendations.append({
                        "priority": "low",
                        "component": component_name,
                        "action": "Enable ADHD optimizations in .env file",
                        "details": "Set LEAN_ADHD_MODE=true, LEAN_NOTIFICATION_BATCH=true, LEAN_CONTEXT_PRESERVATION=true"
                    })

        self.results["recommendations"] = recommendations

    def format_results(self, verbose: bool = False) -> str:
        """Format health check results for display."""
        output = []

        # Header
        overall_emoji = HealthStatus.get_emoji(self.results["overall_status"])
        output.append(f"\n{overall_emoji} DOPEMUX LEANTIME HEALTH CHECK")
        output.append("=" * 50)
        output.append(f"Overall Status: {self.results['overall_status'].upper()}")
        output.append(f"Timestamp: {self.results['timestamp']}")

        # Component statuses
        output.append(f"\n📊 COMPONENT STATUS")
        output.append("-" * 30)

        for component_name, component_data in self.results["components"].items():
            status = component_data.get("status", HealthStatus.UNKNOWN)
            emoji = HealthStatus.get_emoji(status)
            name = component_name.replace("_", " ").title()

            output.append(f"{emoji} {name}: {status}")

            if verbose and component_data.get("issues"):
                for issue in component_data["issues"]:
                    output.append(f"   ⚠️ {issue}")

        # Recommendations
        if self.results.get("recommendations"):
            output.append(f"\n💡 RECOMMENDATIONS")
            output.append("-" * 30)

            for rec in self.results["recommendations"]:
                priority_emoji = "🚨" if rec["priority"] == "high" else "⚠️" if rec["priority"] == "medium" else "💡"
                output.append(f"{priority_emoji} {rec['action']}")

                if rec.get("command"):
                    output.append(f"   Command: {rec['command']}")
                if rec.get("details"):
                    output.append(f"   Details: {rec['details']}")

        # Performance metrics
        if verbose and self.results.get("metrics"):
            output.append(f"\n📈 PERFORMANCE METRICS")
            output.append("-" * 30)

            for metric_name, metric_data in self.results["metrics"].items():
                if isinstance(metric_data, dict):
                    output.append(f"{metric_name}:")
                    for key, value in metric_data.items():
                        if isinstance(value, float):
                            output.append(f"  {key}: {value:.2f}")
                        else:
                            output.append(f"  {key}: {value}")

        output.append("")
        return "\n".join(output)


# CLI interface
@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Show detailed diagnostics')
@click.option('--json-output', '-j', is_flag=True, help='Output results as JSON')
@click.option('--no-integration', is_flag=True, help='Skip MCP integration tests')
@click.option('--output-file', '-o', help='Save results to file')
def main(verbose, json_output, no_integration, output_file):
    """Dopemux Leantime & Task-Master Health Check."""

    async def run_health_check():
        checker = DopemuxHealthChecker()
        results = await checker.run_health_check(
            verbose=verbose,
            check_integration=not no_integration
        )

        if json_output:
            output = json.dumps(results, indent=2, default=str)
        else:
            output = checker.format_results(verbose=verbose)

        if output_file:
            with open(output_file, 'w') as f:
                f.write(output)
            click.echo(f"✅ Results saved to {output_file}")
        else:
            click.echo(output)

        # Exit with appropriate code
        overall_status = results.get("overall_status", HealthStatus.UNKNOWN)
        if overall_status in [HealthStatus.CRITICAL, HealthStatus.UNHEALTHY]:
            sys.exit(1)
        elif overall_status == HealthStatus.WARNING:
            sys.exit(2)
        else:
            sys.exit(0)

    try:
        asyncio.run(run_health_check())
    except KeyboardInterrupt:
        click.echo("\n❌ Health check cancelled by user")
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Health check failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()