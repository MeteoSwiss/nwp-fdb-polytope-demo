#!/bin/bash
# trace_request.sh - Trace a request across all services

REQUEST_ID="${1:?Usage: $0 <request_id>}"
AWS_PROFILE="${AWS_PROFILE:-aws-polytope-depl}"
AWS_REGION="${AWS_REGION:-eu-central-2}"
LOOKBACK_SECONDS="${LOOKBACK_SECONDS:-86400}"

START_TIME=$(($(date +%s) - LOOKBACK_SECONDS))000
TRACE_DIR="/tmp/trace_$REQUEST_ID"
mkdir -p "$TRACE_DIR"

# Step 1: Fetch logs by request_id
echo "Fetching logs for request $REQUEST_ID..."
aws logs filter-log-events \
  --profile "$AWS_PROFILE" \
  --region "$AWS_REGION" \
  --log-group-name polytope-server-logs \
  --start-time "$START_TIME" \
  --filter-pattern "\"$REQUEST_ID\"" \
  --output json > "$TRACE_DIR/by_request.json"

# Step 2: Extract unique trace_ids
TRACE_IDS=$(jq -r '[.events[].message | fromjson? | .trace_id // empty] | unique | .[]' "$TRACE_DIR/by_request.json" 2>/dev/null)

if [[ -n "$TRACE_IDS" ]]; then
  echo "Found trace IDs: $(echo "$TRACE_IDS" | tr '\n' ' ')"

  # Step 3: Build OR filter pattern for trace_ids
  TRACE_FILTER=""
  for tid in $TRACE_IDS; do
    TRACE_FILTER+="?\"$tid\" "
  done

  # Step 4: Fetch logs by trace_ids
  echo "Fetching related logs by trace_id..."
  aws logs filter-log-events \
    --profile "$AWS_PROFILE" \
    --region "$AWS_REGION" \
    --log-group-name polytope-server-logs \
    --start-time "$START_TIME" \
    --filter-pattern "$TRACE_FILTER" \
    --output json > "$TRACE_DIR/by_trace.json"

  # Step 5: Merge and deduplicate by eventId, sort by timestamp
  jq -s '
    [.[].events[]] |
    unique_by(.eventId) |
    sort_by(.timestamp)
  ' "$TRACE_DIR/by_request.json" "$TRACE_DIR/by_trace.json" > "$TRACE_DIR/merged.json"
else
  echo "No trace IDs found, using request_id logs only"
  jq '.events | sort_by(.timestamp)' "$TRACE_DIR/by_request.json" > "$TRACE_DIR/merged.json"
fi

EVENT_COUNT=$(jq 'length' "$TRACE_DIR/merged.json")
echo "Total events: $EVENT_COUNT"
echo ""

echo "=== REQUEST LIFECYCLE FOR $REQUEST_ID ==="
echo ""

# Header row and separator
printf "%-12s | %-8s | %-12s | %s\n" "TIME" "SERVICE" "TRACE_ID" "MESSAGE"
printf -- "-------------+----------+--------------+%s\n" "$(printf '%.0s-' {1..40})"

# Parse and display timeline from merged logs
jq -r '.[] | "\(.timestamp)\t\(.message)"' "$TRACE_DIR/merged.json" | \
  while IFS=$'\t' read -r ts msg; do
    time=$(date -d @$((ts/1000)) '+%H:%M:%S.%3N')
    service=$(echo "$msg" | jq -r '.resource["service.name"] // "unknown"')
    body=$(echo "$msg" | jq -r '.body')
    trace=$(echo "$msg" | jq -r '.trace_id // "null"')
    printf "%-12s | %-8s | %-12.12s | %s\n" "$time" "$service" "$trace" "$body"
  done

echo ""
echo "=== TIMING BREAKDOWN ==="

# Extract timing from merged logs
grep -oP 'Gribjump/setup time taken: \K[0-9.]+' "$TRACE_DIR/merged.json" 2>/dev/null | \
  xargs -I{} echo "GribJump setup:  {}s"
grep -oP 'Polytope time taken: \K[0-9.]+' "$TRACE_DIR/merged.json" 2>/dev/null | \
  xargs -I{} echo "Polytope:        {}s"
grep -oP 'Covjsonkit time taken: \K[0-9.]+' "$TRACE_DIR/merged.json" 2>/dev/null | \
  xargs -I{} echo "CovJSON:         {}s"

echo ""
echo "Logs saved to: $TRACE_DIR/"
