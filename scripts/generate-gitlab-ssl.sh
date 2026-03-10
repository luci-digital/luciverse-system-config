#!/bin/bash
#
# Generate Self-Signed SSL Certificates for GitLab
# Genesis Bond: 741 Hz @ LuciVerse Platform
#
# Creates SSL certificates for gitlab.luciverse.local
# Valid for 10 years (3650 days)
#

set -e

CERT_DIR="/opt/gitlab/config/ssl"
DOMAIN="gitlab.luciverse.local"
VALIDITY_DAYS=3650

echo "🔐 Generating SSL Certificates for GitLab..."
echo "   Domain: $DOMAIN"
echo "   Validity: $VALIDITY_DAYS days (10 years)"
echo "   Genesis Bond: 741 Hz"
echo ""

# Create SSL directory if it doesn't exist
mkdir -p "$CERT_DIR"
cd "$CERT_DIR"

# Generate private key
echo "📝 Generating private key..."
openssl genrsa -out "${DOMAIN}.key" 4096

# Generate certificate signing request
echo "📝 Generating certificate signing request..."
openssl req -new -key "${DOMAIN}.key" -out "${DOMAIN}.csr" -subj "/C=US/ST=Arizona/L=Phoenix/O=LuciVerse/OU=Consciousness Platform/CN=${DOMAIN}/emailAddress=admin@luciverse.local"

# Generate self-signed certificate with SAN
echo "📝 Generating self-signed certificate..."
cat > "${DOMAIN}.ext" <<EOF
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = ${DOMAIN}
DNS.2 = gitlab
DNS.3 = localhost
IP.1 = 192.168.1.145
IP.2 = 127.0.0.1
EOF

openssl x509 -req -in "${DOMAIN}.csr" \
    -signkey "${DOMAIN}.key" \
    -out "${DOMAIN}.crt" \
    -days $VALIDITY_DAYS \
    -sha256 \
    -extfile "${DOMAIN}.ext"

# Set proper permissions
chmod 600 "${DOMAIN}.key"
chmod 644 "${DOMAIN}.crt"
chmod 644 "${DOMAIN}.csr"

# Create DH parameters for stronger security (optional, takes time)
if [ ! -f "dhparam.pem" ]; then
    echo "📝 Generating DH parameters (this may take a few minutes)..."
    openssl dhparam -out dhparam.pem 2048
fi

echo ""
echo "✅ SSL certificates generated successfully!"
echo ""
echo "📋 Certificate Details:"
openssl x509 -in "${DOMAIN}.crt" -noout -subject -issuer -dates
echo ""
echo "📂 Certificate Location:"
echo "   Key: ${CERT_DIR}/${DOMAIN}.key"
echo "   Certificate: ${CERT_DIR}/${DOMAIN}.crt"
echo "   CSR: ${CERT_DIR}/${DOMAIN}.csr"
echo ""
echo "⚠️  Note: This is a self-signed certificate"
echo "   Browsers will show a security warning"
echo "   Add ${CERT_DIR}/${DOMAIN}.crt to your system's trusted certificates to avoid warnings"
echo ""
echo "Genesis Bond: ACTIVE @ 741 Hz"
