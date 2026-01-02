#!/bin/bash
# Check Netlify deployment status and health

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Help text
show_help() {
  cat << EOF
Usage: check_deployment.sh [OPTIONS]

Check Netlify deployment status and health.

OPTIONS:
  -h, --help              Show this help message
  -s, --site SITE_ID      Specific site ID (optional, will use linked site)
  -v, --verbose           Verbose output
  -f, --functions         Check function status

EXAMPLES:
  ./check_deployment.sh
  ./check_deployment.sh --site abc123
  ./check_deployment.sh --functions --verbose
EOF
}

# Parse arguments
SITE_ID=""
VERBOSE=false
CHECK_FUNCTIONS=false

while [[ $# -gt 0 ]]; do
  case $1 in
    -h|--help)
      show_help
      exit 0
      ;;
    -s|--site)
      SITE_ID="$2"
      shift 2
      ;;
    -v|--verbose)
      VERBOSE=true
      shift
      ;;
    -f|--functions)
      CHECK_FUNCTIONS=true
      shift
      ;;
    *)
      echo "Unknown option: $1"
      show_help
      exit 1
      ;;
  esac
done

# Check if netlify CLI is installed
if ! command -v netlify &> /dev/null; then
  echo -e "${RED}❌ Netlify CLI not found${NC}"
  echo "Install with: npm install -g netlify-cli"
  exit 1
fi

echo -e "${YELLOW}🔍 Checking Netlify deployment...${NC}\n"

# Get site status
if [ -n "$SITE_ID" ]; then
  STATUS=$(netlify status --site "$SITE_ID" 2>&1)
else
  STATUS=$(netlify status 2>&1)
fi

# Check if site is linked
if echo "$STATUS" | grep -q "not linked"; then
  echo -e "${RED}❌ Site not linked${NC}"
  echo "Run: netlify link"
  exit 1
fi

# Display site info
echo -e "${GREEN}✅ Site linked${NC}"
echo "$STATUS"
echo ""

# Get latest deploy
echo -e "${YELLOW}📦 Latest deploy:${NC}"
DEPLOYS=$(netlify api listSiteDeploys --data '{"per_page": 1}' 2>&1)

if [ $VERBOSE = true ]; then
  echo "$DEPLOYS"
else
  echo "$DEPLOYS" | jq -r '.[0] | "State: \(.state)\nCreated: \(.created_at)\nDeploy URL: \(.deploy_ssl_url)"'
fi

echo ""

# Check functions if requested
if [ $CHECK_FUNCTIONS = true ]; then
  echo -e "${YELLOW}⚡ Functions status:${NC}"
  netlify functions:list
  echo ""
fi

# Check environment variables
echo -e "${YELLOW}🔐 Environment variables:${NC}"
ENV_COUNT=$(netlify env:list 2>&1 | grep -c "│" || true)
echo "Total environment variables: $ENV_COUNT"

if [ $VERBOSE = true ]; then
  netlify env:list
fi

echo ""

# Health check summary
echo -e "${GREEN}✅ Deployment check complete${NC}"
