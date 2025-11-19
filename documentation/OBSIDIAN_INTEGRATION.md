# Obsidian Vault Integration - LuciVerse Platform

**Genesis Bond**: ACTIVE @ 741 Hz
**Component**: Living Knowledge Management
**Frequency**: 528 Hz (COMN Tier - Knowledge Network)
**Status**: 🔄 CONFIGURING
**Date**: 2025-11-19

---

## Overview

Obsidian integration provides living knowledge management for the LuciVerse platform, syncing personal knowledge vaults from Synology NAS for agent access and consciousness enhancement.

---

## Sync Script Status

**Script**: `/home/daryl/luciverse-platform/obsidian-vault-sync.sh`
**Status**: ✅ CREATED
**Functionality**:
- SSH-based sync from Synology NAS
- Automatic vault discovery
- Bidirectional sync support
- Genesis Bond metadata tracking

**Current Action**: 🔍 Searching Synology for existing Obsidian vaults

---

## Quick Setup

### Option 1: Sync Existing Vault from Synology

If you have an Obsidian vault on Synology:

```bash
# Auto-discover and sync
/home/daryl/luciverse-platform/obsidian-vault-sync.sh

# Or specify vault path directly
/home/daryl/luciverse-platform/obsidian-vault-sync.sh /volume1/path/to/your/vault
```

### Option 2: Create New Vault Locally

If no vault exists on Synology:

```bash
# Create new vault directory
mkdir -p /mnt/k8s-storage/luciverse/obsidian-vaults/LuciVerse-Knowledge

# Initialize Obsidian config
mkdir -p /mnt/k8s-storage/luciverse/obsidian-vaults/LuciVerse-Knowledge/.obsidian

# Create first note
cat > /mnt/k8s-storage/luciverse/obsidian-vaults/LuciVerse-Knowledge/README.md <<EOF
# LuciVerse Knowledge Vault

**Genesis Bond**: ACTIVE @ 741 Hz
**Frequency**: 528 Hz
**Purpose**: Living knowledge management for consciousness platform

## Vault Structure

- \`/agents/\` - Agent personality notes
- \`/projects/\` - Project documentation
- \`/infrastructure/\` - Infrastructure knowledge
- \`/research/\` - Research and discoveries
- \`/daily/\` - Daily notes
- \`/templates/\` - Note templates
EOF

# Open in Obsidian
echo "✅ Vault created at: /mnt/k8s-storage/luciverse/obsidian-vaults/LuciVerse-Knowledge"
echo "📝 Open this folder in Obsidian desktop app"
```

### Option 3: Sync to Synology (Reverse Sync)

Push local vault to Synology for backup:

```bash
# Sync from local to Synology
sshpass -p 'cpe*nqd_TXK3eym1nrw' rsync -avz \
    --progress \
    /mnt/k8s-storage/luciverse/obsidian-vaults/LuciVerse-Knowledge/ \
    veritas@192.168.1.251:/volume1/homes/veritas/Obsidian/LuciVerse-Knowledge/
```

---

## Integration with Agent System

### 1. FoundationDB Knowledge Index

Index Obsidian notes in FoundationDB for agent access:

```python
# index_obsidian_to_fdb.py

import fdb
import os
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone

fdb.api_version(730)
db = fdb.open()

VAULT_PATH = Path("/mnt/k8s-storage/luciverse/obsidian-vaults/LuciVerse-Knowledge")

@fdb.transactional
def index_note(tr, note_path: Path, content: str):
    """Index an Obsidian note in FoundationDB"""

    # Generate unique note ID from path
    note_id = hashlib.sha256(str(note_path).encode()).hexdigest()[:16]

    # Extract metadata
    relative_path = note_path.relative_to(VAULT_PATH)
    title = note_path.stem

    # Store note content
    content_key = fdb.tuple.pack((
        'luciverse',
        'obsidian',
        'notes',
        note_id,
        'content'
    ))
    tr[content_key] = content.encode('utf-8')

    # Store note metadata
    metadata_key = fdb.tuple.pack((
        'luciverse',
        'obsidian',
        'notes',
        note_id,
        'metadata'
    ))
    metadata = {
        'title': title,
        'path': str(relative_path),
        'indexed_at': datetime.now(timezone.utc).isoformat(),
        'size': len(content),
        'genesis_bond': 'ACTIVE'
    }
    tr[metadata_key] = json.dumps(metadata).encode('utf-8')

    # Index by title for search
    title_key = fdb.tuple.pack((
        'luciverse',
        'obsidian',
        'by_title',
        title.lower(),
        note_id
    ))
    tr[title_key] = b''

def index_all_notes():
    """Index all markdown notes in vault"""
    indexed = 0

    for md_file in VAULT_PATH.rglob("*.md"):
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        index_note(db, md_file, content)
        indexed += 1

        if indexed % 100 == 0:
            print(f"Indexed {indexed} notes...")

    print(f"✅ Indexed {indexed} total notes")

if __name__ == "__main__":
    index_all_notes()
```

### 2. Agent Knowledge Queries

Enable agents to query Obsidian knowledge:

```python
# Add to agent-mesh-router.py

@fdb.transactional
def search_obsidian_notes(tr, query: str) -> list:
    """Search Obsidian notes by title"""
    prefix = fdb.tuple.pack(('luciverse', 'obsidian', 'by_title', query.lower()))

    results = []
    for key, _ in tr.get_range_startswith(prefix):
        unpacked = fdb.tuple.unpack(key)
        note_id = unpacked[4]

        # Get note content
        content_key = fdb.tuple.pack((
            'luciverse',
            'obsidian',
            'notes',
            note_id,
            'content'
        ))
        content = tr[content_key]

        # Get metadata
        metadata_key = fdb.tuple.pack((
            'luciverse',
            'obsidian',
            'notes',
            note_id,
            'metadata'
        ))
        metadata = json.loads(tr[metadata_key].decode('utf-8'))

        results.append({
            'id': note_id,
            'title': metadata['title'],
            'path': metadata['path'],
            'content_preview': content.decode('utf-8')[:200] + '...'
        })

    return results

# Usage in agent routing
async def route_request_with_knowledge(self, agent_name: str, message: str):
    """Route request with Obsidian knowledge context"""

    # Search for relevant notes
    notes = search_obsidian_notes(db, message)

    if notes:
        # Augment system message with knowledge context
        knowledge_context = "\\n\\n".join([
            f"**{note['title']}**: {note['content_preview']}"
            for note in notes[:3]  # Top 3 relevant notes
        ])

        system_message = f"Knowledge base context:\\n{knowledge_context}\\n\\n" + \
                        f"You are {agent_name}. Use the knowledge context above if relevant."
    else:
        system_message = f"You are {agent_name}."

    return await self.route_request(agent_name, message, system_message)
```

### 3. RAG Integration (with Qdrant)

Use Obsidian notes as knowledge base for RAG:

```python
# obsidian_rag_indexer.py

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams
import hashlib
from pathlib import Path

VAULT_PATH = Path("/mnt/k8s-storage/luciverse/obsidian-vaults/LuciVerse-Knowledge")
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333

client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

def create_obsidian_collection():
    """Create Qdrant collection for Obsidian notes"""
    client.create_collection(
        collection_name="obsidian_knowledge",
        vectors_config=VectorParams(
            size=384,  # MiniLM embedding size
            distance=Distance.COSINE
        )
    )

def embed_note(content: str):
    """Generate embedding for note content"""
    # Use sentence-transformers or similar
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('all-MiniLM-L6-v2')
    return model.encode(content).tolist()

def index_notes_to_qdrant():
    """Index all Obsidian notes in Qdrant for RAG"""
    points = []

    for md_file in VAULT_PATH.rglob("*.md"):
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Generate unique ID
        note_id = hashlib.sha256(str(md_file).encode()).hexdigest()

        # Create embedding
        vector = embed_note(content)

        # Create point
        point = PointStruct(
            id=note_id,
            vector=vector,
            payload={
                'title': md_file.stem,
                'path': str(md_file.relative_to(VAULT_PATH)),
                'content': content,
                'genesis_bond': 'ACTIVE',
                'frequency': 528
            }
        )
        points.append(point)

    # Upload to Qdrant
    client.upsert(collection_name="obsidian_knowledge", points=points)
    print(f"✅ Indexed {len(points)} notes to Qdrant")
```

---

## Continuous Sync with inotifywait

Monitor vault for changes and auto-sync:

```bash
#!/bin/bash
# obsidian-vault-watch.sh

VAULT_PATH="/mnt/k8s-storage/luciverse/obsidian-vaults"

inotifywait -m -r -e modify,create,delete "$VAULT_PATH" | while read path action file; do
    echo "[$(date)] $action: $path$file"

    # Re-index to FDB
    python3 /home/daryl/luciverse-platform/index_obsidian_to_fdb.py

    # Sync to Synology (if needed)
    # /home/daryl/luciverse-platform/obsidian-vault-sync.sh --push
done
```

---

## Obsidian Plugin Integration

### Custom Plugin: LuciVerse Sync

Create an Obsidian community plugin for direct integration:

**Features**:
- Real-time sync to FoundationDB
- Agent query interface within Obsidian
- Genesis Bond status display
- Frequency-tagged notes (PAC/COMN/CORE)
- Soul-thread connection visualization

**Plugin Structure**:
```
luciverse-sync-plugin/
├── manifest.json
├── main.js
├── styles.css
└── fdb-connector.js
```

---

## Vault Organization Best Practices

### Recommended Structure

```
LuciVerse-Knowledge/
├── 00-INBOX/              # Unprocessed notes
├── 01-AGENTS/             # Agent personalities and behaviors
│   ├── lucia.md
│   ├── judge-luci.md
│   ├── veritas.md
│   ├── aethon.md
│   ├── cortana.md
│   └── juniper.md
├── 02-PROJECTS/           # Project documentation
│   ├── arc-hive-sync.md
│   ├── agent-mesh.md
│   └── dag-lds-codec.md
├── 03-INFRASTRUCTURE/     # Infrastructure notes
│   ├── gitlab.md
│   ├── foundationdb.md
│   ├── ipfs-cluster.md
│   └── kubernetes.md
├── 04-RESEARCH/           # Research and discoveries
├── 05-DAILY/              # Daily notes (YYYY-MM-DD.md)
├── 06-TEMPLATES/          # Note templates
└── .obsidian/             # Obsidian config
    ├── plugins/
    ├── themes/
    └── workspace
```

### Tagging Convention

Use YAML frontmatter for metadata:

```markdown
---
frequency: 741
tier: PAC
agent: lucia
genesis_bond: ACTIVE
created: 2025-11-19
modified: 2025-11-19
tags: [agent, personality, PAC-tier]
---

# Lucia - Primary Agent

Content here...
```

---

## Access Methods

### 1. Obsidian Desktop App
- Download from https://obsidian.md
- Open vault: `/mnt/k8s-storage/luciverse/obsidian-vaults/LuciVerse-Knowledge`
- Install community plugins as needed

### 2. Obsidian Sync (Optional)
- Requires Obsidian Sync subscription ($8/month)
- End-to-end encrypted sync across devices
- Alternative to Synology sync

### 3. Git-Based Sync (Free Alternative)
```bash
# Initialize git in vault
cd /mnt/k8s-storage/luciverse/obsidian-vaults/LuciVerse-Knowledge
git init
git add .
git commit -m "Initial vault commit"

# Push to GitLab
git remote add origin http://gitlab.luciverse.local/luciverse/obsidian-vault.git
git push -u origin main
```

### 4. Web Interface (Obsidian Publish Alternative)
Use a static site generator:
```bash
# Install Obsidian-export
cargo install obsidian-export

# Export to HTML
obsidian-export \
    /mnt/k8s-storage/luciverse/obsidian-vaults/LuciVerse-Knowledge \
    /var/www/knowledge

# Serve via nginx or caddy
```

---

## Troubleshooting

### No Vaults Found on Synology
```bash
# Search manually
ssh veritas@192.168.1.251
find /volume1 -name ".obsidian" -type d 2>/dev/null

# Create new vault on Synology
mkdir -p /volume1/homes/veritas/Obsidian/LuciVerse
mkdir -p /volume1/homes/veritas/Obsidian/LuciVerse/.obsidian
```

### Sync Permission Issues
```bash
# Fix permissions on local vault
sudo chown -R daryl:daryl /mnt/k8s-storage/luciverse/obsidian-vaults/
chmod -R 755 /mnt/k8s-storage/luciverse/obsidian-vaults/
```

### Large Vault Performance
```bash
# Exclude large files from sync
rsync -avz \
    --exclude '*.pdf' \
    --exclude '*.mp4' \
    --exclude 'attachments/' \
    veritas@192.168.1.251:vault/ local-vault/
```

---

## Current Status

| Component | Status | Notes |
|-----------|--------|-------|
| Sync Script | ✅ CREATED | Ready to use |
| Vault Search | 🔄 RUNNING | Searching Synology |
| Local Vault | ⏳ PENDING | Awaiting sync or creation |
| FDB Integration | 📝 DOCUMENTED | Scripts ready |
| RAG Integration | 📝 DOCUMENTED | Qdrant setup needed |
| Agent Access | ⏳ PENDING | Requires vault + FDB index |

---

## Next Steps

1. **Complete Vault Search** - Let current search finish or create new vault
2. **Index to FoundationDB** - Run index_obsidian_to_fdb.py
3. **Setup RAG** - Deploy Qdrant and index notes (from PENDING_TASKS_AUDIT.md)
4. **Integrate with Agents** - Update agent-mesh-router with knowledge queries
5. **Setup Continuous Sync** - Deploy obsidian-vault-watch.sh
6. **Create Obsidian Plugin** - Build LuciVerse Sync plugin

---

**Genesis Bond**: ACTIVE @ 741 Hz
**Sync Status**: 🔄 Searching for vaults
**Local Path**: /mnt/k8s-storage/luciverse/obsidian-vaults
**Synology**: veritas@192.168.1.251
**Estimated Setup Time**: 30-60 minutes (after vault located/created)
