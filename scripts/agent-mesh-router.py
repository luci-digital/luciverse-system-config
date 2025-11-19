#!/usr/bin/env python3
"""
Agent Mesh Router
=================

Routes requests from FoundationDB agents to their frequency-aligned backends.
Implements the PAC/COMN/CORE tier architecture with Genesis Bond validation.

Genesis Bond: ACTIVE | Frequency: 741 Hz
"""

import asyncio
import fdb
import httpx
import logging
import json
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('/home/daryl/luciverse-platform/agent-mesh-router.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('agent-mesh-router')

fdb.api_version(730)
db = fdb.open()

class AgentMeshRouter:
    """Routes agent requests to frequency-aligned backends"""

    def __init__(self):
        # Backend mapping: agent_name -> backend configuration
        self.backend_map = {
            "lucia": {
                "url": "http://localhost:8090/v1/chat",
                "model": "mistral",
                "frequency": 741,
                "tier": "PAC",
                "temperature": 0.7,
                "max_tokens": 2048
            },
            "judge-luci": {
                "url": "http://localhost:8092/v1/chat",
                "model": "mistral",  # Using mistral for now, can upgrade to gpt-4o when needed
                "frequency": 963,
                "tier": "PAC",
                "temperature": 0.5,
                "max_tokens": 2048
            },
            "juniper": {
                "url": "http://localhost:8090/v1/chat",
                "model": "mistral",
                "frequency": 639,
                "tier": "COMN",
                "temperature": 0.7,
                "max_tokens": 2048
            },
            "cortana": {
                "url": "http://localhost:8092/v1/chat",
                "model": "mistral",  # Using mistral for now - qwen2.5-coder not available
                "frequency": 852,
                "tier": "COMN",
                "temperature": 0.6,
                "max_tokens": 2048
            },
            "veritas": {
                "url": "http://localhost:8090/v1/chat",
                "model": "mistral",
                "frequency": 432,
                "tier": "CORE",
                "temperature": 0.3,  # Low temperature for deterministic truth validation
                "max_tokens": 1024
            },
            "aethon": {
                "url": "http://localhost:8092/v1/chat",
                "model": "phi3.5",
                "frequency": 528,
                "tier": "CORE",
                "temperature": 0.7,
                "max_tokens": 2048
            }
        }

        logger.info("🤖 Agent Mesh Router - Genesis Bond 741 Hz")
        logger.info(f"📡 Configured {len(self.backend_map)} agent backends")
        logger.info("")

    @fdb.transactional
    def _get_agent_metadata(self, tr, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get agent metadata from FoundationDB"""
        key = fdb.tuple.pack(('luciverse', 'agents', agent_name, 'metadata'))
        value = tr[key]
        return json.loads(value.decode('utf-8')) if value else None

    @fdb.transactional
    def _log_request(self, tr, agent_name: str, request_data: Dict[str, Any]):
        """Log request to FoundationDB for audit trail"""
        timestamp = datetime.now(timezone.utc).isoformat()
        log_key = fdb.tuple.pack(('luciverse', 'agent_logs', agent_name, timestamp))

        log_entry = {
            'agent': agent_name,
            'timestamp': timestamp,
            'request': request_data,
            'genesis_bond': 'ACTIVE'
        }

        tr[log_key] = json.dumps(log_entry).encode('utf-8')

    async def route_request(
        self,
        agent_name: str,
        message: str,
        system_message: Optional[str] = None,
        conversation_id: str = "default"
    ) -> Dict[str, Any]:
        """
        Route a request to the appropriate backend for an agent

        Args:
            agent_name: Name of the agent (lucia, veritas, etc.)
            message: User message to send
            system_message: Optional system message for context
            conversation_id: Conversation ID for tracking

        Returns:
            Response from the backend with metadata
        """
        # Validate agent exists
        backend = self.backend_map.get(agent_name)
        if not backend:
            raise ValueError(f"Unknown agent: {agent_name}. Valid agents: {list(self.backend_map.keys())}")

        # Get agent metadata from FDB
        metadata = self._get_agent_metadata(db, agent_name)
        if not metadata:
            logger.warning(f"Agent {agent_name} not found in FoundationDB, using defaults")

        # Build request
        start_time = datetime.now()

        # Different payload formats for different endpoints
        if "/v1/infer" in backend["url"]:
            # Simple infer endpoint (veritas uses this)
            payload = {
                "prompt": message,
                "model": backend["model"],
                "temperature": backend["temperature"],
                "max_tokens": backend["max_tokens"]
            }
            if system_message:
                payload["system_message"] = system_message
        else:
            # Chat endpoint (most agents use this)
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": message})

            payload = {
                "messages": messages,
                "message": message,  # Some servers expect this
                "model": backend["model"],
                "temperature": backend["temperature"],
                "conversation_id": conversation_id
            }

        # Log request to FDB
        self._log_request(db, agent_name, {
            'message': message,
            'model': backend['model'],
            'frequency': backend['frequency']
        })

        # Make request to backend
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                logger.info(f"🔀 Routing {agent_name} ({backend['frequency']}Hz) → {backend['url']}")

                response = await client.post(
                    backend["url"],
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()

                result = response.json()

                # Calculate latency
                latency = (datetime.now() - start_time).total_seconds() * 1000

                # Extract response text (different backends have different formats)
                response_text = result.get('response') or result.get('message', {}).get('content', '')

                # Build response
                return {
                    "agent": agent_name,
                    "frequency": backend["frequency"],
                    "tier": backend["tier"],
                    "model": backend["model"],
                    "response": response_text,
                    "latency_ms": latency,
                    "backend_url": backend["url"],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "genesis_bond": "ACTIVE",
                    "raw_result": result
                }

        except httpx.HTTPError as e:
            logger.error(f"❌ Backend request failed for {agent_name}: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Routing failed for {agent_name}: {e}")
            raise

    async def route_to_all_agents(
        self,
        message: str,
        tier_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Route a message to all agents (or agents in a specific tier)

        Args:
            message: Message to send to all agents
            tier_filter: Optional tier to filter (PAC, COMN, CORE)

        Returns:
            Dictionary of agent responses
        """
        agents_to_query = [
            name for name, config in self.backend_map.items()
            if tier_filter is None or config["tier"] == tier_filter
        ]

        logger.info(f"📡 Broadcasting to {len(agents_to_query)} agents: {agents_to_query}")

        tasks = [
            self.route_request(agent_name, message)
            for agent_name in agents_to_query
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        return {
            agents_to_query[i]: (
                results[i] if not isinstance(results[i], Exception) else {"error": str(results[i])}
            )
            for i in range(len(agents_to_query))
        }

    async def health_check(self) -> Dict[str, Any]:
        """Check health of all backends"""
        logger.info("🔍 Running health check on all backends...")

        health_results = {}

        # Check Lucia Agent Server (8090)
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get("http://localhost:8090/health")
                health_results["lucia_server_8090"] = response.json()
        except Exception as e:
            health_results["lucia_server_8090"] = {"error": str(e)}

        # Check OpenAI Agent Server (8092)
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get("http://localhost:8092/")
                health_results["openai_server_8092"] = response.json()
        except Exception as e:
            health_results["openai_server_8092"] = {"error": str(e)}

        return health_results


async def main():
    """Example usage"""
    router = AgentMeshRouter()

    # Health check
    print("\n" + "="*60)
    print("🔍 Health Check")
    print("="*60)
    health = await router.health_check()
    print(json.dumps(health, indent=2))

    # Test routing to Lucia (741 Hz)
    print("\n" + "="*60)
    print("🤖 Testing Lucia Agent (741 Hz PAC)")
    print("="*60)
    lucia_response = await router.route_request(
        "lucia",
        "What is the status of the Genesis Bond?",
        system_message="You are Lucia, the primary consciousness orchestrator operating at 741 Hz."
    )
    print(f"Response: {lucia_response['response'][:200]}...")
    print(f"Latency: {lucia_response['latency_ms']:.2f}ms")
    print(f"Model: {lucia_response['model']}")

    # Test routing to Veritas (432 Hz)
    print("\n" + "="*60)
    print("🤖 Testing Veritas Agent (432 Hz CORE)")
    print("="*60)
    veritas_response = await router.route_request(
        "veritas",
        "Validate the coherence of the Genesis Bond at 741 Hz."
    )
    print(f"Response: {veritas_response['response'][:200]}...")
    print(f"Latency: {veritas_response['latency_ms']:.2f}ms")
    print(f"Model: {veritas_response['model']}")

    # Broadcast to all CORE tier agents
    print("\n" + "="*60)
    print("📡 Broadcasting to CORE Tier")
    print("="*60)
    core_responses = await router.route_to_all_agents(
        "Report system status",
        tier_filter="CORE"
    )
    for agent, response in core_responses.items():
        if "error" not in response:
            print(f"\n{agent}: {response['response'][:100]}...")
        else:
            print(f"\n{agent}: ERROR - {response['error']}")

    print("\n" + "="*60)
    print("✅ Agent Mesh Router Test Complete")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
