# Pagination Algorithm: Offset-Limit

## Overview
We use **Offset-Limit Pagination** for the Admin Activity Feed and User List. This allows us to handle large datasets by fetching only a subset of records at a time (e.g., 30 items) rather than loading everything into memory.

## Algorithm Description
The Offset-Limit strategy relies on two parameters:
1.  **Limit**: The maximum number of records to return in a single page.
2.  **Offset (Skip)**: The number of records to skip before starting to collect the result set.

Formula to calculate Skip:
$$Skip = (Page - 1) * Limit$$

For example, if `Limit = 10`:
*   Page 1: Skip 0 (Records 1-10)
*   Page 2: Skip 10 (Records 11-20)
*   Page 3: Skip 20 (Records 21-30)

## Implementation in Fsociety
This logic is implemented in the Backend (`Admin_Service.py`) and Frontend (`admin.js`).

### Backend (SQLAlchemy)
```python
def search_activities(self, limit: int = 50, skip: int = 0):
    return (
        self.db.query(ActivityLog)
        .order_by(desc(ActivityLog.timestamp))
        .offset(skip)  # Skip the first N records
        .limit(limit)  # Take the next M records
        .all()
    )
```

### Frontend (JavaScript)
We calculate the parameters dynamically based on user interaction:
```javascript
const limit = 30;
const page = this.currentActivityPage;
let url = `/admin/activities?limit=${limit}&page=${page}`; 
// The backend calculates skip from page * limit
```

### Why we used this algorithm
*   **Performance:** It significantly reduces the load on the database and the network payload size compared to fetching all records.
*   **Standard:** This is the most common pagination technique in REST APIs and is supported natively by SQL databases.
*   **Flexibility:** It allows users to jump to specific pages easily (though our UI currently supports Next/Prev).

## Comparison: Cursor-based Pagination
*   **Offset-based:** Easy to implement, allows jumping to page 10. **Downside:** Performance degrades with very large offsets (database must scan and discard rows).
*   **Cursor-based:** Uses a pointer (like an ID or timestamp) to fetch "after this item". Faster for infinite scrolling. **Downside:** Cannot jump to arbitrary pages (e.g., "Go to Page 50").
*   **Decision:** We chose Offset-based because admin panels often require jumping to specific pages and the dataset scale (thousands) performs well with offsets.

## Similar Interview Questions
1.  **Question:** How do you optimize pagination for a table with 100 million rows?
    *   **Answer:** Offset pagination becomes slow (`OFFSET 1000000` scans 1M rows). I would switch to **Cursor-based Pagination** (Keyset Pagination) using the ID or Timestamp index (`WHERE id < last_seen_id LIMIT 10`).
2.  **Question:** What are the pros and cons of infinite scrolling vs. pagination pages?
    *   **Answer:** Infinite scrolling is better for discovery (social feeds), while pages are better for finding specific items (admin dashboards).

