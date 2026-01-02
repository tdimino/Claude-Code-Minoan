#!/bin/bash
# Test Netlify functions locally

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
Usage: test_function_locally.sh [FUNCTION_NAME] [OPTIONS]

Test Netlify functions locally with sample data.

ARGUMENTS:
  FUNCTION_NAME           Name of the function to test (required)

OPTIONS:
  -h, --help              Show this help message
  -m, --method METHOD     HTTP method (GET, POST, PUT, DELETE) [default: POST]
  -d, --data DATA         JSON data to send
  -f, --file FILE         File containing JSON data
  -H, --header HEADER     Add custom header (can be used multiple times)
  -p, --port PORT         Function port [default: 9999]
  --start                 Start netlify dev before testing
  --no-start              Don't start netlify dev (assume already running)

EXAMPLES:
  # Test webhook function with inline data
  ./test_function_locally.sh webhook -d '{"test": "data"}'

  # Test with data from file
  ./test_function_locally.sh webhook -f test-payload.json

  # Test with custom headers
  ./test_function_locally.sh webhook -H "Authorization: Bearer token"

  # Start server and test
  ./test_function_locally.sh webhook --start -d '{"test": "data"}'
EOF
}

# Default values
FUNCTION_NAME=""
METHOD="POST"
DATA=""
DATA_FILE=""
HEADERS=()
PORT="9999"
START_SERVER=false
NO_START=false

# Parse arguments
if [ $# -eq 0 ]; then
  show_help
  exit 1
fi

# First argument is function name (if not a flag)
if [[ ! "$1" =~ ^- ]]; then
  FUNCTION_NAME="$1"
  shift
fi

while [[ $# -gt 0 ]]; do
  case $1 in
    -h|--help)
      show_help
      exit 0
      ;;
    -m|--method)
      METHOD="$2"
      shift 2
      ;;
    -d|--data)
      DATA="$2"
      shift 2
      ;;
    -f|--file)
      DATA_FILE="$2"
      shift 2
      ;;
    -H|--header)
      HEADERS+=("$2")
      shift 2
      ;;
    -p|--port)
      PORT="$2"
      shift 2
      ;;
    --start)
      START_SERVER=true
      shift
      ;;
    --no-start)
      NO_START=true
      shift
      ;;
    *)
      if [ -z "$FUNCTION_NAME" ]; then
        FUNCTION_NAME="$1"
        shift
      else
        echo "Unknown option: $1"
        show_help
        exit 1
      fi
      ;;
  esac
done

# Validate function name
if [ -z "$FUNCTION_NAME" ]; then
  echo -e "${RED}❌ Function name required${NC}"
  show_help
  exit 1
fi

# Check if netlify CLI is installed
if ! command -v netlify &> /dev/null; then
  echo -e "${RED}❌ Netlify CLI not found${NC}"
  echo "Install with: npm install -g netlify-cli"
  exit 1
fi

echo -e "${BLUE}🧪 Testing function: $FUNCTION_NAME${NC}\n"

# Start server if requested
if [ "$START_SERVER" = true ]; then
  echo -e "${YELLOW}🚀 Starting netlify dev...${NC}"
  netlify dev &
  SERVER_PID=$!

  # Wait for server to start
  echo "Waiting for server to start..."
  sleep 5

  # Cleanup on exit
  trap "kill $SERVER_PID 2>/dev/null" EXIT
fi

# Load data from file if provided
if [ -n "$DATA_FILE" ]; then
  if [ ! -f "$DATA_FILE" ]; then
    echo -e "${RED}❌ Data file not found: $DATA_FILE${NC}"
    exit 1
  fi
  DATA=$(cat "$DATA_FILE")
fi

# Build URL
URL="http://localhost:$PORT/.netlify/functions/$FUNCTION_NAME"

# Build curl command
CURL_CMD="curl -X $METHOD \"$URL\""

# Add headers
for HEADER in "${HEADERS[@]}"; do
  CURL_CMD="$CURL_CMD -H \"$HEADER\""
done

# Add content-type for POST/PUT
if [[ "$METHOD" == "POST" || "$METHOD" == "PUT" ]]; then
  CURL_CMD="$CURL_CMD -H \"Content-Type: application/json\""
fi

# Add data
if [ -n "$DATA" ]; then
  CURL_CMD="$CURL_CMD -d '$DATA'"
fi

# Add verbose flag
CURL_CMD="$CURL_CMD -v"

# Display request details
echo -e "${BLUE}📤 Request:${NC}"
echo "  Method: $METHOD"
echo "  URL: $URL"
if [ ${#HEADERS[@]} -gt 0 ]; then
  echo "  Headers:"
  for HEADER in "${HEADERS[@]}"; do
    echo "    $HEADER"
  done
fi
if [ -n "$DATA" ]; then
  echo "  Data:"
  echo "$DATA" | jq '.' 2>/dev/null || echo "$DATA"
fi
echo ""

# Check if server is running (if not starting it)
if [ "$START_SERVER" = false ] && [ "$NO_START" = false ]; then
  if ! nc -z localhost "$PORT" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Function server not running on port $PORT${NC}"
    echo "Start with: netlify dev"
    echo "Or use: $0 $FUNCTION_NAME --start"
    exit 1
  fi
fi

# Execute request
echo -e "${BLUE}📥 Response:${NC}"
eval "$CURL_CMD" 2>&1 | tee /tmp/curl_response.txt

echo ""
echo -e "${GREEN}✅ Test complete${NC}"

# Parse response
RESPONSE_CODE=$(grep "< HTTP" /tmp/curl_response.txt | tail -1 | awk '{print $3}')
if [ -n "$RESPONSE_CODE" ]; then
  echo "Response code: $RESPONSE_CODE"
fi

rm -f /tmp/curl_response.txt
