# Upgrade Analysis: operationcode-pybot

## Executive Summary

This document analyzes the operationcode-pybot application to determine the effort required to upgrade to supported versions of Python and PostgreSQL. The primary challenge is the abandoned `sirbot` framework dependency, which requires forking and modernizing.

**Current State:**
- Python 3.7 (EOL: June 2023)
- Dependencies targeting Python 3.6-3.7 era
- Abandoned `sirbot` and `slack-sansio` dependencies (last commits: July 2020)

**Target State:**
- Python 3.11 or 3.12 (recommended: 3.12)
- PostgreSQL 15+ (if database is added in future)
- Modernized async patterns

---

## 1. Current Application Architecture

### 1.1 Technology Stack

| Component | Current Version | Status |
|-----------|-----------------|--------|
| Python | 3.7 | EOL (June 2023) |
| sirbot | 0.1.1 | Abandoned (July 2020) |
| slack-sansio | 1.0.0 | Abandoned (July 2020) |
| aiohttp | ^3.4 | Outdated |
| sentry-sdk | ^0.17.8 | Outdated |
| pyyaml | ^5.3.1 | Outdated |

### 1.2 Application Structure

```
pybot/
├── __main__.py          # Entry point, uses SirBot and SlackPlugin
├── endpoints/
│   ├── airtable/        # Airtable webhook handlers
│   ├── api/             # REST API endpoints
│   └── slack/           # Slack event/command/action handlers
│       ├── actions/     # Interactive message handlers
│       ├── commands.py  # Slash commands (/lunch, /mentor, etc.)
│       ├── events.py    # Slack events (team_join)
│       └── messages.py  # Message handlers
└── plugins/
    ├── airtable/        # Custom Airtable plugin
    └── api/             # Custom API plugin
```

### 1.3 Key Integration Points with sirbot

The application uses `sirbot` as its core framework:

1. **SirBot class** (`sirbot.SirBot`): Main application class extending `aiohttp.web.Application`
2. **SlackPlugin** (`sirbot.plugins.slack.SlackPlugin`): Handles Slack API interactions
3. **Plugin system**: Custom plugins (Airtable, API) follow sirbot's plugin pattern with `load()` method

---

## 2. Dependency Analysis

### 2.1 Direct Dependencies (pyproject.toml)

| Package | Current | Latest | Breaking Changes |
|---------|---------|--------|------------------|
| python | ^3.7 | 3.12.x | Significant async changes |
| aiocontextvars | ^0.2.2 | N/A | Obsolete in Python 3.7+ |
| cchardet | ^2.1.6 | N/A | Abandoned, use charset-normalizer |
| cython | ^0.29.21 | 3.0.x | Major version bump |
| python-dotenv | ^0.14.0 | 1.0.x | Minor API changes |
| pyyaml | ^5.3.1 | 6.0.x | Minor changes |
| sentry-sdk | ^0.17.8 | 1.x | API changes |
| sirbot | ^0.1.1 | N/A | **ABANDONED - Must fork** |
| zipcodes | ^1.1.2 | 1.2.x | Compatible |

### 2.2 sirbot's Transitive Dependencies

From `pyslackers/sir-bot-a-lot-2` pyproject.toml:

| Package | Version in sirbot | Status |
|---------|-------------------|--------|
| aiohttp | ^3.4 | Needs update to 3.9+ |
| aiofiles | ^0.4.0 | Needs update |
| asyncpg | ^0.18.2 | Needs update to 0.29+ |
| asyncio-contextmanager | ^1.0 | **Obsolete** - use native `@contextlib.asynccontextmanager` |
| slack-sansio | ^1.0.0 | **ABANDONED - Must fork** |
| gidgethub | ^3.0 | Needs update |
| ujson | ^1.35 | Needs update to 5.x |
| apscheduler | ^3.5 | Needs update to 3.10+ |

### 2.3 slack-sansio Analysis

From `pyslackers/slack-sansio` pyproject.toml:

- **Python requirement**: ^3.6
- **Last commit**: July 10, 2020
- **Dependencies**: aiohttp (optional), requests (optional)
- **Key classes used by pybot**:
  - `slack.events.Event`, `EventRouter`, `MessageRouter`
  - `slack.actions.Action`, `Router`
  - `slack.commands.Command`, `Router`
  - `slack.methods` (API method definitions)
  - `slack.io.aiohttp.SlackAPI`

---

## 3. Critical Breaking Changes

### 3.1 Python 3.7 → 3.12 Breaking Changes

#### asyncio.coroutine Decorator (CRITICAL)
```python
# sirbot uses this deprecated pattern extensively:
if not asyncio.iscoroutinefunction(handler):
    handler = asyncio.coroutine(handler)  # REMOVED in Python 3.11
```
**Impact**: All handler registration in SlackPlugin needs updating.
**Fix**: Use `async def` functions exclusively.

#### asyncio.get_event_loop() Behavior
```python
# sirbot/bot.py current code:
self["http_session"] = aiohttp.ClientSession(
    loop=kwargs.get("loop") or asyncio.get_event_loop()
)
```
**Impact**: `asyncio.get_event_loop()` deprecation warnings in 3.10+, different behavior in 3.12.
**Fix**: Remove explicit loop passing; aiohttp 3.9+ handles this automatically.

#### aiocontext / asyncio-contextmanager (OBSOLETE)
```python
# sirbot/plugins/postgres/plugin.py uses:
from aiocontext import async_contextmanager
```
**Impact**: This library is obsolete.
**Fix**: Use `contextlib.asynccontextmanager` (built-in since Python 3.7).

### 3.2 Deprecated/Removed Patterns

| Pattern | Location | Fix |
|---------|----------|-----|
| `asyncio.coroutine()` | sirbot slack plugin | Use `async def` |
| `loop=` parameter | sirbot bot.py | Remove, use implicit loop |
| `aiocontext` library | sirbot postgres plugin | Use `contextlib` |
| Type comments | Various | Use annotations |

---

## 4. Repository Status

### 4.1 pyslackers/sir-bot-a-lot-2

- **Last commit**: September 5, 2019
- **Stars**: ~50
- **Open issues**: Unknown
- **Python tested**: 3.6, 3.7
- **CI status**: Unknown

### 4.2 pyslackers/slack-sansio

- **Last commit**: July 10, 2020 ("python 3.9 tests")
- **Stars**: ~130
- **Open issues**: Unknown
- **Python tested**: 3.6, 3.7, 3.8, 3.9 (claimed)
- **Note**: Despite "python 3.9 tests" commit, not published to PyPI after

---

## 5. Upgrade Effort Estimation

### 5.1 Vendoring Approach (RECOMMENDED)

| Task | Effort | Risk |
|------|--------|------|
| Create `pybot/_vendor/` structure | Low | Low |
| Copy slack-sansio core (~10 files) | Low | Low |
| Copy sirbot core (~5 files, skip unused plugins) | Low | Low |
| Replace `asyncio.coroutine()` calls | Medium | Low |
| Remove explicit event loop passing | Low | Low |
| Update imports across pybot | Medium | Low |
| Update pyproject.toml dependencies | Low | Low |
| Update Dockerfile to Python 3.12 | Low | Low |
| Test all Slack integrations | High | Medium |
| **Total vendoring approach** | **~2-3 weeks** | **Low** |

### 5.2 Fork Approach (Alternative)

#### sirbot Fork Work

| Task | Effort | Risk |
|------|--------|------|
| Update pyproject.toml for Python 3.12 | Low | Low |
| Replace `asyncio.coroutine()` calls | Medium | Medium |
| Remove explicit event loop passing | Low | Low |
| Replace aiocontext with contextlib | Low | Low |
| Update aiohttp usage patterns | Medium | Medium |
| Update asyncpg to 0.29+ | Low | Low |
| Replace ujson with orjson (optional) | Low | Low |
| Test suite updates | High | Medium |
| **Total sirbot fork** | **~2-3 weeks** | **Medium** |

#### slack-sansio Fork Work

| Task | Effort | Risk |
|------|--------|------|
| Update pyproject.toml for Python 3.12 | Low | Low |
| Review/update async patterns | Medium | Low |
| Update aiohttp usage | Low | Low |
| Verify Slack API compatibility | Medium | Medium |
| Test suite updates | Medium | Medium |
| **Total slack-sansio fork** | **~1-2 weeks** | **Low-Medium** |

#### operationcode-pybot Updates

| Task | Effort | Risk |
|------|--------|------|
| Update pyproject.toml dependencies | Low | Low |
| Point to forked sirbot/slack-sansio | Low | Low |
| Remove aiocontextvars dependency | Low | Low |
| Replace cchardet with charset-normalizer | Low | Low |
| Update Dockerfile to Python 3.12 | Low | Low |
| Update test dependencies | Low | Low |
| Test all Slack integrations | High | Medium |
| **Total pybot updates** | **~1 week** | **Low** |

### 5.3 Total Effort Comparison

| Approach | Duration | Complexity |
|----------|----------|------------|
| **Vendoring (recommended)** | **2-3 weeks** | **Low** |
| Fork (separate repos) | 5-8 weeks | Medium |
| Replace with slack-bolt | 8-12 weeks | High |

---

## 6. Alternative Approaches

### 6.1 Option A: Vendor Dependencies (RECOMMENDED)

Copy only the required code from sirbot and slack-sansio directly into pybot as a `_vendor/` directory.

**Pros:**
- Single repository to maintain
- No external dependency management for abandoned libs
- Can strip unused features (postgres, github, apscheduler plugins)
- Simpler CI/CD - everything in one place
- Changes are immediate, no release coordination
- Minimal code footprint (~15 files total)

**Cons:**
- Slightly larger repository
- Need to handle namespace carefully

**Actual usage from sirbot:**
- `SirBot` class (1 file)
- `SlackPlugin` class + endpoints (3 files)

**Actual usage from slack-sansio:**
- `slack.events` (Event, Message, EventRouter, MessageRouter)
- `slack.actions` (Action, Router)
- `slack.commands` (Command, Router)
- `slack.methods` (API method constants)
- `slack.exceptions` (SlackAPIError)
- `slack.io.aiohttp` (SlackAPI)
- `slack.sansio` (core request/response handling)

**Unused sirbot components (can omit):**
- `plugins/postgres/` - PostgreSQL integration
- `plugins/github/` - GitHub webhooks
- `plugins/apscheduler/` - Scheduled tasks
- `plugins/readthedocs/` - RTD webhooks

### 6.2 Option B: Fork and Update (Separate Repos)

**Pros:**
- Preserves existing architecture
- Minimal changes to pybot codebase
- Maintains test compatibility

**Cons:**
- Takes on maintenance burden of two separate repositories
- Need to coordinate releases between 3 repos
- sirbot/slack-sansio may have subtle bugs

### 6.3 Option C: Replace sirbot with slack-bolt

**Pros:**
- Official Slack SDK, actively maintained
- Modern Python support
- Better documentation

**Cons:**
- Complete rewrite of handler registration
- Different API patterns
- Higher initial effort (~2-3 months)

### 6.4 Option D: Replace with slack-sdk + aiohttp

**Pros:**
- Most flexibility
- Official Slack SDK

**Cons:**
- Need to build plugin architecture from scratch
- Highest effort (~3-4 months)

---

## 7. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Slack API breaking changes | Low | High | Test against current Slack API |
| Hidden sirbot bugs | Medium | Medium | Comprehensive testing |
| asyncpg compatibility | Low | Medium | asyncpg actively maintained |
| aiohttp 4.0 release | Low | Low | Pin to 3.9.x initially |
| Test suite failures | High | Low | Update test dependencies first |

---

## 8. Test Coverage Assessment

### 8.1 Current State: ~5-10% Coverage

| Module | Files | Functions | Tests | Coverage |
|--------|-------|-----------|-------|----------|
| Slack Commands | 1 | 6 | 0 | **0%** |
| Slack Actions | 5 | ~25 | 2 | **~8%** |
| Slack Events | 1 | 2 | 2 | **~50%** |
| Slack Messages | 1 | ~3 | 0 | **0%** |
| Airtable Plugin | 3 | ~12 | 0 | **0%** |
| API Plugin | 3 | ~5 | 1 | **~20%** |
| Utils | 7 | ~30 | 0 | **0%** |

### 8.2 Testing Challenge: Python 3.7 Unavailable

Python 3.7 cannot be installed on modern macOS (especially Apple Silicon).
**Solution**: Use Docker containers to run tests in both Python 3.7 (baseline) and 3.12 (target).

### 8.3 Recommended Pre-Upgrade Tests

| Category | New Tests | Purpose |
|----------|-----------|---------|
| Import safety | ~18 | Catch syntax errors from Python upgrade |
| Async verification | ~12 | Verify handlers are `async def` |
| Unit tests | ~23 | LunchCommand, dice parsing, message builders |
| **Total to add** | **~53** | |

### 8.4 Risk Reduction

Adding these tests before the upgrade reduces risk by:

1. **Establishing baseline** - Know what works before changes
2. **Catching async issues** - The `asyncio.coroutine()` removal is critical
3. **Verifying imports** - Syntax changes will break imports first
4. **Enabling comparison** - Same tests run in 3.7 and 3.12 containers

---

## 9. PostgreSQL Considerations

The current operationcode-pybot does **not use PostgreSQL directly**. However, sirbot includes a `PgPlugin` that uses `asyncpg`:

- **asyncpg** is actively maintained and supports Python 3.12
- **asyncpg 0.29+** supports PostgreSQL 9.5 to 16
- If PostgreSQL is added in the future, target PostgreSQL 15 or 16

---

## 10. Recommendations

1. **Vendor dependencies** directly into `pybot/_vendor/`:
   - Copy only the files actually used from sirbot and slack-sansio
   - Skip unused plugins (postgres, github, apscheduler, readthedocs)
   - Single repo, simpler maintenance

2. **Target Python 3.12** for the upgrade (LTS-like stability, well-tested async)

3. **Modernize async patterns** during vendoring:
   - Replace `asyncio.coroutine()` with `async def` requirement
   - Remove `loop=` parameter passing
   - Use stdlib `contextlib.asynccontextmanager`

4. **Consider future migration** to slack-bolt after stabilizing on Python 3.12

5. **Add comprehensive tests** for vendored code to catch regressions

---

## Appendix A: Proposed Vendor Structure

```
pybot/
├── _vendor/
│   ├── __init__.py
│   ├── sirbot/
│   │   ├── __init__.py          # Exports SirBot
│   │   ├── bot.py               # Core SirBot class
│   │   ├── endpoints.py         # /sirbot/plugins endpoint
│   │   └── plugins/
│   │       ├── __init__.py
│   │       └── slack/
│   │           ├── __init__.py  # Exports SlackPlugin
│   │           ├── plugin.py    # SlackPlugin class
│   │           └── endpoints.py # Slack webhook endpoints
│   └── slack/
│       ├── __init__.py          # Package exports
│       ├── actions.py           # Action class + Router
│       ├── commands.py          # Command class + Router
│       ├── events.py            # Event, Message, Routers
│       ├── exceptions.py        # SlackAPIError
│       ├── methods.py           # API method constants
│       ├── sansio.py            # Core request/response
│       ├── io/
│       │   ├── __init__.py
│       │   ├── abc.py           # SlackAPI abstract base
│       │   └── aiohttp.py       # aiohttp implementation
│       └── tests/
│           └── plugin.py        # Test fixtures (used by conftest)
```

**Total: ~15 files** (vs. full repos with ~50+ files each)

## Appendix B: Import Changes Required

```python
# BEFORE (external packages)
from sirbot import SirBot
from sirbot.plugins.slack import SlackPlugin
from slack.events import Event
from slack.actions import Action

# AFTER (vendored)
from pybot._vendor.sirbot import SirBot
from pybot._vendor.sirbot.plugins.slack import SlackPlugin
from pybot._vendor.slack.events import Event
from pybot._vendor.slack.actions import Action
```

Or with package aliasing in `pybot/_vendor/__init__.py`:
```python
# pybot/_vendor/__init__.py
from pybot._vendor import sirbot, slack

# Then imports remain cleaner:
from pybot._vendor.sirbot import SirBot
```

## Appendix C: Files to Vendor from Each Repo

### From pyslackers/slack-sansio (MIT License)

| File | Purpose | Modifications Needed |
|------|---------|---------------------|
| `slack/__init__.py` | Package exports | Minor |
| `slack/actions.py` | Action handling | None |
| `slack/commands.py` | Command handling | None |
| `slack/events.py` | Event handling | None |
| `slack/exceptions.py` | Error classes | None |
| `slack/methods.py` | API constants | None |
| `slack/sansio.py` | Core logic | Minor async updates |
| `slack/io/__init__.py` | IO exports | None |
| `slack/io/abc.py` | Abstract base | None |
| `slack/io/aiohttp.py` | aiohttp client | Remove loop= param |
| `slack/tests/plugin.py` | Test fixtures | None |

### From pyslackers/sir-bot-a-lot-2 (MIT License)

| File | Purpose | Modifications Needed |
|------|---------|---------------------|
| `sirbot/__init__.py` | Package exports | Minor |
| `sirbot/bot.py` | SirBot class | Remove loop=, async session |
| `sirbot/endpoints.py` | Plugin list endpoint | None |
| `sirbot/plugins/__init__.py` | Empty | None |
| `sirbot/plugins/slack/__init__.py` | Exports | None |
| `sirbot/plugins/slack/plugin.py` | SlackPlugin | Remove asyncio.coroutine |
| `sirbot/plugins/slack/endpoints.py` | Webhooks | None |

### NOT Needed (skip these)

- `sirbot/plugins/postgres/` - Not used
- `sirbot/plugins/github/` - Not used
- `sirbot/plugins/apscheduler/` - Not used
- `sirbot/plugins/readthedocs/` - Not used
