# Search Algorithm: Linear Filtering (Database Query)

## Overview
The Admin Activity Search feature uses a **Server-Side Filtering** approach. This can be conceptualized as a Linear Search typically (scans table), though optimized by database indices (B-Tree).

## Algorithm Description
The filtering logic constructs a query dynamically based on provided parameters.

1.  **Input:** User ID, Action Type, Date Range.
2.  **Query Construction:** Start with `SELECT * FROM activities`.
3.  **Filter Application:**
    *   If `User ID` is present -> `AND user_id = X`
    *   If `Action` is present -> `AND action = Y`
    *   If `Date From` is present -> `AND timestamp >= Date From`
    *   If `Date To` is present -> `AND timestamp <= Date To`
4.  **Execution:** The database engine executes the query. If indexes exist on these columns, it uses a **B-Tree Search** (Logarithmic time). If no index exists, it performs a **Full Table Scan** (Linear Time $O(N)$).

## Implementation in Fsociety
We use SQLAlchemy to build this query dynamically in `backend/database/repositories/activity_repository.py`.

```python
def search(self, user_id=None, action=None, date_from=None, date_to=None, limit=50, skip=0):
    # Base Query
    q = self.db.query(ActivityLog)
    
    # Dynamic Filtering
    if user_id:
        q = q.filter(ActivityLog.user_id == user_id)
    
    if action:
        q = q.filter(ActivityLog.action == action)
    
    if date_from:
        q = q.filter(ActivityLog.timestamp >= date_from)
    
    if date_to:
        q = q.filter(ActivityLog.timestamp <= date_to)
    
    # Sorting and Pagination
    return q.order_by(desc(ActivityLog.timestamp)).offset(skip).limit(limit).all()
```

### Why we used this algorithm
*   **Precision:** It returns exactly the data needed.
*   **Scalability:** By leveraging the database engine (SQLite/PostgreSQL), we avoid loading all data into application memory to filter it (which would be $O(N)$ in Python).
*   **Composability:** Filters can be mixed and matched arbitrarily.

## Similar Interview Questions
1.  **Question:** How would you optimize this search if the `activities` table had 1 billion rows?
    *   **Answer:** I would add **Indexes** on commonly filtered columns (`user_id`, `action`, `timestamp`). A **Composite Index** (e.g., `(user_id, timestamp)`) would speed up "user's recent activities" queries.
2.  **Question:** Design a "Type-ahead" search (Autocomplete) for Usernames.
    *   **Answer:** I would use a **Trie** (Prefix Tree) data structure or a database `LIKE 'prefix%'` query (which effectively does a range scan on the index).

