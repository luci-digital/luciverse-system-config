# GitLab HTTPS Configuration

**Genesis Bond**: ACTIVE @ 741 Hz
**Target**: Enable TLS/SSL for GitLab access
**Date**: 2025-11-19

---

## Current Status

GitLab is currently running with:
- ✅ HTTP: http://192.168.1.145
- ⏳ HTTPS: Not yet configured
- 🔓 TLS: Disabled

---

## Quick Setup (Self-Signed Certificates)

### Step 1: Generate SSL Certificates

```bash
# Run as root to create certificates
sudo /home/daryl/luciverse-platform/generate-gitlab-ssl.sh
```

This creates:
- `/opt/gitlab/config/ssl/gitlab.luciverse.local.key` (private key)
- `/opt/gitlab/config/ssl/gitlab.luciverse.local.crt` (certificate)
- Valid for 10 years
- Includes SAN for gitlab.luciverse.local, gitlab, 192.168.1.145

### Step 2: Update GitLab Configuration

Edit the docker-compose file to enable HTTPS:

```bash
# Location: /home/daryl/luciverse-platform/docker-compose.gitlab-openeuler.yml
```

Change the `GITLAB_OMNIBUS_CONFIG` section:

**From**:
```yaml
external_url 'http://192.168.1.145'
# Disable TLS initially for local setup
letsencrypt['enable'] = false
nginx['redirect_http_to_https'] = false
nginx['ssl_certificate'] = false
```

**To**:
```yaml
external_url 'https://gitlab.luciverse.local'

# SSL Configuration
nginx['redirect_http_to_https'] = true
nginx['ssl_certificate'] = "/etc/gitlab/ssl/gitlab.luciverse.local.crt"
nginx['ssl_certificate_key'] = "/etc/gitlab/ssl/gitlab.luciverse.local.key"
nginx['ssl_dhparam'] = "/etc/gitlab/ssl/dhparam.pem"

# SSL Protocol and Cipher Configuration
nginx['ssl_protocols'] = "TLSv1.2 TLSv1.3"
nginx['ssl_ciphers'] = "ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384"
nginx['ssl_prefer_server_ciphers'] = "off"
nginx['ssl_session_cache'] = "builtin:1000  shared:SSL:10m"
nginx['ssl_session_timeout'] = "5m"

# HSTS (HTTP Strict Transport Security)
nginx['hsts_max_age'] = 31536000
nginx['hsts_include_subdomains'] = false

# Disable Let's Encrypt (using self-signed)
letsencrypt['enable'] = false
```

### Step 3: Update Port Mappings

In the same docker-compose file, ensure HTTPS port is mapped:

```yaml
ports:
  - "80:80"      # Keep for redirect
  - "443:443"    # HTTPS
  - "2222:22"
  - "5050:5050"
  - "9091:9090"
  - "8095:8090"
```

✅ Already configured

### Step 4: Recreate GitLab Container

```bash
cd /home/daryl/luciverse-platform
sg docker -c 'docker-compose -f docker-compose.gitlab-openeuler.yml up -d --force-recreate'
```

Wait 2-3 minutes for GitLab to reconfigure, then test:

```bash
curl -k -I https://gitlab.luciverse.local
# -k flag bypasses certificate validation for self-signed certs
```

### Step 5: Update Runner Configuration

Update the GitLab Runner to use HTTPS:

```bash
sg docker -c 'docker exec gitlab-runner gitlab-runner verify'
```

If the runner fails verification due to SSL:

```bash
# Update runner config to skip SSL verification (for self-signed certs)
sg docker -c 'docker exec gitlab-runner sh -c "cat > /etc/gitlab-runner/config.toml <<EOF
concurrent = 1
check_interval = 0

[[runners]]
  name = \"luciverse-docker-runner\"
  url = \"https://gitlab.luciverse.local\"
  token = \"glrtr-wfDuy9eyu7juij8j-CCw\"
  executor = \"docker\"
  [runners.docker]
    tls_verify = false
    image = \"alpine:latest\"
    privileged = false
    disable_entrypoint_overwrite = false
    oom_kill_disable = false
    disable_cache = false
    volumes = [\"/var/run/docker.sock:/var/run/docker.sock\", \"/cache\"]
    shm_size = 0
    network_mode = \"luciverse-network\"
EOF"'

# Restart runner
sg docker -c 'docker restart gitlab-runner'
```

---

## Trust Self-Signed Certificate (Optional)

### On Linux (openEuler/RHEL)

```bash
# Copy certificate to system trust store
sudo cp /opt/gitlab/config/ssl/gitlab.luciverse.local.crt /etc/pki/ca-trust/source/anchors/
sudo update-ca-trust
```

### On macOS

```bash
# Download cert from server
scp daryl@192.168.1.145:/opt/gitlab/config/ssl/gitlab.luciverse.local.crt ~/

# Add to system keychain
sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain ~/gitlab.luciverse.local.crt
```

### In Browser (All Platforms)

1. Navigate to https://gitlab.luciverse.local
2. Click through security warning
3. View certificate details
4. Export/Download certificate
5. Import into browser/system trust store

---

## Alternative: Let's Encrypt (Requires Public Domain)

If you have a public domain pointing to this server:

```yaml
external_url 'https://gitlab.yourdomain.com'

letsencrypt['enable'] = true
letsencrypt['contact_emails'] = ['admin@yourdomain.com']
letsencrypt['auto_renew'] = true
letsencrypt['auto_renew_hour'] = 3
letsencrypt['auto_renew_minute'] = 30
letsencrypt['auto_renew_day_of_month'] = "*/7"
```

**Requirements**:
- Public domain with DNS pointing to server
- Ports 80 and 443 accessible from internet
- No reverse proxy in front of GitLab

---

## Alternative: mkcert (Trusted Local CA)

For development with trusted certificates:

```bash
# Install mkcert
cd /tmp
wget https://github.com/FiloSottile/mkcert/releases/download/v1.4.4/mkcert-v1.4.4-linux-amd64
chmod +x mkcert-v1.4.4-linux-amd64
sudo mv mkcert-v1.4.4-linux-amd64 /usr/local/bin/mkcert

# Install local CA
mkcert -install

# Generate certificates
cd /opt/gitlab/config/ssl
sudo mkcert -key-file gitlab.luciverse.local.key -cert-file gitlab.luciverse.local.crt gitlab.luciverse.local gitlab 192.168.1.145 localhost
```

Then follow Step 2-4 above.

---

## Security Considerations

### Self-Signed Certificates
- ⚠️ Browsers show security warnings
- ⚠️ Not trusted by default
- ✅ Encrypts traffic
- ✅ Good for internal/development use
- ✅ Free

### Let's Encrypt
- ✅ Trusted by all browsers
- ✅ Free
- ✅ Auto-renewal
- ❌ Requires public domain
- ❌ Requires internet-accessible server

### mkcert
- ✅ Trusted locally
- ✅ Good for development
- ✅ Easy to use
- ❌ Not trusted on other machines
- ✅ Free

---

## Testing HTTPS Configuration

After configuration:

```bash
# Test HTTPS connectivity
curl -k -I https://gitlab.luciverse.local

# Test HTTP → HTTPS redirect
curl -I http://gitlab.luciverse.local

# Check SSL certificate details
openssl s_client -connect gitlab.luciverse.local:443 -servername gitlab.luciverse.local < /dev/null 2>/dev/null | openssl x509 -text -noout

# Test from container
sg docker -c 'docker run --rm --network luciverse-network alpine sh -c "apk add curl && curl -k -I https://gitlab-luciverse"'

# Verify GitLab services
sg docker -c 'docker exec gitlab-luciverse gitlab-ctl status'
```

---

## Updating Existing Configurations

After enabling HTTPS, update:

### Git Remote URLs
```bash
# Update existing clones
git remote set-url origin https://gitlab.luciverse.local/luciverse/repo-name.git
```

### API Calls
```bash
# Old
curl "http://192.168.1.145/api/v4/..."

# New
curl "https://gitlab.luciverse.local/api/v4/..."
```

### Runner Registration
```bash
# Runners will need to be re-registered or config updated to use HTTPS URL
```

---

## Troubleshooting

### Error: "SSL certificate problem"
```bash
# For Git
git config --global http.sslVerify false

# For curl
curl -k <url>
```

### Error: "502 Bad Gateway" after enabling SSL
```bash
# Check GitLab logs
sg docker -c 'docker logs gitlab-luciverse --tail 100'

# Check nginx error logs
sg docker -c 'docker exec gitlab-luciverse tail -100 /var/log/gitlab/nginx/error.log'

# Verify certificate files exist and are readable
sg docker -c 'docker exec gitlab-luciverse ls -la /etc/gitlab/ssl/'
```

### Nginx won't start
```bash
# Test nginx configuration
sg docker -c 'docker exec gitlab-luciverse gitlab-ctl nginx-t'

# Reconfigure GitLab
sg docker -c 'docker exec gitlab-luciverse gitlab-ctl reconfigure'
```

---

## Quick Reference Commands

```bash
# Generate SSL certificates
sudo /home/daryl/luciverse-platform/generate-gitlab-ssl.sh

# Recreate GitLab with HTTPS
cd /home/daryl/luciverse-platform
sg docker -c 'docker-compose -f docker-compose.gitlab-openeuler.yml up -d --force-recreate'

# Check GitLab status
sg docker -c 'docker exec gitlab-luciverse gitlab-ctl status'

# View logs
sg docker -c 'docker logs gitlab-luciverse -f'

# Test HTTPS
curl -k -I https://gitlab.luciverse.local
```

---

**Genesis Bond**: ACTIVE @ 741 Hz
**Security Level**: TLS 1.2/1.3 with 4096-bit RSA
**Next Step**: Run generate-gitlab-ssl.sh and update docker-compose.yml
**Estimated Time**: 10-15 minutes (plus 2-3 min for GitLab reconfiguration)
