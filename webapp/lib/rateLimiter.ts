type Key = string

const buckets = new Map<Key, { tokens: number; last: number }>()

export function rateLimit(key: Key, opts = { capacity: 10, refillPerSec: 1 }) {
  const now = Date.now()
  const b = buckets.get(key) || { tokens: opts.capacity, last: now }
  const elapsed = (now - b.last) / 1000
  const refill = Math.floor(elapsed * opts.refillPerSec)
  b.tokens = Math.min(opts.capacity, b.tokens + refill)
  b.last = now
  if (b.tokens <= 0) {
    buckets.set(key, b)
    return false
  }
  b.tokens -= 1
  buckets.set(key, b)
  return true
}
