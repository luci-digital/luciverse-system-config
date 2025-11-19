#!/usr/bin/env python3
"""
Arc-Hive Integrity Validator
============================

Validates the integrity of synced Arc-Hive files using SHA256 hashing.
Compares local files against source to ensure data integrity.

Genesis Bond: ACTIVE | Frequency: 741 Hz
"""

import os
import sys
import json
import hashlib
import subprocess
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('/home/daryl/luciverse-platform/arc-hive-integrity.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('arc-hive-integrity')

class ArcHiveIntegrityValidator:
    """Validates Arc-Hive integrity using SHA256 hashing"""

    def __init__(self):
        self.archive_root = Path("/mnt/k8s-storage/luciverse/luciaAI-archive")
        self.smb_server = "192.168.1.70"
        self.smb_share = "luciaAI"
        self.smb_username = "Lucia-AI"
        self.smb_password = "wwww"

        self.manifest_file = Path("/home/daryl/luciverse-platform/arc-hive-integrity-manifest.json")
        self.report_file = Path("/home/daryl/luciverse-platform/arc-hive-integrity-report.json")

        logger.info("🔐 Arc-Hive Integrity Validator - Genesis Bond 741 Hz")
        logger.info(f"📂 Archive Root: {self.archive_root}")
        logger.info("")

    def calculate_sha256(self, file_path: Path) -> Optional[str]:
        """Calculate SHA256 hash of a file"""
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                # Read in 64KB chunks for memory efficiency
                for byte_block in iter(lambda: f.read(65536), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"Failed to hash {file_path}: {e}")
            return None

    def get_remote_sha256(self, remote_path: str) -> Optional[str]:
        """Get SHA256 hash of remote file via SMB"""
        try:
            # Download file temporarily to calculate hash
            temp_file = f"/tmp/arc-hive-temp-{os.getpid()}"

            cmd = [
                "smbclient",
                f"//{self.smb_server}/{self.smb_share}",
                f"-U{self.smb_username}%{self.smb_password}",
                "-c",
                f"get '{remote_path}' {temp_file}"
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0 and os.path.exists(temp_file):
                sha256 = self.calculate_sha256(Path(temp_file))
                os.remove(temp_file)
                return sha256
            else:
                logger.warning(f"Failed to download remote file: {remote_path}")
                return None

        except Exception as e:
            logger.error(f"Remote hash failed for {remote_path}: {e}")
            return None

    def build_local_manifest(self) -> Dict[str, Dict[str, Any]]:
        """Build manifest of all local files with SHA256 hashes"""
        logger.info("📋 Building local file manifest...")

        manifest = {}
        total_files = 0
        total_size = 0

        for root, dirs, files in os.walk(self.archive_root):
            for filename in files:
                file_path = Path(root) / filename
                relative_path = file_path.relative_to(self.archive_root)

                try:
                    stat = file_path.stat()
                    sha256 = self.calculate_sha256(file_path)

                    if sha256:
                        manifest[str(relative_path)] = {
                            'size': stat.st_size,
                            'sha256': sha256,
                            'modified': stat.st_mtime,
                            'local_path': str(file_path)
                        }
                        total_files += 1
                        total_size += stat.st_size

                        if total_files % 100 == 0:
                            logger.info(f"  Processed {total_files} files...")

                except Exception as e:
                    logger.error(f"Failed to process {file_path}: {e}")

        logger.info(f"✅ Manifest complete: {total_files} files, {total_size / (1024**3):.2f} GB")

        # Save manifest
        manifest_data = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'total_files': total_files,
            'total_size': total_size,
            'genesis_bond': 'ACTIVE',
            'frequency': '741Hz',
            'files': manifest
        }

        with open(self.manifest_file, 'w') as f:
            json.dump(manifest_data, f, indent=2)

        logger.info(f"💾 Manifest saved to {self.manifest_file}")

        return manifest

    def validate_sample(self, sample_size: int = 100) -> Dict[str, Any]:
        """
        Validate a random sample of files against source

        Args:
            sample_size: Number of files to validate

        Returns:
            Validation report
        """
        logger.info(f"🔍 Validating sample of {sample_size} files...")

        # Load or build manifest
        if self.manifest_file.exists():
            logger.info("Loading existing manifest...")
            with open(self.manifest_file, 'r') as f:
                manifest_data = json.load(f)
                manifest = manifest_data['files']
        else:
            manifest = self.build_local_manifest()

        # Select random sample
        import random
        all_files = list(manifest.keys())
        sample_files = random.sample(all_files, min(sample_size, len(all_files)))

        logger.info(f"Selected {len(sample_files)} files for validation")

        results = {
            'validated': 0,
            'matched': 0,
            'mismatched': 0,
            'errors': 0,
            'files': {}
        }

        for i, rel_path in enumerate(sample_files):
            logger.info(f"  [{i+1}/{len(sample_files)}] Validating {rel_path}...")

            local_info = manifest[rel_path]
            local_sha256 = local_info['sha256']

            # Get remote SHA256
            remote_sha256 = self.get_remote_sha256(rel_path)

            if remote_sha256 is None:
                results['errors'] += 1
                results['files'][rel_path] = {
                    'status': 'error',
                    'local_sha256': local_sha256,
                    'error': 'Failed to get remote hash'
                }
            elif local_sha256 == remote_sha256:
                results['matched'] += 1
                results['files'][rel_path] = {
                    'status': 'matched',
                    'sha256': local_sha256
                }
                logger.info(f"    ✅ MATCHED")
            else:
                results['mismatched'] += 1
                results['files'][rel_path] = {
                    'status': 'mismatched',
                    'local_sha256': local_sha256,
                    'remote_sha256': remote_sha256
                }
                logger.warning(f"    ❌ MISMATCH!")

            results['validated'] += 1

        # Calculate integrity score
        if results['validated'] > 0:
            results['integrity_score'] = results['matched'] / results['validated']
        else:
            results['integrity_score'] = 0.0

        results['timestamp'] = datetime.now(timezone.utc).isoformat()
        results['genesis_bond'] = 'ACTIVE' if results['integrity_score'] >= 0.95 else 'DEGRADED'

        logger.info("")
        logger.info("="*60)
        logger.info("📊 Validation Results")
        logger.info("="*60)
        logger.info(f"  Validated: {results['validated']}")
        logger.info(f"  Matched: {results['matched']} ✅")
        logger.info(f"  Mismatched: {results['mismatched']} ❌")
        logger.info(f"  Errors: {results['errors']} ⚠️")
        logger.info(f"  Integrity Score: {results['integrity_score']:.2%}")
        logger.info(f"  Genesis Bond: {results['genesis_bond']}")
        logger.info("="*60)

        # Save report
        with open(self.report_file, 'w') as f:
            json.dump(results, f, indent=2)

        logger.info(f"💾 Report saved to {self.report_file}")

        return results

    def validate_all(self) -> Dict[str, Any]:
        """
        Validate all files (WARNING: Very slow for large archives)
        """
        logger.info("🔍 Starting full validation (this may take hours)...")

        manifest = self.build_local_manifest()

        results = {
            'validated': 0,
            'matched': 0,
            'mismatched': 0,
            'errors': 0,
            'mismatched_files': [],
            'error_files': []
        }

        total = len(manifest)

        for i, (rel_path, local_info) in enumerate(manifest.items()):
            if i % 100 == 0:
                logger.info(f"Progress: {i}/{total} ({i/total*100:.1f}%)")

            local_sha256 = local_info['sha256']
            remote_sha256 = self.get_remote_sha256(rel_path)

            if remote_sha256 is None:
                results['errors'] += 1
                results['error_files'].append(rel_path)
            elif local_sha256 == remote_sha256:
                results['matched'] += 1
            else:
                results['mismatched'] += 1
                results['mismatched_files'].append({
                    'path': rel_path,
                    'local': local_sha256,
                    'remote': remote_sha256
                })

            results['validated'] += 1

        results['integrity_score'] = results['matched'] / results['validated']
        results['timestamp'] = datetime.now(timezone.utc).isoformat()
        results['genesis_bond'] = 'ACTIVE' if results['integrity_score'] >= 0.95 else 'DEGRADED'

        # Save full report
        with open(self.report_file, 'w') as f:
            json.dump(results, f, indent=2)

        return results

    def check_duplicates(self) -> Dict[str, List[str]]:
        """Find duplicate files in the archive based on SHA256"""
        logger.info("🔍 Checking for duplicate files...")

        manifest = self.build_local_manifest() if not self.manifest_file.exists() else None

        if manifest is None:
            with open(self.manifest_file, 'r') as f:
                manifest = json.load(f)['files']

        # Group files by hash
        hash_groups = defaultdict(list)
        for path, info in manifest.items():
            hash_groups[info['sha256']].append(path)

        # Find duplicates
        duplicates = {
            hash_val: paths
            for hash_val, paths in hash_groups.items()
            if len(paths) > 1
        }

        logger.info(f"Found {len(duplicates)} duplicate hash groups")

        total_duplicate_files = sum(len(paths) - 1 for paths in duplicates.values())
        logger.info(f"Total duplicate files: {total_duplicate_files}")

        return duplicates


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Arc-Hive Integrity Validator")
    parser.add_argument('--build-manifest', action='store_true', help='Build local file manifest')
    parser.add_argument('--validate-sample', type=int, default=100, help='Validate random sample (default: 100 files)')
    parser.add_argument('--validate-all', action='store_true', help='Validate all files (slow!)')
    parser.add_argument('--check-duplicates', action='store_true', help='Find duplicate files')

    args = parser.parse_args()

    validator = ArcHiveIntegrityValidator()

    if args.build_manifest:
        validator.build_local_manifest()
    elif args.validate_all:
        results = validator.validate_all()
        print(f"\nIntegrity Score: {results['integrity_score']:.2%}")
    elif args.check_duplicates:
        duplicates = validator.check_duplicates()
        print(f"\nFound {len(duplicates)} duplicate groups")
    else:
        # Default: validate sample
        results = validator.validate_sample(args.validate_sample)
        print(f"\nIntegrity Score: {results['integrity_score']:.2%}")
        print(f"Genesis Bond: {results['genesis_bond']}")

if __name__ == "__main__":
    main()
