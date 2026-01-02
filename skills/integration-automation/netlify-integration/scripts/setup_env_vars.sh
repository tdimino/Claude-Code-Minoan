#!/bin/bash
# Interactive script to set up Netlify environment variables

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Help text
show_help() {
  cat << EOF
Usage: setup_env_vars.sh [OPTIONS]

Interactive setup for Netlify environment variables.

OPTIONS:
  -h, --help              Show this help message
  -f, --file FILE         Import from .env file
  -c, --context CONTEXT   Set context (production, deploy-preview, branch-deploy, all)
  --twilio-aldea          Use Twilio-Aldea preset

EXAMPLES:
  ./setup_env_vars.sh
  ./setup_env_vars.sh --file .env.production
  ./setup_env_vars.sh --twilio-aldea --context production
EOF
}

# Parse arguments
ENV_FILE=""
CONTEXT="all"
PRESET=""

while [[ $# -gt 0 ]]; do
  case $1 in
    -h|--help)
      show_help
      exit 0
      ;;
    -f|--file)
      ENV_FILE="$2"
      shift 2
      ;;
    -c|--context)
      CONTEXT="$2"
      shift 2
      ;;
    --twilio-aldea)
      PRESET="twilio-aldea"
      shift
      ;;
    *)
      echo "Unknown option: $1"
      show_help
      exit 1
      ;;
  esac
done

# Check netlify CLI
if ! command -v netlify &> /dev/null; then
  echo -e "${RED}❌ Netlify CLI not found${NC}"
  echo "Install with: npm install -g netlify-cli"
  exit 1
fi

echo -e "${BLUE}🔧 Netlify Environment Variables Setup${NC}\n"

# Import from file if provided
if [ -n "$ENV_FILE" ]; then
  if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}❌ File not found: $ENV_FILE${NC}"
    exit 1
  fi

  echo -e "${YELLOW}📥 Importing from $ENV_FILE...${NC}"
  netlify env:import "$ENV_FILE"
  echo -e "${GREEN}✅ Import complete${NC}"
  exit 0
fi

# Function to set variable
set_var() {
  local key=$1
  local description=$2
  local default=$3
  local secret=${4:-false}

  echo -e "${YELLOW}$description${NC}"

  if [ "$secret" = true ]; then
    read -sp "  $key: " value
    echo ""
  else
    if [ -n "$default" ]; then
      read -p "  $key [$default]: " value
      value=${value:-$default}
    else
      read -p "  $key: " value
    fi
  fi

  if [ -n "$value" ]; then
    netlify env:set "$key" "$value" --context "$CONTEXT" > /dev/null 2>&1
    echo -e "${GREEN}  ✅ Set $key${NC}"
  else
    echo -e "${YELLOW}  ⏭️  Skipped $key${NC}"
  fi
  echo ""
}

# Twilio-Aldea preset
if [ "$PRESET" = "twilio-aldea" ]; then
  echo -e "${BLUE}Setting up Twilio-Aldea environment variables...${NC}\n"

  # Database
  echo -e "${BLUE}━━━ Database (Supabase) ━━━${NC}"
  set_var "SUPABASE_URL" "Supabase project URL" "" false
  set_var "SUPABASE_SERVICE_KEY" "Supabase service role key" "" true
  set_var "SUPABASE_ANON_KEY" "Supabase anon key" "" true

  # SMS Provider
  echo -e "${BLUE}━━━ SMS Provider ━━━${NC}"
  set_var "SMS_PROVIDER" "SMS provider (telnyx or twilio)" "telnyx" false
  set_var "TELNYX_API_KEY" "Telnyx API key" "" true
  set_var "TELNYX_PUBLIC_KEY" "Telnyx public key (for signature validation)" "" false

  # Application
  echo -e "${BLUE}━━━ Application ━━━${NC}"
  set_var "NEXT_PUBLIC_APP_URL" "Application URL" "https://your-site.netlify.app" false
  set_var "NEXTAUTH_SECRET" "NextAuth secret (min 32 chars)" "" true

  # LLM/AI
  echo -e "${BLUE}━━━ LLM/AI ━━━${NC}"
  set_var "OPENROUTER_API_KEY" "OpenRouter API key" "" true

  echo -e "${GREEN}✅ Twilio-Aldea setup complete${NC}"
  exit 0
fi

# Generic interactive mode
echo -e "${BLUE}Interactive mode - Enter values or skip with Enter${NC}\n"
echo -e "${YELLOW}Context: $CONTEXT${NC}\n"

# Database
echo -e "${BLUE}━━━ Database ━━━${NC}"
set_var "DATABASE_URL" "Database connection string" "" true
set_var "SUPABASE_URL" "Supabase URL (if using Supabase)" "" false
set_var "SUPABASE_SERVICE_KEY" "Supabase service key" "" true

# API Keys
echo -e "${BLUE}━━━ API Keys ━━━${NC}"
set_var "API_KEY" "Primary API key" "" true
set_var "API_SECRET" "API secret" "" true

# Application
echo -e "${BLUE}━━━ Application ━━━${NC}"
set_var "NEXT_PUBLIC_APP_URL" "Public application URL" "" false
set_var "NODE_ENV" "Node environment" "production" false

echo -e "${GREEN}✅ Environment variables setup complete${NC}"
echo ""
echo "To view all variables:"
echo "  netlify env:list"
