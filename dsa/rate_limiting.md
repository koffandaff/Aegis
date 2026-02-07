# Rate Limiting Algorithm: Fixed Window Counter

## Overview
We use a **Fixed Window Counter** algorithm to implement rate limiting on sensitive API endpoints (like `/login`). This prevents brute-force attacks and abuse by limiting the number of requests a user (identified by IP) can make within a specific time window.

## Algorithm Description
The Fixed Window Counter algorithm works by dividing time into fixed windows (e.g., 60 seconds) and maintaining a counter for each user within that window.

1.  **Request Arrival:** When a request comes in, we identify the client (IP address) and the target endpoint.
2.  **Window Check:** We check the current time window.
3.  **Counter Increment:** We increment the request count for that user in the current window.
4.  **Threshold Check:**
    *   If the count is within the limit (e.g., 10 requests), the request is allowed.
    *   If the count exceeds the limit, the request is rejected (HTTP 429 Too Many Requests).
5.  **Reset:** After the window expires (e.g., after 60 seconds), the counter resets or old timestamps are discarded.

## Implementation in Fsociety
We implemented a custom in-memory `SimpleRateLimiter` class in `backend/routers/limiter.py`.

### Code Snippet given below:
```python
class SimpleRateLimiter:
    def __init__(self):
        # Dictionary to store (ip, endpoint) -> [timestamps]
        self.requests = defaultdict(list)

    def is_rate_limited(self, ip: str, endpoint: str, limit: int, window: int) -> bool:
        now = time.time()
        key = (ip, endpoint)
        
        # Clean up old timestamps (Lazy Expiration)
        self.requests[key] = [t for t in self.requests[key] if now - t < window]
        
        if len(self.requests[key]) >= limit:
            return True
        
        self.requests[key].append(now)
        return False
```

### Why we used this algorithm
*   **Simplicity:** It is easy to understand and implement without complex dependencies like Redis (for a standalone app).
*   **Effectiveness:** It effectively stops rapid-fire brute-force attacks.
*   **Memory Efficiency:** By using lazy cleanup (removing old timestamps only when a new request comes), we keep memory usage low.

## Similar Interview Questions
1.  **Question:** Design a Rate Limiter.
    *   **Discussion:** Compare Fixed Window, Sliding Window Log, and Token Bucket algorithms. Discuss trade-offs between accuracy (Sliding Window) and performance (Fixed Window).
2.  **Question:** How would you scale this rate limiter to a distributed system?
    *   **Answer:** Use a shared store like Redis or Memcached to count requests across multiple server instances.

