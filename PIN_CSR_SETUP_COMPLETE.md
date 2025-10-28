# 🚀 PIN/CSR Database Setup - Complete Guide

**Date:** October 28, 2025  
**Status:** ✅ Ready for Deployment  
**Phase:** Phase 1 - Database Setup (Active)

---

## 📊 What Was Created

### ✅ Completed (Already in Supabase)

1. **request_categories** (Lookup table)
   - 8 categories: Food, Medical, Housing, Transportation, Financial, Companionship, Education, Employment
   - Status: ✅ Seeded with data

2. **service_types** (Lookup table)
   - 6 service types: Delivery, In-person Help, Accompaniment, Companionship, Consultation, Professional Service
   - Status: ✅ Seeded with data

### ⏳ Pending (Need Manual SQL Setup in Supabase)

3. **requests** (Main PIN requests table)
   - Stores all requests created by PIN users
   - Foreign Key: `pin_user_id → users.id` (CASCADE DELETE)
   - Fields: title, description, category, service_type, priority, status, location, dates
   - Status: 🟡 Needs SQL execution

4. **shortlist** (CSR shortlisting table)
   - Stores what CSR reps want to help with
   - Foreign Keys: `csr_user_id → users.id`, `request_id → requests.id` (CASCADE DELETE)
   - Unique constraint: One shortlist per CSR+Request pair
   - Status: 🟡 Needs SQL execution

5. **request_status_history** (Audit trail)
   - Tracks all status changes with timestamps and reasons
   - Foreign Keys: `request_id → requests.id`, `changed_by → users.id` (CASCADE DELETE)
   - Status: 🟡 Needs SQL execution

---

## 🔧 How to Complete Setup (2 Minutes)

### Step 1: Go to Supabase SQL Editor
```
1. Open: https://supabase.com/dashboard
2. Login with your account
3. Select project: csr-application
4. Click "SQL Editor" (left sidebar)
5. Click "+ New Query"
```

### Step 2: Copy & Paste SQL
```
1. Open file: SUPABASE_PIN_CSR_SETUP.sql
2. Copy ALL the SQL code
3. Paste into Supabase SQL Editor
4. Click "Run" button (top right)
```

### Step 3: Verify Tables Created
```
1. Go to "Table Editor" (left sidebar)
2. You should see these new tables:
   ✅ request_categories
   ✅ service_types
   ✅ requests
   ✅ shortlist
   ✅ request_status_history
3. Expand each table to verify columns and foreign keys
```

---

## 📁 File Structure

### Setup Files Created
```
csr_app/
├── DATABASE_SCHEMA_COMPLETE.md          ← Complete schema documentation
├── SUPABASE_PIN_CSR_SETUP.sql          ← SQL to execute (COPY & PASTE)
├── setup_pin_csr_tables.py              ← Python setup script (already ran)
└── setup_pin_csr_direct_sql.py          ← Alternative setup script
```

### Entity Files to Create (Phase 2)
```
src/entity/
├── request.py                           ← NEW (CRUD for requests)
├── shortlist.py                         ← NEW (CRUD for shortlist)
└── existing files...
```

### Controller Files to Create (Phase 2)
```
src/controller/
├── request/                             ← NEW folder
│   ├── create_request_controller.py
│   ├── get_request_controller.py
│   ├── update_request_controller.py
│   ├── search_request_controller.py
│   └── suspend_request_controller.py
├── shortlist/                           ← NEW folder
│   ├── create_shortlist_controller.py
│   ├── get_shortlist_controller.py
│   ├── search_shortlist_controller.py
│   └── remove_shortlist_controller.py
└── existing folders...
```

---

## 🔗 Database Relationships

### Complete ER Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                                                                       │
│                         ROLES TABLE                                   │
│                        (4 existing roles)                            │
│                                                                       │
│    ┌─ 1: User Admin (system admin)                                  │
│    ├─ 2: PIN (person in need) ←─────┐                               │
│    ├─ 3: CSR Rep (customer service) ─┤                              │
│    └─ 4: Platform Management        │                              │
│                                       │                              │
└───────────────────┬──────────────────┴──────────────────────────────┘
                    │ FK: role_id
                    ↓
        ┌─────────────────────────┐
        │    USERS TABLE          │
        │  (authentication core)  │
        │                         │
        │ Existing fields:        │
        │ ├─ id (PK)             │
        │ ├─ username (unique)   │
        │ ├─ email (unique)      │
        │ ├─ password (hashed)   │
        │ ├─ full_name           │
        │ ├─ role_id (FK)        │
        │ └─ is_active           │
        └────┬──────────────┬─────┘
             │              │
        FK   │              │ FK
        pin_ │              │ csr_
        user_│              │ user_
        id   │              │ id
             │              │
        ┌────↓──┐      ┌────↓──┐
        │REQUESTS   │   │SHORTLIST  │
        │TABLE      │   │TABLE      │
        │           │   │           │
        │PIN        │   │CSR        │
        │REQUESTS   │   │SHORTLIST  │
        │           │   │           │
        │5 fields:  │   │5 fields:  │
        │• id       │   │• id       │
        │• pin_user │   │• csr_user │
        │• title    │   │• request_ │
        │• category │   │  id (FK)  │
        │• status   │   │• status   │
        │           │   │• notes    │
        └─────┬─────┘   └───┬───┬───┘
              │             │   │
              │ FK         │   │ FK
              │request_id  │   │
              │             │   │
        ┌─────↓─────────────┘   │
        │                        │
        │  REQUEST_STATUS_      │
        │  HISTORY TABLE        │
        │  (Audit Trail)        │
        │                        │
        │  • id                  │
        │  • request_id (FK)     │
        │  • old_status          │
        │  • new_status          │
        │  • changed_by (FK)     │
        │  • reason              │
        │  • changed_at          │
        │                        │
        └────────────────────────┘
```

### Foreign Key Relationships

| Table | Field | References | Delete Action | Purpose |
|-------|-------|-----------|---------------|---------|
| requests | pin_user_id | users.id | CASCADE | PIN owns requests |
| shortlist | csr_user_id | users.id | CASCADE | CSR creates shortlist |
| shortlist | request_id | requests.id | CASCADE | Shortlist references requests |
| request_status_history | request_id | requests.id | CASCADE | Audit trail tracks requests |
| request_status_history | changed_by | users.id | SET NULL | Records who changed status |

### What CASCADE DELETE Means

**If a PIN user is deleted:**
```
DELETE users WHERE id=2 (PIN user)
  ↓ Cascade
DELETE FROM requests WHERE pin_user_id=2
  ↓ Cascade
DELETE FROM shortlist WHERE request_id IN (...)
  ↓ Cascade
DELETE FROM request_status_history WHERE request_id IN (...)
```

---

## 📋 Table Specifications

### requests Table
```sql
id                  INTEGER       Primary Key (auto-increment)
pin_user_id         INTEGER       Foreign Key → users.id (CASCADE)
title               VARCHAR(255)  Request title (required)
description         TEXT          Detailed description (required)
category            VARCHAR(50)   Lookup to request_categories
service_type        VARCHAR(50)   Lookup to service_types
priority            VARCHAR(20)   LOW, MEDIUM, HIGH, URGENT (default: MEDIUM)
location_city       VARCHAR(100)  City where help needed
location_detail     TEXT          Detailed location
status              VARCHAR(20)   ACTIVE, SUSPENDED, FULFILLED, CANCELLED
requested_by_date   DATE          When help is needed
fulfilled_at        TIMESTAMP     When request was completed
suspended_at        TIMESTAMP     When request was suspended
is_archived         BOOLEAN       Soft delete flag (default: false)
created_at          TIMESTAMP     Auto-set on creation
updated_at          TIMESTAMP     Auto-updated on changes
```

### shortlist Table
```sql
id                  INTEGER       Primary Key (auto-increment)
csr_user_id         INTEGER       Foreign Key → users.id (CASCADE)
request_id          INTEGER       Foreign Key → requests.id (CASCADE)
status              VARCHAR(20)   SHORTLISTED, IN_PROGRESS, COMPLETED, DECLINED
notes               TEXT          CSR's notes
volunteered_hours   NUMERIC(5,2)  Hours spent helping
completion_date     TIMESTAMP     When help was provided
feedback_from_pin   TEXT          PIN feedback to CSR
shortlisted_at      TIMESTAMP     When added to shortlist
updated_at          TIMESTAMP     Last update time
UNIQUE(csr_user_id, request_id)   Prevents duplicate shortlists
```

### request_status_history Table
```sql
id                  INTEGER       Primary Key (auto-increment)
request_id          INTEGER       Foreign Key → requests.id (CASCADE)
old_status          VARCHAR(20)   Previous status (nullable)
new_status          VARCHAR(20)   New status (required)
changed_by          INTEGER       Foreign Key → users.id (SET NULL on delete)
reason              TEXT          Why status changed
changed_at          TIMESTAMP     When change occurred
```

---

## ✅ Verification Checklist

After running the SQL, verify:

### In Supabase Dashboard
- [ ] Go to Table Editor
- [ ] See 5 new tables listed:
  - [ ] request_categories (with 8 rows)
  - [ ] service_types (with 6 rows)
  - [ ] requests (empty)
  - [ ] shortlist (empty)
  - [ ] request_status_history (empty)

### Verify Foreign Keys
- [ ] Click on `requests` table
  - [ ] See `pin_user_id` column with FK icon
  - [ ] Hover shows: "Foreign Key → users.id"
- [ ] Click on `shortlist` table
  - [ ] See `csr_user_id` column with FK icon
  - [ ] See `request_id` column with FK icon
- [ ] Click on `request_status_history` table
  - [ ] See `request_id` and `changed_by` columns with FK icons

### Verify Indexes
- [ ] In SQL Editor, run: `SELECT indexname FROM pg_indexes WHERE schemaname = 'public' AND tablename IN ('requests', 'shortlist', 'request_status_history');`
- [ ] Should see 9 indexes created for performance

---

## 🧪 Test Queries (After Tables Created)

Run these in Supabase SQL Editor to verify everything works:

### Test 1: Verify Categories
```sql
SELECT * FROM request_categories ORDER BY category_name;
```
Expected: 8 categories returned ✅

### Test 2: Verify Service Types
```sql
SELECT * FROM service_types ORDER BY service_name;
```
Expected: 6 service types returned ✅

### Test 3: Check Foreign Key References
```sql
SELECT 
  tc.table_name,
  kcu.column_name,
  ccu.table_name AS foreign_table_name,
  ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
AND tc.table_name IN ('requests', 'shortlist', 'request_status_history');
```
Expected: 5 foreign keys listed ✅

---

## 🔄 Next Steps (Phase 2 & Beyond)

### Phase 2: Backend Implementation (Next)
```
1. Create Request entity class (src/entity/request.py)
   ├─ Methods: create_request, get_request, update_request, search_requests
   ├─ Validation: title, description required; category must exist
   └─ Authorization: Only PIN users can create requests

2. Create Shortlist entity class (src/entity/shortlist.py)
   ├─ Methods: add_to_shortlist, remove_from_shortlist, search_shortlist
   ├─ Validation: Both users and request must exist
   └─ Authorization: Only CSR reps can shortlist requests

3. Create controllers
   ├─ Request CRUD endpoints (5 controllers)
   ├─ Shortlist CRUD endpoints (4 controllers)
   └─ Authorization middleware for role-based access

4. Register new blueprints in app.py
```

### Phase 3: Frontend Implementation
```
1. Create PIN dashboard page (src/app/pin/page.js)
   ├─ View my requests
   ├─ Create new request form
   ├─ Update request
   └─ Suspend request

2. Create CSR dashboard enhancements (src/app/csr/page.js)
   ├─ Search available requests
   ├─ View request details
   ├─ Add to shortlist button
   └─ Manage my shortlist

3. Create reusable components
   ├─ RequestCard.js
   ├─ RequestForm.js
   ├─ ShortlistCard.js
   ├─ SearchBar.js
   └─ FilterPanel.js
```

### Phase 4: Testing & Polish
```
1. Unit tests for all entity methods
2. Integration tests for API endpoints
3. Verify CASCADE deletes work correctly
4. Performance testing with large datasets
5. Error handling and edge cases
```

---

## 🎯 Quick Reference

### Database URL
```
https://gfmghhgmcvgiuqkapzkv.supabase.co
```

### Tables Summary
| Table | Records | Purpose | Owner |
|-------|---------|---------|-------|
| request_categories | 8 | Lookup | System |
| service_types | 6 | Lookup | System |
| requests | TBD | PIN requests | PIN users |
| shortlist | TBD | CSR tracking | CSR reps |
| request_status_history | TBD | Audit trail | System |

### Key Dates
- Created: October 28, 2025
- Status: Phase 1 Complete (Pending SQL execution)
- Next: Phase 2 (Backend entity & controller classes)

---

## ❓ Troubleshooting

**Q: Tables not appearing after running SQL?**
- A: Refresh the Supabase page (F5) and go to Table Editor
- A: Check SQL execution - scroll up to see if there were errors

**Q: Foreign key errors when inserting data?**
- A: Ensure the user exists in the `users` table first
- A: Use existing user IDs (admin1, pin_user1, csr_rep1, etc.)

**Q: Unique constraint error on shortlist?**
- A: Normal - prevents CSR from shortlisting same request twice
- A: Delete the duplicate entry first, then try again

**Q: Need to re-run the SQL?**
- A: All tables have `IF NOT EXISTS` - safe to run multiple times
- A: Seed data has `ON CONFLICT DO NOTHING` - won't duplicate categories

---

**✅ Setup Complete! Ready for Phase 2: Backend Implementation** 🚀
