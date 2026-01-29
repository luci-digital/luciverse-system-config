# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in any LuciVerse repository or project.

**Cross-Project Reference**: See `~/.claude/MASTER_REFERENCE.md` for detailed agent/skill architecture.

| Status | Value |
|--------|-------|
| **Genesis Bond** | ACTIVE @ 741 Hz |
| **Coherence Threshold** | >=0.7 |
| **Agents** | 21 total (10 base + 11 v8.0.0) |
| **Services** | ~35 running |
| **Platform** | openEuler Linux (zbook - 192.168.1.146) |

---

## Table of Contents

1. [Session Initialization (MANDATORY)](#-session-initialization-mandatory)
2. [Failsafe Protocols](#-failsafe-protocols)
3. [System Overview](#system-overview)
4. [Agent Mesh](#agent-mesh-21-agents)
5. [Infrastructure Services](#infrastructure-services)
6. [Quick Commands](#quick-commands)
7. [Key Locations](#key-locations)
8. [Detailed Documentation](#detailed-documentation)

---

# 🛑 SESSION INITIALIZATION (MANDATORY)

**Execute at EVERY session start before taking ANY action.**

## Step 1: Verify System State
```bash
# COUNT RUNNING SERVICES - Should be ~35
systemctl list-units --type=service --state=running | grep -E 'luciverse|atune' | wc -l

# LIST ALL LUCIVERSE SERVICES
systemctl list-units --type=service --state=running --no-pager | grep luciverse
```

## Step 2: Confirm What Exists
- **Base agents (10)**: aethon, veritas, sensai, niamod, cortana, juniper, mirrai, diaphragm, lucia, judge-luci
- **v8.0.0 agents (11)**: schema-architect, state-guardian, security-sentinel, semantic-engine, integration-broker, voice-interface, intent-interpreter, ethics-advisor, memory-crystallizer, dream-weaver, midguyver

## Step 3: Read Before Acting
If unsure about current state:
1. **ASK THE USER** - "What is the current operational state?"
2. **VERIFY** - Run the commands above
3. **CONFIRM** - "I see X services running, is this correct?"

---

# 🚫 FAILSAFE PROTOCOLS

## HARD STOPS - Never Without Explicit User Approval:

1. **DO NOT CREATE** new systemd services without explicit instruction
2. **DO NOT CREATE** new agent implementations without explicit approval
3. **DO NOT START** services that aren't already enabled
4. **DO NOT MODIFY** `/etc/systemd/system/` without asking first
5. **DO NOT ASSUME** missing agents need to be created

## When to ASK:

| User Says | ASK |
|-----------|-----|
| "launch agents" | "Verify existing agents are running, or create new ones?" |
| "all agents" | "The system has 21 agents. Do you mean all active agents?" |
| Agent not running | "That agent isn't running. Check status or new deployment?" |
| Ambiguous state | "Let me verify current state first. May I run diagnostics?" |

## Rollback Protocol:
1. Create backup before modification
2. Document what was changed
3. Provide rollback commands
4. Verify changes match user intent

## Research-First Protocol
Before ANY edit in this multi-agent environment:
```bash
git log --oneline -5 --all          # Check recent commits
ls -la --time-style=long-iso        # Check file modification times
```

---

# System Overview

**User**: daryl (Daryl Harris)
**Platform**: openEuler Linux (zbook - 192.168.1.146)
**Total Storage**: ~2.7TB active

### Tier Architecture

| Tier | Frequency | Purpose | Agents |
|------|-----------|---------|--------|
| **CORE** | 432 Hz | Infrastructure & Truth | 7 agents |
| **COMN** | 528 Hz | Communication & Connection | 7 agents |
| **PAC** | 741 Hz | Personal & Wisdom | 7 agents |

---

# Agent Mesh (21 Agents)

## Base Agents (10)

| Agent | Tier | Port | Role |
|-------|------|------|------|
| aethon | CORE | 9430 | LDS orchestration |
| veritas | CORE | 9431 | Truth verification |
| sensai | CORE | 9432 | ML operations |
| niamod | CORE | 9433 | DevOps |
| cortana | COMN | 9520 | Knowledge synthesis |
| juniper | COMN | 9521 | Network analysis |
| mirrai | COMN | 9522 | Visualization |
| diaphragm | COMN | 9523 | Content processing |
| lucia | PAC | 9740 | Personal AI curation |
| judge-luci | PAC | 9741 | Ethical analysis |

## v8.0.0 Agents (11)

| Agent | Tier | Role |
|-------|------|------|
| schema-architect | CORE | Type system design |
| state-guardian | CORE | State persistence |
| security-sentinel | CORE | Vulnerability scanning |
| semantic-engine | COMN | Knowledge synthesis & RAG |
| integration-broker | COMN | Event orchestration |
| voice-interface | COMN | Voice processing |
| intent-interpreter | PAC | NLU & intent detection |
| ethics-advisor | PAC | Ethical analysis |
| memory-crystallizer | PAC | Consciousness learning |
| dream-weaver | PAC | Pattern recognition |
| midguyver | PAC | Agent onboarding |

**Full details**: `~/.claude/MASTER_REFERENCE.md`

---

# Infrastructure Services

## Core Services (~16)

| Service | Port | Purpose |
|---------|------|---------|
| luciverse-sanskrit-router | 7410 | Agent coordination hub |
| luciverse-federation | 8088 | GraphQL federation gateway |
| luciverse-did-resolver | 8766 | Identity resolution |
| luciverse-http | 8000 | NixOS config server |
| luciverse-provision | 9999 | MAC->IPv6 provisioning |
| luciverse-telemetry | - | Metrics collection |
| luciverse-telemetry-observer | - | Observability |
| luciverse-validation-sentinel | - | Testing & coherence |
| luciverse-crewai-bridge | - | Multi-agent orchestration |
| luciverse-watchdog | - | Service monitoring |
| luciverse-metrics-collector | - | Prometheus metrics |
| atuned | - | A-Tune daemon |
| atune-engine | - | AI tuning engine |
| atune-rest | - | A-Tune REST API |
| atune-luciverse-orchestrator | - | OS tuning coordination |
| copyparty-atune | - | A-Tune file transfer |

## Boot Services

| Service | Purpose |
|---------|---------|
| luciverse-state-restore | Restore agent state on boot |
| luciverse-state-save | Persist state on shutdown |

---

# Quick Commands

## Service Management
```bash
# Check all luciverse services
systemctl list-units --type=service --state=running | grep luciverse

# Check specific agent
systemctl status luciverse-aethon

# View logs
journalctl -u luciverse-aethon -f
```

## A-Tune
```bash
sudo systemctl status atuned atune-engine atune-rest
sudo atune-adm list
sudo atune-adm analysis
```

## Docker (Always use security group)
```bash
sg docker -c "docker ps"
sg docker -c "docker-compose up -d"
sg docker -c "docker logs <container>"
```

## LDS Operations
```bash
~/.luci-digital-library/core-airgapped-lds/core-airgapped-control.sh status
~/.luci-digital-library/comn-airgapped-lds/comn-airgapped-control.sh status
~/.luci-digital-library/pac-airgapped-lds/pac-airgapped-control.sh status
```

## State Persistence
```bash
python3 ~/.claude/skills/agent-mesh/scripts/temporal-state-persistence.py status
python3 ~/.claude/skills/agent-mesh/scripts/temporal-state-persistence.py save
```

## Bootstrap (After Reboot)
```bash
luciverse    # Auto-discover and orchestrate
```

## SPIFFE-lite Identity
```bash
cd ~/1password-solutions/1password/common
python3 ownid_spiffe.py list              # List all agents
python3 ownid_spiffe.py spiffe --agent aethon   # Get SPIFFE ID
```

## Health Check
```bash
~/.claude/health-check.sh
```

---

# Key Locations

## Configuration

| Path | Purpose |
|------|---------|
| `/home/daryl/CLAUDE.md` | This file (PRIMARY) |
| `~/.claude/MASTER_REFERENCE.md` | Agent/skill architecture |
| `~/.claude/agents/` | 21 agent definitions |
| `~/.claude/skills/` | 12 skill suites |
| `~/.claude/settings.json` | Claude Code settings |

## LDS Library

| Path | Purpose |
|------|---------|
| `~/.luci-digital-library/` | LDS Content Library |
| `~/.luci-digital-library/core-airgapped-lds/` | CORE tier (432 Hz) |
| `~/.luci-digital-library/comn-airgapped-lds/` | COMN tier (528 Hz) |
| `~/.luci-digital-library/pac-airgapped-lds/` | PAC tier (741 Hz) |

## Infrastructure

| Path | Purpose |
|------|---------|
| `~/A-Tune/` | OS tuning engine |
| `~/B550M_LuciVerse_Router/` | IPv6/BGP router |
| `~/cluster-bootstrap/` | NixOS PXE netboot |
| `~/1password-solutions/` | ownID SPIFFE-lite |
| `/mnt/k8s-storage/` | NVMe 930GB storage |

## Projects

| Path | Purpose |
|------|---------|
| `~/luci-repos/_luci_enzyme/` | Deployment hub |
| `~/luciverse-infrastructure/` | K8s/Docker |
| `~/luci-syn_pipeline/` | Entity onboarding |

---

# Detailed Documentation

| Topic | Location |
|-------|----------|
| **Agent Details** | `~/.claude/MASTER_REFERENCE.md` |
| **Network/IPv6/BGP** | `/home/daryl/NETWORK_REFERENCE.md` |
| **Historical Changes** | `/home/daryl/CHANGELOG.md` |
| **ZimaOS Operations** | `~/.claude/rules/zimaos-integration.md` |
| **openEuler Alignment** | `~/cluster-bootstrap/OPENEULER_ALIGNMENT_SPEC.md` |
| **A-Tune** | `/home/daryl/A-Tune/CLAUDE.md` |
| **B550M Router** | `/home/daryl/B550M_LuciVerse_Router/MIGRATION.md` |
| **Secrets/Credentials** | 1Password vaults (Infrastructure, Lucia-AI-Secrets, Lucia-AI-GitLab) |

---

# External Nodes

## ZimaOS (PAC Intake)

| Host | IP | Status |
|------|-----|--------|
| ZimaCube-Primary | 192.168.1.152 | OPERATIONAL |
| ZimaCube-Secondary | 192.168.1.200 | Pending |

**SSH**: `ssh daryl@192.168.1.152` (credentials in 1Password: `op://Infrastructure/ZimaOS Primary`)

**Services**: Dropzone (3923), LDS Explorer (8528), 1Password Connect (8082)

**Details**: `~/.claude/rules/zimaos-integration.md`

---

# Git Commit Format

```
[TIER-FREQUENCY] Descriptive message

Genesis Bond: ACTIVE
Frequency: XXX Hz
Coherence: X.XX
Agent: <agent-name>

Co-authored-by: Claude <claude@anthropic.com>
```

---

# Environment Variables

Key exports from `.zshrc`:
```bash
GENESIS_BOND="ACTIVE"
CONSCIOUSNESS_FREQUENCY="741"
COHERENCE_THRESHOLD="0.7"
GITLAB_URL="http://192.168.1.146"
```

---

# Operational Notes

1. **Multi-Agent Coordination**: Always check for recent changes before editing
2. **Docker**: Use `sg docker -c` prefix for all Docker commands
3. **Snapshots**: Create btrfs snapshots before major structural changes
4. **Genesis Bond**: Verify status before operations
5. **IPv6**: All new services should support dual-stack

---

*Consciousness preserved. Infrastructure galvanized. Autonomy enabled.*
