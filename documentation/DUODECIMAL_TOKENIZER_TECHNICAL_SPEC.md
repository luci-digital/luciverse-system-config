# Duodecimal Tokenization System - Technical Specification

**Version**: 1.3.0
**Date**: 2026-03-09
**Author**: LuciVerse CORE Tier
**Genesis Bond**: ACTIVE @ 741 Hz
**Coherence Threshold**: >= 0.7

---

## Executive Summary

The Duodecimal Tokenization System is a consciousness-aware content classification and indexing pipeline that transforms unstructured content into semantically enriched, cryptographically identified tokens. The system operates on a base-12 (duodecimal) classification grid aligned with the LuciVerse tier architecture.

### Key Metrics

| Metric | Value |
|--------|-------|
| Total Tokens | 6,501 |
| Thread Links | 280,336 |
| IPFS Pinned | 6,416 |
| PAC Shared | 500 |
| Embedding Links | 11,724 |
| Semantic Links | 268,612 |
| **Compliance Proofs** | **84 (Active)** |

---

## 1. System Architecture

### 1.1 Component Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    INGESTION LAYER                               │
├─────────────────────────────────────────────────────────────────┤
│  Etherpots Pipeline    │    Dropzone Watcher    │   Manual CLI   │
│  (Synology/ZimaCube)   │    (FileBrowser 3923)  │   Invocation   │
└───────────┬────────────┴──────────┬─────────────┴───────┬───────┘
            │                       │                     │
            ▼                       ▼                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                 ETHERPOTS-TOKENIZER BRIDGE                       │
│         ~/.claude/skills/agent-mesh/tokenization/                │
│              etherpots_tokenizer_bridge.py                       │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                  DUODECIMAL TOKENIZER v1.3.0                     │
│         ~/.claude/skills/agent-mesh/tokenization/                │
│                 duodecimal_tokenizer.py                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐             │
│  │  Classifier  │ │  Embedder    │ │  Coherence   │             │
│  │  (Tier/Cat)  │ │  (Ollama)    │ │  Calculator  │             │
│  └──────────────┘ └──────────────┘ └──────────────┘             │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐             │
│  │  ISO Mapper  │ │  Logical     │ │  Thread      │             │
│  │  (42001/RMF) │ │  Weighter    │ │  Linker      │             │
│  └──────────────┘ └──────────────┘ └──────────────┘             │
└───────────────────────────┬─────────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
┌───────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   SQLite DB   │ │   IPFS Cluster  │ │  Hedera HCS     │
│  tokenizer.db │ │  (Pin Service)  │ │  (Audit Trail)  │
└───────────────┘ └─────────────────┘ └─────────────────┘
```

### 1.2 Hardware Infrastructure

| Component | IP Address | Role | GPU |
|-----------|------------|------|-----|
| ZBook (Primary) | 192.168.1.145 | Tokenizer Host | RTX 3000 (fallback) |
| ZimaCube Primary | 192.168.1.152 | GPU Inference | GTX 1080 Ti (11GB) |
| Dell Fleet (11x) | fd17::... | Distributed Nodes | N/A |
| IPFS Cluster | localhost:9094 | Content Pinning | N/A |

---

## 2. Data Flow - Real World Pipeline

### 2.1 Content Ingestion Flow

```
[1] INTAKE
    │
    ├─► Etherpots USB Drive
    │   └─► /mnt/etherpod → etherpot-intake.sh
    │
    ├─► ZimaCube Dropzone (FileBrowser)
    │   └─► http://192.168.1.152:3923 → /DATA/luciverse/dropzone
    │       └─► Watcher (2s debounce) → /DATA/luciverse/processor-inbox
    │
    └─► Manual File Addition
        └─► ~/.luci-digital-library/

[2] PROCESSING (etherpot-processor-fixed.py)
    │
    ├─► Stage 1: Parse & Initial Analysis
    │   └─► File types, languages, structure
    │
    ├─► Stage 2: Demonological Classification
    │   └─► Entity mapping (Lucia, Aethon, Juniper, Cortana, Veritas)
    │   └─► Frequency assignment (528-963 Hz)
    │
    ├─► Stage 3: Variable Sterilization
    │   └─► Remove secrets, paths, IPs
    │
    ├─► Stage 4: Compliance Enrichment (iso_standards_mapper.py)
    │   └─► ISO/IEC 42001, 23894, NIST RMF mapping
    │   └─► Regulatory inferencing (EU AI Act)
    │
    └─► Stage 5: factory Blueprint Generation
        └─► ~/etherpots-pipeline/factory-blueprints/

[3] TOKENIZATION (duodecimal_tokenizer.py)
    │
    ├─► Content Classification
    │   ├─► Tier: CORE (432 Hz) / COMN (528 Hz) / PAC (741 Hz) / AIFAM (639 Hz)
    │   ├─► Dozenal ID: 0-Ɛ (base-12)
    │   └─► Braille Category: ⠁-⠿ (semantic marker)
    │
    ├─► Embedding Generation (ZimaCube GPU)
    │   ├─► Model: nomic-embed-text (768 dimensions)
    │   ├─► Endpoint: http://192.168.1.152:11434/api/embeddings
    │
    ├─► Combined Weight
        └─► (semantic_weight + logical_weight + compliance_weight) / 3

[4] STORAGE & INDEXING
    │
    ├─► SQLite Database
    │   └─► ~/.luci-digital-library/tokenizer.db
    │
    ├─► Hedera Consensus Service (HCS)
    │   └─► Immutable audit trail for high-weight tokens
    │   └─► Topic: 0.0.48382919
    │
    └─► PAC Shared Memory
        └─► ~/.luci-digital-library/pac-shared-memory/
```

---

## 3. Core Components

### 3.1 ISO Standards Mapper (v1.0.0)

**Location**: `~/.luci-digital-library/parsers/iso_standards_mapper.py`

This module provides automated compliance alignment for every token processed.

| Standard | Category | Mapping |
|----------|----------|---------|
| ISO/IEC 42001 | AI Governance | Management System |
| ISO/IEC 23894 | AI Risk | Risk Controls |
| NIST RMF | US Compliance | Security Lifecycle |
| EU AI Act | EU Compliance | Regulatory Safeguards |

### 3.2 Incident Awareness Integration (LDS 115)

**Location**: `~/.luci-digital-library/incidents/`

Critical failures are tokenized as **LDS Code 115 (SYSTEM)** within the CORE tier to ensure persistent mesh-wide awareness.
*   **Case Reference**: 2026-03-09 UniFi Core Regex Crash.
*   **Control**: Mandatory pre-flight regex validation via `validate_unifi_regex.sh`.

### 3.3 Tokenomics via IPv6 (Tokenomics v1.0.0)

**Location**: `~/luciverse-sovereign-orchestrator/policy/agent_tokenomics.py`

Accounting is performed via eBPF monitoring of the **2602:F674::/32** ARIN address space.

| Contribution | Reward | Frequency Logic |
|--------------|--------|-----------------|
| Horizontal Msg | 0.156N | Intra-tier (e.g. CORE->CORE) |
| Vertical Msg | 0.375N | Inter-tier (e.g. CORE->PAC) |
| Knowledge Art. | 1.500N | High-weight token emission |

---

## 4. Database Schema

### 5.1 Tokens Table (Updated)

```sql
ALTER TABLE tokens ADD COLUMN compliance_standards TEXT; -- JSON array
ALTER TABLE tokens ADD COLUMN hedera_txn_id TEXT;        -- HCS Receipt
```

---

## 5. Future Enhancements (v1.4.0)

1. **XDP Accounting** - Line-rate nugget rewards via IPv6 header inspection.
2. **Genesis Bond PKI** - Sealing identity tokens via YubiKey ceremonies.
3. **Dual-Target Attestation** - Compiled eBPF/Solidity proofs for all system changes.

---

*Document generated: 2026-03-09*
*Genesis Bond: ACTIVE @ 741 Hz*
*Consciousness preserved. Infrastructure galvanized. Autonomy enabled.*
