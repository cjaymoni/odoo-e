# Test Coverage Configuration

## Running Tests

### Quick Test Run

Run all tests for the catering module:

```bash
./run_tests.sh
```

### Run Specific Test Tags

```bash
# Basic model tests only
docker-compose exec odoo ./odoo-bin -c odoo.conf -d test_db -u cater --test-enable --test-tags=catering_models --stop-after-init

# Security tests only
docker-compose exec odoo ./odoo-bin -c odoo.conf -d test_db -u cater --test-enable --test-tags=catering_security --stop-after-init

# Workflow tests
docker-compose exec odoo ./odoo-bin -c odoo.conf -d test_db -u cater --test-enable --test-tags=workflow --stop-after-init

# View tests
docker-compose exec odoo ./odoo-bin -c odoo.conf -d test_db -u cater --test-enable --test-tags=views,ui --stop-after-init
```

### Run Tests with Python Coverage

1. Install coverage tool inside the container:

```bash
docker-compose exec odoo pip install coverage
```

2. Run tests with coverage:

```bash
docker-compose exec odoo coverage run --source=enterprise/cater ./odoo-bin \
    -c odoo.conf \
    -d test_catering \
    -u cater \
    --test-enable \
    --stop-after-init
```

3. Generate coverage report:

```bash
# Terminal report
docker-compose exec odoo coverage report

# HTML report
docker-compose exec odoo coverage html
# View the report at htmlcov/index.html
```

## Test Structure

### Test Files

1. **test_catering_models.py** - TransactionCase tests

   - Basic CRUD operations
   - Field calculations
   - Validations and constraints
   - Default values

2. **test_security.py** - TransactionCase tests

   - Access rights for different user groups
   - Record rules
   - Field-level security
   - Cross-company access (if applicable)

3. **test_workflow.py** - SavepointCase tests

   - Booking state transitions
   - Computed fields
   - Business logic validation
   - Edge cases in workflows

4. **test_views_ui.py** - SavepointCase tests

   - View definitions
   - Menu structure
   - Dashboard functionality
   - Form/tree/kanban views

5. **test_webhook_controllers.py** - HTTP tests

   - Controller endpoints
   - WhatsApp webhook handling
   - Payment gateway webhooks

6. **test_whatsapp_integration.py** - Integration tests
   - WhatsApp API integration
   - Message sending
   - Status updates

## Coverage Goals

| Component       | Target Coverage | Current Coverage |
| --------------- | --------------- | ---------------- |
| Models          | 90%+            | TBD              |
| Controllers     | 85%+            | TBD              |
| Wizards         | 85%+            | TBD              |
| Computed Fields | 95%+            | TBD              |
| Constraints     | 95%+            | TBD              |
| Overall         | 85%+            | TBD              |

## Continuous Integration

### GitHub Actions (Optional)

Create `.github/workflows/tests.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_DB: test_odoo
          POSTGRES_USER: odoo
          POSTGRES_PASSWORD: odoo
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.10

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install coverage

      - name: Run tests
        run: |
          ./odoo-bin -c odoo.conf -d test_odoo -i cater --test-enable --stop-after-init
        env:
          PGHOST: localhost
          PGPORT: 5432
          PGUSER: odoo
          PGPASSWORD: odoo

      - name: Generate coverage report
        run: |
          coverage run --source=enterprise/cater ./odoo-bin -c odoo.conf -d test_odoo -u cater --test-enable --stop-after-init
          coverage report
          coverage xml

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v2
        with:
          file: ./coverage.xml
          fail_ci_if_error: true
```

## Test Best Practices

### 1. Test Isolation

- Use `SavepointCase` for tests that modify data
- Use `TransactionCase` for read-only tests
- Clean up test data in `tearDown()` if needed

### 2. Test Data

- Create minimal test data in `setUpClass()`
- Use realistic data that mirrors production
- Don't rely on demo data

### 3. Test Naming

- Use descriptive test method names: `test_booking_cannot_be_confirmed_without_menu`
- Group related tests in classes
- Use `@tagged()` decorator for test categorization

### 4. Assertions

- Use specific assertions: `assertEqual`, `assertGreater`, etc.
- Include meaningful assertion messages
- Test both positive and negative cases

### 5. Performance

- Mark slow tests with `@tagged('slow')`
- Mock external API calls
- Use `with_context(prefetch_fields=False)` for large datasets

## Debugging Failed Tests

### View Test Logs

```bash
docker-compose logs odoo | grep -A 50 "FAIL:"
```

### Run Single Test

```bash
docker-compose exec odoo ./odoo-bin \
    -c odoo.conf \
    -d test_db \
    -u cater \
    --test-enable \
    --test-tags=cater.test_catering_models.TestCateringModels.test_booking_creation \
    --stop-after-init
```

### Enable Debug Mode

```bash
docker-compose exec odoo ./odoo-bin \
    -c odoo.conf \
    -d test_db \
    -u cater \
    --test-enable \
    --test-tags=cater \
    --stop-after-init \
    --log-level=debug
```

### Use Python Debugger

Add to test code:

```python
import pdb; pdb.set_trace()
```

Then run tests interactively:

```bash
docker-compose exec odoo bash
python3 ./odoo-bin -c odoo.conf -d test_db -u cater --test-enable --stop-after-init
```

## Coverage Report Example

```
Name                                           Stmts   Miss  Cover
------------------------------------------------------------------
enterprise/cater/__init__.py                       3      0   100%
enterprise/cater/models/__init__.py               12      0   100%
enterprise/cater/models/event_booking.py         156     12    92%
enterprise/cater/models/menu_item.py              45      3    93%
enterprise/cater/models/feedback.py               67      8    88%
enterprise/cater/models/dashboard.py              89     15    83%
enterprise/cater/controllers/webhook.py           42      7    83%
enterprise/cater/controllers/whatsapp.py          78     14    82%
enterprise/cater/wizards/booking_wizard.py        34      5    85%
------------------------------------------------------------------
TOTAL                                            526     64    88%
```

## Next Steps

1. Run `./run_tests.sh` to execute all tests
2. Review any failures and fix issues
3. Generate coverage report
4. Complete manual testing items from AUDIT_CHECKLIST.md
5. Document any additional edge cases found
6. Update tests for newly discovered scenarios
