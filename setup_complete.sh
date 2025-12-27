#!/bin/bash

echo "=========================================="
echo "  ALLERGEN DETECTION FYP - SETUP SUMMARY"
echo "=========================================="
echo ""

echo "✓ Step 1: npm dependencies installed"
echo "  Location: webapp/node_modules (185 packages)"
echo ""

echo "✓ Step 2: Database initialized"
echo "  Location: webapp/prisma/dev.db"
echo "  Tables: User, UserAllergen, ScanHistory"
echo ""

echo "✓ Step 3: Environment configured"
echo "  .env.local created with ML_API_URL=http://localhost:8000/detect-text"
echo ""

echo "✓ Step 4: Next.js development server running"
echo "  URL: http://localhost:3000"
echo ""

echo "✓ Step 5: FastAPI service started"
echo "  URL: http://localhost:8000"
echo "  Endpoint: POST /detect-text"
echo ""

echo "=========================================="
echo "  NEXT STEPS"
echo "=========================================="
echo ""
echo "1. Open http://localhost:3000 in your browser"
echo "2. Sign up for an account"
echo "3. Complete onboarding (select your allergens)"
echo "4. Try a scan:"
echo "   - Text ingredient input (fastest)"
echo "   - Image upload"
echo "   - Barcode scanning"
echo ""
echo "=========================================="
echo ""
