# Changelog

## 2026-06-07

### Changed

- Decoupled history retention from live request cleanup.
- Added `request_contexts_memory_len` to control how many old Mnemosyne memory injections are kept in the real LLM request before the current round injects new memory.
- Kept `contexts_memory_len` focused on history retention and stored context cleanup, so long-term memory can remain preserved without forcing old injected blocks to be re-sent on every request.
- Defaulted live request cleanup to `0`, which clears old Mnemosyne injections from the outgoing request while keeping history and Milvus storage intact.
- Added regression coverage for user-prompt and inserted-system memory cleanup behavior.
- Bumped plugin version to `v2.1.0-test3` in both runtime registration and `metadata.yaml` to make hot-reload state easier to verify.
- Added plugin version and request length breakdown fields to request trace output, plus startup logs for the effective memory injection settings.
