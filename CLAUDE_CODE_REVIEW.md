# Code Review: Potential Crash & Stacktrace Issues

**Review Date:** 2026-01-05
**Reviewer:** Claude Code
**Codebase:** operationcode-pybot

---

## Executive Summary

This review identified **15 issues** across the codebase that could lead to crashes, unhandled exceptions, or stacktraces in production. Issues are categorized by severity and grouped into a phased remediation plan.

---

## Issues Identified

### 1. Empty Businesses Array Crash in Lunch Command

**Severity:** High
**Location:** `pybot/endpoints/slack/utils/slash_lunch.py:32-34`

```python
def select_random_lunch(self, lunch_response: dict) -> dict:
    location_count = len(lunch_response["businesses"])
    selected_location = randint(0, location_count - 1)  # Crashes if businesses is empty!
```

**Problem:** If Yelp returns zero businesses (no restaurants found), `randint(0, -1)` raises `ValueError: empty range for randrange()`.

**Fix:** Add guard clause to check for empty results before selection.

---

### 2. Unhandled Yelp API Errors

**Severity:** High
**Location:** `pybot/endpoints/slack/commands.py:95-97`

```python
async with app.http_session.get(**request) as r:
    r.raise_for_status()  # Raises on 4xx/5xx with no try/except
    message_params = lunch.select_random_lunch(await r.json())
```

**Problem:** HTTP errors from Yelp API (rate limiting, auth failures, network issues) will crash the handler. The `catch_command_slack_error` decorator only catches `SlackAPIError`, not `aiohttp.ClientError`.

**Fix:** Wrap in try/except to handle `aiohttp.ClientResponseError` and `aiohttp.ClientError`.

---

### 3. Missing Email KeyError in Multiple Locations

**Severity:** High
**Locations:**
- `pybot/endpoints/slack/utils/event_utils.py:88-89`
- `pybot/endpoints/slack/actions/mentor_request.py:27-28`
- `pybot/endpoints/slack/actions/mentor_request.py:129-130`

```python
user_info = await slack_api.query(methods.USERS_INFO, {"user": slack_id})
email = user_info["user"]["profile"]["email"]  # KeyError if user has no email
```

**Problem:** Not all Slack users have an email in their profile (guests, restricted accounts, privacy settings). Accessing this without a check raises `KeyError`.

**Fix:** Use `.get()` with fallback or wrap in try/except.

---

### 4. Empty Service Records IndexError

**Severity:** High
**Location:** `pybot/endpoints/slack/message_templates/mentor_request.py:99-100`

```python
service_records = await airtable.find_records("Services", "Name", self.service)
params["Service"] = [service_records[0]["id"]]  # IndexError if no records found!
```

**Problem:** If no matching service is found in Airtable, accessing `[0]` raises `IndexError`.

**Fix:** Add guard clause to verify records exist before accessing.

---

### 5. Airtable API Response Key Errors

**Severity:** High
**Location:** `pybot/plugins/airtable/api.py:58-62`

```python
res_json = await self.get(url, params=params)
records = res_json["records"]  # KeyError if API returns error response
self.record_id_to_name[table_name] = {
    record["id"]: record["fields"]["Name"] for record in records
}
```

**Problem:** Airtable API error responses don't include `records` key. Also assumes all records have a `Name` field.

**Fix:** Add error response checking before accessing `records`.

---

### 6. Empty Mentor Dict KeyError

**Severity:** High
**Location:** `pybot/endpoints/airtable/utils.py:18-21`

```python
mentor = await airtable.get_row_from_record_id("Mentors", requested_mentor)
email = mentor["Email"]  # mentor could be {} from exception handler
```

**Problem:** `get_row_from_record_id` returns `{}` on exception, causing `KeyError` when accessing `Email`.

**Fix:** Check if mentor dict is populated before accessing keys.

---

### 7. No Error Handling in Mentor Request Flow

**Severity:** Medium
**Location:** `pybot/endpoints/airtable/requests.py:20-45`

```python
async def mentor_request(request: dict, app: SirBot) -> None:
    slack_id = await _slack_user_id_from_email(...)
    futures = [...]
    service_translation, requested_mentor_message, mentors = await asyncio.gather(*futures)
    # If any gather call fails, entire handler crashes
```

**Problem:** Multiple async operations with no error handling. Any failure crashes the entire handler.

**Fix:** Wrap in try/except or use `asyncio.gather(return_exceptions=True)`.

---

### 8. Incorrect Exception Logging Pattern

**Severity:** Medium
**Locations:**
- `pybot/plugins/airtable/api.py:70`
- `pybot/plugins/airtable/api.py:108`
- `pybot/plugins/airtable/api.py:125`
- `pybot/endpoints/slack/actions/mentor_request.py:144`

```python
logger.exception(f"Couldn't get row from record id {record_id}", ex)  # Wrong
```

**Problem:** Passing exception as second argument treats it as a format argument. The exception traceback is not logged.

**Fix:** Remove the exception argument; `logger.exception()` automatically captures it:
```python
logger.exception(f"Couldn't get row from record id {record_id}")
```

---

### 9. Deprecated asyncio.wait Usage

**Severity:** Medium
**Location:** `pybot/endpoints/slack/events.py:40`

```python
await asyncio.wait(futures)  # futures is a list of coroutines
```

**Problem:** In Python 3.10+, passing coroutines directly to `asyncio.wait()` is deprecated. Should pass Task objects or use `asyncio.gather()`.

**Fix:** Use `asyncio.gather(*futures)` instead.

---

### 10. Unreachable Code in Backend Auth

**Severity:** Medium
**Location:** `pybot/endpoints/slack/utils/event_utils.py:111-114`

```python
if 400 <= response.status:
    logger.exception("Failed to authenticate with backend")
    return {}
response.raise_for_status()  # Never reached when status >= 400
```

**Problem:** `raise_for_status()` is unreachable after the early return. This isn't a crash risk but indicates confused error handling logic.

**Fix:** Remove the redundant `raise_for_status()` call.

---

### 11. Decorator Only Catches SlackAPIError

**Severity:** Medium
**Location:** `pybot/endpoints/slack/utils/general_utils.py:9-39`

```python
@functools.wraps(func)
async def handler(command: Command, app: SirBot, *args, **kwargs):
    try:
        await func(command, app, *args, **kwargs)
    except SlackAPIError:
        # Only catches SlackAPIError - other exceptions propagate!
```

**Problem:** Commands can fail with `KeyError`, `IndexError`, `aiohttp.ClientError`, etc. These are not caught and crash the handler.

**Fix:** Add broader exception handling or create specific decorators for different error types.

---

### 12. Invalid Type Annotation

**Severity:** Low
**Location:** `pybot/endpoints/slack/message_templates/mentor_request.py:39`

```python
@property
def skillsets(self) -> [str]:  # Invalid syntax
```

**Problem:** `[str]` is not valid type annotation syntax. Should be `list[str]`.

**Fix:** Change to `list[str]`.

---

### 13. Airtable get Method Missing Error Check

**Severity:** Medium
**Location:** `pybot/plugins/airtable/api.py:18-22`

```python
async def get(self, url, **kwargs):
    async with self.session.get(url, headers=auth_header, **kwargs) as r:
        return await r.json()  # No status check - returns error JSON silently
```

**Problem:** Unlike `patch`, the `get` method doesn't call `raise_for_status()`. Error responses are returned as normal data.

**Fix:** Add `r.raise_for_status()` or check `ok` field in response.

---

### 14. Potential Division Issues in Pagination

**Severity:** Low
**Location:** `pybot/plugins/airtable/api.py:35-43`

```python
async def _depaginate_records(self, url, params, offset):
    records = []
    while offset:
        params["offset"] = offset
        response = await self.get(url, params=params)
        records.extend(response["records"])  # KeyError if error response
```

**Problem:** If Airtable returns an error during pagination, `response["records"]` raises KeyError.

**Fix:** Add error checking within the pagination loop.

---

### 15. Missing YELP_TOKEN Validation

**Severity:** Low
**Location:** `pybot/endpoints/slack/utils/__init__.py:12`

```python
YELP_TOKEN = os.environ.get("YELP_TOKEN", "token")
```

**Problem:** Defaults to literal string "token" which will fail Yelp API auth silently, returning error responses that may crash downstream code.

**Fix:** Either require the token or handle missing token gracefully in the lunch command.

---

## Phased Remediation Plan

### Phase 1: Critical Crash Prevention (Immediate)

**Goal:** Prevent the most likely crashes in production.

| Issue # | Description | File | Estimated Effort |
|---------|-------------|------|------------------|
| 1 | Empty businesses array crash | slash_lunch.py | 15 min |
| 2 | Unhandled Yelp API errors | commands.py | 20 min |
| 4 | Empty service records IndexError | mentor_request.py | 15 min |
| 6 | Empty mentor dict KeyError | airtable/utils.py | 15 min |

**Deliverable:** PR with defensive checks for critical data access patterns.

---

### Phase 2: Error Handling Improvements (Short-term)

**Goal:** Improve error handling in API integrations.

| Issue # | Description | File | Estimated Effort |
|---------|-------------|------|------------------|
| 3 | Missing email KeyError | Multiple files | 30 min |
| 5 | Airtable API response errors | api.py | 30 min |
| 7 | Mentor request flow errors | requests.py | 30 min |
| 11 | Decorator exception coverage | general_utils.py | 20 min |
| 13 | Airtable get error check | api.py | 15 min |

**Deliverable:** PR with comprehensive error handling for external API calls.

---

### Phase 3: Code Quality Fixes (Medium-term)

**Goal:** Fix incorrect patterns and deprecation warnings.

| Issue # | Description | File | Estimated Effort |
|---------|-------------|------|------------------|
| 8 | Incorrect exception logging | Multiple files | 15 min |
| 9 | Deprecated asyncio.wait | events.py | 10 min |
| 10 | Unreachable code | event_utils.py | 5 min |
| 12 | Invalid type annotation | mentor_request.py | 5 min |
| 14 | Pagination error handling | api.py | 20 min |

**Deliverable:** PR with code quality improvements and deprecation fixes.

---

### Phase 4: Configuration & Validation (Long-term)

**Goal:** Improve configuration validation and startup checks.

| Issue # | Description | File | Estimated Effort |
|---------|-------------|------|------------------|
| 15 | YELP_TOKEN validation | __init__.py | 20 min |
| - | Add startup validation for required env vars | __main__.py | 30 min |
| - | Add health check for external service connectivity | endpoints | 45 min |

**Deliverable:** PR with configuration validation and improved observability.

---

## Testing Recommendations

1. **Add unit tests for edge cases:**
   - Empty Yelp API responses
   - Users without email addresses
   - Missing Airtable records
   - API error responses

2. **Add integration tests:**
   - Mock external API failures
   - Test error message delivery to users

3. **Add error tracking:**
   - Ensure Sentry captures all unhandled exceptions
   - Add custom context for debugging

---

## Appendix: Quick Reference

### Files Requiring Changes

| File | Issues |
|------|--------|
| `pybot/endpoints/slack/utils/slash_lunch.py` | #1 |
| `pybot/endpoints/slack/commands.py` | #2 |
| `pybot/endpoints/slack/utils/event_utils.py` | #3, #10 |
| `pybot/endpoints/slack/actions/mentor_request.py` | #3, #8 |
| `pybot/endpoints/slack/message_templates/mentor_request.py` | #4, #12 |
| `pybot/plugins/airtable/api.py` | #5, #8, #13, #14 |
| `pybot/endpoints/airtable/utils.py` | #6 |
| `pybot/endpoints/airtable/requests.py` | #7 |
| `pybot/endpoints/slack/utils/general_utils.py` | #11 |
| `pybot/endpoints/slack/events.py` | #9 |
| `pybot/endpoints/slack/utils/__init__.py` | #15 |
