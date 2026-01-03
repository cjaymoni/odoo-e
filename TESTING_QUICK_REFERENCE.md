# Quick Reference: Testing & QA

## 🚀 Quick Start

### Run All Tests

```bash
./run_tests.sh
```

### Run Specific Test Category

```bash
# Models
docker-compose exec odoo python3 odoo-bin -c /etc/odoo/odoo.conf -d test_db -u cater --test-enable --test-tags=catering_models --stop-after-init

# Security
docker-compose exec odoo python3 odoo-bin -c /etc/odoo/odoo.conf -d test_db -u cater --test-enable --test-tags=catering_security --stop-after-init

# Workflow
docker-compose exec odoo python3 odoo-bin -c /etc/odoo/odoo.conf -d test_db -u cater --test-enable --test-tags=workflow --stop-after-init

# Views
docker-compose exec odoo python3 odoo-bin -c /etc/odoo/odoo.conf -d test_db -u cater --test-enable --test-tags=views,ui --stop-after-init
```

## 📊 Coverage Report

```bash
# Install coverage
docker-compose exec odoo pip install coverage

# Run with coverage
docker-compose exec odoo coverage run --source=enterprise/cater python3 odoo-bin -c /etc/odoo/odoo.conf -d test_db -u cater --test-enable --stop-after-init

# View report
docker-compose exec odoo coverage report

# HTML report
docker-compose exec odoo coverage html
```

## 🔍 Performance Monitoring

### Add to Model Methods

```python
from odoo.addons.cater.tools.profiling import log_performance, log_database_queries

@log_performance
@log_database_queries
def my_method(self):
    # Your code here
    pass
```

### Use Context Manager

```python
from odoo.addons.cater.tools.profiling import PerformanceLogger

def complex_operation(self):
    with PerformanceLogger("My Operation") as perf:
        with perf.section("Part 1"):
            # Code for part 1
            pass

        with perf.section("Part 2"):
            # Code for part 2
            pass
```

## 📋 Audit Process

1. **Run Tests:** `./run_tests.sh`
2. **Check Coverage:** See above
3. **Manual Audit:** Open `AUDIT_CHECKLIST.md` and work through items
4. **Document:** Add findings to checklist notes
5. **Sign-off:** Complete sign-off section

## 📁 Key Files

| File                     | Purpose                      |
| ------------------------ | ---------------------------- |
| `run_tests.sh`           | Automated test runner        |
| `TEST_COVERAGE.md`       | Testing documentation        |
| `AUDIT_CHECKLIST.md`     | 100+ item QA checklist       |
| `README_WEEK10.md`       | Complete deliverables guide  |
| `tools/profiling.py`     | Performance monitoring tools |
| `tests/test_workflow.py` | Workflow tests               |
| `tests/test_views_ui.py` | View/UI tests                |

## 🎯 Test Tags

| Tag                 | Purpose            |
| ------------------- | ------------------ |
| `cater`             | All catering tests |
| `catering_models`   | Basic model tests  |
| `catering_security` | Security tests     |
| `workflow`          | Workflow tests     |
| `views,ui`          | View/UI tests      |
| `integration`       | Integration tests  |

## 📈 Coverage Goals

- Models: 90%+
- Controllers: 85%+
- Views: 85%+
- Overall: 85%+

## 🐛 Debugging

```bash
# View recent test logs
docker-compose logs odoo | grep -A 50 "FAIL:"

# Run with debug
docker-compose exec odoo python3 odoo-bin -c /etc/odoo/odoo.conf -d test_db -u cater --test-enable --test-tags=cater --stop-after-init --log-level=debug

# Single test
docker-compose exec odoo python3 odoo-bin -c /etc/odoo/odoo.conf -d test_db -u cater --test-enable --test-tags=cater.tests.test_workflow.TestBookingWorkflow.test_booking_draft_to_confirmed --stop-after-init
```

## ✅ Checklist

Before deployment:

- [ ] All tests passing
- [ ] Coverage > 85%
- [ ] Manual audit complete
- [ ] Critical issues addressed
- [ ] Documentation updated
- [ ] Sign-off obtained
