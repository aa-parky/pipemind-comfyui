# GitHub Actions Workflows

This directory contains the CI/CD workflows for Pipemind ComfyUI Custom Nodes.

## 🔄 Workflows Overview

### 1. Tests (`tests.yml`)

**Triggers:** Push to `master`/`develop`, Pull Requests

**Jobs:**
- **test**: Runs unit and smoke tests on Python 3.12
- **test-with-coverage**: Generates coverage reports and uploads to Codecov
- **test-installation**: Verifies package installation and imports

**Purpose:** Ensures all tests pass and tracks code coverage.

### 2. Code Quality (`code-quality.yml`)

**Triggers:** Push to `master`/`develop`, Pull Requests

**Jobs:**
- **lint**: Checks code style with Flake8
- **format-check**: Validates formatting with Black
- **type-check**: Runs type checking with mypy (non-blocking)
- **security-check**: Scans for security issues with Bandit
- **dependency-check**: Checks for vulnerable dependencies

**Purpose:** Maintains code quality and security standards.

### 3. PR Validation (`pr-validation.yml`)

**Triggers:** Pull Request events (opened, synchronized, reopened)

**Jobs:**
- **validate-pr**: Checks PR title format and CHANGELOG updates
- **check-node-structure**: Validates node structure and registrations
- **size-report**: Reports PR size and complexity

**Purpose:** Enforces PR standards and provides review information.

### 4. Release (`release.yml`)

**Triggers:** Push tags matching `v*.*.*` (e.g., `v0.3.0`)

**Jobs:**
- **create-release**: Creates GitHub release with changelog
- **publish-notification**: Provides installation instructions
- **test-release**: Validates the released version

**Purpose:** Automates the release process.

## 📋 Workflow Status

You can view the status of all workflows:
- [Actions Dashboard](https://github.com/aa-parky/pipemind-comfyui/actions)

## 🚀 Using the Workflows

### Running Tests Locally

Before pushing, run tests locally:

```bash
# Install dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Check formatting
black --check .

# Run linter
flake8 .
```

### Creating a Release

To create a new release:

1. Update `CHANGELOG.md` with version changes
2. Commit changes to `master`
3. Create and push a tag:

```bash
git tag -a v0.3.0 -m "Release version 0.3.0"
git push origin v0.3.0
```

The release workflow will automatically:
- Create a GitHub release
- Extract changelog for the version
- Run installation tests

### PR Requirements

All PRs must:
- ✅ Pass all tests
- ✅ Pass code quality checks
- ✅ Have properly formatted title (e.g., "Add: New feature")
- ✅ Update CHANGELOG.md (except docs-only changes)
- ✅ Pass node structure validation

## 🔒 Secrets Required

### Optional Secrets

- `CODECOV_TOKEN`: For uploading coverage reports to Codecov
  - Get from: https://codecov.io
  - Add in: Settings → Secrets and variables → Actions

## 🎯 Badge Status

Badges in README.md show:
- [![Tests](https://github.com/aa-parky/pipemind-comfyui/actions/workflows/tests.yml/badge.svg)](https://github.com/aa-parky/pipemind-comfyui/actions/workflows/tests.yml) - Test status
- [![Code Quality](https://github.com/aa-parky/pipemind-comfyui/actions/workflows/code-quality.yml/badge.svg)](https://github.com/aa-parky/pipemind-comfyui/actions/workflows/code-quality.yml) - Code quality status
- Coverage percentage (if Codecov configured)

## 🐛 Troubleshooting

### Tests Failing?

1. Check the [Actions tab](https://github.com/aa-parky/pipemind-comfyui/actions)
2. Review the failed job logs
3. Run tests locally to reproduce
4. Fix issues and push again

### Code Quality Issues?

Run locally:
```bash
# Auto-fix formatting
black .

# Check for issues
flake8 .

# Fix imports
isort .
```

## 📝 Adding New Workflows

When adding new workflows:

1. Create `.github/workflows/your-workflow.yml`
2. Test locally with [act](https://github.com/nektos/act) if possible
3. Document the workflow in this README
4. Add status badge to main README if appropriate

## 🔄 Workflow Maintenance

Workflows are automatically updated when:
- GitHub Actions versions are released
- Security patches are needed
- New features are added

Review and update workflows periodically to:
- Use latest action versions
- Add new checks as needed
- Optimize performance

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
- [pytest Documentation](https://docs.pytest.org/)
- [Black Documentation](https://black.readthedocs.io/)
- [Flake8 Documentation](https://flake8.pycqa.org/)
