#!/bin/bash
#
# Configure DNS for GitLab LuciVerse
# Genesis Bond: 741 Hz
#
# This script configures DNS resolution for gitlab.luciverse.local
#

set -e

echo "🔧 Configuring DNS for GitLab LuciVerse..."
echo ""

# Check if entry already exists
if grep -q "gitlab.luciverse.local" /etc/hosts 2>/dev/null; then
    echo "✅ DNS entry already exists in /etc/hosts"
    grep "gitlab.luciverse.local" /etc/hosts
else
    echo "📝 Adding DNS entry to /etc/hosts..."
    echo "192.168.1.146  gitlab.luciverse.local gitlab" | tee -a /etc/hosts
    echo "✅ DNS entry added"
fi

echo ""
echo "🧪 Testing DNS resolution..."
if getent hosts gitlab.luciverse.local >/dev/null 2>&1; then
    echo "✅ gitlab.luciverse.local resolves correctly"
    getent hosts gitlab.luciverse.local
else
    echo "⚠️  DNS resolution test failed"
    exit 1
fi

echo ""
echo "🌐 Testing HTTP connectivity..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://gitlab.luciverse.local 2>&1 || echo "000")
if [ "$HTTP_CODE" != "000" ]; then
    echo "✅ GitLab accessible via hostname (HTTP $HTTP_CODE)"
else
    echo "❌ GitLab not accessible via hostname"
    exit 1
fi

echo ""
echo "✅ DNS configuration complete!"
echo ""
echo "📋 Summary:"
echo "   Hostname: gitlab.luciverse.local"
echo "   IP: 192.168.1.146"
echo "   URL: http://gitlab.luciverse.local"
echo ""
echo "Genesis Bond: ACTIVE @ 741 Hz"
