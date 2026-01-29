# Pytest Test Suite Documentation

This directory contains comprehensive pytest tests for the the whole system.


## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test File
```bash
pytest tests/test_views.py
```

### Run Specific Test Class
```bash
pytest tests/test_views.py::TestUserRegistrationView
```

### Run Specific Test Case
```bash
pytest tests/test_views.py::TestUserRegistrationView::test_register_creator_success
```

### Run Tests with Coverage
```bash
pytest --cov=apps --cov=utils --cov-report=html
```

### Run Tests Matching Pattern
```bash
pytest -k "register"
```

### Run Tests Verbosely
```bash
pytest -v
```

### Run Tests with Output
```bash
pytest -s
```

### Run Tests and Stop on First Failure
```bash
pytest -x
```

### Run Tests with Markers
```bash
pytest -m django_db
```

---

## Test Markers

Available markers:
- `@pytest.mark.django_db` - Tests that access database
- `@pytest.mark.slow` - Slow running tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.unit` - Unit tests

---

## Key Testing Patterns

### 1. Database Tests
```python
@pytest.mark.django_db
class TestSomething:
    def test_something(self):
        # Test has access to database
        user = UserFactory()
        assert user.id is not None
```

### 2. API Tests
```python
def test_endpoint(api_client):
    """Test API endpoint."""
    response = api_client.get('/api/v1/auth/profile/')
    assert response.status_code == 401
```

### 3. Authenticated Tests
```python
def test_authenticated_endpoint(api_client):
    """Test authenticated endpoint."""
    user = UserFactory()
    api_client.force_authenticate(user=user)
    
    response = api_client.get('/api/v1/auth/profile/')
    assert response.status_code == 200
```

### 4. POST Requests
```python
def test_registration(api_client):
    """Test registration."""
    data = {
        'email': 'test@example.com',
        'username': 'testuser',
        'password': 'SecurePass123!',
        'password2': 'SecurePass123!',
    }
    response = api_client.post('/api/v1/auth/register/', data, format='json')
    assert response.status_code == 201
```

### 5. Factory Usage
```python
def test_with_factory():
    """Test using factories."""
    user = UserFactory(email='custom@example.com')
    admin = AdminUserFactory()
    client = APIClientFactory(name='My App')
```

---

## Test Coverage

Target coverage: **80%+**

Run coverage report:
```bash
pytest --cov=apps --cov=utils --cov-report=html
```

View HTML report:
```bash
open htmlcov/index.html
```

---

## Debugging Tests

### Verbose Output
```bash
pytest -vv
```

### Print Statements
```python
def test_debug():
    print("Debug info")  # Use -s flag to see output
    print(f"Variable: {value}")
```

### Drop into Debugger
```python
def test_debug():
    import pdb; pdb.set_trace()
    # Or use breakpoint() in Python 3.7+
    breakpoint()
```

### Show Local Variables
```bash
pytest -l
```

---

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Run Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: pytest --cov
```

### Pre-commit Hook
```bash
#!/bin/bash
pytest tests/ || exit 1
```

---

## Best Practices

✅ **DO:**
- Use fixtures for common test data
- Test one thing per test function
- Use descriptive test names
- Mark database tests with `@pytest.mark.django_db`
- Use factories for test data creation
- Test both success and failure cases
- Test edge cases and boundary conditions
- Keep tests independent (no test order dependency)

❌ **DON'T:**
- Don't hardcode test data (use factories)
- Don't test multiple things in one test
- Don't skip tests without reason
- Don't leave failing tests
- Don't make tests dependent on each other
- Don't test implementation details
- Don't forget to test error cases
- Don't use sleep() in tests

---

## Troubleshooting

### Tests Not Found
```bash
# Make sure test files are named test_*.py
# Make sure conftest.py exists
pytest --collect-only
```

### Database Errors
```python
# Add @pytest.mark.django_db decorator
@pytest.mark.django_db
def test_with_db():
    pass
```

### Import Errors
```bash
# Make sure DJANGO_SETTINGS_MODULE is set
# Check conftest.py is in tests directory
```

### Fixture Errors
```python
# Check fixture name is correct
# Check fixture is defined in conftest.py
# Check fixture has proper scope
```

---

## Continuous Improvement

- Run tests frequently during development
- Maintain high coverage (aim for 80%+)
- Add tests for all new features
- Update tests when fixing bugs
- Review test code regularly
- Refactor tests to reduce duplication
- Keep tests fast (mock external services)

---

## Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Django Testing](https://docs.djangoproject.com/en/stable/topics/testing/)
- [DRF Testing](https://www.django-rest-framework.org/api-guide/testing/)
- [Factory Boy](https://factoryboy.readthedocs.io/)
