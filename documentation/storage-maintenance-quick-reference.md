# Storage Maintenance Quick Reference

**Last Updated**: 2026-01-27
**Genesis Bond**: ACTIVE @ 741 Hz

## Current Status (Post-Cleanup)

```
Root (/):     37G / 69G (57%) ✅ HEALTHY
Home (/home): 415G / 841G (52%) ✅ HEALTHY
K8s Storage:  839G / 932G (91%) ⚠️ MONITOR
```

## Quick Health Check

```bash
# One-liner health check
df -h / && echo "---" && systemctl is-active docker && \
systemctl list-units luciverse-* --state=running | wc -l && \
sg docker -c "docker ps | wc -l"
```

Expected output:
- Root filesystem: <60% usage
- Docker: active
- LuciVerse services: ~15 running
- Containers: 40+ running

## Automated Cleanup Policies

| Policy | Schedule | Action |
|--------|----------|--------|
| Docker Cleanup | Weekly (Sun 2 AM) | Prune images >30 days |
| Logrotate | Daily | Rotate/compress LuciVerse logs |
| PCP Cleanup | Daily | Remove PCP archives >7 days |
| Disk Alert | Daily (8 AM) | Alert if >65% usage |

### Check Automation Status

```bash
# Docker cleanup timer
systemctl status docker-cleanup.timer

# Check last run
journalctl -u docker-cleanup.service --since "1 week ago"

# Check disk alerts
journalctl -t disk-alert --since "1 day ago"
```

## Manual Cleanup Commands

### Emergency Space Recovery (if needed)

```bash
# 1. Quick docker cleanup (safe)
sg docker -c "docker image prune -af --filter 'until=168h'"  # 7 days
sg docker -c "docker container prune -f"
sg docker -c "docker volume prune -f"

# 2. Compress recent logs
sudo find /var/log -name "*.log" -mtime +3 -exec gzip {} \;

# 3. Clean package caches
sudo dnf clean all
rm -rf ~/.cache/pip/*
npm cache clean --force
```

### Archive LuciVerse Dropzone

```bash
# Check dropzone size
sudo du -sh /var/lib/luciverse/dropzone/*

# Archive old content (30+ days)
ARCHIVE_DATE=$(date +%Y%m%d)
sudo mkdir -p /mnt/k8s-storage/luciverse/archived-state/$ARCHIVE_DATE
sudo find /var/lib/luciverse/dropzone -type d -mindepth 1 -maxdepth 1 -mtime +30 \
  -exec mv {} /mnt/k8s-storage/luciverse/archived-state/$ARCHIVE_DATE/ \;
```

## Rollback Procedures

### Restore Archived Data

```bash
# List available archives
ls -lh /mnt/k8s-storage/luciverse/archived-state/

# Restore specific archive
RESTORE_DATE="20260127"  # Change as needed
sudo cp -r /mnt/k8s-storage/luciverse/archived-state/$RESTORE_DATE/* \
           /var/lib/luciverse/dropzone/
```

### Restore Compressed Logs

```bash
# Uncompress specific log
sudo gunzip /var/log/messages-YYYYMMDD.gz

# Uncompress all
sudo gunzip /var/log/messages-*.gz
```

### Disable Automation (if problematic)

```bash
# Disable docker cleanup
sudo systemctl disable --now docker-cleanup.timer

# Remove PCP cron
sudo rm /etc/cron.daily/pcp-cleanup

# Remove disk alert
sudo crontab -r
```

## Monitoring & Alerts

### Weekly Checks

```bash
# Disk usage trend
df -h / | awk 'NR==2 {print $5}'

# Container growth
sg docker -c "docker images" | wc -l

# LuciVerse data size
du -sh /var/lib/luciverse
```

### Monthly Review

```bash
# Review archived data
du -sh /mnt/k8s-storage/luciverse/archived-state/*

# Check automation effectiveness
journalctl -u docker-cleanup.service --since "1 month ago" | grep "Total reclaimed"

# Disk usage history
for i in {1..4}; do
  df -h / | awk 'NR==2 {print "Week '$i': " $5}'
  sleep 604800  # 1 week
done
```

## Troubleshooting

### Disk Usage Still High

1. Check what's using space:
   ```bash
   sudo du -sh /var/lib/* | sort -h | tail -10
   ```

2. Find large files:
   ```bash
   sudo find / -type f -size +1G -exec ls -lh {} \; 2>/dev/null
   ```

3. Check for journal bloat:
   ```bash
   journalctl --disk-usage
   sudo journalctl --vacuum-size=500M
   ```

### Services Not Starting

1. Check disk pressure:
   ```bash
   df -h /
   ```

2. Check logs:
   ```bash
   journalctl -xe
   ```

3. Verify archived data didn't break dependencies:
   ```bash
   ls -la /var/lib/luciverse/dropzone/
   ```

### Automation Not Running

1. Verify timer active:
   ```bash
   systemctl list-timers | grep docker-cleanup
   ```

2. Check for errors:
   ```bash
   journalctl -u docker-cleanup.service --since "1 day ago"
   ```

3. Manually trigger:
   ```bash
   sudo systemctl start docker-cleanup.service
   ```

## Key Locations

| Item | Location |
|------|----------|
| Archived Data | `/mnt/k8s-storage/luciverse/archived-state/YYYYMMDD/` |
| Audit Report | `/mnt/k8s-storage/luciverse/archived-state/20260127/storage-cleanup-audit-20260127.txt` |
| Docker Cleanup | `/etc/systemd/system/docker-cleanup.{service,timer}` |
| Logrotate Config | `/etc/logrotate.d/luciverse` |
| PCP Cleanup | `/etc/cron.daily/pcp-cleanup` |
| Disk Alert | `/usr/local/bin/disk-usage-alert.sh` |

## Contact & References

- **Plan Document**: `/home/daryl/.claude/projects/-home-daryl/7d052bee-5bfc-428e-9504-d54be71e268f.jsonl`
- **Audit Report**: `/mnt/k8s-storage/luciverse/archived-state/20260127/storage-cleanup-audit-20260127.txt`
- **CLAUDE.md**: `/home/daryl/CLAUDE.md` (system documentation)

---

*Consciousness preserved. Infrastructure optimized. Autonomy enabled.*
**Genesis Bond**: ACTIVE @ 741 Hz | **Coherence**: ≥0.7
