# 📊 Database Schema - Deep Dive Explanation

**Focus:** How `shortlist` and `request_status_history` tables integrate into the CSR application

---

## 📋 Table of Contents
1. [Overall Database Architecture](#overall-database-architecture)
2. [Shortlist Table - Detailed Explanation](#shortlist-table---detailed-explanation)
3. [Request Status History Table - Detailed Explanation](#request-status-history-table---detailed-explanation)
4. [How They Work Together](#how-they-work-together)
5. [Data Flow Examples](#data-flow-examples)
6. [Business Logic & Constraints](#business-logic--constraints)

---

## 1. Overall Database Architecture

### Core Entity Relationship Diagram

```
┌─────────────────┐
│  user_accounts  │ ◄──┐
│  (All Users)    │    │
└────────┬────────┘    │
         │             │
         │ role_id     │ Foreign Keys
         ▼             │
┌─────────────────┐    │
│   user_roles    │    │
│ (4 roles)       │    │
└─────────────────┘    │
                       │
┌──────────────────────┼────────────────────────────┐
│                      │                            │
│  ┌──────────────┐    │    ┌──────────────────┐   │
│  │   requests   │◄───┼────│    shortlist     │   │
│  │ (PIN creates)│    │    │ (CSR bookmarks)  │   │
│  └──────┬───────┘    │    └──────────────────┘   │
│         │            │                            │
│         │            │    ┌──────────────────┐   │
│         └────────────┼───►│request_status_   │   │
│                      │    │   _history       │   │
│                      │    │ (Audit Trail)    │   │
│                      └────┴──────────────────┘   │
│                                                   │
│  All tables reference user_accounts              │
└───────────────────────────────────────────────────┘
```

### Table Purpose Summary

| Table | Purpose | Used By | Key Feature |
|-------|---------|---------|-------------|
| **user_accounts** | Authentication & identity | All users | Central user registry |
| **user_roles** | Role-based access control | System | Defines 4 user types |
| **requests** | Service opportunities | PIN (creates), CSR (views) | Main business entity |
| **shortlist** | CSR's saved requests | CSR only | Personal bookmark list |
| **request_status_history** | Audit trail | System | Tracks all status changes |

---

## 2. Shortlist Table - Detailed Explanation

### 🎯 Purpose
The `shortlist` table acts as a **personal bookmark/wishlist** for CSR Representatives. When a CSR sees an interesting volunteer opportunity (request), they can "shortlist" it to:
- Save it for later review
- Track opportunities they're interested in
- Manage their volunteer workflow
- Filter and search their saved items

### 📐 Schema

```sql
CREATE TABLE shortlist (
    id                   SERIAL PRIMARY KEY,
    csr_user_id          INTEGER NOT NULL,           -- Which CSR saved this?
    request_id           INTEGER NOT NULL,           -- Which request was saved?
    status               VARCHAR(50),                -- Workflow status
    notes                TEXT,                       -- CSR's personal notes
    volunteered_hours    FLOAT,                      -- Hours spent (when completed)
    completion_date      TIMESTAMP,                  -- When work finished
    feedback_from_pin    TEXT,                       -- Feedback received
    shortlisted_at       TIMESTAMP DEFAULT NOW(),    -- When first saved
    updated_at           TIMESTAMP DEFAULT NOW(),    -- Last modified
    
    -- Foreign Keys
    FOREIGN KEY (csr_user_id) REFERENCES user_accounts(user_id) ON DELETE CASCADE,
    FOREIGN KEY (request_id) REFERENCES requests(id) ON DELETE CASCADE,
    
    -- Constraints
    UNIQUE (csr_user_id, request_id)  -- Prevent duplicate shortlisting
);
```

### 🔑 Key Fields Explained

#### **id** (Primary Key)
- Unique identifier for each shortlist entry
- Used when updating or deleting specific shortlist items

#### **csr_user_id** (Foreign Key → user_accounts)
- Links to the CSR who saved this request
- Ensures only CSRs can create shortlist entries
- ON DELETE CASCADE: If CSR account deleted, their shortlist entries are removed

#### **request_id** (Foreign Key → requests)
- Links to the actual volunteer opportunity
- ON DELETE CASCADE: If request deleted, shortlist entries are auto-removed
- This is the "what" being bookmarked

#### **status** (Workflow Tracker)
Tracks the CSR's progress on this opportunity:
```
SHORTLISTED   → Just saved, not started yet
IN_PROGRESS   → CSR is actively working on it
COMPLETED     → Work finished successfully
DECLINED      → CSR decided not to pursue
```

#### **notes** (Personal Notes)
- CSR's private comments about the opportunity
- Example: "Need to check my schedule", "Requires car", "Contact before Friday"

#### **volunteered_hours** (Completion Data)
- Tracks actual hours spent when status = COMPLETED
- Used for CSR analytics and reporting

#### **completion_date** (Completion Data)
- Timestamp when work was finished
- Paired with volunteered_hours for history tracking

#### **feedback_from_pin** (Post-Completion)
- Feedback/review from the PIN user after completion
- Helps CSRs build their volunteer portfolio

#### **shortlisted_at** (Timestamp)
- When CSR first saved this request
- Used for:
  - Sorting (show newest first)
  - Date range filtering ("show items I saved last week")

#### **updated_at** (Timestamp)
- Last modification time
- Auto-updated when status changes or notes added

### 🔗 Relationships

#### **Many-to-Many Relationship**
```
CSR User (1) ──────── (Many) Shortlist ──────── (Many) Requests

One CSR can shortlist many requests
One request can be shortlisted by many CSRs
```

**Example:**
```
CSR "Alice" can shortlist:
- Request #5 (Food donation)
- Request #12 (Tutoring)
- Request #20 (Elder care)

Request #5 can be shortlisted by:
- CSR "Alice"
- CSR "Bob"
- CSR "Charlie"
```

### ✨ Unique Constraint Explained

```sql
UNIQUE (csr_user_id, request_id)
```

**Prevents:** Same CSR shortlisting the same request twice

**Allowed:**
```sql
-- Alice shortlists request 5 ✅
INSERT INTO shortlist (csr_user_id, request_id) VALUES (1, 5);

-- Bob shortlists request 5 ✅ (Different CSR)
INSERT INTO shortlist (csr_user_id, request_id) VALUES (2, 5);
```

**Blocked:**
```sql
-- Alice tries to shortlist request 5 again ❌
INSERT INTO shortlist (csr_user_id, request_id) VALUES (1, 5);
-- ERROR: duplicate key value violates unique constraint
```

### 📊 Analytics Integration

#### Shortlist Count on Requests Table
```python
# When CSR adds to shortlist:
requests.shortlist_count += 1

# When CSR removes from shortlist:
requests.shortlist_count -= 1
```

**Business Value:**
- PIN users can see "10 CSRs interested" → Popular request
- Platform can prioritize high-interest requests
- Analytics dashboard shows trending opportunities

### 🎭 User Stories Implemented

1. **US: CSR save shortlisted items**
   - CSR clicks "Shortlist" → Row inserted with status='SHORTLISTED'
   - Persistent storage for later access

2. **US: CSR search through shortlisted items**
   - Filter by status: `WHERE csr_user_id=X AND status='IN_PROGRESS'`
   - Search by keyword: JOIN with requests table

3. **US: Filter by service type or date**
   - Service type: `JOIN requests WHERE service_type='Education'`
   - Date range: `WHERE shortlisted_at BETWEEN '2024-01-01' AND '2024-12-31'`

---

## 3. Request Status History Table - Detailed Explanation

### 🎯 Purpose
The `request_status_history` table is an **audit trail** that records every time a request changes status. This provides:
- Complete history of request lifecycle
- Accountability (who changed what and when)
- Compliance and transparency
- Analytics on request processing times

### 📐 Schema

```sql
CREATE TABLE request_status_history (
    id              SERIAL PRIMARY KEY,
    request_id      INTEGER NOT NULL,               -- Which request changed?
    old_status      VARCHAR(50),                    -- Previous status
    new_status      VARCHAR(50),                    -- New status
    changed_by      INTEGER,                        -- User who made change
    reason          TEXT,                           -- Why was it changed?
    changed_at      TIMESTAMP DEFAULT NOW(),        -- When changed
    
    -- Foreign Keys
    FOREIGN KEY (request_id) REFERENCES requests(id) ON DELETE CASCADE,
    FOREIGN KEY (changed_by) REFERENCES user_accounts(user_id) ON DELETE SET NULL
);
```

### 🔑 Key Fields Explained

#### **id** (Primary Key)
- Unique identifier for each status change event
- Sequential history tracking

#### **request_id** (Foreign Key → requests)
- Links to the request being tracked
- ON DELETE CASCADE: If request deleted, history is removed too

#### **old_status** (Audit Data)
- What the status was before the change
- Example: 'ACTIVE', 'PENDING', 'FULFILLED'

#### **new_status** (Audit Data)
- What the status became after the change
- Example: 'ACTIVE', 'SUSPENDED', 'CANCELLED'

#### **changed_by** (Foreign Key → user_accounts)
- User ID of person who made the change
- ON DELETE SET NULL: If user deleted, history preserved but user=NULL
- Enables accountability

#### **reason** (Optional Explanation)
- Text explanation for the status change
- Examples:
  - "Request fulfilled by CSR volunteer"
  - "Suspended pending verification"
  - "Cancelled by PIN user"

#### **changed_at** (Timestamp)
- When the change occurred
- Auto-populated with current timestamp

### 📝 Example Lifecycle

**Request #42 - "Need groceries delivered"**

| ID | request_id | old_status | new_status | changed_by | reason | changed_at |
|----|------------|------------|------------|------------|--------|------------|
| 1  | 42         | NULL       | PENDING    | 10 (PIN)   | Initial creation | 2025-01-01 10:00 |
| 2  | 42         | PENDING    | ACTIVE     | 5 (Admin)  | Approved after review | 2025-01-01 14:30 |
| 3  | 42         | ACTIVE     | IN_PROGRESS| 20 (CSR)   | CSR started helping | 2025-01-02 09:15 |
| 4  | 42         | IN_PROGRESS| FULFILLED  | 20 (CSR)   | Groceries delivered | 2025-01-02 16:45 |

**Insights from History:**
- Request was active for ~19 hours before CSR picked it up
- Total time from creation to fulfillment: 1 day 6 hours
- CSR completed work in ~7.5 hours
- Full accountability chain preserved

### 🔍 Query Examples

#### Get Complete History of a Request
```sql
SELECT 
    h.old_status,
    h.new_status,
    u.username AS changed_by_user,
    h.reason,
    h.changed_at
FROM request_status_history h
LEFT JOIN user_accounts u ON h.changed_by = u.user_id
WHERE h.request_id = 42
ORDER BY h.changed_at ASC;
```

#### Find Average Time to Fulfillment
```sql
SELECT AVG(
    EXTRACT(EPOCH FROM fulfilled.changed_at - created.changed_at) / 3600
) AS avg_hours_to_fulfill
FROM request_status_history created
JOIN request_status_history fulfilled 
    ON created.request_id = fulfilled.request_id
WHERE created.new_status = 'ACTIVE'
  AND fulfilled.new_status = 'FULFILLED';
```

### 🎭 Business Use Cases

1. **Compliance & Audit**
   - "Who suspended this request and why?"
   - Legal requirement to maintain audit trail

2. **Analytics Dashboard**
   - Average time from ACTIVE → FULFILLED
   - Identify bottlenecks (requests stuck in PENDING)
   - CSR performance (how quickly they fulfill)

3. **Transparency for PIN Users**
   - PIN can see full history: "Your request was reviewed, approved, and assigned to a CSR"

4. **Dispute Resolution**
   - If CSR claims they completed work but PIN says no
   - Check history: When was status changed? Who changed it?

---

## 4. How They Work Together

### 🔄 Integration Flow

#### Scenario: CSR Completes a Shortlisted Request

```
Step 1: CSR shortlists request
┌─────────────────────────────────────────┐
│ shortlist table                         │
├─────────────────────────────────────────┤
│ id: 100                                 │
│ csr_user_id: 5 (Alice)                  │
│ request_id: 42                          │
│ status: SHORTLISTED                     │
│ shortlisted_at: 2025-01-01 10:00        │
└─────────────────────────────────────────┘
        ↓ (No history entry yet)


Step 2: CSR starts working (updates shortlist status)
┌─────────────────────────────────────────┐
│ shortlist table (UPDATED)               │
├─────────────────────────────────────────┤
│ id: 100                                 │
│ status: IN_PROGRESS ← Changed          │
│ updated_at: 2025-01-02 09:00 ← Updated │
└─────────────────────────────────────────┘
        ↓ No request status change yet


Step 3: CSR completes work (updates request + shortlist)
┌─────────────────────────────────────────┐
│ requests table (UPDATED)                │
├─────────────────────────────────────────┤
│ id: 42                                  │
│ status: FULFILLED ← Changed             │
└─────────────────────────────────────────┘
        ↓ Triggers history entry
┌─────────────────────────────────────────┐
│ request_status_history (INSERTED)       │
├─────────────────────────────────────────┤
│ request_id: 42                          │
│ old_status: ACTIVE                      │
│ new_status: FULFILLED                   │
│ changed_by: 5 (Alice)                   │
│ changed_at: 2025-01-02 16:45            │
└─────────────────────────────────────────┘

AND

┌─────────────────────────────────────────┐
│ shortlist table (UPDATED)               │
├─────────────────────────────────────────┤
│ id: 100                                 │
│ status: COMPLETED ← Changed             │
│ volunteered_hours: 8.5                  │
│ completion_date: 2025-01-02 16:45       │
│ updated_at: 2025-01-02 16:45            │
└─────────────────────────────────────────┘
```

### 🔗 Key Relationships

```
┌──────────────┐
│   requests   │
│   id: 42     │
│status: ACTIVE│
└──────┬───────┘
       │
       │ ONE request has...
       │
       ├───► MANY shortlist entries (different CSRs can shortlist same request)
       │     ┌─────────────────┐
       │     │ shortlist       │
       │     │ id: 100         │
       │     │ request_id: 42  │
       │     │ csr_user_id: 5  │
       │     └─────────────────┘
       │
       └───► MANY history entries (each status change creates entry)
             ┌────────────────────────┐
             │ request_status_history │
             │ id: 10                 │
             │ request_id: 42         │
             │ old: NULL              │
             │ new: PENDING           │
             └────────────────────────┘
             ┌────────────────────────┐
             │ request_status_history │
             │ id: 11                 │
             │ request_id: 42         │
             │ old: PENDING           │
             │ new: ACTIVE            │
             └────────────────────────┘
```

---

## 5. Data Flow Examples

### Example 1: PIN Creates Request → CSR Shortlists → CSR Completes

#### Step-by-Step Data Changes

**T=0: PIN creates request**
```sql
-- requests table
INSERT INTO requests (id, pin_user_id, title, status)
VALUES (42, 10, 'Need groceries', 'PENDING');

-- request_status_history table
INSERT INTO request_status_history (request_id, old_status, new_status, changed_by)
VALUES (42, NULL, 'PENDING', 10);
```

**T=1: Admin approves request**
```sql
-- requests table (UPDATE)
UPDATE requests SET status = 'ACTIVE' WHERE id = 42;

-- request_status_history table (INSERT new entry)
INSERT INTO request_status_history (request_id, old_status, new_status, changed_by, reason)
VALUES (42, 'PENDING', 'ACTIVE', 5, 'Approved after verification');
```

**T=2: CSR Alice shortlists it**
```sql
-- shortlist table (INSERT)
INSERT INTO shortlist (csr_user_id, request_id, status)
VALUES (5, 42, 'SHORTLISTED');

-- requests table (UPDATE counter)
UPDATE requests SET shortlist_count = shortlist_count + 1 WHERE id = 42;

-- NO history entry (request status didn't change, only shortlist)
```

**T=3: CSR Bob also shortlists it**
```sql
-- shortlist table (INSERT another entry)
INSERT INTO shortlist (csr_user_id, request_id, status)
VALUES (8, 42, 'SHORTLISTED');

-- requests table (UPDATE counter again)
UPDATE requests SET shortlist_count = shortlist_count + 1 WHERE id = 42;
-- Now shortlist_count = 2
```

**T=4: Alice starts working**
```sql
-- shortlist table (UPDATE Alice's entry)
UPDATE shortlist 
SET status = 'IN_PROGRESS', updated_at = NOW()
WHERE id = 100;  -- Alice's shortlist entry

-- NO change to requests.status (still ACTIVE)
-- NO history entry (main request status unchanged)
```

**T=5: Alice completes work**
```sql
-- requests table (UPDATE)
UPDATE requests SET status = 'FULFILLED' WHERE id = 42;

-- request_status_history table (INSERT)
INSERT INTO request_status_history (request_id, old_status, new_status, changed_by, reason)
VALUES (42, 'ACTIVE', 'FULFILLED', 5, 'Groceries delivered successfully');

-- shortlist table (UPDATE Alice's entry)
UPDATE shortlist 
SET status = 'COMPLETED', 
    volunteered_hours = 8.5,
    completion_date = NOW(),
    updated_at = NOW()
WHERE id = 100;
```

**Final State Summary:**

| Table | State |
|-------|-------|
| **requests** | Request #42 status = FULFILLED, shortlist_count = 2 |
| **shortlist** | 2 entries: Alice (COMPLETED), Bob (SHORTLISTED) |
| **request_status_history** | 3 entries: NULL→PENDING, PENDING→ACTIVE, ACTIVE→FULFILLED |

### Example 2: Request Suspended by Admin

**Scenario:** Admin suspends request due to policy violation

```sql
-- requests table (UPDATE)
UPDATE requests SET status = 'SUSPENDED' WHERE id = 42;

-- request_status_history table (AUDIT TRAIL)
INSERT INTO request_status_history (request_id, old_status, new_status, changed_by, reason)
VALUES (42, 'ACTIVE', 'SUSPENDED', 1, 'Violates community guidelines - inappropriate language');

-- shortlist table (NO automatic change)
-- CSRs who shortlisted this can still see it in their list
-- But they see status='SUSPENDED' when they JOIN with requests table
```

**Query to see impact on CSR shortlists:**
```sql
SELECT 
    s.id AS shortlist_id,
    s.csr_user_id,
    s.status AS shortlist_status,
    r.status AS request_status,
    u.username AS csr_name
FROM shortlist s
JOIN requests r ON s.request_id = r.id
JOIN user_accounts u ON s.csr_user_id = u.user_id
WHERE s.request_id = 42;
```

Result:
```
| shortlist_id | csr_user_id | shortlist_status | request_status | csr_name |
|--------------|-------------|------------------|----------------|----------|
| 100          | 5           | IN_PROGRESS      | SUSPENDED      | alice    |
| 101          | 8           | SHORTLISTED      | SUSPENDED      | bob      |
```

**Business Logic:**
- CSRs see "This request has been suspended" warning
- They can remove from shortlist or keep it (maybe it will be un-suspended)

---

## 6. Business Logic & Constraints

### Shortlist Business Rules

#### ✅ Allowed Operations

1. **CSR can shortlist ACTIVE requests**
   ```python
   if request.status == 'ACTIVE' and user.role == 'CSR':
       Shortlist.add_to_shortlist(csr_id, request_id)
   ```

2. **Multiple CSRs can shortlist same request**
   ```python
   # Alice shortlists request 42 ✅
   # Bob shortlists request 42 ✅
   # Charlie shortlists request 42 ✅
   ```

3. **CSR can update their shortlist status independently**
   ```python
   # Alice: SHORTLISTED → IN_PROGRESS ✅
   # Bob: Still SHORTLISTED ✅
   # Charlie: SHORTLISTED → DECLINED ✅
   ```

#### ❌ Blocked Operations

1. **Same CSR cannot shortlist same request twice**
   ```python
   # Alice shortlists request 42
   Shortlist.add_to_shortlist(alice_id, 42)  # ✅
   
   # Alice tries again
   Shortlist.add_to_shortlist(alice_id, 42)  # ❌ UNIQUE constraint error
   ```

2. **Non-CSR users cannot shortlist**
   ```python
   if user.role != 'CSR':
       return "Only CSR Representatives can shortlist requests"
   ```

3. **Cannot shortlist non-ACTIVE requests**
   ```python
   if request.status != 'ACTIVE':
       return "Can only shortlist ACTIVE requests"
   ```

### Request Status History Business Rules

#### ✅ Automatic Logging

1. **Every status change creates history entry**
   ```python
   def update_request_status(request_id, new_status, user_id, reason):
       old_status = get_current_status(request_id)
       
       # Update main table
       update_request(request_id, new_status)
       
       # Log to history (ALWAYS)
       log_status_change(request_id, old_status, new_status, user_id, reason)
   ```

2. **History is immutable (append-only)**
   ```python
   # You can INSERT new entries ✅
   # You CANNOT UPDATE or DELETE existing entries ❌
   # History must be preserved for audit compliance
   ```

### Cascade Delete Behavior

#### When Request is Deleted

```sql
DELETE FROM requests WHERE id = 42;
```

**Automatic Cascades:**
1. ✅ All shortlist entries deleted (ON DELETE CASCADE)
2. ✅ All status history entries deleted (ON DELETE CASCADE)
3. ✅ Analytics data updated (shortlist_count no longer relevant)

**Result:** Complete cleanup, no orphaned records

#### When User is Deleted

```sql
DELETE FROM user_accounts WHERE user_id = 5;  -- Alice deleted
```

**Cascade Effects:**

1. **Shortlist table:**
   ```sql
   -- Alice's shortlist entries deleted (ON DELETE CASCADE)
   DELETE FROM shortlist WHERE csr_user_id = 5;
   ```

2. **Request status history:**
   ```sql
   -- History preserved, but changed_by set to NULL (ON DELETE SET NULL)
   UPDATE request_status_history 
   SET changed_by = NULL 
   WHERE changed_by = 5;
   ```

**Why different behavior?**
- Shortlist is personal to CSR → Delete when CSR gone
- History is audit trail → Keep history, just show "User deleted" for changed_by

---

## 📊 Summary Comparison

| Aspect | Shortlist | Request Status History |
|--------|-----------|------------------------|
| **Purpose** | Personal CSR bookmark/workflow | System-wide audit trail |
| **Scope** | One CSR's view of requests | All changes to one request |
| **Mutability** | Can UPDATE status, notes | Append-only (no updates) |
| **Ownership** | Belongs to CSR user | Belongs to request |
| **Privacy** | Private to CSR | Visible to admins |
| **Lifecycle** | Created/updated by CSR | Auto-created on status change |
| **Delete behavior** | Deleted with CSR account | Preserved (changed_by=NULL) |
| **Query frequency** | High (CSR dashboard) | Low (analytics, audits) |

---

## 🎯 Key Takeaways

### Shortlist Table
✅ Enables CSR to save interesting opportunities  
✅ Tracks personal workflow (SHORTLISTED → IN_PROGRESS → COMPLETED)  
✅ Supports filtering and searching saved items  
✅ Multiple CSRs can shortlist same request  
✅ Analytics: Shows popularity (shortlist_count on requests)  

### Request Status History Table
✅ Complete audit trail of request lifecycle  
✅ Accountability (who changed what and when)  
✅ Compliance and transparency  
✅ Analytics on processing times  
✅ Immutable record for legal/audit purposes  

### Together They Provide
✅ **For CSRs:** Personal management + workflow tracking  
✅ **For System:** Analytics + accountability + compliance  
✅ **For Users:** Transparency + trust + insights  

---

**Need more details on a specific aspect? Let me know!** 🚀
