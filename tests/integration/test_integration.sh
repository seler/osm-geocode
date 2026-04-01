#!/usr/bin/env bash
set -euo pipefail

HA_URL="http://localhost:8123"
MAX_WAIT=120
COMPOSE_FILE="tests/integration/docker-compose.yml"
PASS=0
FAIL=0

cleanup() {
    echo ""
    echo "=== Cleaning up ==="
    docker compose -f "$COMPOSE_FILE" down --remove-orphans 2>/dev/null || true
}
trap cleanup EXIT

pass() {
    echo "PASS: $1"
    PASS=$((PASS + 1))
}

fail() {
    echo "FAIL: $1"
    FAIL=$((FAIL + 1))
}

get_http_code() {
    curl -so /dev/null -w '%{http_code}' "$1" 2>/dev/null || true
}

echo "=== Building and starting Home Assistant ==="
docker compose -f "$COMPOSE_FILE" up -d --build 2>&1

echo "=== Waiting for Home Assistant HTTP server (max ${MAX_WAIT}s) ==="
elapsed=0
while [ $elapsed -lt $MAX_WAIT ]; do
    http_code=$(get_http_code "$HA_URL/")
    if [ -n "$http_code" ] && [ "$http_code" != "000" ]; then
        echo "Home Assistant HTTP server ready (HTTP $http_code) after ${elapsed}s"
        break
    fi
    sleep 3
    elapsed=$((elapsed + 3))
done

if [ $elapsed -ge $MAX_WAIT ]; then
    echo "FAIL: Home Assistant did not start within ${MAX_WAIT}s"
    docker compose -f "$COMPOSE_FILE" logs --no-color
    exit 1
fi

echo "=== Waiting for platforms to finish loading ==="
# Wait until we see our component in the logs (it logs warnings about the missing entity)
platform_wait=0
while [ $platform_wait -lt 60 ]; do
    if docker compose -f "$COMPOSE_FILE" logs --no-color 2>&1 | grep -qi "custom_components.osm_geocode"; then
        echo "Component loaded after additional ${platform_wait}s"
        break
    fi
    sleep 3
    platform_wait=$((platform_wait + 3))
done

logs=$(docker compose -f "$COMPOSE_FILE" logs --no-color 2>&1)

echo ""
echo "=== Test 1: Home Assistant is responding ==="
http_code=$(get_http_code "$HA_URL/")
if [ -n "$http_code" ] && [ "$http_code" != "000" ]; then
    pass "HA HTTP server responding (HTTP $http_code)"
else
    fail "HA HTTP server not responding"
fi

echo ""
echo "=== Test 2: Component loaded without critical errors ==="
if echo "$logs" | grep -qi "error loading.*osm_geocode\|failed to set up.*osm_geocode\|unable to set up.*osm_geocode"; then
    fail "Component loading errors found"
    echo "$logs" | grep -i "osm_geocode"
else
    pass "No component loading errors"
fi

echo ""
echo "=== Test 3: Sensor platform was set up ==="
if echo "$logs" | grep -qi "custom_components.osm_geocode"; then
    pass "Sensor platform loaded"
else
    fail "No evidence of component loading in logs"
fi

echo ""
echo "=== Test 4: HACS loaded without conflicts ==="
if echo "$logs" | grep -qi "error loading.*hacs\|failed to set up.*hacs"; then
    fail "HACS loading errors found"
else
    pass "No HACS conflicts"
fi

echo ""
echo "=== Test 5: No Python tracebacks in logs ==="
if echo "$logs" | grep -q "Traceback (most recent call last)"; then
    traceback_count=$(echo "$logs" | grep -c "Traceback (most recent call last)")
    fail "Found $traceback_count traceback(s) in logs"
    echo "$logs" | grep -B2 -A5 "Traceback"
else
    pass "No tracebacks in logs"
fi

echo ""
echo "==============================="
echo "Results: $PASS passed, $FAIL failed"
echo "==============================="

if [ $FAIL -gt 0 ]; then
    echo ""
    echo "=== Relevant logs ==="
    echo "$logs" | grep -i "osm_geocode\|hacs\|error\|traceback" || true
    exit 1
fi
