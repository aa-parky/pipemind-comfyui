# 📘 Pipemind ComfyUI - Development Workflow Guide

This guide explains how to work with the repository using a simple **main + develop** branch strategy.

---

## 🌳 Branch Structure

```
main (production)     ← Stable releases only
  └── develop         ← Active development (you work here)
       └── feature/*  ← Optional feature branches for big changes
```

**Simple Rule:**
- **main** = Production ready, users install from here
- **develop** = Where you do all your work

---

## 🚀 Initial Setup (One-Time)

### Step 1: Get Your Repository Up to Date

```bash
# Navigate to your repository
cd /path/to/pipemind-comfyui

# Make sure you have the latest from GitHub
git fetch origin

# Switch to main and update
git checkout main
git pull origin main
```

### Step 2: Create Your Permanent Development Branch

```bash
# Create develop branch from main
git checkout -b develop

# Push it to GitHub (first time only)
git push -u origin develop
```

**Note:** The CI currently requires branches to start with `claude/` for pushing. For now, we'll work around this with a simple workflow.

---

## 💼 Daily Workflow

### Starting New Work

```bash
# 1. Always start from develop
git checkout develop

# 2. Get latest changes
git pull origin develop

# 3. Do your work...
# Edit files, add features, fix bugs

# 4. Check what changed
git status
```

### Committing Your Changes

```bash
# 1. See what you changed
git status
git diff

# 2. Add your changes
git add .
# Or add specific files: git add file1.py file2.py

# 3. Commit with a descriptive message
git commit -m "Add: New aspect ratio node for Flux 3"

# 4. Check you're still on develop
git branch
# Should show: * develop
```

### Pushing to GitHub

Since GitHub requires `claude/` branch names for direct pushes, here's the workflow:

```bash
# 1. Create a claude/ branch from your develop branch
git checkout -b claude/my-feature-name-01EZGMz7FmrCuM9L8v2fEsiX

# 2. Push to GitHub
git push -u origin claude/my-feature-name-01EZGMz7FmrCuM9L8v2fEsiX

# 3. Go to GitHub and create a Pull Request from this branch to main
#    (I'll show you how below)

# 4. After PR is merged, switch back to develop locally
git checkout develop

# 5. Update your local develop from main
git pull origin main
```

---

## 🔄 Creating a Pull Request

### Method 1: Via GitHub Web Interface

**Step 1:** After pushing your `claude/` branch, GitHub will show a banner:
```
claude/my-feature-name just pushed. Compare & pull request
```
Click that button!

**Step 2:** Fill out the PR:
```
Title: Add: New aspect ratio node for Flux 3

Description:
## Description
Added Flux 3 aspect ratio support with new presets

## Type of Change
- [x] New feature

## Testing
- [x] Tested in ComfyUI
- [x] No console errors
- [x] All nodes load correctly

## Checklist
- [x] Code follows style guidelines
- [x] Updated CHANGELOG.md
- [x] Tests pass
```

**Step 3:** Set:
- Base branch: `main`
- Compare branch: `claude/my-feature-name-...`

**Step 4:** Click "Create Pull Request"

**Step 5:** Wait for CI checks to pass (usually 2-5 minutes)
- ✅ Tests
- ✅ Code Quality
- ✅ PR Validation

**Step 6:** If all green, click "Merge pull request" → "Confirm merge"

**Step 7:** Delete the claude/ branch after merging (GitHub will prompt you)

### Method 2: Via Command Line (Alternative)

If you have GitHub CLI installed:

```bash
# After pushing your claude/ branch
gh pr create --base main --head claude/my-feature-name-01EZGMz7FmrCuM9L8v2fEsiX \
  --title "Add: New aspect ratio node" \
  --body "Description of changes"

# View your PR
gh pr view

# Merge when ready
gh pr merge --merge
```

---

## 🏷️ Creating a Release

When you're ready to release a new version:

### Step 1: Update Version Information

```bash
# Make sure you're on main with latest changes
git checkout main
git pull origin main

# Edit CHANGELOG.md
nano CHANGELOG.md
# or: code CHANGELOG.md
# or: vim CHANGELOG.md
```

**Update the changelog:**
```markdown
## [Unreleased]
### Added
- Feature 1
- Feature 2

### Fixed
- Bug fix 1
```

**Change to:**
```markdown
## [0.3.0] - 2025-11-24

### Added
- Feature 1
- Feature 2

### Fixed
- Bug fix 1

## [Unreleased]
### Added
### Changed
### Fixed
```

### Step 2: Commit the Version Update

```bash
# Commit the changelog
git add CHANGELOG.md
git commit -m "Update CHANGELOG for v0.3.0"

# Push to main
# (You'll need to use a claude/ branch here too)
git checkout -b claude/release-v0.3.0-01EZGMz7FmrCuM9L8v2fEsiX
git push -u origin claude/release-v0.3.0-01EZGMz7FmrCuM9L8v2fEsiX

# Create and merge PR to main
# (Use GitHub web interface as shown above)
```

### Step 3: Create and Push the Tag

```bash
# After the release PR is merged, update main
git checkout main
git pull origin main

# Create annotated tag
git tag -a v0.3.0 -m "Release version 0.3.0 - Testing & CI/CD"

# Push the tag
git push origin v0.3.0
```

### Step 4: Watch the Magic! ✨

The release workflow will automatically:
1. Create a GitHub release
2. Extract the changelog
3. Run installation tests
4. Publish release notes

**Check it:** Go to `https://github.com/aa-parky/pipemind-comfyui/releases`

---

## 🔍 Checking CI Status

### View Running Workflows

**On GitHub:**
1. Go to: `https://github.com/aa-parky/pipemind-comfyui/actions`
2. See all workflow runs
3. Click any run to see details

**What you'll see:**
- ✅ Green checkmark = Passed
- ❌ Red X = Failed
- 🟡 Yellow circle = Running

### If CI Fails

**Step 1:** Don't panic! Click the failed check

**Step 2:** Look at the error message

**Common issues:**

**Tests failed?**
```bash
# Run tests locally
pytest

# See what failed
pytest -v

# Fix the issue
# Commit and push again
```

**Code quality failed?**
```bash
# Check formatting
black --check .

# Auto-fix formatting
black .

# Check linting
flake8 .

# Commit fixes
git add .
git commit -m "Fix: Code formatting"
git push
```

**PR validation failed?**
- Check your PR title format
- Make sure CHANGELOG.md is updated
- Read the error message for specific issues

---

## 📝 Commit Message Format

**Format:** `Type: Description`

**Types:**
- `Add:` - New features
- `Fix:` - Bug fixes
- `Update:` - Improvements to existing features
- `Docs:` - Documentation changes
- `Refactor:` - Code restructuring
- `Test:` - Adding or updating tests
- `Chore:` - Maintenance tasks
- `Style:` - Code style changes
- `Perf:` - Performance improvements
- `CI:` - CI/CD changes

**Examples:**
```bash
git commit -m "Add: Qwen 2.5 aspect ratio presets"
git commit -m "Fix: Boolean switch not updating color"
git commit -m "Update: Improve token counter performance"
git commit -m "Docs: Add usage examples for batch loader"
git commit -m "Test: Add tests for new aspect ratio node"
```

---

## 🧪 Running Tests Locally

### Before Pushing

```bash
# Install dev dependencies (first time only)
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run just smoke tests (quick check)
pytest -m smoke

# Run with coverage
pytest --cov=. --cov-report=term
```

### Understanding Test Output

```bash
# Green dots = passed
# F = failed
# E = error
# s = skipped

tests/nodes/test_qwen_aspect_ratio.py::test_landscape ✓
tests/nodes/test_boolean_switch.py::test_switch_true ✓

====== 36 passed in 2.5s ======
```

---

## 🆘 Common Scenarios

### Scenario 1: Made changes, need to get them to main

```bash
# 1. Commit your changes
git add .
git commit -m "Add: Description of changes"

# 2. Create claude/ branch
git checkout -b claude/my-changes-01EZGMz7FmrCuM9L8v2fEsiX

# 3. Push
git push -u origin claude/my-changes-01EZGMz7FmrCuM9L8v2fEsiX

# 4. Go to GitHub, create PR to main

# 5. After merge, update local develop
git checkout develop
git pull origin main
```

### Scenario 2: Want to fix a bug quickly

```bash
# 1. Start from develop
git checkout develop
git pull origin develop

# 2. Make your fix
# Edit files...

# 3. Test locally
pytest -m smoke

# 4. Commit and push
git add .
git commit -m "Fix: Description of bug fix"
git checkout -b claude/bugfix-description-01EZGMz7FmrCuM9L8v2fEsiX
git push -u origin claude/bugfix-description-01EZGMz7FmrCuM9L8v2fEsiX

# 5. Create PR, wait for CI, merge
```

### Scenario 3: Want to try something experimental

```bash
# 1. Create a feature branch
git checkout develop
git checkout -b experiment/new-idea

# 2. Work on it freely
# Edit, commit, test...

# 3. When ready to share:
git checkout -b claude/experiment-new-idea-01EZGMz7FmrCuM9L8v2fEsiX
git push -u origin claude/experiment-new-idea-01EZGMz7FmrCuM9L8v2fEsiX

# 4. Create PR when ready
```

### Scenario 4: Accidentally worked on main

```bash
# Don't commit yet! Move changes to develop:

# 1. Stash your changes
git stash

# 2. Switch to develop
git checkout develop

# 3. Apply changes
git stash pop

# 4. Now commit normally
git add .
git commit -m "Add: My changes"
```

---

## 🎯 Quick Reference

### Daily Commands
```bash
git checkout develop              # Switch to develop
git pull origin develop           # Get latest changes
git status                        # See what changed
git add .                         # Stage all changes
git commit -m "Type: Message"    # Commit
```

### Push to GitHub
```bash
git checkout -b claude/feature-01EZGMz7FmrCuM9L8v2fEsiX
git push -u origin claude/feature-01EZGMz7FmrCuM9L8v2fEsiX
# Then create PR on GitHub
```

### After PR Merged
```bash
git checkout develop
git pull origin main
```

### Create Release
```bash
# Edit CHANGELOG.md
git checkout main
git pull origin main
git tag -a v0.3.0 -m "Release v0.3.0"
git push origin v0.3.0
```

---

## 📞 Need Help?

**Check CI Status:**
https://github.com/aa-parky/pipemind-comfyui/actions

**View Open PRs:**
https://github.com/aa-parky/pipemind-comfyui/pulls

**See Releases:**
https://github.com/aa-parky/pipemind-comfyui/releases

**Test Locally:**
```bash
pytest -v
```

---

## 🎓 Visual Workflow Summary

```
You work here ──┐
                ↓
    [develop branch]
         │
         │ git commit
         │ git push (via claude/ branch)
         ↓
    [Pull Request]
         │
         │ CI runs tests
         │ You review
         ↓
    [Merge to main]
         │
         ↓
    [main branch] ← Users install from here
         │
         │ git tag (when ready)
         ↓
    [Release] ← Automatic via CI
```

---

**Remember:**
- Work on `develop` (or feature branches)
- Push via `claude/` branches
- Create PRs to `main`
- Wait for CI ✅
- Merge when green
- Tag `main` for releases

You've got this! 🚀
