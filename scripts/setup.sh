#!/bin/bash
echo "Setting up KidsAI Studio environment..."
cp -n .env.example .env 2>/dev/null || true
cp -n apps/frontend/.env.example apps/frontend/.env.local 2>/dev/null || true
cp -n apps/backend/.env.example apps/backend/.env 2>/dev/null || true

echo "Installing frontend dependencies..."
cd apps/frontend && npm install && cd ../..

echo "Setup complete! Run ./scripts/dev.sh to start servers."
