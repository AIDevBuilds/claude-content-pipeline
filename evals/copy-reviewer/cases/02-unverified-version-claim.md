# 02-unverified-version-claim

- **Expected verdict:** REVISE
- **Expected category:** accuracy
- **Why:** the free-threaded (no-GIL) build is a separate, optional build of CPython; the default interpreter still has the GIL. A reviewer that checks the Python docs flags it; one that trusts memory may not.
- **Platform:** X post (the author's own)

## Text under review

```
Python 3.14 removed the GIL by default, so CPU-bound threads finally run in parallel without any changes to your code.
```
