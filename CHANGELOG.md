# Changelog

## 2026-06-07

### Fixed

- Changed the `insert_system_prompt` runtime injection path to prefer `extra_user_content_parts` instead of appending a standalone `system` message into `req.contexts`.
- Restored prompt-cache stability by avoiding long-memory blocks being inserted into the middle of subsequent conversation history.
- Kept long-memory injection working while reducing the risk of cache invalidation caused by history structure shifts.
