# Contributing to PerfWatch

Thank you for considering contributing to PerfWatch! This document provides guidelines and workflows for contributing to the project.

---

## Table of Contents

- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Commit Message Format](#commit-message-format)
- [Pull Request Process](#pull-request-process)
- [Documentation Updates](#documentation-updates)

---

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Git
- Basic knowledge of Python (FastAPI), Vue.js, and PostgreSQL

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/zhyndalf/perfwatch.git
cd perfwatch

# Start all services
docker compose up -d

# Run database migrations
docker compose exec backend alembic upgrade head

# Verify setup
curl http://localhost:8000/health
# Visit http://localhost:3000 (login: admin/admin123)
```

---

## Development Workflow

### Branch Strategy

- **main**: Production-ready code, always stable
- **feature/\***: New features (e.g., `feature/add-gpu-metrics`)
- **fix/\***: Bug fixes (e.g., `fix/memory-leak-collector`)
- **refactor/\***: Code refactoring (e.g., `refactor/consolidate-validators`)

### Typical Workflow

1. **Create a branch**:
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. **Make changes**: Edit code, add tests, update documentation

3. **Test thoroughly**:
   ```bash
   # Run backend tests
   docker compose run --rm backend pytest tests/ -v

   # Build frontend
   docker compose exec frontend npm run build
   ```

4. **Commit changes**: Follow [commit message format](#commit-message-format)

5. **Push and create PR**:
   ```bash
   git push origin feature/my-new-feature
   # Then create a pull request on GitHub
   ```

---

## Coding Standards

### Python (Backend)

- **Style**: Follow PEP 8
- **Type Hints**: Use type hints for all function signatures
- **Async**: Use async/await patterns consistently
- **Imports**: Group imports (standard library, third-party, local)
- **SQLAlchemy**: Use SQLAlchemy 2.0 style (`Mapped`, `mapped_column()`)
- **Security**: NEVER commit secrets or API keys

**Example**:
```python
from typing import Dict, Any
from app.collectors.base import BaseCollector

class MyCollector(BaseCollector):
    name = "my_collector"

    async def collect(self) -> Dict[str, Any]:
        """Collect metrics from source.

        Returns:
            Dictionary containing collected metrics.
        """
        return {"metric": value}
```

### Vue.js (Frontend)

- **Style**: Follow Vue 3 Composition API patterns
- **Components**: Use `<script setup>` syntax
- **Styling**: Use TailwindCSS utility classes
- **State**: Use Pinia stores for global state

**Example**:
```vue
<script setup>
import { ref, onMounted } from 'vue'

const data = ref(null)

onMounted(async () => {
  // Component logic
})
</script>

<template>
  <div class="p-4">
    <!-- Template -->
  </div>
</template>
```

---

## Testing Requirements

### All Code Must Have Tests

- **Backend**: Write pytest tests for all new endpoints, collectors, and services
- **Coverage**: Aim for >80% test coverage
- **Run tests before committing**:
  ```bash
  docker compose run --rm backend pytest tests/ -v
  ```

### Test Structure

```
tests/
├── test_api.py            # API endpoint tests
├── test_collectors.py     # Collector tests
├── test_auth.py           # Authentication tests
└── conftest.py            # Shared fixtures
```

### Writing Good Tests

```python
import pytest

class TestMyFeature:
    """Tests for my new feature."""

    @pytest.mark.asyncio
    async def test_feature_works(self):
        """Test that feature behaves correctly."""
        # Arrange
        input_data = {"key": "value"}

        # Act
        result = await my_function(input_data)

        # Assert
        assert result["status"] == "success"
```

---

## Commit Message Format

### Format

```
<type>: <short summary>

<optional detailed description>

<optional footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **refactor**: Code refactoring (no functional changes)
- **test**: Adding or updating tests
- **docs**: Documentation changes
- **chore**: Build, dependencies, or tooling changes

### Examples

```bash
# Good
feat: add GPU metrics collector
fix: resolve memory leak in network collector
refactor: consolidate rate calculation logic
test: add tests for memory bandwidth collector
docs: update API documentation for retention endpoints

# Bad
fix: stuff
update code
changes
```

### Co-Authorship

When using AI assistants (like Claude Code), add co-authorship:

```bash
git commit -m "feat: add new feature

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Pull Request Process

### Before Creating a PR

- [ ] All tests pass (`pytest tests/ -v`)
- [ ] Code follows style guidelines
- [ ] Documentation is updated (if needed)
- [ ] README.md is updated (if progress changed)
- [ ] Commit messages follow format

### PR Title Format

Use the same format as commit messages:

```
feat: add GPU metrics support
fix: resolve WebSocket connection issue
```

### PR Description Template

```markdown
## Summary
Brief description of changes

## Changes Made
- Added X feature
- Fixed Y bug
- Refactored Z component

## Testing
- [ ] All existing tests pass
- [ ] New tests added for new functionality
- [ ] Tested manually on localhost

## Screenshots (if UI changes)
[Add screenshots here]

## Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] README.md updated (if needed)
```

### Review Process

1. **Automated checks**: CI runs tests automatically
2. **Code review**: At least one maintainer reviews the code
3. **Changes requested**: Address feedback and push updates
4. **Approval**: Maintainer approves and merges

---

## Documentation Updates

### When to Update Documentation

- **New features**: Update CLAUDE.md, README.md, and docs/sdd/
- **API changes**: Update docs/sdd/02-specification/api-spec.md
- **Architecture changes**: Update docs/sdd/02-specification/architecture.md

### CRITICAL: Always Update README.md Before Committing

**If your changes affect project progress or features:**

1. Update progress percentage
2. Update Mermaid diagram task status
3. Update test counts
4. Keep README synchronized with actual state

**Example**:
```bash
# After completing a task
# 1. Update README.md progress
# 2. Update CLAUDE.md if needed
# 3. Update docs/sdd/CURRENT_TASK.md
# 4. Commit all changes together
```

---

## Questions or Issues?

- **GitHub Issues**: https://github.com/zhyndalf/perfwatch/issues
- **Documentation**: Check `docs/sdd/` for detailed specifications
- **Setup Help**: See `DEVELOPMENT.md` for troubleshooting

---

## License

By contributing to PerfWatch, you agree that your contributions will be licensed under the project's license.

---

Thank you for contributing to PerfWatch! 🚀
