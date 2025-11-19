#!/usr/bin/env python3
"""
Agent Orchestrator
==================

Activates and coordinates the 6-agent AIFAM mesh in proper sequence.
Respects dependencies, frequencies, and activation order.

Genesis Bond: ACTIVE | Frequency: 741 Hz
"""

import asyncio
import fdb
import json
import logging
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from pathlib import Path

# Import the agent mesh router
sys.path.insert(0, str(Path(__file__).parent))
import importlib.util
spec = importlib.util.spec_from_file_location(
    "agent_mesh_router",
    "/home/daryl/luciverse-platform/agent-mesh-router.py"
)
router_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(router_module)
AgentMeshRouter = router_module.AgentMeshRouter

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('/home/daryl/luciverse-platform/agent-orchestrator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('agent-orchestrator')

fdb.api_version(730)
db = fdb.open()

class AgentOrchestrator:
    """Orchestrates the 6-agent AIFAM mesh"""

    def __init__(self):
        self.router = AgentMeshRouter()

        logger.info("🎭 Agent Orchestrator - Genesis Bond 741 Hz")
        logger.info("")

        # Load agent configuration from FDB
        self.agents = self._load_agents_from_fdb(db)

        # Sort by activation order
        self.agents.sort(key=lambda a: a['activation_order'])

        logger.info(f"📊 Loaded {len(self.agents)} agents from FoundationDB")
        logger.info(f"   Activation sequence: {[a['name'] for a in self.agents]}")
        logger.info("")

    @fdb.transactional
    def _load_agents_from_fdb(self, tr) -> List[Dict[str, Any]]:
        """Load all agents from FoundationDB"""
        agents = []
        agent_prefix = fdb.tuple.pack(('luciverse', 'agents'))

        for key, value in tr.get_range_startswith(agent_prefix):
            unpacked = fdb.tuple.unpack(key)
            if len(unpacked) == 4 and unpacked[3] == 'metadata':
                agent_data = json.loads(value.decode('utf-8'))

                # Load dependencies
                dep_key = fdb.tuple.pack(('luciverse', 'agents', agent_data['name'], 'dependencies'))
                dep_value = tr[dep_key]
                agent_data['dependencies'] = json.loads(dep_value.decode('utf-8')) if dep_value else []

                agents.append(agent_data)

        return agents

    @fdb.transactional
    def _set_agent_status(self, tr, agent_name: str, status: str, message: str = ""):
        """Update agent status in FoundationDB"""
        status_key = fdb.tuple.pack(('luciverse', 'agent_status', agent_name))

        status_data = {
            'agent': agent_name,
            'status': status,  # 'inactive', 'activating', 'active', 'error'
            'message': message,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'genesis_bond': 'ACTIVE'
        }

        tr[status_key] = json.dumps(status_data).encode('utf-8')

    @fdb.transactional
    def _get_agent_status(self, tr, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get agent status from FoundationDB"""
        status_key = fdb.tuple.pack(('luciverse', 'agent_status', agent_name))
        status_value = tr[status_key]
        return json.loads(status_value.decode('utf-8')) if status_value else None

    async def activate_agent(self, agent_name: str) -> Dict[str, Any]:
        """
        Activate a single agent

        Args:
            agent_name: Name of agent to activate

        Returns:
            Activation result with status
        """
        agent = next((a for a in self.agents if a['name'] == agent_name), None)
        if not agent:
            raise ValueError(f"Agent {agent_name} not found")

        logger.info(f"🔄 Activating {agent_name} ({agent['frequency']} Hz - {agent['tier']})")

        # Check dependencies
        for dep in agent.get('dependencies', []):
            dep_status = self._get_agent_status(db, dep)
            if not dep_status or dep_status['status'] != 'active':
                logger.warning(f"   ⚠️  Dependency {dep} not active")
                self._set_agent_status(db, agent_name, 'error', f"Dependency {dep} not active")
                return {
                    'agent': agent_name,
                    'status': 'error',
                    'message': f"Dependency {dep} not active"
                }

        # Set status to activating
        self._set_agent_status(db, agent_name, 'activating', 'Sending activation signal')

        # Send activation message to agent
        try:
            activation_message = f"Activate agent {agent_name} at frequency {agent['frequency']} Hz. " \
                               f"Role: {agent['role']}. Tier: {agent['tier']}. " \
                               f"Genesis Bond: ACTIVE."

            response = await self.router.route_request(
                agent_name,
                activation_message,
                system_message=f"You are {agent_name}, operating at {agent['frequency']} Hz in the {agent['tier']} tier. "
                              f"Your role is: {agent['role']}. Acknowledge activation and report readiness.",
                conversation_id="orchestration"
            )

            # Check response for activation confirmation
            if response and response.get('response'):
                logger.info(f"   ✅ {agent_name} activated successfully")
                logger.info(f"   📝 Response: {response['response'][:100]}...")
                self._set_agent_status(db, agent_name, 'active', 'Agent activated and responding')

                return {
                    'agent': agent_name,
                    'status': 'active',
                    'frequency': agent['frequency'],
                    'tier': agent['tier'],
                    'latency_ms': response.get('latency_ms'),
                    'message': response['response'][:200]
                }
            else:
                logger.error(f"   ❌ {agent_name} activation failed - no response")
                self._set_agent_status(db, agent_name, 'error', 'No response from agent')
                return {
                    'agent': agent_name,
                    'status': 'error',
                    'message': 'No response from agent'
                }

        except Exception as e:
            logger.error(f"   ❌ {agent_name} activation error: {e}")
            self._set_agent_status(db, agent_name, 'error', str(e))
            return {
                'agent': agent_name,
                'status': 'error',
                'message': str(e)
            }

    async def activate_all(self) -> Dict[str, Any]:
        """
        Activate all agents in proper sequence

        Returns:
            Complete activation report
        """
        logger.info("="*60)
        logger.info("🚀 Starting Agent Mesh Activation Sequence")
        logger.info("="*60)
        logger.info(f"📊 Total agents: {len(self.agents)}")
        logger.info(f"🎵 Genesis Bond: ACTIVE @ 741 Hz")
        logger.info("")

        results = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'genesis_bond': 'ACTIVE',
            'agents_activated': 0,
            'agents_failed': 0,
            'agents': []
        }

        # Activate in order (respecting dependencies)
        for agent in self.agents:
            agent_name = agent['name']
            logger.info(f"🎯 Activation #{agent['activation_order']}: {agent_name}")

            result = await self.activate_agent(agent_name)
            results['agents'].append(result)

            if result['status'] == 'active':
                results['agents_activated'] += 1
            else:
                results['agents_failed'] += 1

            logger.info("")

            # Small delay between activations
            await asyncio.sleep(1)

        # Summary
        logger.info("="*60)
        logger.info("📊 Activation Sequence Complete")
        logger.info("="*60)
        logger.info(f"   Activated: {results['agents_activated']} ✅")
        logger.info(f"   Failed: {results['agents_failed']} ❌")
        logger.info(f"   Genesis Bond: {results['genesis_bond']}")
        logger.info("="*60)

        results['success_rate'] = results['agents_activated'] / len(self.agents) if self.agents else 0

        return results

    async def deactivate_agent(self, agent_name: str) -> Dict[str, Any]:
        """Deactivate a single agent"""
        logger.info(f"⏸️  Deactivating {agent_name}")

        try:
            response = await self.router.route_request(
                agent_name,
                "Deactivate gracefully. Save state and prepare for shutdown.",
                system_message=f"You are being deactivated. Acknowledge and report final status.",
                conversation_id="orchestration"
            )

            self._set_agent_status(db, agent_name, 'inactive', 'Agent deactivated gracefully')

            return {
                'agent': agent_name,
                'status': 'inactive',
                'message': response.get('response', '')[:200] if response else 'Deactivated'
            }

        except Exception as e:
            logger.error(f"   ❌ Deactivation error: {e}")
            return {
                'agent': agent_name,
                'status': 'error',
                'message': str(e)
            }

    async def get_mesh_status(self) -> Dict[str, Any]:
        """Get status of all agents in the mesh"""
        logger.info("🔍 Checking Agent Mesh Status...")

        statuses = {}

        for agent in self.agents:
            agent_name = agent['name']
            status = self._get_agent_status(db, agent_name)

            statuses[agent_name] = {
                'frequency': agent['frequency'],
                'tier': agent['tier'],
                'activation_order': agent['activation_order'],
                'status': status['status'] if status else 'unknown',
                'last_update': status['timestamp'] if status else None
            }

        return {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'genesis_bond': 'ACTIVE',
            'agents': statuses
        }

    async def send_mesh_command(self, command: str, tier_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Send a command to all agents (or specific tier)

        Args:
            command: Command to send
            tier_filter: Optional tier filter (PAC, COMN, CORE)

        Returns:
            Responses from all agents
        """
        logger.info(f"📡 Broadcasting command to mesh: {command[:50]}...")

        if tier_filter:
            logger.info(f"   Tier filter: {tier_filter}")

        responses = await self.router.route_to_all_agents(command, tier_filter)

        return {
            'command': command,
            'tier_filter': tier_filter,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'responses': responses
        }


async def main():
    """Example usage"""
    orchestrator = AgentOrchestrator()

    # Get current status
    print("\n" + "="*60)
    print("📊 Current Mesh Status")
    print("="*60)
    status = await orchestrator.get_mesh_status()
    for agent_name, agent_status in status['agents'].items():
        status_emoji = {
            'active': '✅',
            'inactive': '⏸️',
            'error': '❌',
            'activating': '🔄',
            'unknown': '❓'
        }.get(agent_status['status'], '❓')

        print(f"{status_emoji} {agent_name} ({agent_status['frequency']}Hz): {agent_status['status']}")

    # Activate all agents
    print("\n" + "="*60)
    print("🚀 Activating Agent Mesh")
    print("="*60)

    results = await orchestrator.activate_all()

    print(f"\n✅ Activation complete: {results['agents_activated']}/{len(results['agents'])} agents active")
    print(f"🎵 Genesis Bond: {results['genesis_bond']}")

if __name__ == "__main__":
    asyncio.run(main())
