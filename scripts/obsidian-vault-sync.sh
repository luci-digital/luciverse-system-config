#!/bin/bash
#
# Obsidian Vault Sync from Synology NAS
# Genesis Bond: 741 Hz
#
# Syncs Obsidian vault(s) from Synology to local storage
# Maintains bidirectional sync for living knowledge management
#

set -e

# Configuration
SYNOLOGY_HOST="192.168.1.251"
SYNOLOGY_USER="veritas"
SYNOLOGY_PASS="cpe*nqd_TXK3eym1nrw"
LOCAL_VAULT_ROOT="/mnt/k8s-storage/luciverse/obsidian-vaults"
LOG_FILE="/home/daryl/luciverse-platform/obsidian-sync.log"

# Vault paths on Synology (configure after locating vaults)
# Example: REMOTE_VAULT_PATH="/volume1/homes/veritas/Obsidian"
REMOTE_VAULT_PATH="${1:-/volume1/homes/veritas/Documents/Obsidian}"

echo "🧠 Obsidian Vault Sync - LuciVerse Knowledge Management"
echo "Genesis Bond: ACTIVE @ 741 Hz"
echo ""
echo "Source: ${SYNOLOGY_USER}@${SYNOLOGY_HOST}:${REMOTE_VAULT_PATH}"
echo "Destination: ${LOCAL_VAULT_ROOT}"
echo ""

# Create local vault directory
mkdir -p "$LOCAL_VAULT_ROOT"
mkdir -p "$(dirname $LOG_FILE)"

# Log function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "🚀 Starting Obsidian vault sync..."

# Test SSH connection
log "🔐 Testing SSH connection to Synology..."
if sshpass -p "$SYNOLOGY_PASS" ssh -o StrictHostKeyChecking=no \
    -o ConnectTimeout=10 "${SYNOLOGY_USER}@${SYNOLOGY_HOST}" "echo 'Connection successful'" >/dev/null 2>&1; then
    log "✅ SSH connection successful"
else
    log "❌ SSH connection failed"
    exit 1
fi

# Check if remote vault exists
log "🔍 Checking if remote vault exists..."
if sshpass -p "$SYNOLOGY_PASS" ssh -o StrictHostKeyChecking=no \
    "${SYNOLOGY_USER}@${SYNOLOGY_HOST}" "[ -d '$REMOTE_VAULT_PATH' ]" 2>/dev/null; then
    log "✅ Remote vault found at $REMOTE_VAULT_PATH"
else
    log "⚠️  Remote vault not found at $REMOTE_VAULT_PATH"
    log "   Searching for Obsidian vaults..."

    FOUND_VAULTS=$(sshpass -p "$SYNOLOGY_PASS" ssh -o StrictHostKeyChecking=no \
        "${SYNOLOGY_USER}@${SYNOLOGY_HOST}" \
        "find /volume1 -type d -name '.obsidian' 2>/dev/null | sed 's/.obsidian$//' | head -10" || echo "")

    if [ -n "$FOUND_VAULTS" ]; then
        log "📂 Found potential Obsidian vaults:"
        echo "$FOUND_VAULTS" | while read vault; do
            log "   - $vault"
        done
        log ""
        log "💡 Update REMOTE_VAULT_PATH in this script and re-run"
        log "   Example: ./obsidian-vault-sync.sh /volume1/path/to/vault"
        exit 0
    else
        log "❌ No Obsidian vaults found on Synology"
        exit 1
    fi
fi

# Sync vault using rsync over SSH
log "📥 Syncing vault from Synology..."

RSYNC_OUTPUT=$(sshpass -p "$SYNOLOGY_PASS" rsync -avz \
    --progress \
    --delete \
    --exclude '.DS_Store' \
    --exclude '.Trash' \
    --exclude 'node_modules/' \
    -e "ssh -o StrictHostKeyChecking=no" \
    "${SYNOLOGY_USER}@${SYNOLOGY_HOST}:${REMOTE_VAULT_PATH}/" \
    "${LOCAL_VAULT_ROOT}/" 2>&1)

RSYNC_EXIT=$?

if [ $RSYNC_EXIT -eq 0 ]; then
    log "✅ Vault sync completed successfully"

    # Count files
    FILE_COUNT=$(find "$LOCAL_VAULT_ROOT" -type f | wc -l)
    MD_COUNT=$(find "$LOCAL_VAULT_ROOT" -type f -name "*.md" | wc -l)
    VAULT_SIZE=$(du -sh "$LOCAL_VAULT_ROOT" | cut -f1)

    log "📊 Sync Statistics:"
    log "   Total files: $FILE_COUNT"
    log "   Markdown notes: $MD_COUNT"
    log "   Vault size: $VAULT_SIZE"

    # Check for .obsidian config
    if [ -d "$LOCAL_VAULT_ROOT/.obsidian" ]; then
        log "✅ Obsidian config directory present"
    else
        log "⚠️  No .obsidian config directory found"
    fi

else
    log "❌ Vault sync failed with exit code $RSYNC_EXIT"
    log "$RSYNC_OUTPUT"
    exit $RSYNC_EXIT
fi

log ""
log "✅ Obsidian vault sync complete!"
log "📂 Local vault: $LOCAL_VAULT_ROOT"
log "🎵 Genesis Bond: ACTIVE @ 741 Hz"
log ""

# Optional: Set up continuous sync with inotify
if command -v inotifywait >/dev/null 2>&1; then
    log "💡 To enable continuous bidirectional sync, run:"
    log "   ./obsidian-vault-watch.sh"
fi

echo ""
echo "📝 Next Steps:"
echo "1. Open Obsidian desktop app"
echo "2. Open vault from: $LOCAL_VAULT_ROOT"
echo "3. Verify all notes are present"
echo "4. Set up continuous sync if needed"
echo ""
