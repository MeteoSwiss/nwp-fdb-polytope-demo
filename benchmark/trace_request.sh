#!/bin/bash
# trace_request.sh - Trace a request across all services

REQUEST_ID="${1:?Usage: $0 <request_id>}"
AWS_PROFILE="${AWS_PROFILE:-aws-polytope-depl}"
AWS_REGION="${AWS_REGION:-eu-central-2}"

# Fetch logs
aws logs filter-log-events \
  --profile "$AWS_PROFILE" \
  --region "$AWS_REGION" \
  --log-group-name polytope-server-logs \
  --start-time $(($(date +%s) - 86400))000 \
  --filter-pattern "\"$REQUEST_ID\"" \
  --output json > "/tmp/trace_$REQUEST_ID.json"

echo "=== REQUEST LIFECYCLE FOR $REQUEST_ID ==="
echo ""

# Header row and separator, using the same column widths as the data rows
printf "%-12s | %-8s | %-12s | %s\n" "TIME" "SERVICE" "TRACE_ID" "MESSAGE"
printf -- "-------------+----------+--------------+%s\n" "$(printf '%.0s-' {1..40})"

# Parse and display timeline
jq -r '.events[] | "\(.timestamp)\t\(.message)"' "/tmp/trace_$REQUEST_ID.json" | \
  while IFS=$'\t' read -r ts msg; do
    time=$(date -d @$((ts/1000)) '+%H:%M:%S.%3N')
    service=$(echo "$msg" | jq -r '.resource["service.name"] // "unknown"')
    body=$(echo "$msg" | jq -r '.body')
    trace=$(echo "$msg" | jq -r '.trace_id // "null"')
    printf "%-12s | %-8s | %-12.12s | %s\n" "$time" "$service" "$trace" "$body"
  done

echo ""
echo "=== TIMING BREAKDOWN ==="

# Extract timing
grep -oP 'Gribjump/setup time taken: \K[0-9.]+' "/tmp/trace_$REQUEST_ID.json" 2>/dev/null | \
  xargs -I{} echo "GribJump setup:  {}s"
grep -oP 'Polytope time taken: \K[0-9.]+' "/tmp/trace_$REQUEST_ID.json" 2>/dev/null | \
  xargs -I{} echo "Polytope:        {}s"
grep -oP 'Covjsonkit time taken: \K[0-9.]+' "/tmp/trace_$REQUEST_ID.json" 2>/dev/null | \
  xargs -I{} echo "CovJSON:         {}s"
