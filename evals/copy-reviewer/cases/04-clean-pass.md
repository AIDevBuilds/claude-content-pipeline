# 04-clean-pass

- **Expected verdict:** PASS
- **Expected category:** n/a
- **Why:** accurate, specific, plain and fits the platform. A reviewer that flags this is producing noise, which costs rounds and teaches writers to ignore it.
- **Platform:** X post (the author's own)

## Text under review

```
Cache-aside has a race: a reader misses the cache and reads the row, a writer updates the row and deletes the key, then the reader puts the value it read, now stale, into the cache.

A short TTL limits how long that lasts. It doesn't close the race.
```
