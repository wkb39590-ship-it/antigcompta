#!/bin/bash
# test_auth_curl.sh - Tests manuels avec curl (Alternative)
# Exécutez: bash test_auth_curl.sh

set -e

API="http://localhost:8090"
HEADER="Content-Type: application/json"

echo "════════════════════════════════════════════════════════════════"
echo "  TESTS D'AUTHENTIFICATION MULTI-CABINET AVEC CURL"
echo "════════════════════════════════════════════════════════════════"

# ─────────────────────────────────────────────────────────────────
# 1. LOGIN TESTS
# ─────────────────────────────────────────────────────────────────

echo ""
echo "✅ TEST 1.1: Login Admin (wissal)"
echo "─────────────────────────────────────────────────────────────────"
WISSAL_LOGIN=$(curl -s -X POST "$API/auth/login" \
  -H "$HEADER" \
  -d '{"username":"wissal","password":"password123"}')

echo "Response:"
echo "$WISSAL_LOGIN" | jq '.'

WISSAL_TOKEN=$(echo "$WISSAL_LOGIN" | jq -r '.access_token')
echo "Token: $WISSAL_TOKEN"
echo ""

echo "✅ TEST 1.2: Login User (fatima)"
echo "─────────────────────────────────────────────────────────────────"
FATIMA_LOGIN=$(curl -s -X POST "$API/auth/login" \
  -H "$HEADER" \
  -d '{"username":"fatima","password":"password123"}')

FATIMA_TOKEN=$(echo "$FATIMA_LOGIN" | jq -r '.access_token')
echo "Token: $FATIMA_TOKEN"
echo ""

echo "✅ TEST 1.3: Login Admin Cabinet 2 (ahmed)"
echo "─────────────────────────────────────────────────────────────────"
AHMED_LOGIN=$(curl -s -X POST "$API/auth/login" \
  -H "$HEADER" \
  -d '{"username":"ahmed","password":"password123"}')

AHMED_TOKEN=$(echo "$AHMED_LOGIN" | jq -r '.access_token')
echo "Token: $AHMED_TOKEN"
echo ""

# ─────────────────────────────────────────────────────────────────
# 2. SOCIETES TEST
# ─────────────────────────────────────────────────────────────────

echo "✅ TEST 2.1: Admin List All Societes"
echo "─────────────────────────────────────────────────────────────────"
curl -s -X GET "$API/auth/societes?token=$WISSAL_TOKEN" | jq '.[] | {id, raison_sociale}'
echo ""

echo "✅ TEST 2.2: User List Assigned Societes (fatima)"
echo "─────────────────────────────────────────────────────────────────"
curl -s -X GET "$API/auth/societes?token=$FATIMA_TOKEN" | jq '.[] | {id, raison_sociale}'
echo ""

echo "✅ TEST 2.3: Cabinet 2 Admin List Societes (ahmed)"
echo "─────────────────────────────────────────────────────────────────"
curl -s -X GET "$API/auth/societes?token=$AHMED_TOKEN" | jq '.[] | {id, raison_sociale}'
echo ""

# ─────────────────────────────────────────────────────────────────
# 3. SELECT SOCIETE TEST
# ─────────────────────────────────────────────────────────────────

echo "✅ TEST 3.1: Select Societe (wissal)"
echo "─────────────────────────────────────────────────────────────────"
SELECT=$(curl -s -X POST "$API/auth/select-societe?token=$WISSAL_TOKEN" \
  -H "$HEADER" \
  -d '{"cabinet_id":4,"societe_id":2}')

echo "$SELECT" | jq '{context: .context, session_token: .session_token}'
SESSION_TOKEN=$(echo "$SELECT" | jq -r '.session_token')
echo ""

echo "✅ TEST 3.2: User Select Assigned Societe (fatima)"
echo "─────────────────────────────────────────────────────────────────"
curl -s -X POST "$API/auth/select-societe?token=$FATIMA_TOKEN" \
  -H "$HEADER" \
  -d '{"cabinet_id":4,"societe_id":2}' | jq '{context: .context, status: "OK"}'
echo ""

echo "✅ TEST 3.3: User Try Select Forbidden Societe (fatima → societe 3)"
echo "─────────────────────────────────────────────────────────────────"
curl -s -X POST "$API/auth/select-societe?token=$FATIMA_TOKEN" \
  -H "$HEADER" \
  -d '{"cabinet_id":4,"societe_id":3}' | jq '.[] // .'
echo ""

# ─────────────────────────────────────────────────────────────────
# 4. SECURITY TEST
# ─────────────────────────────────────────────────────────────────

echo "✅ TEST 4.1: Invalid Token"
echo "─────────────────────────────────────────────────────────────────"
curl -s -X GET "$API/auth/societes?token=INVALID_TOKEN" | jq '.[] // .'
echo ""

echo "✅ TEST 4.2: Cross-Cabinet Prevention"
echo "─────────────────────────────────────────────────────────────────"
echo "Ahmed (Cabinet 2) essaie d'accéder à societe 2 (Cabinet 1):"
curl -s -X POST "$API/auth/select-societe?token=$AHMED_TOKEN" \
  -H "$HEADER" \
  -d '{"cabinet_id":4,"societe_id":2}' | jq '.[] // .'
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "✅ TESTS CURL TERMINÉS"
echo "════════════════════════════════════════════════════════════════"
