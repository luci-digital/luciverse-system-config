#!/usr/bin/env python3
"""
Knowledge Indexer - LuciVerse RAG System
=========================================

Indexes Arc-Hive knowledge into Qdrant for semantic search and RAG.
Integrates with FoundationDB for metadata and agent access.

Genesis Bond: ACTIVE | Frequency: 528 Hz (COMN - Knowledge Network)
"""

import os
import hashlib
import json
import asyncio
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

# Vector database
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct,
    Filter, FieldCondition, MatchValue
)

# Embeddings
from sentence_transformers import SentenceTransformer

# Database
import fdb

# Logging
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('/home/daryl/luciverse-platform/knowledge-indexer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('knowledge-indexer')

# Configuration
QDRANT_HOST = "192.168.1.146"
QDRANT_PORT = 6333
ARC_HIVE_ROOT = Path("/mnt/k8s-storage/luciverse/luciaAI-archive")
OBSIDIAN_ROOT = Path("/mnt/k8s-storage/luciverse/obsidian-vaults")
COLLECTION_NAME = "luciverse_knowledge"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # 384 dimensions, fast
BATCH_SIZE = 100

# FoundationDB
fdb.api_version(730)
db = fdb.open()


class KnowledgeIndexer:
    """Index knowledge from Arc-Hive and Obsidian into Qdrant"""

    def __init__(self):
        self.qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        self.genesis_bond = "ACTIVE"
        self.frequency = 528  # COMN tier

        logger.info("🔬 Knowledge Indexer - Genesis Bond @ 528 Hz")
        logger.info(f"   Qdrant: {QDRANT_HOST}:{QDRANT_PORT}")
        logger.info(f"   Embedding Model: {EMBEDDING_MODEL}")
        logger.info("")

    def ensure_collection(self):
        """Create Qdrant collection if it doesn't exist"""
        try:
            self.qdrant.get_collection(COLLECTION_NAME)
            logger.info(f"✅ Collection '{COLLECTION_NAME}' exists")
        except Exception:
            logger.info(f"📝 Creating collection '{COLLECTION_NAME}'...")
            self.qdrant.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=384,  # MiniLM embedding dimension
                    distance=Distance.COSINE
                )
            )
            logger.info(f"✅ Collection created")

    def generate_document_id(self, file_path: Path) -> str:
        """Generate unique ID for document"""
        return hashlib.sha256(str(file_path).encode()).hexdigest()

    def chunk_text(self, text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks for better retrieval"""
        words = text.split()
        chunks = []

        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk:
                chunks.append(chunk)

        return chunks if chunks else [text]

    def extract_metadata(self, file_path: Path, content: str) -> Dict[str, Any]:
        """Extract metadata from file and content"""
        stat = file_path.stat()

        metadata = {
            'filename': file_path.name,
            'path': str(file_path),
            'relative_path': str(file_path.relative_to(file_path.parent.parent)) if file_path.is_relative_to(file_path.parent.parent) else str(file_path),
            'extension': file_path.suffix,
            'size': stat.st_size,
            'modified': datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
            'indexed_at': datetime.now(timezone.utc).isoformat(),
            'genesis_bond': self.genesis_bond,
            'frequency': self.frequency
        }

        # Detect tier from path
        path_str = str(file_path).lower()
        if 'pac-' in path_str or '/pac/' in path_str:
            metadata['tier'] = 'PAC'
            metadata['tier_frequency'] = 741
        elif 'comn-' in path_str or '/comn/' in path_str:
            metadata['tier'] = 'COMN'
            metadata['tier_frequency'] = 528
        elif 'core-' in path_str or '/core/' in path_str:
            metadata['tier'] = 'CORE'
            metadata['tier_frequency'] = 432
        else:
            metadata['tier'] = 'UNKNOWN'
            metadata['tier_frequency'] = 0

        # Extract keywords from content
        if content:
            words = content.lower().split()
            metadata['word_count'] = len(words)
            # Simple keyword extraction (top frequent non-common words)
            word_freq = {}
            common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
            for word in words:
                cleaned = ''.join(c for c in word if c.isalnum())
                if cleaned and cleaned not in common_words and len(cleaned) > 3:
                    word_freq[cleaned] = word_freq.get(cleaned, 0) + 1

            top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
            metadata['keywords'] = [kw[0] for kw in top_keywords]

        return metadata

    @fdb.transactional
    def store_in_fdb(self, tr, doc_id: str, metadata: Dict[str, Any]):
        """Store document metadata in FoundationDB"""
        key = fdb.tuple.pack(('luciverse', 'knowledge', 'documents', doc_id))
        value = json.dumps(metadata).encode('utf-8')
        tr[key] = value

        # Index by tier
        tier_key = fdb.tuple.pack((
            'luciverse', 'knowledge', 'by_tier',
            metadata.get('tier', 'UNKNOWN'), doc_id
        ))
        tr[tier_key] = b''

    def index_file(self, file_path: Path) -> int:
        """Index a single file into Qdrant and FDB"""
        try:
            # Read content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            if not content.strip():
                return 0  # Skip empty files

            # Generate document ID
            doc_id = self.generate_document_id(file_path)

            # Extract metadata
            metadata = self.extract_metadata(file_path, content)

            # Store in FDB
            self.store_in_fdb(db, doc_id, metadata)

            # Chunk text
            chunks = self.chunk_text(content)

            # Create points for each chunk
            points = []
            for chunk_idx, chunk in enumerate(chunks):
                # Generate embedding
                embedding = self.model.encode(chunk).tolist()

                # Create point - use hash of doc_id+chunk_idx as integer ID
                point_id_str = f"{doc_id}_{chunk_idx}"
                point_id = int(hashlib.sha256(point_id_str.encode()).hexdigest()[:15], 16)

                payload = {
                    **metadata,
                    'chunk_index': chunk_idx,
                    'chunk_text': chunk[:500],  # Store preview
                    'total_chunks': len(chunks),
                    'point_id_str': point_id_str  # Store string ID for reference
                }

                point = PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=payload
                )
                points.append(point)

            # Upload to Qdrant in batches
            for i in range(0, len(points), BATCH_SIZE):
                batch = points[i:i + BATCH_SIZE]
                self.qdrant.upsert(
                    collection_name=COLLECTION_NAME,
                    points=batch
                )

            logger.info(f"✅ Indexed: {file_path.name} ({len(chunks)} chunks)")
            return len(chunks)

        except Exception as e:
            logger.error(f"❌ Error indexing {file_path}: {e}")
            return 0

    def index_directory(self, directory: Path, extensions: List[str] = None) -> Dict[str, int]:
        """Index all files in a directory"""
        if extensions is None:
            extensions = ['.md', '.txt', '.py', '.yaml', '.yml', '.json', '.rst']

        stats = {
            'files_indexed': 0,
            'chunks_created': 0,
            'files_skipped': 0,
            'errors': 0
        }

        logger.info(f"📂 Indexing directory: {directory}")
        logger.info(f"   Extensions: {extensions}")
        logger.info("")

        if not directory.exists():
            logger.warning(f"⚠️  Directory does not exist: {directory}")
            return stats

        for file_path in directory.rglob("*"):
            if file_path.is_file() and file_path.suffix in extensions:
                # Skip hidden files and special directories
                if any(part.startswith('.') for part in file_path.parts):
                    stats['files_skipped'] += 1
                    continue

                chunks = self.index_file(file_path)
                if chunks > 0:
                    stats['files_indexed'] += 1
                    stats['chunks_created'] += chunks
                else:
                    stats['files_skipped'] += 1

                # Progress update every 10 files
                if (stats['files_indexed'] + stats['files_skipped']) % 10 == 0:
                    logger.info(f"📊 Progress: {stats['files_indexed']} files indexed, "
                              f"{stats['chunks_created']} chunks created")

        return stats

    def search(self, query: str, limit: int = 5, tier_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search knowledge base"""
        # Generate query embedding
        query_embedding = self.model.encode(query).tolist()

        # Optional tier filter
        search_filter = None
        if tier_filter:
            search_filter = Filter(
                must=[
                    FieldCondition(
                        key="tier",
                        match=MatchValue(value=tier_filter)
                    )
                ]
            )

        # Search Qdrant
        results = self.qdrant.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_embedding,
            limit=limit,
            query_filter=search_filter
        )

        return [
            {
                'score': hit.score,
                'filename': hit.payload.get('filename'),
                'path': hit.payload.get('path'),
                'tier': hit.payload.get('tier'),
                'chunk_text': hit.payload.get('chunk_text'),
                'chunk_index': hit.payload.get('chunk_index'),
                'total_chunks': hit.payload.get('total_chunks')
            }
            for hit in results
        ]


async def main():
    """Main indexing workflow"""
    indexer = KnowledgeIndexer()

    # Ensure collection exists
    indexer.ensure_collection()

    # Index Arc-Hive (priority directories first)
    priority_dirs = [
        ARC_HIVE_ROOT / "03-knowledge",
        ARC_HIVE_ROOT / "02-production",
        ARC_HIVE_ROOT / "01-specifications"
    ]

    total_stats = {
        'files_indexed': 0,
        'chunks_created': 0,
        'files_skipped': 0
    }

    for directory in priority_dirs:
        if directory.exists():
            logger.info(f"\n{'='*60}")
            logger.info(f"📚 Indexing: {directory.name}")
            logger.info(f"{'='*60}\n")

            stats = indexer.index_directory(directory)
            total_stats['files_indexed'] += stats['files_indexed']
            total_stats['chunks_created'] += stats['chunks_created']
            total_stats['files_skipped'] += stats['files_skipped']

            logger.info(f"\n✅ {directory.name} complete:")
            logger.info(f"   Files: {stats['files_indexed']}")
            logger.info(f"   Chunks: {stats['chunks_created']}")
            logger.info(f"   Skipped: {stats['files_skipped']}\n")
        else:
            logger.warning(f"⚠️  Directory not found: {directory}")

    # Index Obsidian vaults if they exist
    if OBSIDIAN_ROOT.exists():
        logger.info(f"\n{'='*60}")
        logger.info(f"🧠 Indexing Obsidian Vaults")
        logger.info(f"{'='*60}\n")

        obs_stats = indexer.index_directory(OBSIDIAN_ROOT, extensions=['.md'])
        total_stats['files_indexed'] += obs_stats['files_indexed']
        total_stats['chunks_created'] += obs_stats['chunks_created']
        total_stats['files_skipped'] += obs_stats['files_skipped']

        logger.info(f"\n✅ Obsidian complete:")
        logger.info(f"   Notes: {obs_stats['files_indexed']}")
        logger.info(f"   Chunks: {obs_stats['chunks_created']}\n")

    # Final summary
    logger.info(f"\n{'='*60}")
    logger.info(f"📊 Indexing Complete")
    logger.info(f"{'='*60}")
    logger.info(f"   Total Files: {total_stats['files_indexed']}")
    logger.info(f"   Total Chunks: {total_stats['chunks_created']}")
    logger.info(f"   Files Skipped: {total_stats['files_skipped']}")
    logger.info(f"{'='*60}")
    logger.info(f"🎵 Genesis Bond: ACTIVE @ 528 Hz")
    logger.info(f"{'='*60}\n")

    # Test search
    logger.info("🔍 Testing search functionality...\n")
    test_queries = [
        "agent mesh architecture",
        "FoundationDB schema",
        "consciousness frequency"
    ]

    for query in test_queries:
        results = indexer.search(query, limit=3)
        logger.info(f"Query: '{query}'")
        for i, result in enumerate(results, 1):
            logger.info(f"  {i}. {result['filename']} "
                       f"(score: {result['score']:.3f}, tier: {result['tier']})")
        logger.info("")


if __name__ == "__main__":
    asyncio.run(main())
