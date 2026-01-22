# Copyright (©) 2025, Alexander Suvorov. All rights reserved.
import ipaddress
import socket
import requests
from typing import Dict, Any, Tuple, List, Optional
from urllib.parse import urlparse
from datetime import datetime


class NetworkCheckResult:

    def __init__(self):
        self.is_online: bool = False
        self.timestamp: str = ""
        self.check_duration: float = 0.0
        self.detailed_results: List[Dict[str, Any]] = []
        self.recommendations: List[str] = []

    def __str__(self) -> str:
        status = "✅ Online" if self.is_online else "❌ Offline"
        return f"NetworkCheckResult({status}, checks={len(self.detailed_results)})"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_online": self.is_online,
            "timestamp": self.timestamp,
            "check_duration": self.check_duration,
            "detailed_results": self.detailed_results,
            "recommendations": self.recommendations
        }


class NetworkService:

    DEFAULT_CHECK_SERVERS = [
        {
            "name": "Google DNS",
            "url": "https://8.8.8.8",
            "description": "Google Public DNS"
        },
        {
            "name": "Cloudflare DNS",
            "url": "https://1.1.1.1",
            "description": "Cloudflare DNS"
        },
        {
            "name": "GitHub",
            "url": "https://api.github.com",
            "description": "GitHub API endpoint"
        },
        {
            "name": "Google",
            "url": "https://www.google.com",
            "description": "Google homepage"
        }
    ]

    def __init__(self, timeout: int = 3, check_servers: List[Dict[str, str]] = None):
        self.timeout = timeout
        self.check_servers = check_servers or self.DEFAULT_CHECK_SERVERS

    def check_network(self) -> NetworkCheckResult:
        import time

        result = NetworkCheckResult()
        result.timestamp = datetime.now().isoformat()
        start_time = time.time()

        successful_checks = 0

        for server in self.check_servers:
            check_result = self._check_single_server(server)
            result.detailed_results.append(check_result)

            if check_result["success"]:
                successful_checks += 1

        result.is_online = successful_checks > 0
        result.check_duration = time.time() - start_time

        if not result.is_online:
            result.recommendations = [
                "Check your internet connection,"
                "Make sure your network cable is connected (if using a wired connection),"
                "Check your Wi-Fi settings (if using a wireless connection),"
                "Try restarting your router,"
                "Check your firewall settings,"
                "If using a VPN, make sure it's connected."
            ]

        return result

    def is_online(self) -> bool:
        try:
            response = requests.get("https://8.8.8.8", timeout=self.timeout)
            return response.status_code < 500
        except Exception as e:
            print(e)
            return self._fallback_check()

    def check_git_connectivity(self) -> Tuple[bool, str]:
        git_servers = [
            ("GitHub", "https://github.com"),
            ("GitLab", "https://gitlab.com"),
            ("Bitbucket", "https://bitbucket.org")
        ]

        results = []
        for name, url in git_servers:
            success, message = self._check_server(url, name)
            results.append((name, success, message))

            if success:
                return True, f"Connection to {name} is working"

        error_details = ", ".join([f"{name}: {msg}" for name, success, msg in results if not success])
        return False, f"Unable to connect to Git servers: {error_details}"

    def check_dns_resolution(self, hostname: str = "github.com") -> Tuple[bool, str, List[str]]:
        try:
            import socket

            ip_addresses = []
            try:
                addr_info = socket.getaddrinfo(hostname, None)
                for info in addr_info:
                    ip = info[4][0]
                    if ip not in ip_addresses:
                        ip_addresses.append(ip)
            except socket.gaierror:
                pass

            if ip_addresses:
                return True, f"DNS resolution works for {hostname}", ip_addresses
            else:
                return False, f"Failed to resolve {hostname}", []

        except Exception as e:
            return False, f"DNS check error: {str(e)}", []

    def get_network_info(self) -> Dict[str, Any]:
        try:
            import socket
            import psutil

            network_info = {
                "hostname": socket.gethostname(),
                "ip_address": socket.gethostbyname(socket.gethostname()),
                "interfaces": []
            }

            for interface, addrs in psutil.net_if_addrs().items():
                interface_info = {
                    "interface": interface,
                    "addresses": []
                }

                for addr in addrs:
                    if addr.family.name == 'AF_INET' or addr.family.name == 'AF_INET6':
                        interface_info["addresses"].append({
                            "family": addr.family.name,
                            "address": addr.address,
                            "netmask": addr.netmask
                        })

                network_info["interfaces"].append(interface_info)

            return network_info

        except ImportError:
            import socket
            return {
                "hostname": socket.gethostname(),
                "ip_address": socket.gethostbyname(socket.gethostname()),
                "note": "Install psutil for detailed network information"
            }
        except Exception as e:
            return {"error": str(e)}

    def _check_single_server(self, server: Dict[str, str]) -> Dict[str, Any]:
        start_time = datetime.now()

        try:
            response = requests.get(
                server["url"],
                timeout=self.timeout,
                headers={"User-Agent": "SmartGitCore/1.0.0"}
            )

            duration = (datetime.now() - start_time).total_seconds()

            return {
                "name": server["name"],
                "url": server["url"],
                "description": server.get("description", ""),
                "success": response.status_code < 500,
                "status_code": response.status_code,
                "response_time": duration,
                "timestamp": start_time.isoformat(),
                "error": None
            }

        except requests.exceptions.Timeout:
            duration = (datetime.now() - start_time).total_seconds()
            return {
                "name": server["name"],
                "url": server["url"],
                "description": server.get("description", ""),
                "success": False,
                "status_code": None,
                "response_time": duration,
                "timestamp": start_time.isoformat(),
                "error": "Timeout"
            }

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            return {
                "name": server["name"],
                "url": server["url"],
                "description": server.get("description", ""),
                "success": False,
                "status_code": None,
                "response_time": duration,
                "timestamp": start_time.isoformat(),
                "error": str(e)
            }

    def _fallback_check(self) -> bool:
        fallback_methods = [
            self._check_with_socket,
            self._check_with_ping,
            self._check_dns_resolution_fallback
        ]

        for method in fallback_methods:
            try:
                if method():
                    return True
            except Exception as e:
                print(e)
                continue

        return False

    def _check_with_socket(self) -> bool:
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=self.timeout)
            return True
        except Exception as e:
            print(e)
            return False

    def _check_with_ping(self) -> bool:
        import platform
        import subprocess

        param = "-n" if platform.system().lower() == "windows" else "-c"
        command = ["ping", param, "1", "8.8.8.8"]

        try:
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=self.timeout
            )
            return result.returncode == 0
        except Exception as e:
            print(e)
            return False

    def _check_dns_resolution_fallback(self) -> bool:
        try:
            socket.gethostbyname("google.com")
            return True
        except Exception as e:
            print(e)
            return False

    def _check_server(self, url: str, name: str) -> Tuple[bool, str]:
        try:
            parsed_url = urlparse(url)
            hostname = parsed_url.netloc or parsed_url.path

            dns_ok, dns_msg, _ = self.check_dns_resolution(hostname)
            if not dns_ok:
                return False, f"DNS error: {dns_msg}"

            response = requests.get(url, timeout=self.timeout)
            if response.status_code < 500:
                return True, f"Connected successfully"
            else:
                return False, f"HTTP {response.status_code}"

        except requests.exceptions.Timeout:
            return False, "Timeout"
        except Exception as e:
            return False, str(e)

    def get_external_ip(self) -> Optional[str]:
        ip_services = [
            "https://api.ipify.org",
            "https://icanhazip.com",
            "https://ident.me",
            "https://checkip.amazonaws.com",
            "https://ifconfig.me/ip"
        ]

        for service in ip_services:
            try:
                response = requests.get(service, timeout=3)
                if response.status_code == 200:
                    ip = response.text.strip()
                    if self.is_valid_ip(ip):
                        return ip
            except Exception as e:
                print(e)
                continue

        try:
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            if self.is_valid_ip(ip_address):
                return f"{ip_address} (local)"
        except Exception as e:
            print(e)
            pass

        return None

    @staticmethod
    def is_valid_ip(ip: str) -> bool:
        try:
            clean_ip = ip.split(' ')[0]
            ipaddress.ip_address(clean_ip)
            return True
        except ValueError:
            return False
