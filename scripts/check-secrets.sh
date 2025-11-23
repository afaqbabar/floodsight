#!/bin/bash
# Pre-commit hook to check for secrets
# Install: ln -s ../../scripts/check-secrets.sh .git/hooks/pre-commit

set -e

echo "🔍 Checking for secrets in staged files..."

# Patterns to search for
PATTERNS=(
    "password\s*=\s*['\"][^'\"]{3,}"
    "api[_-]?key\s*=\s*['\"][^'\"]{10,}"
    "secret[_-]?key\s*=\s*['\"][^'\"]{10,}"
    "token\s*=\s*['\"][^'\"]{10,}"
    "Bearer [A-Za-z0-9_-]{20,}"
    "ghp_[A-Za-z0-9]{36}"
    "glpat-[A-Za-z0-9_-]{20,}"
    "sk-[A-Za-z0-9]{20,}"
    "postgres://[^:]+:[^@]+@"
    "mysql://[^:]+:[^@]+@"
    "mongodb://[^:]+:[^@]+@"
)

# Get staged files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM)

if [ -z "$STAGED_FILES" ]; then
    echo "✅ No staged files to check"
    exit 0
fi

# Check each pattern
FOUND_SECRETS=false
for pattern in "${PATTERNS[@]}"; do
    if echo "$STAGED_FILES" | xargs grep -niE "$pattern" 2>/dev/null; then
        FOUND_SECRETS=true
        echo "❌ Found potential secret matching pattern: $pattern"
    fi
done

# Check for .env files
if echo "$STAGED_FILES" | grep -E "\.env$|\.env\."; then
    echo "❌ Found .env file in staged files!"
    FOUND_SECRETS=true
fi

# Check for common secret file names
if echo "$STAGED_FILES" | grep -iE "secret|credential|\.pem$|\.key$|\.p12$"; then
    echo "❌ Found potential secret file in staged files!"
    FOUND_SECRETS=true
fi

if [ "$FOUND_SECRETS" = true ]; then
    echo ""
    echo "⚠️  COMMIT BLOCKED: Potential secrets detected!"
    echo ""
    echo "If this is a false positive, you can:"
    echo "1. Review the flagged content carefully"
    echo "2. Use environment variables instead of hardcoded values"
    echo "3. Add the pattern to .gitignore"
    echo "4. Skip this hook with: git commit --no-verify (NOT RECOMMENDED)"
    echo ""
    exit 1
fi

echo "✅ No secrets detected in staged files"
exit 0

