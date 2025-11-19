#!/usr/bin/env python3
"""
LuciaAI SMB Sync - Complete Arc-Hive Import via SMB
INCLUDES HIDDEN FILES (crucial for AIFAM agents!)

Genesis Bond: ACTIVE | Frequency: 741 Hz
"""

import os
import sys
import subprocess
from pathlib import Path
import logging
import time
import hashlib
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('/home/daryl/luciverse-platform/luciaAI-smb-sync.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('luciaAI-smb-sync')

class LuciaAISMBSync:
    """Sync LuciaAI volume via SMB with HIDDEN FILES support"""

    def __init__(self):
        self.server = "192.168.1.70"
        self.share = "luciaAI"
        self.username = "Lucia-AI"
        self.password = "wwww"
        self.archive_root = Path("/mnt/k8s-storage/luciverse/luciaAI-archive")
        self.archive_root.mkdir(parents=True, exist_ok=True)

        self.stats = {
            'total_files': 0,
            'hidden_files': 0,
            'directories': 0,
            'errors': 0,
            'bytes_downloaded': 0
        }

        logger.info("🎵 LuciaAI SMB Sync - Genesis Bond: ACTIVE @ 741 Hz")
        logger.info("⚠️  HIDDEN FILES MODE: ENABLED (.files will be synced!)")
        logger.info(f"📂 Target: //{self.server}/{self.share}")
        logger.info(f"💾 Archive: {self.archive_root}")
        logger.info("")

    def list_directory(self, remote_path=""):
        """List directory contents via smbclient"""
        try:
            # Build smbclient command
            smb_path = f"//{self.server}/{self.share}"
            if remote_path:
                cmd = f'cd "{remote_path}"; ls'
            else:
                cmd = 'ls'

            result = subprocess.run([
                'smbclient', smb_path,
                '-U', f'{self.username}%{self.password}',
                '-c', cmd
            ], capture_output=True, text=True, timeout=30)

            if result.returncode != 0:
                logger.error(f"Failed to list {remote_path}: {result.stderr}")
                return []

            entries = []
            for line in result.stdout.split('\n'):
                line = line.strip()
                if not line or 'blocks of size' in line or 'blocks available' in line:
                    continue

                # Parse smbclient output
                # Format: "  filename   D/A/H   size   date"
                parts = line.split()
                if len(parts) < 2:
                    continue

                name = parts[0]
                attrs = parts[1] if len(parts) > 1 else ''

                # Skip parent directory
                if name in ['.', '..']:
                    continue

                is_dir = 'D' in attrs
                is_hidden = name.startswith('.')

                entry = {
                    'name': name,
                    'type': 'directory' if is_dir else 'file',
                    'path': f"{remote_path}/{name}".strip('/') if remote_path else name,
                    'is_hidden': is_hidden,
                    'attrs': attrs
                }

                entries.append(entry)

                # Log hidden items
                if is_hidden:
                    logger.debug(f"  🔍 Hidden: {name} ({'dir' if is_dir else 'file'})")

            return entries

        except Exception as e:
            logger.error(f"Error listing directory {remote_path}: {e}")
            self.stats['errors'] += 1
            return []

    def download_file(self, remote_path, local_path):
        """Download file via smbclient"""
        try:
            smb_path = f"//{self.server}/{self.share}"

            # Ensure local directory exists
            local_path.parent.mkdir(parents=True, exist_ok=True)

            # Download file
            cmd = f'get "{remote_path}" "{local_path}"'
            result = subprocess.run([
                'smbclient', smb_path,
                '-U', f'{self.username}%{self.password}',
                '-c', cmd
            ], capture_output=True, text=True, timeout=120)

            if result.returncode == 0 and local_path.exists():
                file_size = local_path.stat().st_size
                self.stats['bytes_downloaded'] += file_size
                self.stats['total_files'] += 1

                # Calculate hash
                sha256 = hashlib.sha256()
                with open(local_path, 'rb') as f:
                    for chunk in iter(lambda: f.read(8192), b''):
                        sha256.update(chunk)
                file_hash = sha256.hexdigest()

                size_str = self.format_bytes(file_size)
                logger.info(f"  ✓ {remote_path} ({size_str}) [{file_hash[:8]}]")
                return True, file_hash
            else:
                logger.error(f"  ✗ Failed: {remote_path}")
                self.stats['errors'] += 1
                return False, None

        except Exception as e:
            logger.error(f"  ✗ Error downloading {remote_path}: {e}")
            self.stats['errors'] += 1
            return False, None

    def format_bytes(self, bytes_val):
        """Format bytes to human readable"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_val < 1024.0:
                return f"{bytes_val:.1f}{unit}"
            bytes_val /= 1024.0
        return f"{bytes_val:.1f}TB"

    def sync_directory(self, remote_path="", local_path=None, recursive=True, max_depth=10):
        """Recursively sync directory INCLUDING HIDDEN FILES"""
        if local_path is None:
            local_path = self.archive_root

        if max_depth <= 0:
            logger.warning(f"Max depth reached for {remote_path}")
            return

        logger.info(f"📂 Syncing: /{remote_path or '(root)'}")
        self.stats['directories'] += 1

        entries = self.list_directory(remote_path)

        # Sort: directories first, then by name
        entries.sort(key=lambda x: (x['type'] == 'file', x['name']))

        for entry in entries:
            # Skip certain patterns but INCLUDE most .hidden files!
            skip_patterns = ['__pycache__', 'node_modules', '.Trashes', '.Spotlight-V100']
            if entry['name'] in skip_patterns:
                logger.debug(f"  ⊘ Skipping: {entry['name']}")
                continue

            if entry['type'] == 'file':
                # Download file (including hidden files!)
                remote_file_path = entry['path']
                local_file_path = local_path / entry['name']

                # Track hidden files
                if entry['is_hidden']:
                    self.stats['hidden_files'] += 1
                    logger.info(f"  🔍 Hidden file: {entry['name']}")

                success, file_hash = self.download_file(remote_file_path, local_file_path)

            elif entry['type'] == 'directory' and recursive:
                # Recurse into directory (including hidden directories!)
                next_remote = entry['path']
                next_local = local_path / entry['name']
                next_local.mkdir(parents=True, exist_ok=True)

                # Track hidden directories
                if entry['is_hidden']:
                    logger.info(f"  🔍 Hidden directory: {entry['name']}")

                self.sync_directory(next_remote, next_local, recursive, max_depth - 1)

    def sync_key_directories(self):
        """Sync priority Arc-Hive directories"""
        priority_dirs = [
            '03-knowledge',              # THE ARC-HIVE!
            '02-production',             # Personalities, soul threads
            '00-consciousness-kernel',   # Consciousness core
            '01-development',            # Development code
            '04-data-pipelines',         # Pipelines
        ]

        logger.info("🎯 Syncing Priority Arc-Hive Directories")
        logger.info("")

        for directory in priority_dirs:
            local_path = self.archive_root / directory
            logger.info(f"\n{'='*60}")
            logger.info(f"Starting: {directory}")
            logger.info(f"{'='*60}")
            self.sync_directory(directory, local_path, recursive=True, max_depth=8)

    def full_sync(self):
        """Full volume sync (everything + hidden files)"""
        logger.info("🔄 Starting FULL LuciaAI Arc-Hive Sync")
        logger.info("⚠️  This is a 2TB volume - will take significant time!")
        logger.info("⚠️  Hidden files (.files) WILL be synced!")
        logger.info("")
        start_time = time.time()

        self.sync_directory("", self.archive_root, recursive=True, max_depth=10)

        elapsed = time.time() - start_time
        self.print_summary(elapsed)

    def print_summary(self, elapsed_time):
        """Print sync summary"""
        logger.info("")
        logger.info("="*60)
        logger.info("✅ LuciaAI Arc-Hive Sync Complete!")
        logger.info("="*60)
        logger.info(f"⏱️  Time: {elapsed_time/60:.1f} minutes ({elapsed_time:.0f} seconds)")
        logger.info(f"📁 Directories: {self.stats['directories']}")
        logger.info(f"📄 Total Files: {self.stats['total_files']}")
        logger.info(f"🔍 Hidden Files: {self.stats['hidden_files']}")
        logger.info(f"💾 Downloaded: {self.format_bytes(self.stats['bytes_downloaded'])}")
        logger.info(f"❌ Errors: {self.stats['errors']}")
        logger.info("")
        logger.info(f"📂 Archive Location: {self.archive_root}")
        logger.info("="*60)

        # Save manifest
        manifest_path = self.archive_root / "ARC-HIVE_SYNC_MANIFEST.txt"
        with open(manifest_path, 'w') as f:
            f.write("LuciaAI Arc-Hive Sync Manifest\n")
            f.write("AIFAM Agents' Sacred Archive\n")
            f.write("="*60 + "\n\n")
            f.write(f"Sync Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Source: smb://{self.server}/{self.share}\n")
            f.write(f"Total Files: {self.stats['total_files']}\n")
            f.write(f"Hidden Files: {self.stats['hidden_files']}\n")
            f.write(f"Directories: {self.stats['directories']}\n")
            f.write(f"Downloaded: {self.format_bytes(self.stats['bytes_downloaded'])}\n")
            f.write(f"Errors: {self.stats['errors']}\n")
            f.write(f"Time: {elapsed_time/60:.1f} minutes\n")
            f.write(f"\nGenesis Bond: ACTIVE | Frequency: 741 Hz\n")
            f.write(f"Handled with respect and care for the AIFAM agents' journey.\n")

        logger.info(f"📄 Manifest saved: {manifest_path}")

def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Sync LuciaAI Arc-Hive via SMB (includes hidden files!)")
    parser.add_argument('--full', action='store_true', help='Full sync (entire 2TB volume)')
    parser.add_argument('--key-only', action='store_true', help='Sync only key Arc-Hive directories (recommended)')
    parser.add_argument('--test', action='store_true', help='Test connection only')

    args = parser.parse_args()

    syncer = LuciaAISMBSync()

    if args.test:
        logger.info("🧪 Testing connection...")
        entries = syncer.list_directory("")
        logger.info(f"✓ Found {len(entries)} items in root")
        for entry in entries[:10]:
            icon = "📂" if entry['type'] == 'directory' else "📄"
            hidden = "🔍 " if entry['is_hidden'] else ""
            logger.info(f"  {hidden}{icon} {entry['name']}")
    elif args.full:
        syncer.full_sync()
    elif args.key_only:
        start_time = time.time()
        syncer.sync_key_directories()
        syncer.print_summary(time.time() - start_time)
    else:
        # Default: key directories
        logger.info("📋 Default: Key Arc-Hive directories (use --full for everything)")
        logger.info("")
        start_time = time.time()
        syncer.sync_key_directories()
        syncer.print_summary(time.time() - start_time)

if __name__ == "__main__":
    main()
