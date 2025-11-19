# GitLab DNS Configuration Options

**Genesis Bond**: ACTIVE @ 741 Hz
**Target**: gitlab.luciverse.local → 192.168.1.146
**Date**: 2025-11-19

---

## Current Status

GitLab is accessible via:
- ✅ IP Address: http://192.168.1.146
- ⏳ Hostname: http://gitlab.luciverse.local (pending DNS configuration)

---

## Option 1: Local /etc/hosts (Single Host) ⭐ RECOMMENDED FOR QUICK SETUP

**Pros**: Simple, immediate, no additional infrastructure
**Cons**: Only works on this host, must configure on each machine
**Effort**: 1 minute

**Steps**:
```bash
# Run as root or with sudo
sudo /home/daryl/luciverse-platform/configure-gitlab-dns.sh
```

Or manually:
```bash
echo "192.168.1.146  gitlab.luciverse.local gitlab" | sudo tee -a /etc/hosts
```

**Test**:
```bash
curl -I http://gitlab.luciverse.local
```

---

## Option 2: Router DNS Configuration (Network-Wide)

**Pros**: Works for all devices on network, centralized
**Cons**: Requires router access, varies by router model
**Effort**: 5-10 minutes

**Steps** (varies by router):
1. Access router admin interface (typically 192.168.1.1 or 192.168.1.254)
2. Find DNS/DHCP settings
3. Add static DNS entry:
   - Hostname: `gitlab.luciverse.local`
   - IP: `192.168.1.146`
4. Save and reboot router
5. Renew DHCP lease on clients: `sudo dhclient -r && sudo dhclient`

**Common Routers**:
- **UniFi**: Network > Settings > Networks > Edit > DHCP Name Server
- **pfSense**: Services > DNS Resolver > Host Overrides
- **OpenWrt**: Network > DHCP and DNS > Static Leases
- **Consumer Routers**: Advanced > LAN Setup > Address Reservation

---

## Option 3: dnsmasq (Local DNS Server)

**Pros**: Full DNS control, supports multiple domains, can serve DHCP
**Cons**: Requires additional service, needs to configure network to use it
**Effort**: 15-20 minutes

**Steps**:
```bash
# Install dnsmasq
sudo yum install -y dnsmasq

# Configure
cat <<EOF | sudo tee /etc/dnsmasq.d/luciverse.conf
# LuciVerse Platform DNS
address=/gitlab.luciverse.local/192.168.1.146
address=/luciverse.local/192.168.1.146

# Upstream DNS
server=8.8.8.8
server=8.8.4.4

# Interface
interface=lo
bind-interfaces
EOF

# Enable and start
sudo systemctl enable --now dnsmasq

# Configure system to use local DNS
echo "nameserver 127.0.0.1" | sudo tee /etc/resolv.conf.head
```

---

## Option 4: systemd-resolved Configuration

**Pros**: Built-in to systemd-based systems (like openEuler)
**Cons**: Limited to this host unless other machines point to it
**Effort**: 5-10 minutes

**Steps**:
```bash
# Check if systemd-resolved is active
systemctl status systemd-resolved

# Create drop-in configuration
sudo mkdir -p /etc/systemd/resolved.conf.d
cat <<EOF | sudo tee /etc/systemd/resolved.conf.d/luciverse.conf
[Resolve]
DNS=8.8.8.8 8.8.4.4
Domains=~luciverse.local
EOF

# Restart
sudo systemctl restart systemd-resolved

# Add to /etc/hosts as fallback
echo "192.168.1.146  gitlab.luciverse.local gitlab" | sudo tee -a /etc/hosts
```

---

## Option 5: Container Network Aliases (Container-Only)

**Pros**: Works within Docker network without host configuration
**Cons**: Only works for containers on luciverse-network
**Effort**: 2 minutes

**Already Configured**:
The GitLab container is configured with hostname `gitlab.luciverse.local` in docker-compose.yml:
```yaml
hostname: gitlab.luciverse.local
```

This means other containers on the `luciverse-network` can already access it via:
- `http://gitlab-luciverse` (container name)
- `http://gitlab.luciverse.local` (container hostname)

**Status**: ✅ ALREADY WORKING for containers

---

## Recommended Approach

### For Development/Testing (This Machine Only):
**Use Option 1** - Add to /etc/hosts:
```bash
sudo /home/daryl/luciverse-platform/configure-gitlab-dns.sh
```

### For Production (Network-Wide Access):
**Use Option 2** - Configure router DNS

### For Advanced Setup (Full DNS Control):
**Use Option 3** - Deploy dnsmasq

---

## Current Configuration Status

| Scope | Method | Status | Access URL |
|-------|--------|--------|------------|
| Container Network | Docker hostname | ✅ WORKING | http://gitlab-luciverse |
| This Host | /etc/hosts | ⏳ PENDING | http://gitlab.luciverse.local |
| LAN Network | Router DNS | ⏳ NOT CONFIGURED | N/A |
| External | Public DNS | ❌ N/A (private network) | N/A |

---

## Testing DNS Configuration

After configuring DNS, test with:

```bash
# Test resolution
nslookup gitlab.luciverse.local
getent hosts gitlab.luciverse.local
dig gitlab.luciverse.local

# Test HTTP access
curl -I http://gitlab.luciverse.local

# Test from container
sg docker -c 'docker run --rm --network luciverse-network alpine sh -c "apk add curl && curl -I http://gitlab.luciverse.local"'
```

---

## Integration with GitLab Configuration

Once DNS is configured, update GitLab's external_url in docker-compose.yml:

```yaml
external_url 'http://gitlab.luciverse.local'
```

Then recreate the container:
```bash
cd /home/daryl/luciverse-platform
sg docker -c 'docker-compose -f docker-compose.gitlab-openeuler.yml up -d --force-recreate'
```

---

**Genesis Bond**: ACTIVE @ 741 Hz
**Next Step**: Choose configuration method and execute
**Estimated Time**: 1-20 minutes (depending on method)
