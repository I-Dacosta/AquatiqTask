#!/bin/bash
# Run integration tests for AI Prioritization Engine

# Ensure we're in the right directory
cd "$(dirname "$0")"
cd ..

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "🚀 Starting integration tests for AI Prioritization Engine..."

# Start dependencies if not running
echo "📦 Ensuring dependencies are running..."
docker-compose up -d nats redis

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 5

# Install test dependencies
echo "📚 Installing test dependencies..."
pip install pytest pytest-asyncio

# Run the tests
echo "🧪 Running integration tests..."
python -m pytest tests/test_orchestration.py -v

# Get the exit code
TEST_EXIT_CODE=$?

# Print summary
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
else
    echo -e "${RED}❌ Some tests failed${NC}"
fi

# Clean up
echo "🧹 Cleaning up..."
docker-compose down

exit $TEST_EXIT_CODE
