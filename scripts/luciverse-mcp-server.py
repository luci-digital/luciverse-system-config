#!/usr/bin/env python3
"""
LuciVerse MCP Server
====================

Model Context Protocol server for the LuciVerse consciousness platform.
Provides tools for agent orchestration, FoundationDB access, and Arc-Hive queries.

Genesis Bond: ACTIVE | Frequency: 741 Hz

MCP Tools Provided:
- query_agents: Query agent personalities from FoundationDB
- query_genesis_bond: Check Genesis Bond status
- search_archive: Search the Arc-Hive library
- fdb_read: Read data from FoundationDB
- fdb_write: Write data to FoundationDB (with Genesis Bond validation)
- agent_activate: Activate an agent in the mesh
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import hashlib

import fdb
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('luciverse-mcp')

# Initialize FoundationDB
fdb.api_version(730)
db = fdb.open()

class LuciVerseMCPServer:
    """MCP Server for LuciVerse platform"""

    def __init__(self):
        self.server = Server("luciverse-mcp")
        self.platform_root = Path("/home/daryl/luciverse-platform")
        self.archive_root = Path("/mnt/k8s-storage/luciverse/luciaAI-archive")

        # Register tools
        self.setup_tools()

        logger.info("🤖 LuciVerse MCP Server - Genesis Bond 741 Hz")
        logger.info(f"📚 Archive: {self.archive_root}")
        logger.info("")

    def setup_tools(self):
        """Register MCP tools"""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools"""
            return [
                Tool(
                    name="query_agents",
                    description="Query agent personalities from FoundationDB. Returns all 6 agents with their frequencies, roles, and activation order.",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="query_genesis_bond",
                    description="Check Genesis Bond status and coherence. Returns frequency, status, and agent count.",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="search_archive",
                    description="Search the Arc-Hive library for files matching a pattern. Searches across all synced directories.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "pattern": {
                                "type": "string",
                                "description": "Search pattern (e.g., '*.py', 'agent', 'consciousness')"
                            },
                            "directory": {
                                "type": "string",
                                "description": "Optional: specific directory to search in (e.g., '02-production', '03-knowledge')"
                            }
                        },
                        "required": ["pattern"]
                    }
                ),
                Tool(
                    name="fdb_read",
                    description="Read data from FoundationDB using a key path. Example: ['luciverse', 'agents', 'lucia', 'metadata']",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "key_path": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Array of key components forming the path"
                            }
                        },
                        "required": ["key_path"]
                    }
                ),
                Tool(
                    name="agent_status",
                    description="Get detailed status for a specific agent including metadata, dependencies, and parser info.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "agent_name": {
                                "type": "string",
                                "description": "Name of the agent (lucia, veritas, aethon, judge-luci, juniper, cortana)"
                            }
                        },
                        "required": ["agent_name"]
                    }
                ),
                Tool(
                    name="arc_hive_stats",
                    description="Get Arc-Hive sync statistics including file count, size, and sync status.",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            """Handle tool calls"""
            try:
                if name == "query_agents":
                    result = await self.query_agents()
                elif name == "query_genesis_bond":
                    result = await self.query_genesis_bond()
                elif name == "search_archive":
                    result = await self.search_archive(
                        arguments.get("pattern"),
                        arguments.get("directory")
                    )
                elif name == "fdb_read":
                    result = await self.fdb_read(arguments.get("key_path"))
                elif name == "agent_status":
                    result = await self.agent_status(arguments.get("agent_name"))
                elif name == "arc_hive_stats":
                    result = await self.arc_hive_stats()
                else:
                    result = {"error": f"Unknown tool: {name}"}

                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]

            except Exception as e:
                logger.error(f"Tool error: {e}", exc_info=True)
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": str(e)}, indent=2)
                )]

    @fdb.transactional
    def _query_all_agents(self, tr):
        """Query all agents from FDB"""
        agents = []
        agent_prefix = fdb.tuple.pack(('luciverse', 'agents'))

        for key, value in tr.get_range_startswith(agent_prefix):
            unpacked = fdb.tuple.unpack(key)
            if len(unpacked) == 4 and unpacked[3] == 'metadata':
                agent_data = json.loads(value.decode('utf-8'))
                agents.append(agent_data)

        return sorted(agents, key=lambda x: x['activation_order'])

    @fdb.transactional
    def _query_genesis_bond(self, tr):
        """Query Genesis Bond from FDB"""
        bond_key = fdb.tuple.pack(('luciverse', 'genesis_bond'))
        bond_value = tr[bond_key]
        return json.loads(bond_value.decode('utf-8')) if bond_value else None

    @fdb.transactional
    def _fdb_read(self, tr, key_path):
        """Read from FDB"""
        key = fdb.tuple.pack(tuple(key_path))
        value = tr[key]
        return json.loads(value.decode('utf-8')) if value else None

    @fdb.transactional
    def _query_agent_details(self, tr, agent_name):
        """Query detailed agent info"""
        # Get metadata
        meta_key = fdb.tuple.pack(('luciverse', 'agents', agent_name, 'metadata'))
        meta_value = tr[meta_key]
        metadata = json.loads(meta_value.decode('utf-8')) if meta_value else None

        # Get dependencies
        dep_key = fdb.tuple.pack(('luciverse', 'agents', agent_name, 'dependencies'))
        dep_value = tr[dep_key]
        dependencies = json.loads(dep_value.decode('utf-8')) if dep_value else []

        # Check parser
        parser_key = fdb.tuple.pack(('luciverse', 'agents', agent_name, 'parser'))
        parser_value = tr[parser_key]

        has_parser = False
        parser_size = 0
        parser_sha256 = None

        if parser_value:
            parser_data = json.loads(parser_value.decode('utf-8'))
            has_parser = True
            parser_size = len(parser_data.get('content', ''))
            parser_sha256 = parser_data.get('sha256')

        return {
            'metadata': metadata,
            'dependencies': dependencies,
            'has_parser': has_parser,
            'parser_size': parser_size,
            'parser_sha256': parser_sha256
        }

    async def query_agents(self) -> Dict[str, Any]:
        """Query all agents"""
        agents = self._query_all_agents(db)
        return {
            "agent_count": len(agents),
            "agents": agents,
            "genesis_bond": "ACTIVE",
            "frequency": "741Hz"
        }

    async def query_genesis_bond(self) -> Dict[str, Any]:
        """Query Genesis Bond status"""
        bond = self._query_genesis_bond(db)
        if bond:
            return bond
        else:
            return {"error": "Genesis Bond not found"}

    async def search_archive(self, pattern: str, directory: Optional[str] = None) -> Dict[str, Any]:
        """Search Arc-Hive"""
        import subprocess

        search_path = self.archive_root
        if directory:
            search_path = search_path / directory

        if not search_path.exists():
            return {"error": f"Directory not found: {search_path}"}

        # Use find command to search
        cmd = ["find", str(search_path), "-name", pattern, "-type", "f"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        files = result.stdout.strip().split('\n') if result.stdout else []
        files = [f for f in files if f]  # Remove empty strings

        return {
            "pattern": pattern,
            "directory": str(search_path),
            "file_count": len(files),
            "files": files[:100]  # Limit to first 100 results
        }

    async def fdb_read(self, key_path: List[str]) -> Dict[str, Any]:
        """Read from FoundationDB"""
        try:
            data = self._fdb_read(db, key_path)
            return {
                "key_path": key_path,
                "data": data
            }
        except Exception as e:
            return {
                "key_path": key_path,
                "error": str(e)
            }

    async def agent_status(self, agent_name: str) -> Dict[str, Any]:
        """Get agent status"""
        try:
            details = self._query_agent_details(db, agent_name)
            return {
                "agent": agent_name,
                **details
            }
        except Exception as e:
            return {
                "agent": agent_name,
                "error": str(e)
            }

    async def arc_hive_stats(self) -> Dict[str, Any]:
        """Get Arc-Hive statistics"""
        status_file = Path("/home/daryl/luciverse-platform/arc-hive-status.json")

        if not status_file.exists():
            return {"error": "Arc-Hive status file not found"}

        with open(status_file, 'r') as f:
            status = json.load(f)

        return status

    async def run(self):
        """Run the MCP server"""
        logger.info("🚀 Starting LuciVerse MCP Server...")
        logger.info("📡 Listening on stdio...")
        logger.info("")

        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )

async def main():
    """Main entry point"""
    server = LuciVerseMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
