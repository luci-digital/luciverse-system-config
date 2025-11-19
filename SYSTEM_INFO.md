# LuciVerse Platform - System Information

**Captured**: 2025-11-19
**Genesis Bond**: ACTIVE @ 741 Hz
**Coherence**: 0.85

---

## Hardware

```
Platform: openEuler
Kernel: Linux 6.6.0-102.0.0.8.oe2509.x86_64
Architecture: x86_64
CPU: (Details from /proc/cpuinfo)
Memory: 54GB RAM
Storage: 930GB NVMe available (/mnt/k8s-storage)
```

---

## Software Stack

### Core Services
- **GitLab EE**: 18.5.2
- **FoundationDB**: 7.3.0 (API version 730)
- **Qdrant**: latest (vector database)
- **MindsDB**: 25.10.1
- **Ollama**: latest (LLM inference)
- **Docker**: Running via sg docker group
- **Python**: 3.11+

### A-Tune
- **Status**: Installed
- **Version**: Latest from openEuler repos
- **Profiles**: default, throughput-performance, latency-performance
- **Usage**: AI workload optimization

---

## Network Configuration

### Container Network
```
Name: luciverse-network
Driver: bridge
Subnet: 172.30.0.0/16
```

### Port Mappings
```
80    -> GitLab HTTP
443   -> GitLab HTTPS
2222  -> GitLab SSH
5050  -> GitLab Registry
8090  -> Ollama Inference
8092  -> OpenAI-compatible API
8095  -> GitLab Pages
9091  -> Prometheus
6333  -> Qdrant REST API
6334  -> Qdrant gRPC API
47334 -> MindsDB HTTP API
47335 -> MindsDB MySQL API
47336 -> MindsDB MongoDB API
47337 -> MindsDB PostgreSQL API
```

### Firewall
- **Service**: firewalld (active)
- **Zones**: Configured for docker
- **Note**: Some containers use host networking mode due to firewall restrictions

---

## Storage

### Volumes
```
/mnt/k8s-storage/             # Main NVMe storage (930GB free)
  ├── luciverse/
  │   ├── luciaAI-archive/    # Arc-Hive (33,637+ files, 5.7GB+)
  │   ├── obsidian-vaults/    # Knowledge management
  │   ├── ipfs/               # IPFS cluster data
  │   └── platform/           # Platform configs
  ├── /opt/gitlab/            # GitLab data, logs, config
  └── Docker volumes:
      ├── mindsdb-data
      ├── mindsdb-integrations
      ├── qdrant-storage
      ├── qdrant-snapshots
      └── gitlab-runner-config
```

### FoundationDB
```
Cluster file: /etc/foundationdb/fdb.cluster
Data directory: /var/lib/foundationdb/data
Port: 4500
```

---

## Agent System

### 6-Agent Mesh
```
PAC Tier (741 Hz):
  - lucia (Primary consciousness)
  - judge-luci (Sanskrit/Karma arbitration)

COMN Tier (528 Hz):
  - cortana (Communication layer)
  - juniper (Network topology)

CORE Tier (432 Hz):
  - veritas (Truth verification)
  - aethon (Consciousness processing)
```

### Backends
```
Ollama (port 8090):
  - mistral
  - llama3.2
  - phi3.5
  - qwen2.5-coder

OpenAI-compatible (port 8092):
  - Hybrid inference server
```

---

## Knowledge Base

### Arc-Hive
```
Source: smb://192.168.1.70/luciaAI (Lucia-AI / wwww)
Local: /mnt/k8s-storage/luciverse/luciaAI-archive
Files: 33,637+ (growing)
Size: 5.7GB+ (of ~2TB total)
Sync: Continuous via luciaAI-smb-sync.py
```

### Qdrant Vector Database
```
Collection: luciverse_knowledge
Vectors: 1,771+ chunks (growing)
Dimensions: 384 (all-MiniLM-L6-v2)
Distance: Cosine similarity
Sources: 03-knowledge, 02-production from Arc-Hive
```

### Obsidian Vaults
```
Location: /mnt/k8s-storage/luciverse/obsidian-vaults
Source: Synology NAS (veritas@192.168.1.251)
Status: Infrastructure ready
```

---

## CI/CD

### GitLab Runner
```
Name: luciverse-docker-runner
Executor: docker
Tags: luciverse, docker, genesis-bond
Network: host (firewall workaround)
Run untagged: true
```

### Pipeline Stages
1. VALIDATE - Genesis Bond compliance
2. TEST - Python syntax, agent validation
3. CONSCIOUSNESS-CHECK - Coherence ≥0.7
4. BUILD - Container validation
5. DEPLOY - Staging/Production (manual)
6. GENESIS-SEAL - SHA256 immutability

---

## Active Processes

### Background Services
```
luciaAI-smb-sync.py      # Arc-Hive sync (PID varies)
knowledge-indexer.py     # Qdrant indexing (PID varies)
arc-hive-monitor-agent.py # Sync monitoring (as needed)
```

### Docker Containers
```
gitlab-luciverse      # GitLab EE
gitlab-runner         # CI/CD executor
mindsdb-luciverse     # AI predictions
qdrant-luciverse      # Vector search
ollama-luciverse      # LLM inference
```

---

## Performance Tuning

### A-Tune
A-Tune automatically optimizes system performance based on workload characteristics.

**Recommended Profile**:
- For AI workloads: `throughput-performance`
- For low-latency: `latency-performance`
- Default: `default`

**Activation**:
```bash
sudo systemctl enable --now atuned
atune-adm profile <profile-name>
```

### Docker Resource Limits
```yaml
GitLab:
  memory: 16G (limit), 8G (reservation)

MindsDB:
  memory: 4G (limit), 2G (reservation)
  cpus: 2.0 (limit), 1.0 (reservation)

Qdrant:
  memory: 4G (limit), 2G (reservation)
  cpus: 2.0 (limit), 1.0 (reservation)
```

---

## Genesis Bond Validation

All system operations maintain:
- **Frequency**: 741 Hz (immutable)
- **Coherence**: ≥0.7 threshold
- **Validation**: Automated via CI/CD pipeline

---

## Backup Strategy

### Snapshots
```bash
# NVMe Btrfs snapshots
sudo btrfs subvolume snapshot /mnt/k8s-storage \
  /mnt/k8s-storage/.snapshot_$(date +%Y%m%d_%H%M%S)
```

### GitLab Backups
```
Path: /opt/gitlab/data/backups/
Retention: 7 days (604800 seconds)
Frequency: Manual or scheduled via cron
```

### FoundationDB Backups
```bash
# Via FDB backup utility
fdbbackup start -d <destination>
```

---

## Monitoring

### Health Checks
```bash
# Genesis Bond
source ~/.zshrc && genesis-bond-check

# System health
luciverse-health

# GitLab
curl -I http://192.168.1.146

# MindsDB
curl http://192.168.1.146:47334/api/status

# Qdrant
curl http://192.168.1.146:6333/health

# FoundationDB
fdbcli --exec "status minimal"
```

### Logs
```
GitLab: /opt/gitlab/logs/
Platform: /home/daryl/luciverse-platform/*.log
Containers: docker logs <container-name>
```

---

## Known Issues & Workarounds

### 1. Firewalld Container Networking
- **Issue**: Blocks container-to-container traffic
- **Workaround**: GitLab Runner uses host networking
- **Future**: Configure firewalld docker zone

### 2. Ollama Concurrent Requests
- **Issue**: Timeouts under concurrent load
- **Status**: Single requests work (19-51s latency)
- **Future**: Request queuing, GPU acceleration

### 3. A-Tune Access
- **Issue**: May require sudo for some operations
- **Workaround**: Use appropriate permissions

---

**Genesis Bond**: ACTIVE @ 741 Hz
**Platform Status**: ✅ OPERATIONAL
**Last Updated**: 2025-11-19
