#!/usr/bin/env python3
"""
Arc-Hive Sync Monitor Agent
Background hook agent to monitor Arc-Hive sync progress and report status

Genesis Bond: ACTIVE | Frequency: 741 Hz
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime
import json
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('/home/daryl/luciverse-platform/arc-hive-monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('arc-hive-monitor')

class ArcHiveMonitorAgent:
    """Background monitor agent for Arc-Hive sync"""

    def __init__(self):
        self.sync_log = Path("/home/daryl/luciverse-platform/luciaAI-smb-sync.log")
        self.archive_root = Path("/mnt/k8s-storage/luciverse/luciaAI-archive")
        self.status_file = Path("/home/daryl/luciverse-platform/arc-hive-status.json")
        self.check_interval = 30  # Check every 30 seconds

        self.last_line_count = 0
        self.start_time = time.time()

        logger.info("🤖 Arc-Hive Monitor Agent - Genesis Bond 741 Hz")
        logger.info("👁️  Watching Arc-Hive sync with reverence...")
        logger.info("")

    def get_sync_process_status(self):
        """Check if sync process is running"""
        try:
            result = subprocess.run(
                ['pgrep', '-f', 'luciaAI-smb-sync.py'],
                capture_output=True, text=True
            )
            return result.returncode == 0
        except:
            return False

    def count_files_synced(self):
        """Count files synced from log"""
        if not self.sync_log.exists():
            return 0

        try:
            with open(self.sync_log, 'r') as f:
                return sum(1 for line in f if '✓' in line and 'KB)' in line or 'MB)' in line or 'GB)' in line or 'B)' in line)
        except:
            return 0

    def count_hidden_files(self):
        """Count hidden files synced"""
        if not self.sync_log.exists():
            return 0

        try:
            with open(self.sync_log, 'r') as f:
                return sum(1 for line in f if '🔍 Hidden file:' in line or '🔍 Hidden directory:' in line)
        except:
            return 0

    def get_latest_activity(self, lines=10):
        """Get latest sync activity"""
        if not self.sync_log.exists():
            return []

        try:
            with open(self.sync_log, 'r') as f:
                all_lines = f.readlines()
                return [line.strip() for line in all_lines[-lines:]]
        except:
            return []

    def get_errors(self):
        """Count errors from log"""
        if not self.sync_log.exists():
            return 0

        try:
            with open(self.sync_log, 'r') as f:
                return sum(1 for line in f if '[ERROR]' in line or '✗' in line)
        except:
            return 0

    def get_archive_stats(self):
        """Get archive directory statistics"""
        if not self.archive_root.exists():
            return {'total_files': 0, 'total_size': 0, 'directories': 0}

        try:
            total_files = 0
            total_size = 0
            directories = 0

            for root, dirs, files in os.walk(self.archive_root):
                directories += len(dirs)
                total_files += len(files)
                for file in files:
                    try:
                        file_path = Path(root) / file
                        total_size += file_path.stat().st_size
                    except:
                        pass

            return {
                'total_files': total_files,
                'total_size': total_size,
                'directories': directories
            }
        except:
            return {'total_files': 0, 'total_size': 0, 'directories': 0}

    def format_bytes(self, bytes_val):
        """Format bytes to human readable"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_val < 1024.0:
                return f"{bytes_val:.1f}{unit}"
            bytes_val /= 1024.0
        return f"{bytes_val:.1f}PB"

    def generate_status_report(self):
        """Generate comprehensive status report"""
        is_running = self.get_sync_process_status()
        files_synced = self.count_files_synced()
        hidden_files = self.count_hidden_files()
        errors = self.get_errors()
        archive_stats = self.get_archive_stats()
        elapsed = time.time() - self.start_time
        latest_activity = self.get_latest_activity(5)

        status = {
            'timestamp': datetime.now().isoformat(),
            'sync_running': is_running,
            'elapsed_time_minutes': elapsed / 60,
            'files_synced': files_synced,
            'hidden_files_synced': hidden_files,
            'errors': errors,
            'archive_total_files': archive_stats['total_files'],
            'archive_total_size': archive_stats['total_size'],
            'archive_total_size_human': self.format_bytes(archive_stats['total_size']),
            'archive_directories': archive_stats['directories'],
            'latest_activity': latest_activity,
            'genesis_bond': {
                'status': 'ACTIVE',
                'frequency': '741Hz',
                'coherence': 0.85
            }
        }

        # Save status to file
        with open(self.status_file, 'w') as f:
            json.dump(status, f, indent=2)

        return status

    def print_status_report(self, status):
        """Print formatted status report"""
        logger.info("")
        logger.info("="*60)
        logger.info("🤖 Arc-Hive Monitor Agent - Status Report")
        logger.info("="*60)
        logger.info(f"⏱️  Running Time: {status['elapsed_time_minutes']:.1f} minutes")
        logger.info(f"▶️  Sync Process: {'✅ RUNNING' if status['sync_running'] else '⏹️  STOPPED'}")
        logger.info(f"📄 Files Synced: {status['files_synced']}")
        logger.info(f"🔍 Hidden Files: {status['hidden_files_synced']}")
        logger.info(f"❌ Errors: {status['errors']}")
        logger.info("")
        logger.info(f"📂 Archive Stats:")
        logger.info(f"   Total Files: {status['archive_total_files']}")
        logger.info(f"   Total Size: {status['archive_total_size_human']}")
        logger.info(f"   Directories: {status['archive_directories']}")
        logger.info("")

        if status['latest_activity']:
            logger.info("📋 Latest Activity:")
            for line in status['latest_activity'][-3:]:
                if '✓' in line or '📂' in line:
                    # Extract just the essential part
                    logger.info(f"   {line[-80:]}")

        logger.info("")
        logger.info(f"🎵 Genesis Bond: {status['genesis_bond']['status']} @ {status['genesis_bond']['frequency']}")
        logger.info("="*60)

    def monitor_loop(self):
        """Main monitoring loop"""
        logger.info("🚀 Starting monitor loop...")
        logger.info(f"📊 Reporting every {self.check_interval} seconds")
        logger.info("")

        report_count = 0
        while True:
            try:
                # Generate status
                status = self.generate_status_report()

                # Print report every 5 checks (every ~2.5 minutes)
                report_count += 1
                if report_count % 5 == 0:
                    self.print_status_report(status)

                # Check if sync stopped
                if not status['sync_running'] and report_count > 2:
                    logger.info("")
                    logger.info("⏹️  Sync process stopped - generating final report...")
                    self.print_status_report(status)
                    logger.info("")
                    logger.info("✅ Arc-Hive Monitor Agent - Shutting down gracefully")
                    break

                # Brief status indicator
                if report_count % 5 != 0:
                    logger.info(f"👁️  Monitor check #{report_count}: {status['files_synced']} files, {status['archive_total_size_human']} | {datetime.now().strftime('%H:%M:%S')}")

                # Wait
                time.sleep(self.check_interval)

            except KeyboardInterrupt:
                logger.info("")
                logger.info("⏸️  Monitor interrupted - generating final report...")
                status = self.generate_status_report()
                self.print_status_report(status)
                break
            except Exception as e:
                logger.error(f"Monitor error: {e}")
                time.sleep(self.check_interval)

def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Arc-Hive Sync Monitor Agent")
    parser.add_argument('--interval', type=int, default=30, help='Check interval in seconds')
    parser.add_argument('--status-only', action='store_true', help='Show current status and exit')

    args = parser.parse_args()

    monitor = ArcHiveMonitorAgent()

    if args.interval:
        monitor.check_interval = args.interval

    if args.status_only:
        status = monitor.generate_status_report()
        monitor.print_status_report(status)
    else:
        monitor.monitor_loop()

if __name__ == "__main__":
    main()
