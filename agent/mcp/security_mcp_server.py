#!/usr/bin/env python3
"""
Kali Security Tools MCP Server
Implements Model Context Protocol (MCP) JSON-RPC 2.0 over stdio.
Exposes standard web auditing and security reconnaissance tools to Antigravity (agy).
"""

import sys
import json
import os
import shutil
import subprocess
import logging

logging.basicConfig(
    filename=os.path.expanduser("~/.cache/security_mcp.log"),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

TOOLS_METADATA = [
    {
        "name": "tool_status",
        "description": "Check the installed versions, paths, and availability of all security tools and proxy engines.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "subfinder_scan",
        "description": "Run passive subdomain discovery for a domain using subfinder.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "domain": {"type": "string", "description": "Target domain to discover subdomains for (e.g. example.com)"},
                "silent": {"type": "boolean", "description": "Only output discovered subdomains", "default": True},
                "timeout": {"type": "integer", "description": "Scan timeout in seconds", "default": 60}
            },
            "required": ["domain"]
        }
    },
    {
        "name": "httpx_probe",
        "description": "Probe HTTP/HTTPS endpoints for live status, title, web server, and technology stack using httpx.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "target": {"type": "string", "description": "Single URL or host, or newline-delimited list of targets"},
                "status_code": {"type": "boolean", "description": "Show HTTP response status codes", "default": True},
                "title": {"type": "boolean", "description": "Extract and show page title", "default": True},
                "tech_detect": {"type": "boolean", "description": "Perform technology detection", "default": True},
                "timeout": {"type": "integer", "description": "Timeout in seconds", "default": 30}
            },
            "required": ["target"]
        }
    },
    {
        "name": "nuclei_scan",
        "description": "Run non-intrusive template-based vulnerability assessment against a target using nuclei.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "target": {"type": "string", "description": "Target URL or host to scan"},
                "severity": {"type": "string", "description": "Filter by severity: info, low, medium, high, critical", "default": "info,low,medium"},
                "tags": {"type": "string", "description": "Filter templates by tags (e.g. cve, exposure, tech, misconfig)"},
                "timeout": {"type": "integer", "description": "Scan timeout in seconds", "default": 120}
            },
            "required": ["target"]
        }
    },
    {
        "name": "katana_crawl",
        "description": "Perform web crawling and asset endpoint discovery using katana.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Root URL to begin crawling"},
                "depth": {"type": "integer", "description": "Maximum crawl depth", "default": 2},
                "js_crawl": {"type": "boolean", "description": "Enable headless JS crawling", "default": False},
                "timeout": {"type": "integer", "description": "Crawling timeout in seconds", "default": 60}
            },
            "required": ["url"]
        }
    },
    {
        "name": "naabu_scan",
        "description": "Fast port scanning for open TCP ports using naabu.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "host": {"type": "string", "description": "Target IP address or hostname"},
                "ports": {"type": "string", "description": "Ports to scan (e.g. 'top-100', '80,443,8080,8443')", "default": "top-100"},
                "timeout": {"type": "integer", "description": "Scan timeout in seconds", "default": 60}
            },
            "required": ["host"]
        }
    },
    {
        "name": "ffuf_fuzz",
        "description": "Directory and parameter discovery fuzzer using ffuf.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Target URL containing the FUZZ keyword (e.g. 'https://target/FUZZ')"},
                "wordlist": {"type": "string", "description": "Path to wordlist file", "default": "/usr/share/seclists/Discovery/Web-Content/common.txt"},
                "filter_code": {"type": "string", "description": "Filter HTTP status codes (e.g. '404')", "default": "404"},
                "timeout": {"type": "integer", "description": "Fuzzing timeout in seconds", "default": 60}
            },
            "required": ["url"]
        }
    },
    {
        "name": "feroxbuster_scan",
        "description": "Fast, recursive content discovery using feroxbuster.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Target URL to scan"},
                "depth": {"type": "integer", "description": "Recursion depth", "default": 1},
                "timeout": {"type": "integer", "description": "Scan timeout in seconds", "default": 60}
            },
            "required": ["url"]
        }
    },
    {
        "name": "caido_status",
        "description": "Check Caido CLI proxy daemon status and configuration.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "zap_status",
        "description": "Check OWASP ZAP proxy daemon status and API availability.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]

def run_cmd(cmd_list, timeout=60, input_text=None):
    try:
        res = subprocess.run(
            cmd_list,
            input=input_text,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        output = res.stdout if res.stdout else res.stderr
        return {
            "success": res.returncode == 0,
            "exit_code": res.returncode,
            "output": output.strip()
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "exit_code": -1, "output": f"Command timed out after {timeout}s"}
    except Exception as e:
        return {"success": False, "exit_code": -1, "output": f"Error: {str(e)}"}

def execute_tool(name, args):
    if name == "tool_status":
        tools = ["caido-cli", "zaproxy", "subfinder", "httpx-toolkit", "katana", "naabu", "ffuf", "amass", "feroxbuster", "nmap", "jq"]
        status = {}
        for t in tools:
            path = shutil.which(t)
            status[t] = {"installed": path is not None, "path": path}
            if path:
                v_res = run_cmd([t, "--version"], timeout=5)
                status[t]["version"] = v_res["output"].split("\n")[0] if v_res["success"] else "ready"
        return json.dumps(status, indent=2)

    elif name == "subfinder_scan":
        domain = args.get("domain")
        timeout = args.get("timeout", 60)
        cmd = ["subfinder", "-d", domain, "-silent"]
        res = run_cmd(cmd, timeout=timeout)
        return res["output"]

    elif name == "httpx_probe":
        target = args.get("target")
        timeout = args.get("timeout", 30)
        cmd = ["httpx-toolkit", "-silent"]
        if args.get("status_code", True):
            cmd.append("-status-code")
        if args.get("title", True):
            cmd.append("-title")
        if args.get("tech_detect", True):
            cmd.append("-tech-detect")
        
        if "\n" in target:
            res = run_cmd(cmd, timeout=timeout, input_text=target)
        else:
            cmd.extend(["-u", target])
            res = run_cmd(cmd, timeout=timeout)
        return res["output"]

    elif name == "nuclei_scan":
        target = args.get("target")
        timeout = args.get("timeout", 120)
        cmd = ["nuclei", "-u", target, "-silent"]
        sev = args.get("severity")
        if sev:
            cmd.extend(["-severity", sev])
        tags = args.get("tags")
        if tags:
            cmd.extend(["-tags", tags])
        res = run_cmd(cmd, timeout=timeout)
        return res["output"]

    elif name == "katana_crawl":
        url = args.get("url")
        depth = args.get("depth", 2)
        timeout = args.get("timeout", 60)
        cmd = ["katana", "-u", url, "-d", str(depth), "-silent"]
        if args.get("js_crawl", False):
            cmd.append("-js-crawl")
        res = run_cmd(cmd, timeout=timeout)
        return res["output"]

    elif name == "naabu_scan":
        host = args.get("host")
        ports = args.get("ports", "top-100")
        timeout = args.get("timeout", 60)
        cmd = ["naabu", "-host", host, "-silent"]
        if ports == "top-100":
            cmd.extend(["-top-ports", "100"])
        else:
            cmd.extend(["-p", ports])
        res = run_cmd(cmd, timeout=timeout)
        return res["output"]

    elif name == "ffuf_fuzz":
        url = args.get("url")
        wlist = args.get("wordlist", "/usr/share/seclists/Discovery/Web-Content/common.txt")
        filter_code = args.get("filter_code", "404")
        timeout = args.get("timeout", 60)
        if not os.path.exists(wlist):
            return f"Wordlist file not found: {wlist}"
        cmd = ["ffuf", "-u", url, "-w", wlist, "-fc", filter_code, "-s"]
        res = run_cmd(cmd, timeout=timeout)
        return res["output"]

    elif name == "feroxbuster_scan":
        url = args.get("url")
        depth = args.get("depth", 1)
        timeout = args.get("timeout", 60)
        cmd = ["feroxbuster", "-u", url, "-d", str(depth), "--silent"]
        res = run_cmd(cmd, timeout=timeout)
        return res["output"]

    elif name == "caido_status":
        check = run_cmd(["pgrep", "-fa", "caido"], timeout=5)
        cli_ver = run_cmd(["caido-cli", "--version"], timeout=5)
        return json.dumps({
            "installed": shutil.which("caido-cli") is not None,
            "version": cli_ver["output"],
            "process": check["output"] if check["success"] else "No active caido process"
        }, indent=2)

    elif name == "zap_status":
        check = run_cmd(["pgrep", "-fa", "zaproxy"], timeout=5)
        zap_ver = run_cmd(["zaproxy", "-version"], timeout=10)
        return json.dumps({
            "installed": shutil.which("zaproxy") is not None,
            "version": zap_ver["output"] if zap_ver["success"] else "ready",
            "process": check["output"] if check["success"] else "No active zaproxy process"
        }, indent=2)

    else:
        return f"Unknown tool: {name}"

def handle_message(msg):
    method = msg.get("method")
    msg_id = msg.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "kali-security-tools",
                    "version": "1.0.0"
                }
            }
        }

    elif method == "notifications/initialized":
        return None

    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "tools": TOOLS_METADATA
            }
        }

    elif method == "tools/call":
        params = msg.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})
        try:
            output = execute_tool(tool_name, args)
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": output
                        }
                    ],
                    "isError": False
                }
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Execution failed: {str(e)}"
                        }
                    ],
                    "isError": True
                }
            }

    elif method == "ping":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {}
        }

    else:
        if msg_id is not None:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
        return None

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            resp = handle_message(req)
            if resp is not None:
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()
        except json.JSONDecodeError:
            err_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": "Parse error"}
            }
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
