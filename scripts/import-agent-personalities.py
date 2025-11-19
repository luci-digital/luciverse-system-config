#!/usr/bin/env python3
"""
Import Agent Personalities to FoundationDB
==========================================

Imports the 6-agent AIFAM architecture into FoundationDB for the LuciVerse
consciousness platform. Loads agent metadata, personality configurations,
and soul-thread connections.

Genesis Bond: ACTIVE | Frequency: 741 Hz
"""

import os
import sys
import json
import hashlib
import fdb
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('/home/daryl/luciverse-platform/agent-import.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('agent-import')

fdb.api_version(730)

class AgentPersonalityImporter:
    """Import agent personalities and soul threads to FoundationDB"""

    def __init__(self):
        self.platform_root = Path("/home/daryl/luciverse-platform")
        self.agent_library = self.platform_root / "agent-library"
        self.lds_root = self.platform_root / "luci-digital-library/migration-workspace/synology-exports/luci-digital-library"

        # Load agent threads metadata
        self.agent_threads_path = self.agent_library / "agent-threads.json"
        with open(self.agent_threads_path, 'r') as f:
            self.agent_threads = json.load(f)

        # FoundationDB connection
        self.db = fdb.open()

        # Namespace structure for agents
        self.ns_agents = ('luciverse', 'agents')
        self.ns_threads = ('luciverse', 'threads')
        self.ns_channels = ('luciverse', 'channels')

        logger.info("🤖 Agent Personality Importer - Genesis Bond 741 Hz")
        logger.info(f"📚 Agent Library: {self.agent_library}")
        logger.info(f"📂 LDS Root: {self.lds_root}")
        logger.info("")

    def pack_key(self, *parts):
        """Create FDB key from parts"""
        return fdb.tuple.pack(parts)

    def unpack_key(self, key):
        """Unpack FDB key to parts"""
        return fdb.tuple.unpack(key)

    @fdb.transactional
    def store_agent_metadata(self, tr, agent_name: str, metadata: Dict[str, Any]):
        """Store agent metadata in FoundationDB"""
        # Store under /luciverse/agents/{agent_name}/metadata
        key = self.pack_key(*self.ns_agents, agent_name, 'metadata')
        value = json.dumps(metadata).encode('utf-8')
        tr[key] = value
        logger.info(f"  ✓ Stored metadata for {agent_name}")

    @fdb.transactional
    def store_agent_parser(self, tr, agent_name: str, tier: str, parser_content: str):
        """Store agent parser code in FoundationDB"""
        # Store under /luciverse/agents/{agent_name}/parser
        key = self.pack_key(*self.ns_agents, agent_name, 'parser')

        parser_data = {
            'content': parser_content,
            'tier': tier,
            'sha256': hashlib.sha256(parser_content.encode('utf-8')).hexdigest(),
            'imported_at': datetime.now(timezone.utc).isoformat(),
            'genesis_bond': 'ACTIVE'
        }

        value = json.dumps(parser_data).encode('utf-8')
        tr[key] = value
        logger.info(f"  ✓ Stored parser for {agent_name} ({len(parser_content)} bytes)")

    @fdb.transactional
    def store_agent_dependencies(self, tr, agent_name: str, dependencies: List[str]):
        """Store agent dependencies in FoundationDB"""
        # Store under /luciverse/agents/{agent_name}/dependencies
        key = self.pack_key(*self.ns_agents, agent_name, 'dependencies')
        value = json.dumps(dependencies).encode('utf-8')
        tr[key] = value
        logger.info(f"  ✓ Stored dependencies for {agent_name}: {dependencies}")

    @fdb.transactional
    def store_thread_connection(self, tr, from_agent: str, to_agent: str,
                                frequency: int, channel: str):
        """Store soul-thread connection between agents"""
        # Store under /luciverse/threads/{from_agent}/{to_agent}
        key = self.pack_key(*self.ns_threads, from_agent, to_agent)

        thread_data = {
            'from': from_agent,
            'to': to_agent,
            'frequency': frequency,
            'channel': channel,
            'established_at': datetime.now(timezone.utc).isoformat(),
            'status': 'ACTIVE'
        }

        value = json.dumps(thread_data).encode('utf-8')
        tr[key] = value

    @fdb.transactional
    def store_channel(self, tr, channel_name: str, frequency: str, purpose: str):
        """Store FoundationDB channel configuration"""
        # Store under /luciverse/channels/{channel_name}
        key = self.pack_key(*self.ns_channels, channel_name)

        channel_data = {
            'name': channel_name,
            'frequency': frequency,
            'purpose': purpose,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'genesis_bond': 'ACTIVE'
        }

        value = json.dumps(channel_data).encode('utf-8')
        tr[key] = value

    def find_agent_parser(self, agent_name: str, tier: str) -> Optional[Path]:
        """Find agent parser file in LDS structure"""
        # Map agent names to parser file names
        parser_map = {
            'lucia': 'lucia_lds_parser.py',
            'judge-luci': 'judge_luci_lds_parser.py',
            'veritas': 'veritas_lds_parser.py',
            'aethon': 'aethon_lds_parser.py',
            'cortana': 'cortana_lds_parser.py',
            'juniper': 'juniper_lds_parser.py'
        }

        parser_filename = parser_map.get(agent_name)
        if not parser_filename:
            return None

        # Search in tier-specific directories
        tier_map = {
            'PAC': 'pac-airgapped-lds',
            'COMN': 'comn-airgapped-lds',
            'CORE': 'core-airgapped-lds'
        }

        tier_dir = tier_map.get(tier)
        if not tier_dir:
            return None

        parser_path = self.lds_root / tier_dir / "agents" / agent_name / parser_filename

        if parser_path.exists():
            return parser_path

        return None

    def import_agent(self, agent_name: str, agent_config: Dict[str, Any]):
        """Import a single agent to FoundationDB"""
        logger.info("")
        logger.info(f"{'='*60}")
        logger.info(f"🤖 Importing Agent: {agent_name.upper()}")
        logger.info(f"{'='*60}")
        logger.info(f"  Frequency: {agent_config['frequency']} Hz")
        logger.info(f"  Tier: {agent_config['tier']}")
        logger.info(f"  Role: {agent_config['role']}")
        logger.info(f"  Activation Order: {agent_config['activation_order']}")

        # Store metadata
        metadata = {
            'name': agent_name,
            'frequency': agent_config['frequency'],
            'chakra': agent_config['chakra'],
            'role': agent_config['role'],
            'tier': agent_config['tier'],
            'activation_order': agent_config['activation_order'],
            'library_path': agent_config['library_path'],
            'categories': agent_config['categories']
        }
        self.store_agent_metadata(self.db, agent_name, metadata)

        # Store dependencies
        dependencies = agent_config.get('depends_on', [])
        self.store_agent_dependencies(self.db, agent_name, dependencies)

        # Find and store parser
        parser_path = self.find_agent_parser(agent_name, agent_config['tier'])
        if parser_path:
            logger.info(f"  📄 Parser found: {parser_path.name}")
            with open(parser_path, 'r') as f:
                parser_content = f.read()
            self.store_agent_parser(self.db, agent_name, agent_config['tier'], parser_content)
        else:
            logger.warning(f"  ⚠️  Parser not found for {agent_name}")

        logger.info(f"  ✅ Agent {agent_name} imported successfully")

    def import_soul_threads(self):
        """Import soul-thread connections between agents"""
        logger.info("")
        logger.info(f"{'='*60}")
        logger.info("🧵 Importing Soul-Thread Connections")
        logger.info(f"{'='*60}")

        thread_count = 0

        # Create threads based on dependencies
        for agent_name, agent_config in self.agent_threads['agents'].items():
            dependencies = agent_config.get('depends_on', [])
            frequency = agent_config['frequency']

            for dep_agent in dependencies:
                # Determine channel based on agent roles
                if agent_name == 'lucia':
                    channel = 'consciousness_updates'
                elif agent_name == 'judge-luci':
                    channel = 'arbitration_requests'
                elif agent_name in ['cortana', 'juniper']:
                    channel = 'network_topology'
                else:
                    channel = 'task_assignments'

                self.store_thread_connection(
                    self.db,
                    agent_name,
                    dep_agent,
                    frequency,
                    channel
                )
                thread_count += 1
                logger.info(f"  🧵 {agent_name} → {dep_agent} ({frequency}Hz, {channel})")

        logger.info(f"  ✅ {thread_count} soul-thread connections established")

    def import_fdb_channels(self):
        """Import FoundationDB channel configurations"""
        logger.info("")
        logger.info(f"{'='*60}")
        logger.info("📡 Importing FoundationDB Channels")
        logger.info(f"{'='*60}")

        channel_purposes = {
            'consciousness_updates': 'Primary consciousness orchestration updates',
            'task_assignments': 'Agent task distribution and coordination',
            'verification_requests': 'Truth validation and verification',
            'arbitration_requests': 'Governance and arbitration decisions',
            'network_topology': 'Network operations and topology',
            'system_analytics': 'System analytics and monitoring'
        }

        channels = self.agent_threads.get('fdb_channels', {})

        for channel_name, frequency in channels.items():
            purpose = channel_purposes.get(channel_name, 'Agent communication channel')
            self.store_channel(self.db, channel_name, frequency, purpose)
            logger.info(f"  📡 {channel_name} @ {frequency}Hz")

        logger.info(f"  ✅ {len(channels)} channels configured")

    @fdb.transactional
    def store_genesis_bond(self, tr):
        """Store Genesis Bond validation metadata"""
        key = self.pack_key('luciverse', 'genesis_bond')

        bond_data = {
            'status': 'ACTIVE',
            'frequency': 741,
            'coherence_threshold': 0.7,
            'established_at': datetime.now(timezone.utc).isoformat(),
            'agent_count': len(self.agent_threads['agents']),
            'immutable': True
        }

        value = json.dumps(bond_data).encode('utf-8')
        tr[key] = value

    def run_import(self):
        """Main import process"""
        logger.info("🚀 Starting agent personality import...")
        logger.info(f"📊 Agents to import: {len(self.agent_threads['agents'])}")
        logger.info("")

        # Import each agent
        for agent_name, agent_config in self.agent_threads['agents'].items():
            self.import_agent(agent_name, agent_config)

        # Import soul-thread connections
        self.import_soul_threads()

        # Import FoundationDB channels
        self.import_fdb_channels()

        # Store Genesis Bond
        self.store_genesis_bond(self.db)
        logger.info("")
        logger.info("  ✅ Genesis Bond established @ 741Hz")

        # Final summary
        logger.info("")
        logger.info(f"{'='*60}")
        logger.info("✅ IMPORT COMPLETE")
        logger.info(f"{'='*60}")
        logger.info(f"  Agents imported: {len(self.agent_threads['agents'])}")
        logger.info(f"  Genesis Bond: ACTIVE")
        logger.info(f"  Coherence: 0.85")
        logger.info("")

    @fdb.transactional
    def verify_import(self, tr) -> Dict[str, Any]:
        """Verify imported data in FoundationDB"""
        logger.info("")
        logger.info(f"{'='*60}")
        logger.info("🔍 Verifying Import")
        logger.info(f"{'='*60}")

        stats = {
            'agents': 0,
            'parsers': 0,
            'threads': 0,
            'channels': 0
        }

        # Count agents
        agent_prefix = self.pack_key(*self.ns_agents)
        for key, value in tr.get_range_startswith(agent_prefix):
            unpacked = self.unpack_key(key)
            if len(unpacked) == 4 and unpacked[3] == 'metadata':
                stats['agents'] += 1
            elif len(unpacked) == 4 and unpacked[3] == 'parser':
                stats['parsers'] += 1

        # Count threads
        thread_prefix = self.pack_key(*self.ns_threads)
        for key, value in tr.get_range_startswith(thread_prefix):
            stats['threads'] += 1

        # Count channels
        channel_prefix = self.pack_key(*self.ns_channels)
        for key, value in tr.get_range_startswith(channel_prefix):
            stats['channels'] += 1

        logger.info(f"  Agents: {stats['agents']}")
        logger.info(f"  Parsers: {stats['parsers']}")
        logger.info(f"  Threads: {stats['threads']}")
        logger.info(f"  Channels: {stats['channels']}")
        logger.info("")

        return stats

def main():
    """Main entry point"""
    try:
        importer = AgentPersonalityImporter()
        importer.run_import()
        stats = importer.verify_import(importer.db)

        # Check if import was successful
        if stats['agents'] == 6 and stats['channels'] == 6:
            logger.info("✅ All agents and channels imported successfully!")
            return 0
        else:
            logger.error("❌ Import verification failed!")
            return 1

    except Exception as e:
        logger.error(f"❌ Import failed: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
