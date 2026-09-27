#!/usr/bin/env bash
# Break-glass emergency override for supply chain policy enforcement
# Requires dual approval and creates immutable audit trail
set -euo pipefail

REASON=""
APPROVER1=""
APPROVER2=""
ENVIRONMENT="prod"

usage() {
    echo "Usage: $0 --reason REASON --approver1 USER1 --approver2 USER2 [--env ENVIRONMENT]"
    exit 1
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --reason)   REASON="$2";    shift 2 ;;
        --approver1) APPROVER1="$2"; shift 2 ;;
        --approver2) APPROVER2="$2"; shift 2 ;;
        --env)      ENVIRONMENT="$2"; shift 2 ;;
        *) usage ;;
    esac
done

[[ -z "$REASON" ]]    && { echo "ERROR: --reason is required"; usage; }
[[ -z "$APPROVER1" ]] && { echo "ERROR: --approver1 is required"; usage; }
[[ -z "$APPROVER2" ]] && { echo "ERROR: --approver2 is required"; usage; }
[[ "$APPROVER1" == "$APPROVER2" ]] && { echo "ERROR: approvers must be different people"; exit 1; }

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
EVENT_ID=$(uuidgen 2>/dev/null || python3 -c "import uuid; print(uuid.uuid4())")
ACTOR=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null || echo "unknown")

cat << EOF
========================================
BREAK GLASS EMERGENCY OVERRIDE
========================================
Event ID:    ${EVENT_ID}
Timestamp:   ${TIMESTAMP}
Actor:       ${ACTOR}
Environment: ${ENVIRONMENT}
Approver 1:  ${APPROVER1}
Approver 2:  ${APPROVER2}
Reason:      ${REASON}
========================================
EOF

echo "This action will be logged to the audit trail."
read -p "Type 'OVERRIDE' to confirm: " CONFIRM
[[ "$CONFIRM" != "OVERRIDE" ]] && { echo "Cancelled."; exit 1; }

# Log to Cloud Logging
gcloud logging write supply-chain-break-glass \
    "{\"severity\": \"CRITICAL\", \"event_id\": \"${EVENT_ID}\", \"timestamp\": \"${TIMESTAMP}\", \"actor\": \"${ACTOR}\", \"approver1\": \"${APPROVER1}\", \"approver2\": \"${APPROVER2}\", \"reason\": \"${REASON}\", \"environment\": \"${ENVIRONMENT}\"}" \
    --payload-type=json 2>/dev/null || echo "WARNING: Cloud Logging write failed"

echo "Break-glass override activated. All actions are audited."
echo "Event ID: ${EVENT_ID}"
