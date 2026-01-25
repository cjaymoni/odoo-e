#!/bin/bash
# Test runner script with coverage report for Catering Module

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Catering Module Test Suite${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Configuration
DB_NAME="${1:-test_catering_db}"
ODOO_BIN="${2:-python3 -m odoo}"
ODOO_CONF="${3:-odoo.conf}"
MODULE_NAME="cater"

echo -e "${YELLOW}Configuration:${NC}"
echo "Database: $DB_NAME"
echo "Odoo Binary: $ODOO_BIN"
echo "Config File: $ODOO_CONF"
echo "Module: $MODULE_NAME"
echo ""

# Check if database exists and drop it for clean test
echo -e "${YELLOW}Preparing test database...${NC}"
if docker-compose exec -T db psql -U odoo -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
    echo "Dropping existing test database..."
    docker-compose exec -T db psql -U odoo -c "DROP DATABASE IF EXISTS $DB_NAME;"
fi

echo "Creating fresh test database..."
docker-compose exec -T db psql -U odoo -c "CREATE DATABASE $DB_NAME;"
echo ""

# Run tests with different tags
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Running Test Suite${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Test 1: Basic model tests
echo -e "${YELLOW}1. Running basic model tests...${NC}"
docker-compose exec -T odoo $ODOO_BIN \
    -c $ODOO_CONF \
    -d $DB_NAME \
    --xmlrpc-port=8070 \
    -i $MODULE_NAME \
    --test-enable \
    --test-tags=cater,catering_models \
    --stop-after-init \
    --log-level=test
echo ""

# Test 2: Security tests
echo -e "${YELLOW}2. Running security tests...${NC}"
docker-compose exec -T odoo $ODOO_BIN \
    -c $ODOO_CONF \
    -d $DB_NAME \
    --xmlrpc-port=8070 \
    -u $MODULE_NAME \
    --test-enable \
    --test-tags=cater,catering_security \
    --stop-after-init \
    --log-level=test
echo ""

# Test 3: Workflow tests
echo -e "${YELLOW}3. Running workflow tests...${NC}"
docker-compose exec -T odoo $ODOO_BIN \
    -c $ODOO_CONF \
    -d $DB_NAME \
    --xmlrpc-port=8070 \
    -u $MODULE_NAME \
    --test-enable \
    --test-tags=cater,workflow \
    --stop-after-init \
    --log-level=test
echo ""

# Test 4: View and UI tests
echo -e "${YELLOW}4. Running view and UI tests...${NC}"
docker-compose exec -T odoo $ODOO_BIN \
    -c $ODOO_CONF \
    -d $DB_NAME \
    --xmlrpc-port=8070 \
    -u $MODULE_NAME \
    --test-enable \
    --test-tags=cater,views,ui \
    --stop-after-init \
    --log-level=test
echo ""

# Test 5: Integration tests
echo -e "${YELLOW}5. Running integration tests...${NC}"
docker-compose exec -T odoo $ODOO_BIN \
    -c $ODOO_CONF \
    -d $DB_NAME \
    --xmlrpc-port=8070 \
    -u $MODULE_NAME \
    --test-enable \
    --test-tags=cater,integration \
    --stop-after-init \
    --log-level=test
echo ""

# Test 6: All tests together for coverage
echo -e "${YELLOW}6. Running complete test suite for coverage...${NC}"
docker-compose exec -T odoo $ODOO_BIN \
    -c $ODOO_CONF \
    -d $DB_NAME \
    --xmlrpc-port=8070 \
    -u $MODULE_NAME \
    --test-enable \
    --test-tags=cater \
    --stop-after-init \
    --log-level=test
echo ""

# Summary
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Test Suite Completed${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Test Coverage Summary:${NC}"
echo "✓ Basic model tests"
echo "✓ Security and access rights tests"
echo "✓ Workflow and state transition tests"
echo "✓ View and UI tests"
echo "✓ Integration tests"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Review test results above for any failures"
echo "2. Check Odoo logs for detailed error messages"
echo "3. Use the AUDIT_CHECKLIST.md to verify manual testing items"
echo "4. Run 'docker-compose exec odoo bash' to access container for debugging"
echo ""
echo -e "${GREEN}To generate detailed coverage report:${NC}"
echo "pip install coverage"
echo "coverage run --source=enterprise/cater $ODOO_BIN -c $ODOO_CONF -d $DB_NAME -u $MODULE_NAME --test-enable --stop-after-init"
echo "coverage report"
echo "coverage html"
echo ""
