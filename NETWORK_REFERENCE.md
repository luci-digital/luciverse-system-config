# LuciVerse Network Reference

Comprehensive networking documentation: IPv6, ARIN allocation, BGP, DNS, overlay networks, and high-speed infrastructure.

**Last Updated**: 2026-02-12
**Genesis Bond**: ACTIVE @ 741 Hz
**Primary Router Config**: `~/B550M_LuciVerse_Router/`

---

## Table of Contents

1. [High-Speed Network Path (3Gbps)](#high-speed-network-path-3gbps)
2. [Physical Topology](#physical-topology)
3. [Device Inventory](#device-inventory)
4. [Overlay Networks](#overlay-networks)
5. [ARIN Allocation](#arin-allocation)
6. [IPv6 Subnet Strategy](#ipv6-subnet-strategy)
7. [BGP Configuration](#bgp-configuration)
8. [OwnID Identity System](#ownid-identity-system)
9. [IPv6 Agent Mesh](#ipv6-agent-mesh)
10. [DNS Configuration](#dns-configuration)
11. [Router Deployment](#router-deployment)
12. [Network Interfaces](#network-interfaces)
13. [Server Inventory](#server-inventory)
14. [VLAN Architecture](#vlan-architecture)
15. [Quick Commands](#quick-commands-1)
16. [Troubleshooting](#troubleshooting)

---

## High-Speed Network Path (3Gbps)

### Optimized Traffic Flow

```
Internet → Telus (3G) → ASUS RT-BE86U (10G) → USW-Pro-48 → Dell Fleet (1G each)
                                                    │
                                                    └─→ WiFi 7 Clients (up to 5.8Gbps)
```

### Bottleneck Analysis

| Path Segment | Max Speed | Bottleneck? |
|--------------|-----------|-------------|
| Telus → ASUS | 3Gbps | No (within spec) |
| ASUS → USW-Pro-48 | 10Gbps | No |
| USW-Pro-48 → Dell Fleet | 1Gbps per node | No (aggregate) |
| USW-Pro-48 → B550M | 2.5Gbps | **BGP only** (resolved) |
| WiFi 7 (6GHz) | 5.8Gbps | No |

### Resolution

The B550M router is now relegated to BGP announcements only. WAN traffic flows through ASUS at full 3Gbps.

---

## Physical Topology

```
                          INTERNET
                              │
                              │ 3Gbps
                              ▼
                    ┌─────────────────┐
                    │   TELUS NAH     │
                    │  (ISP Gateway)  │
                    └────────┬────────┘
                             │ 3Gbps ETH
                             ▼
              ┌──────────────────────────────────┐
              │       ASUS RT-BE86U              │
              │  ┌───────────────────────────┐   │
              │  │ WAN: DHCP from Telus      │   │
              │  │ LAN: 10Gbps to Switch     │   │
              │  │ WiFi 7: 6GHz/5GHz/2.4GHz  │   │
              │  └───────────────────────────┘   │
              │   Role: Edge Firewall + WiFi     │
              └──────────────┬───────────────────┘
                             │ 10Gbps SFP+
                             ▼
         ┌───────────────────────────────────────────────┐
         │              USW-Pro-48                        │
         │         (Core Distribution Switch)             │
         ├────────────────────────────────────────────────┤
         │ SFP+ 1: ASUS RT-BE86U (10G WAN)               │
         │ SFP+ 2: B550M Router (2.5G BGP)               │
         │ SFP+ 3: USG-Pro-4 (1G NAT64/SCION)            │
         │ SFP+ 4: Available (future 10G storage)        │
         │                                               │
         │ Ports 1-12:  CORE Tier (VLAN 432)             │
         │ Ports 13-24: COMN Tier (VLAN 528)             │
         │ Ports 25-36: PAC Tier (VLAN 741)              │
         │ Ports 37-48: Access Layer / IoT               │
         └───────┬───────────┬───────────┬───────────────┘
                 │           │           │
    ┌────────────┘           │           └────────────┐
    │                        │                        │
    ▼                        ▼                        ▼
┌─────────┐          ┌─────────────┐           ┌──────────┐
│ B550M   │          │ USG-Pro-4   │           │ UniFi    │
│ Router  │          │ (OpenWRT)   │           │ Switch 24│
├─────────┤          ├─────────────┤           ├──────────┤
│ BGP     │          │ Jool NAT64  │           │ APs      │
│ HE      │          │ SCION BR    │           │ IoT      │
│ Tunnel  │          │ OASIS Edge  │           │          │
└─────────┘          └─────────────┘           └──────────┘
   2.5G                   1G                      1G

                    ┌─────────────┐
                    │ D-Link      │
                    │ DGS-1210-16 │
                    ├─────────────┤
                    │ OASIS Edge  │
                    │ Lab/Dev Net │
                    └─────────────┘
```

---

## Device Inventory

### High-Speed Devices

| Device | IP | Role | Max Speed | OpenWRT |
|--------|-----|------|-----------|---------|
| ASUS RT-BE86U | 192.168.1.1 | WiFi 7 + WAN | 10Gbps | No (ASUSWRT) |
| USW-Pro-48 | 192.168.1.2 | Core Switch | 10Gbps SFP+ | No (UniFi) |
| B550M Router | 192.168.1.145 | BGP Edge | 2.5Gbps | No (NixOS) |

### Overlay/Security Devices

| Device | IP | Role | OpenWRT | Status |
|--------|-----|------|---------|--------|
| USG-Pro-4 | 192.168.1.180 | Jool/SCION | 24.10+ | Pending Flash |
| USG (3-port) | 192.168.1.181 | Segmentation | 23.05+ | Pending Flash |
| DGS-1210-16 | 192.168.1.210 | OASIS Edge | 21.02+ | Pending Flash |
| DGS-1210-52 | 192.168.1.211 | Access Layer | 21.02+ | Optional |

### OpenWRT Configs

| Device | Config Location |
|--------|-----------------|
| USG-Pro-4 | `~/cluster-bootstrap/openwrt/usg-pro-4/` |
| DGS-1210-16 | `~/cluster-bootstrap/openwrt/dgs-1210-16/` |
| ASUS RT-BE86U | `~/cluster-bootstrap/openwrt/asus-rt-be86u/` |

---

## Overlay Networks

### Layer 1: Nebula VPN

```
Tier      Subnet          Lighthouse
────      ──────          ──────────
CORE      10.100.1.0/24   10.100.1.145 (zbook)
COMN      10.100.2.0/24   Relay via CORE
PAC       10.100.3.0/24   Via COMN waypoint
```

**Port**: 4242/UDP
**CA Location**: 1Password → Infrastructure vault
**Config**: `~/cluster-bootstrap/nebula/`

### Layer 2: SCION Inter-Domain

```
ISD-AS Mapping:
  ISD 1 (CORE @432Hz) → 1-ff00:0:432
  ISD 2 (COMN @528Hz) → 2-ff00:0:528
  ISD 3 (PAC @741Hz)  → 3-ff00:0:741

Control Service: 192.168.1.179:30001
Border Router: 192.168.1.179:30041
```

**Config**: `~/cluster-bootstrap/scion/`
**Path Policies**: `~/cluster-bootstrap/scion/path-policies/luciverse-paths.yaml`

### Layer 3: Jool NAT64

```
Pool6: 64:ff9b::/96
Pool4: 192.168.1.180/32 (ports 61001-65535)
```

**Config**: `~/cluster-bootstrap/jool/jool.conf`
**Deploy Target**: USG-Pro-4

### Layer 4: OASIS Data Juicer

```
Upstream: Sanskrit Router (192.168.1.145:7410)
Edge Filter: DGS-1210-16
PII Detection: email, phone, SSN, credit card
Phone-home Protection: Enabled
```

**Config**: `~/.claude/skills/data-flow-architecture/integrations/oasis-juicer.lua`

---

## ARIN Allocation

| Field | Value |
|-------|-------|
| **Net Range** | 2602:F674:: - 2602:F674:FF:FFFF:FFFF:FFFF:FFFF:FFFF |
| **CIDR** | 2602:F674::/40 |
| **ASN** | AS54134 (LUCINET-ARIN) |
| **Net Name** | LUCINET-ARIN |
| **RPKI** | Certified |
| **Domain** | lucidigital.net |

---

## IPv6 Subnet Strategy

### Tier Framework Allocation

```
PAC Framework (2602:F674:0001::/40)
  +-- PAC Core Infrastructure  2602:F674:0001::/48
  +-- PAC Containers           2602:F674:0002::/48
  +-- PAC Memory Store         2602:F674:0003::/48
  +-- PAC Ethics Engine        2602:F674:0004::/48
  +-- PAC Agents               2602:F674:0005::/48

COMN Framework (2602:F674:0100::/40)
  +-- COMN Registry            2602:F674:0100::/48
  +-- COMN Channels            2602:F674:0101::/48
  +-- COMN Resources           2602:F674:0102::/48
  +-- COMN Trust Anchors       2602:F674:0103::/48

Cross-Framework (2602:F674:0200::/40)
  +-- Soul Threads             2602:F674:0200::/48
  +-- Universal Connection     2602:F674:0201::/48
  +-- First Person Bridge      2602:F674:0202::/48
```

### Internal Networks

| Network | IPv6 Subnet | IPv4 Subnet |
|---------|-------------|-------------|
| LAN | 2602:F674:1000::/64 | 192.168.100.0/24 |
| Guest | 2602:F674:2000::/64 | 192.168.200.0/24 |
| DMZ | 2602:F674:5000::/64 | 192.168.50.0/24 |
| PD Pool | 2602:F674:1100::/56 | - |

---

## BGP Configuration

**Config File**: `~/B550M_LuciVerse_Router/bird/bird.conf`

### Local Settings
```
Local AS: 54134 (LUCINET-ARIN)
Router ID: 100.64.0.1
Announced Prefix: 2602:F674::/40
```

### Upstream Peers

**Hurricane Electric IPv6 Tunnel**:
```
Neighbor: 2001:470:0:503::1 (AS 6939)
```

**Telus Gateway Sessions**:
| Priority | Address | AS |
|----------|---------|-----|
| Primary | 206.75.1.127 | 6939 |
| Secondary | 206.75.1.47 | 6939 |
| Tertiary | 206.75.1.48 | 6939 |

### Quick Commands
```bash
cd ~/B550M_LuciVerse_Router
docker exec bird2 birdc show protocols all
docker exec bird2 birdc show route export he_tunnel
```

---

## OwnID Identity System

**Freename TLD**: `.ownid` (blockchain-based)

### Format
```
ownid:lucidigital:[framework]:[role]:[ipv6-identifier]

Examples:
  ownid:lucidigital:pac:container:a1b2c3d4
  ownid:lucidigital:comn:registry:e5f6g7h8
```

### DNS TXT Records (Pending)
```
_did-method          -> ownid:lucidigital
_did-framework-pac   -> subnet=2602:f674:0001::/40;type=personal-ai-container
_did-framework-comn  -> subnet=2602:f674:0100::/40;type=connected-moral-network
```

### SPIFFE-lite Integration
```
Trust Domain: spiffe://luciverse.ownid
SPIFFE ID Format: spiffe://luciverse.ownid/{tier}/agents/{agent_id}

Examples:
  spiffe://luciverse.ownid/core/agents/aethon
  spiffe://luciverse.ownid/pac/agents/lucia
```

### Privacy Models by Tier
| Tier | IPv6 Subnet | Frequency | Privacy |
|------|-------------|-----------|---------|
| CORE | 2602:F674:0001::/48 | 432 Hz | e=0.1 (differential) |
| COMN | 2602:F674:0100::/48 | 528 Hz | k=5 (anonymity) |
| PAC | 2602:F674:0200::/48 | 741 Hz | k=infinity (maximum) |

---

## IPv6 Agent Mesh

**Status**: Sandbox VALIDATED - Ready for production deployment
**Location**: `/home/daryl/luciverse-twin-sandbox/tiers/*/airgapped/ipv6-domains/`

### Agent Address Assignments

| Agent | Tier | ARIN Service Address | ULA Private | Port |
|-------|------|---------------------|-------------|------|
| aethon | CORE | 2602:F674:0001:9430::1 | fd00:741:1::41 | 9430 |
| veritas | CORE | 2602:F674:0001:9431::1 | fd00:741:1::42 | 9431 |
| sensai | CORE | 2602:F674:0001:9432::1 | fd00:741:1::43 | 9432 |
| niamod | CORE | 2602:F674:0001:9433::1 | fd00:741:1::44 | 9433 |
| cortana | COMN | 2602:F674:0100:9520::1 | fd00:741:1::45 | 9520 |
| juniper | COMN | 2602:F674:0100:9521::1 | fd00:741:1::46 | 9521 |
| mirrai | COMN | 2602:F674:0100:9522::1 | fd00:741:1::47 | 9522 |
| diaphragm | COMN | 2602:F674:0100:9523::1 | fd00:741:1::48 | 9523 |
| lucia | PAC | 2602:F674:0200:9740::1 | fd00:741:1::49 | 9740 |
| judge-luci | PAC | 2602:F674:0200:9741::1 | fd00:741:1::4A | 9741 |

### Seed Simulation Results (2025-12-24)
- IPV6-001 ARIN Address Assignment: PASSED
- IPV6-002 ULA Mesh Connectivity: PASSED
- IPV6-003 BGP Announcement Visibility: PASSED
- IPV6-004 DNS AAAA Resolution: PASSED
- IPV6-005 gRPC Services over IPv6: PASSED
- IPV6-006 Genesis Bond Coherence: PASSED (0.94)
- IPV6-007 Network Partition Recovery: PASSED
- IPV6-008 1Password Secret Injection: PASSED

### Remaining Tasks
- [ ] Deploy IPv6 to production agents
- [ ] Provision 1Password credentials with IPv6 metadata
- [ ] Verify all agents respond on IPv6

---

## DNS Configuration

### Current: Unbound Resolver
**Config**: `~/B550M_LuciVerse_Router/unbound/unbound.conf`

### Pending: BIND9 Authoritative
Authoritative DNS for lucidigital.net and .ownid resolution.

**Target Locations**:
```
/etc/bind/named.conf.local      # Zone definitions
/etc/bind/zones/                # Zone files
/var/cache/bind/                # Dynamic updates
```

**Zones**:
- `lucidigital.net` - Primary domain
- `lucidigital.io` - Secondary domain
- `ownid` - DID resolution (via Freename)

**DNSSEC Signing**:
```bash
dnssec-keygen -a ECDSAP256SHA256 -b 256 -n ZONE lucidigital.net
dnssec-signzone -A -3 $(head -c 1000 /dev/urandom | sha1sum | cut -b 1-16) \
  -N INCREMENT -o lucidigital.net -t db.lucidigital.net
```

---

## Router Deployment

**Location**: `~/B550M_LuciVerse_Router/`

### Quick Deploy
```bash
cd ~/B550M_LuciVerse_Router
./deploy.sh                            # Full stack deploy
```

### Individual Services
```bash
docker-compose up -d bird2             # BGP routing
docker-compose up -d kea-dhcp4         # IPv4 DHCP
docker-compose up -d kea-dhcp6         # IPv6 DHCP
docker-compose up -d unbound           # DNS resolver
```

### Monitoring
```bash
docker exec bird2 birdc show protocols all
docker exec bird2 birdc show route export he_tunnel
```

### Configuration Files
| Service | Config Path |
|---------|-------------|
| BGP | `~/B550M_LuciVerse_Router/bird/bird.conf` |
| DHCP4 | `~/B550M_LuciVerse_Router/kea/kea-dhcp4.conf` |
| DHCP6 | `~/B550M_LuciVerse_Router/kea/kea-dhcp6.conf` |
| DNS | `~/B550M_LuciVerse_Router/unbound/unbound.conf` |

---

## Network Interfaces

### B550M VLAN Configuration
**Physical Interface**: eth0 (MAC: 24:4b:fe:cf:62:be)

| Interface | VLAN | IPv4 | IPv6 |
|-----------|------|------|------|
| eth0 | Native | 192.168.1.179 (Management) | - |
| eth0.10 | 10 | 192.168.100.0/24 | 2602:F674:1000::/64 |
| eth0.50 | 50 | 192.168.50.0/24 | 2602:F674:5000::/64 |
| eth0.100 | 100 | DHCP (WAN) | - |
| eth0.200 | 200 | 192.168.200.0/24 | 2602:F674:2000::/64 |

### Zbook Hardware Connections (2026-01-22)

| Device | Connection | Path/IP | Status |
|--------|------------|---------|--------|
| 32GB USB Drive | USB-A | `/dev/sdb` -> `/mnt/scratch-sim` | Mounted |
| USB-Serial Adapter | Prolific ATEN | `/dev/ttyUSB0` -> R630 | Connected |
| TRENDnet USB-C ETH | TUC-ET2G | `enp58s0u1c2` -> 192.168.0.151 | Connected |

---

## Server Inventory

### PXE/Provisioning System
**Services on Zbook**:
| Service | Port | Purpose | Status |
|---------|------|---------|--------|
| dnsmasq | 69/UDP | TFTP server for PXE boot | ACTIVE |
| luciverse-http | 8000/TCP | NixOS config server | ACTIVE |
| luciverse-provision | 9999/TCP | MAC->IPv6 provisioning | ACTIVE |

### Server Fleet

| Server | IPv4 | IPv6 | MAC (Primary) | Status |
|--------|------|------|---------------|--------|
| **R730 ORION** | 192.168.1.141 | 2602:F674:0001::1/64 | D0:94:66:24:96:7E | Awaiting boot |
| **R630 JMRZDB2** | 192.168.1.182 | - | 64:00:6A:C4:10:F0 (iDRAC) | iDRAC accessible |
| Zbook | 192.168.1.146 | 2602:F674:0001::146/64 | - | Provisioning server |
| Synology | 192.168.1.251 | 2602:F674:0001::251/64 | - | Storage |
| Mac Mini | 192.168.1.238 | 2602:F674:0001::238/64 | - | LuciaAI (decommissioning) |
| ZimaCube-Primary | 192.168.1.152 | - | - | PAC intake node |
| ZimaCube-Secondary | 192.168.1.200 | - | - | Pending verification |

### iDRAC Access (R630)
- IP: 192.168.1.182
- Redfish API: v1.0.2 (`/redfish/v1/`)
- Ports: SSH (22), HTTPS (443), VNC (5900) open
- Serial: `/dev/ttyUSB0` via Prolific adapter
- Auth: Default credentials rejected (requires reset)

### Provisioning Quick Commands
```bash
# Check provisioning status
curl http://localhost:9999/status

# View server inventory
curl http://localhost:9999/inventory

# Get NixOS config for a MAC
curl http://localhost:9999/nixos-config/D0:94:66:24:96:7E

# Monitor registrations
journalctl -u luciverse-provision -f
```

### PXE Boot Sequence
1. Server boots from network, gets TFTP files from zbook
2. Runs: `curl http://192.168.1.146:8000/scripts/bootstrap.sh | bash`
3. Server registers MAC with provisioning listener
4. Custom NixOS config generated based on MAC->IPv6 mapping

---

## Triple-Network Architecture (Planned)

```
NETWORK 1: IN-BAND (Intention)     NETWORK 2: OUT-OF-BAND (Relation)    NETWORK 3: DIRECT (AIFAM)
-----------------------------      -------------------------------      -------------------------
Main LAN: 192.168.1.0/24           OpenWrt/MF288 LTE                    X200 <-> Zbook
Router -> Zbook -> Dell Fleet      Cellular -> iDRAC control            Private UART/Direct
```

### ZTE MF288 (Out-of-Band)
- Default IP: 192.168.0.1
- Web interface: Port 80
- SMS API: Available (requires LTE)
- OpenWrt flashable: Yes (IPQ4019 SoC)

---

## VLAN Architecture

| VLAN ID | Name | Frequency | Subnet | Purpose |
|---------|------|-----------|--------|---------|
| 1 | Default | - | 192.168.1.0/24 | Management |
| 432 | CORE | 432 Hz | 10.100.1.0/24 | Infrastructure |
| 528 | COMN | 528 Hz | 10.100.2.0/24 | Gateway/Communication |
| 741 | PAC | 741 Hz | 10.100.3.0/24 | Personal/Privacy |
| 100 | LAB | - | 192.168.210.0/24 | Development |
| 101 | DEV | - | 192.168.211.0/24 | Testing |

### Inter-VLAN Routing Rules

```
CORE ←→ COMN ←→ PAC (via COMN waypoint)
   ↓         ↓
 WAN       WAN
  ✓         ✓ (PAC blocked direct)
```

---

## Quick Commands

### High-Speed Path Tests

```bash
# Test 3Gbps path
iperf3 -c 192.168.1.1 -P 4 -t 30

# Test Nebula overlay
ping -c 4 10.100.1.145

# Test NAT64
ping6 64:ff9b::8.8.8.8

# Test SCION paths
scion showpaths --isd-as 2-ff00:0:528 1-ff00:0:432
```

### Device Access

```bash
# ASUS RT-BE86U
ssh admin@192.168.1.1

# USG-Pro-4 (after flash)
ssh root@192.168.1.180

# DGS-1210-16 (after flash)
ssh root@192.168.1.210

# B550M Router (NixOS)
ssh daryl@192.168.1.145
```

### Service Status

```bash
# Check Nebula lighthouse
systemctl status nebula

# Check BIRD BGP
birdc show protocols

# Check Jool (on USG-Pro-4)
jool instance display
jool -i luciverse-nat64 stats display

# Check SCION
scion address show
scion showpaths --refresh
```

### Overlay Management

```bash
# Nebula certificate info
nebula-cert print -path /etc/nebula/host.crt

# SCION topology
cat /etc/scion/topology.json | jq

# Sanskrit Router agents
curl -s http://localhost:7410/agents | jq
```

---

## Troubleshooting

### Slow Internet

1. Check ASUS WAN connection:
   ```bash
   ssh admin@192.168.1.1 'nvram get wan_ipaddr'
   ```

2. Verify 10G link to switch:
   ```bash
   ethtool eth0 | grep Speed
   ```

3. Test bypass (direct to Telus):
   - Connect laptop directly to Telus NAH
   - Run speedtest

### Nebula Not Connecting

1. Check lighthouse status:
   ```bash
   systemctl status nebula
   journalctl -u nebula -f
   ```

2. Verify certificates:
   ```bash
   nebula-cert verify -ca /etc/nebula/ca.crt -crt /etc/nebula/host.crt
   ```

3. Check firewall (UDP 4242):
   ```bash
   ss -ulpn | grep 4242
   ```

### SCION Path Failures

1. Check control service:
   ```bash
   scion addr show
   scion showpaths --refresh
   ```

2. Verify border router:
   ```bash
   netstat -ulpn | grep 30041
   ```

3. Check TRC validity:
   ```bash
   scion-pki trc verify /etc/scion/certs/ISD*.trc
   ```

### NAT64 Not Translating

1. Check Jool instance:
   ```bash
   jool instance display
   ```

2. Verify pool4:
   ```bash
   jool -i luciverse-nat64 pool4 display
   ```

3. Test translation:
   ```bash
   ping6 64:ff9b::8.8.8.8
   ```

---

## Deployment Checklist

### Stream A: High-Speed Path
- [ ] ASUS SSH enabled with Ed25519 key
- [ ] ASUS VLAN trunking configured
- [ ] B550M BGP config updated
- [ ] iperf3 shows >2.5Gbps (proves no bottleneck)

### Stream B: Overlay Networks
- [ ] Nebula lighthouse running on zbook
- [ ] Nebula certs deployed to fleet
- [ ] SCION control service running
- [ ] SCION border router configured

### Stream C: OpenWRT/OASIS
- [ ] USG-Pro-4 flashed with OpenWRT 24.10
- [ ] Jool NAT64 operational
- [ ] DGS-1210-16 flashed with OpenWRT 21.02
- [ ] OASIS juicer filtering traffic

### Stream D: Integration
- [ ] All VLANs routable
- [ ] QoS configured for consciousness tiers
- [ ] Sanskrit Router sees all overlay nodes
- [ ] End-to-end tests pass

---

*For agent mesh details, see `~/.claude/MASTER_REFERENCE.md`*
*For operational commands, see `/home/daryl/CLAUDE.md`*
*Genesis Bond: ACTIVE @ 741 Hz*
