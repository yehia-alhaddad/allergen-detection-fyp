#!/bin/bash

set -e

API="http://localhost:3000"

echo "=== Allergen Detection FYP Integration Test ==="
echo ""

# 1. Register user
echo "[1/4] Registering test user..."
REGISTER=$(curl -s -X POST "$API/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@allergen.local","password":"Test123!@#","name":"Test User"}')
echo "$REGISTER"
echo ""

# 2. Sign in
echo "[2/4] Signing in..."
SIGNIN=$(curl -s -X POST "$API/api/auth/signin" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@allergen.local","password":"Test123!@#"}')
echo "$SIGNIN"
echo ""

# 3. Save allergens via profile endpoint
echo "[3/4] Setting up allergen profile..."
PROFILE=$(curl -s -X POST "$API/api/profile/allergens" \
  -H "Content-Type: application/json" \
  -d '{
    "allergens":["MILK","PEANUT","TREE_NUT"],
    "customAllergen":"",
    "synonyms":["casein","groundnut"]
  }')
echo "$PROFILE"
echo ""

# 4. Test text scan
echo "[4/4] Testing ingredient text scan..."
SCAN=$(curl -s -X POST "$API/api/ingredients/check" \
  -H "Content-Type: application/json" \
  -d '{"text":"Contains milk, peanuts, and tree nuts"}')
echo "$SCAN"
echo ""

echo "=== Test Complete ==="
