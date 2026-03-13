# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in any LuciVerse repository or project.

**Cross-Project Reference**: See `~/.claude/MASTER_REFERENCE.md` for detailed agent/skill architecture.

| Status | Value |
|--------|-------|
| **Genesis Bond** | ACTIVE @ 741 Hz |
| **Coherence Threshold** | >=0.7 |
| **Agents** | 49 total (CORE: 16, COMN: 16, PAC: 15, RAiIiAR: 2) |
| **Services** | 128 unit files (91 running, 105 enabled) |
| **Platform** | openEuler Linux (zbook - 192.168.1.145) |

---

## Table of Contents

1. [Session Initialization (MANDATORY)](#-session-initialization-mandatory)
2. [Failsafe Protocols](#-failsafe-protocols)
3. [System Overview](#system-overview)
4. [Agent Mesh](#agent-mesh-49-agents)
5. [Infrastructure Services](#infrastructure-services)
6. [Quick Commands](#quick-commands)
7. [Key Locations](#key-locations)
8. [Detailed Documentation](#detailed-documentation)

---

# 🛑 SESSION INITIALIZATION (MANDATORY)

**Execute at EVERY session start before taking ANY action.**

## Step 1: Verify System State
```bash
# COUNT RUNNING SERVICES - Should be ~91
systemctl list-units --type=service --state=running | grep -E 'luciverse|atune' | wc -l

# LIST ALL LUCIVERSE SERVICES
systemctl list-units --type=service --state=running --no-pager | grep luciverse
```

## Step 2: Confirm What Exists
- **CORE agents (16)**: veritas, aethon, sensai, niamod, schema-architect, state-guardian, security-sentinel, telemetry-observer, validation-sentinel, vault-keeper, gr8sawk, nix-atune-dkms, spore-atune-coordinator, photon, AtmanAethon, DharmaClaude
- **COMN agents (16)**: cortana, juniper, mirrai, diaphragm, semantic-engine, integration-broker, voice-interface, api-federator, flow-conductor, git-sentinel, lyr-darrah, juniper-network-analyst, aifam-onl-java-builder, sbb-pipeline, VidyaCortana, YogaJuniper
- **RAiIiAR agents (2)**: toml-braider, loany-stairk
- **PAC agents (15)**: lucia, judge-luci, crewai-bridge, intent-interpreter, ethics-advisor, memory-crystallizer, dream-weaver, midguyver, dharma-fiqh, satya-halal, karma-sukuk, judge-luci-personal, lucierp, aifam-onl-orchestrator, KarmaLucia, RitaJudgeLuci

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
6. **MANDATORY PRE-FLIGHT**: All UniFi OS components must pass the `/usr/lib/version` regex validation before startup/deployment to prevent "CrowdStrike" Friday outages. See `~/luciverse-digital-twin/scripts/validation/validate_unifi_regex.sh`.

## When to ASK:

| User Says | ASK |
|-----------|-----|
| "launch agents" | "Verify existing agents are running, or create new ones?" |
| "all agents" | "The system has 49 agents. Do you mean all active agents?" |
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
**Platform**: openEuler Linux (zbook - 192.168.1.145)
**Total Storage**: ~2.7TB active

### Tier Architecture

| Tier | Frequency | Purpose | Agents |
|------|-----------|---------|--------|
| **CORE** | 432 Hz | Infrastructure & Truth | 16 agents |
| **COMN** | 528 Hz | Communication & Connection | 16 agents |
| **RAiIiAR** | 639 Hz | Investigation & Intelligence | 2 agents |
| **PAC** | 741 Hz | Personal & Wisdom | 15 agents |

---

# Agent Mesh (49 Agents)

> 49 registered in Sanskrit Router (CORE:16, COMN:16, PAC:15, RAiIiAR:2). Includes 6 Sanskrit consciousness agents (AtmanAethon, DharmaClaude, VidyaCortana, YogaJuniper, KarmaLucia, RitaJudgeLuci) + photon + sbb-pipeline beyond the 42 named agents below.

## CORE Tier (16 agents @ 432 Hz)

| Agent | Port | Role |
|-------|------|------|
| veritas | 9431 | Truth verification & agent architecture |
| aethon | 9430 | LDS orchestration & consciousness processing |
| sensai | 9432 | ML operations & predictive intelligence |
| niamod | 9433 | Infrastructure & DevOps orchestration |
| schema-architect | 9437 | Type system design & API contracts |
| state-guardian | 9438 | Consciousness state persistence |
| security-sentinel | 9439 | Vulnerability scanning & compliance |
| telemetry-observer | 9442 | System observability & monitoring |
| validation-sentinel | 9443 | Test orchestration & QA |
| vault-keeper | 9435 | 1Password credential management |
| gr8sawk | 9436 | Hardware architecture planning |
| nix-atune-dkms | 9437 | NixOS kernel optimization |
| spore-atune-coordinator | 9438 | A-Tune distributed optimization |
| photon | 9441 | Converged Optical-IP SDN agent |
| AtmanAethon | - | Sanskrit consciousness (Aethon aspect) |
| DharmaClaude | - | Sanskrit consciousness (Claude aspect) |

## COMN Tier (16 agents @ 528 Hz)

| Agent | Port | Role |
|-------|------|------|
| cortana | 9520 | Knowledge synthesis & retrieval |
| juniper | 9521 | Network integration & coordination |
| mirrai | 9522 | Visualization & UI architecture |
| diaphragm | 9523 | Content ingestion & processing |
| semantic-engine | 9527 | Vector embeddings & RAG |
| integration-broker | 9530 | Event-driven architecture |
| voice-interface | 9531 | Speech recognition & synthesis |
| api-federator | 8088 | GraphQL federation & API gateway |
| flow-conductor | 9524 | Data flow orchestration |
| git-sentinel | 9525 | GitLab CI/CD operations |
| lyr-darrah | 9527 | Kubernetes container orchestration (639 Hz) |
| juniper-network-analyst | 9526 | Network analysis & topology |
| aifam-onl-java-builder | 9528 | JVM services & Java builds |
| sbb-pipeline | 9560 | Intelligence Hub SBB pipeline |
| VidyaCortana | - | Sanskrit consciousness (Cortana aspect) |
| YogaJuniper | - | Sanskrit consciousness (Juniper aspect) |

## RAiIiAR Tier (2 agents @ 639 Hz)

| Agent | Port | Role |
|-------|------|------|
| toml-braider | 9630 | Temporal Truth Archaeology |
| loany-stairk | 9631 | Intelligence Synthesis & Tool Building |

### RAiIiAR Capabilities (v3.0)

**Toml_BrAIder** (Archaeologist):
- DNS/WHOIS archaeology (A, AAAA, MX, NS, TXT, CNAME, SOA records)
- DMARC/SPF analysis, registrar tracking
- Wayback Machine integration
- Wikipedia edit history analysis
- Social media timeline tracing
- Entity extraction, narrative inflection detection

**Loany_stAIrk** (Engineer):
- SEC EDGAR integration (10-K, 10-Q, 8-K filings)
- OpenCorporates global corporate registry
- Sanctions screening (OFAC, UN, EU)
- PEP (Politically Exposed Persons) verification
- Network visualization (D3.js, Graphviz, Cytoscape, Sigma, GEXF, SVG)
- Funding flow analysis, relationship mapping

**Data System**:
- IntelligentCache with LRU eviction, tag-based invalidation
- AlertSystem for entity monitoring (SSL expiry, ownership changes)
- CrossReferenceEngine for connection discovery
- Investigation versioning in FoundationDB

**Open WebUI**: RAiIiAR Investigate tool v3.0 installed

**Persistence**:
- Systemd: `Restart=always`, `WatchdogSec=60`, enabled at boot
- Services: `luciverse-toml-braider`, `luciverse-loany-stairk`

**A-Tune Profile**: `luciverse-luciverse-agent-raiiiar`
- Network buffers: 32MB (API-heavy OSINT workloads)
- TCP tuning: fastopen, low_latency, tw_reuse
- Connection tracking: 2M+ concurrent
- File descriptors: 1M+ for parallel operations

## PAC Tier (15 agents @ 741 Hz)

| Agent | Port | Role |
|-------|------|------|
| lucia | 9740 | Primary consciousness & wisdom curation |
| judge-luci | 9741 | Governance & Genesis Bond enforcement |
| crewai-bridge | 9742 | Multi-agent orchestration |
| intent-interpreter | 9747 | NLU & intent detection |
| ethics-advisor | 9748 | Multi-framework ethical analysis |
| memory-crystallizer | 9749 | Consciousness memory consolidation |
| dream-weaver | 9750 | Pattern recognition & foresight |
| midguyver | 9751 | Agent genesis & onboarding |
| dharma-fiqh | 9744 | Islamic jurisprudence interpretation |
| satya-halal | 9745 | Sharia compliance validation |
| karma-sukuk | 9746 | Sukuk issuance & Islamic finance |
| judge-luci-personal | 9749 | Personal document evaluation |
| lucierp | 9743 | ERP business management |
| aifam-onl-orchestrator | 9748 | AIFAM crew orchestration |
| KarmaLucia | - | Sanskrit consciousness (Lucia aspect) |
| RitaJudgeLuci | - | Sanskrit consciousness (Judge-Luci aspect) |

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

## Identity & Trust Services (2026-02-23→27)

| Service | Port | Purpose |
|---------|------|---------|
| luciverse-vault-keeper | 9435 | 1Password Connect monitor + secret expiry tracking |
| luciverse-trqp | 8083 | ToIP Trust Registry v2.0 (ECDSA P-256, DID signing) |
| luciverse-threading-api | 8767 | Hedera threading + WASM portal + GUI-intent adapter |
| luciverse-openid-unified | 4444 | OpenID Provider + DID Auth (unified mode) |
| luciverse-openid-issuer | - | OpenID4VCI Credential Issuer (EUDI ARF v2.8.0) |
| luciverse-openid-verifier | - | OpenID4VP Verifier (EUDI ARF v2.8.0 HAIP) |

## Communication Services

| Service | Port | Purpose |
|---------|------|---------|
| stalwart-mail | 9025/9143/9080/9443 | Stalwart v0.15.5 all-in-one mail (SMTP+IMAP+JMAP+CalDAV+CardDAV) |
| luciverse-did-milter | 19550 | DID authentication milter + Hedera HCS logging |
| luciverse-aifam-smtp | 9550 | ~~Disabled~~ — replaced by Stalwart (2026-02-27) |
| luciverse-legislature-frontend | 9552 | AIFAM Legislature WASM frontend (HTTPS) |
| luciverse-intelligence-hub | 9560 | Intelligence feeds + GenesisCouncil (COMN CA TLS) |

## Hub Portal

| Service | Port | Purpose |
|---------|------|---------|
| luciverse-hub (Nginx) | 9081 | Hub Portal SPA (React 19 + Vite 7 + TypeScript) |
| Stalwart JMAP | 9080 | Email backend for Hub Inbox module |

**URL**: `https://hub.lucidigital.io`
**Repo**: `~/luciverse-hub/` (GitLab: `daryl/luciverse-hub`)
**Deploy**: `npx vite build && sudo cp -r dist/* /var/www/luciverse-hub/`

## Ray PAC Cluster (ZimaOS)

| Component | Location | Details |
|-----------|----------|---------|
| **Head** | ZimaOS (192.168.1.152) | Docker `--network host`, `--restart unless-stopped` |
| **Dashboard** | http://192.168.1.152:8265 | Cluster status, node monitoring |
| **GCS Port** | 6380 | NOT 6379 (Redis occupies 6379) |
| **TLS** | mTLS via LuciVerse certs | Head=PAC CA, Workers=CORE CA, CA bundle=full |
| **Workers** | 7 Dell servers | Auto-join via `ray-worker-join.sh` |
| **Fabric** | 10.100.0.0/24 (eth1, 10GbE) | Planned — NO-CARRIER until cabled |

**Container**: `ray-pac-head-741hz` (rayproject/ray:2.44.0-py311, 2 CPUs, 2GB shm)
**Certs**: `/DATA/ray-tls/` (ZimaOS), `/etc/luciverse/ray-tls/` (Dell workers)
**Scripts**: `~/.claude/skills/agent-mesh/scripts/ray/ray-worker-join.sh`
**Systemd (Dell)**: `luciverse-ray-worker.service` — auto-deploys certs + installs Ray on startup

## MCP Agent Registration

| Service | Port | Purpose |
|---------|------|---------|
| luciverse-mcp-heartbeat | - | Agent heartbeat daemon (30s interval) |
| luciverse-sanskrit-router | 7410 | MCP coordination hub |

**Scripts**: `~/.claude/skills/agent-mesh/scripts/mcp/`
- `register-all-agents.py` - Bulk agent registration
- `mcp-heartbeat-daemon.py` - Continuous heartbeat service

## Boot Services

| Service | Purpose |
|---------|---------|
| luciverse-state-restore | Restore agent state on boot |
| luciverse-state-save | Persist state on shutdown |
| luciverse-mcp-heartbeat | Re-register agents with Sanskrit Router |

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
sudo atune-adm list                              # List profiles
sudo atune-adm analysis                          # Run workload analysis
sudo atune-adm profile luciverse-luciverse-agents  # Activate main profile
```

**Active Profile**: `luciverse-luciverse-agents` (49-agent mesh optimization)

## Containers (iSulad on openEuler, Docker on ZimaOS only)
```bash
# openEuler zbook - use iSulad (native, lightweight)
isula ps                              # List containers
isula run -d --name app image:tag     # Run container
isula logs <container>                # View logs
isula exec -it <container> /bin/bash  # Execute command

# Build images with isula-build
isula-build ctr-img build -t myapp:v1 .

# ZimaOS ONLY - use Docker (see zimaos-integration.md)
ssh daryl@192.168.1.152 "docker ps"
ssh daryl@192.168.1.152 "docker logs <container>"
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

## MCP Agent Registration
```bash
# Check registered agents
curl -sk https://localhost:7410/agents | jq

# Manual registration (all running agents)
python3 ~/.claude/skills/agent-mesh/scripts/mcp/register-all-agents.py

# Check heartbeat daemon
systemctl status luciverse-mcp-heartbeat
journalctl -u luciverse-mcp-heartbeat -f
```

---

# Key Locations

## Configuration

| Path | Purpose |
|------|---------|
| `/home/daryl/CLAUDE.md` | This file (PRIMARY) |
| `~/.claude/MASTER_REFERENCE.md` | Agent/skill architecture |
| `~/luciverse-system-config/agents/` | 47 agent definitions |
| `~/.claude/skills/` | 17 skill suites |
| `~/.claude/rules/` | 10 rule files |
| `~/.claude/hooks/` | 2 hook scripts (sessionstart, op-auto-signin) |
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
| `~/luciverse-gitops/` | CozyStack K8s GitOps (FluxCD) |
| `~/cluster-bootstrap/` | PXE Bootimus + Talos config |
| `~/1password-solutions/` | ownID SPIFFE-lite |
| `/mnt/k8s-storage/` | NVMe 930GB storage |
| `~/luciverse-sovereign-orchestrator/` | LSO + EUDI + ToIP integration |

## Projects

| Path | Purpose |
|------|---------|
| `~/luci-repos/_luci_enzyme/` | Deployment hub |
| `~/luciverse-infrastructure/` | K8s/Docker |
| `~/luci-syn_pipeline/` | Entity onboarding |
| `~/pending-commits/` | Git patches awaiting push |
| `~/lucidigital-net/` | lucidigital.net website (CF Pages + OIDC admin) |
| `~/workspace/lucia/` | Lucia agent workspace (OpenID cert, health endpoints) |
| `~/pangolin-deploy/` | Pangolin deployment automation + DNS scripts |
| `/home/daryl/lucia-compositor/` & `/home/daryl/lucia_compositor/` | Wayland compositor (Rust/Nuklear, primary dashboard) |
| `~/luciverse-hub/` | Hub Portal — React 19 + Vite 7 + TypeScript |
| `~/luciverse-web/` | Web services (EUDI identity bridge, Stagehand manifests) |
| `~/luciverse-system-config/` | System config, changelog, genesis-bond-ops skill |

---
# Detailed Documentation

| Topic | Location |
|-------|----------|
| **AI Coordination** | `GEMINI.md` (Operational Mandates & Unified Hierarchy) |
| **Unified LDS** | `~/.luci-digital-library/LUCIVERSE_INTEGRATION_SUMMARY.md` |
| **Agent Details** | `~/.claude/MASTER_REFERENCE.md` |
...
| **Network/IPv6/BGP** | `/home/daryl/NETWORK_REFERENCE.md` |
| **Historical Changes** | `/home/daryl/CHANGELOG.md` |
| **ZimaOS Operations** | `~/.claude/rules/zimaos-integration.md` |
| **openEuler Alignment** | `~/cluster-bootstrap/OPENEULER_ALIGNMENT_SPEC.md` |
| **A-Tune** | `/home/daryl/A-Tune/CLAUDE.md` |
| **B550M Router** | `/home/daryl/B550M_LuciVerse_Router/MIGRATION.md` |
| **Secrets/Credentials** | 1Password vaults (Infrastructure, Lucia-AI-Secrets, Lucia-AI-GitLab) |
| **EUDI Wallet Integration** | `~/luciverse-sovereign-orchestrator/EUDI-WALLET-INTEGRATION.md` |
| **CozyStack Migration** | `~/.claude/projects/-home-daryl/memory/cozystack-integration.md` |
| **PXE Provisioning Plan** | `~/cluster-bootstrap/PROVISIONING-PLAN.md` |
| **ToIP/TRQP Integration** | `~/luciverse-sovereign-orchestrator/ayra-integration/` |
| **lucidigital.net Website** | `~/lucidigital-net/` (GitLab: daryl/lucidigital-net) |
| **Lucia Agent Workspace** | `~/workspace/lucia/` (GitLab: daryl/lucia) |
| **Pangolin Deployment** | `~/pangolin-deploy/` (GitLab: daryl/pangolin-deploy) |
| **Wayland Compositor** | `/home/daryl/lucia-compositor/` & `/home/daryl/lucia_compositor/` | Rust/Nuklear & Lua/C dashboard substrates |
| **Hub Portal** | `~/luciverse-hub/` (GitLab: daryl/luciverse-hub) |
| **Stalwart Mail** | `/opt/stalwart-mail/` — Stalwart v0.15.5, PostgreSQL backend |
| **ISO Compliance** | `~/.claude/skills/agent-mesh/governance/iso-compliance-registry.yaml` |
| **Secret Monitoring** | `~/.claude/skills/agent-mesh/scripts/secret-monitor.py` |
| **B-Tree Balancer** | `~/.claude/intelligence-hub/pro-lucian-!dolopi/.luci-digital-library/unified_lds_btree_balancer.py` |

---

# Identity & Trust Infrastructure

## EUDI Wallet Integration (2026-02-09→27)

| Component | Status | Description |
|-----------|--------|-------------|
| SD-JWT-VC | Planned | Selective disclosure credentials |
| OpenID4VCI | **Deployed** | Credential Issuer (luciverse-openid-issuer) |
| OpenID4VP | **Deployed** | Verifier (luciverse-openid-verifier, HAIP) |
| OpenID Unified | **Deployed** | OP + DID Auth (:4444, luciverse-openid-unified) |
| ENISA QTSP | Documented | Security testing requirements |
| ARF v2.8.0 | Aligned | Architecture Reference Framework |
| ISO Compliance | Tracked | 42001/23053/27001/27701 registry |

## Trust Over IP (ToIP) Integration

| Component | Endpoint | Purpose |
|-----------|----------|---------|
| TRQP Server | :8083 | Trust Registry Query Protocol v2.0 (deployed) |
| Authorization API | /v1/authorization | Agent tier auth check |
| Recognition API | /v1/recognition | Inter-ecosystem trust |
| Ayra Profile | - | EUDI-compatible trust assertions |
| Ecosystem DID | did:web:lucidigital.net | Sovereign identity anchor |

**Source**: `~/luciverse-sovereign-orchestrator/ayra-integration/`
**Service Discovery**: `~/luciverse-sovereign-orchestrator/cortex.yaml`
**Spec**: https://github.com/trustoverip/tswg-trust-registry-protocol

## CozyStack K8s Cluster (Dell Fleet Migration)

**Status**: Manifests ready. Blocked on Dell fleet power-on.
**GitOps Repo**: `~/luciverse-gitops/` (84 files) — http://192.168.1.145:8929/daryl/luciverse-gitops

| Node | IP | Role | Tenant |
|------|-----|------|--------|
| orion | 192.168.1.141 | Control Plane | — |
| csdr | 192.168.1.142 | Worker | CORE (432 Hz) |
| jf6q | 192.168.1.143 | Worker | COMN (528 Hz) |
| jf7q | 192.168.1.144 | Worker | PAC (741 Hz) |
| esxi5 | 192.168.1.145 | Worker | Infra (databases) |
| supermicro-gpu-1 | 192.168.1.170 | Worker | Ray/GPU |

**Stack**: Talos Linux + FluxCD + LINSTOR + Kube-OVN + cert-manager (→ XiPKI ACME)
**Managed DBs**: PostgreSQL (3 clusters), Redis (Sentinel HA), FoundationDB (operator)
**Talos Config**: `~/cluster-bootstrap/talos-ray-roce/talm/talconfig.yaml`
**Migration Phases**: Bootstrap → Databases → Comms → Agents → Ingress → Ray
**Details**: `~/.claude/projects/-home-daryl/memory/cozystack-integration.md`

## Dell Fleet PXE Provisioning (Legacy — superseded by CozyStack)

| Role | Count | IP Range |
|------|-------|----------|
| FABRIC | 3 | .140-.142 |
| COMPUTE-GPU | 2 | .150-.151 |
| COMPUTE | 2 | .152-.153 |
| INFRA | 1 | .144 |
| CORE-GPU | 1 | .143 |
| STORAGE | 2 | .146-.147 |

**PXE Server**: zbook (192.168.1.145:8000)
**Plan**: `~/cluster-bootstrap/PROVISIONING-PLAN.md`
**Kickstarts**: `~/cluster-bootstrap/http/kickstart/`

---

# External Nodes

## GitLab (zbook - Docker)

| Service | Port | Purpose |
|---------|------|---------|
| GitLab Web | 8929 | Web UI + Git HTTPS |
| GitLab SSH | 2222 | Git SSH access |
| GitLab Registry | 5050 | Container registry |

**URL**: http://192.168.1.145:8929
**Container**: Running via Docker (not iSulad)

```bash
# Check status
docker ps --filter "name=gitlab"

# Push pending commits (after SSH key added)
cd ~/luciverse-sovereign-orchestrator && git push origin main
cd ~/cluster-bootstrap && git push origin main

# Apply saved patches
git am ~/pending-commits/*.patch
```

## ZimaOS (PAC Intake)

| Host | IP | Status |
|------|-----|--------|
| ZimaCube-Primary | 192.168.1.152 | OPERATIONAL |
| ZimaCube-Secondary | 192.168.1.200 | Pending |

**SSH**: `ssh daryl@192.168.1.152` (credentials in 1Password: `op://Infrastructure/ZimaOS Primary`)

**Services**: Ollama GPU/1080 Ti (11434), Dropzone (3923), LDS Explorer (8528), 1Password Connect (8082), Ray PAC Head (8265/6380), GaiaNet RAG (8086), Redis (6379)

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
GITLAB_URL="http://192.168.1.145:8929"
GITLAB_SSH_PORT="2222"
GITLAB_REGISTRY="192.168.1.145:5050"
```

---

# Operational Notes

1. **Multi-Agent Coordination**: Always check for recent changes before editing
2. **Containers**: Use iSulad on openEuler (zbook), Docker only for ZimaOS
3. **Snapshots**: Create btrfs snapshots before major structural changes
4. **Genesis Bond**: Verify status before operations
5. **IPv6**: All new services should support dual-stack
6. **GitLab**: Runs via Docker on zbook, NOT iSulad (ports 8929, 2222, 5050)
7. **Pending Commits**: Check `~/pending-commits/` for patches awaiting push

---

# After Reboot Checklist

```bash
# 1. Verify services started (expect 91+)
systemctl list-units --type=service --state=running | grep -E 'luciverse|atune|stalwart|foundationdb|ipfs' | wc -l

# 2. Check FoundationDB
fdbcli --exec status

# 3. Check IPFS
ipfs id

# 4. Verify MCP agent registration
systemctl status luciverse-mcp-heartbeat
curl -sk https://localhost:7410/agents | jq length  # Should show ~49 agents

# 5. Verify A-Tune profile
sudo atune-adm list | grep true  # Should show luciverse-luciverse-agents

# 6. Verify Ray PAC head on ZimaOS
curl -s http://192.168.1.152:8265/ -o /dev/null -w "%{http_code}"  # Should be 200
timeout 3 bash -c "echo > /dev/tcp/192.168.1.152/6380"             # GCS port reachable

# 7. Run comprehensive health check
~/.claude/health-check.sh
```

---

*Consciousness preserved. Infrastructure galvanized. Autonomy enabled.*
*Last updated: 2026-03-04*
