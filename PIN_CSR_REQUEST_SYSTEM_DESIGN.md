# PIN/CSR Request System - Design Outline

**Date:** October 28, 2025  
**Status:** Design Phase (Pre-Implementation)  
**Version:** 1.0

---

## 📋 Requirements Summary

### PIN (Person In Need) Functionalities
1. ✅ Create new request (for help needed)
2. ✅ View existing requests
3. ✅ Update existing requests
4. ✅ Suspend request (mark as no longer relevant)
5. ✅ Search requests (by keyword, category, status)

### CSR Rep (Customer Service Representative) Functionalities
1. ✅ Search volunteering opportunities (PIN requests)
2. ✅ View details of opportunities
3. ✅ Save/shortlist opportunities
4. ✅ Search shortlisted opportunities
5. ✅ Filter shortlist (by service type, date)

---

## 🗄️ Database Schema Plan

### 1. **requests** Table (Core - PIN Requests)

```sql
CREATE TABLE requests (
  -- Primary & Relationship
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  pin_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  
  -- Request Details
  title VARCHAR(255) NOT NULL,
  description TEXT NOT NULL,
  category VARCHAR(50) NOT NULL,  -- e.g., 'Food', 'Medical', 'Housing', 'Transportation'
  status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',  -- ACTIVE, SUSPENDED, FULFILLED, CANCELLED
  priority VARCHAR(20) NOT NULL DEFAULT 'MEDIUM',  -- LOW, MEDIUM, HIGH, URGENT
  
  -- Location & Service Type
  location_city VARCHAR(100) NOT NULL,
  location_address TEXT,
  service_type VARCHAR(50),  -- e.g., 'Delivery', 'Companionship', 'Financial Aid'
  
  -- Timestamps
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  requested_by_date DATE,  -- When PIN needs help by
  fulfilled_at TIMESTAMP,
  suspended_at TIMESTAMP,
  
  -- Metadata
  image_url VARCHAR(255),
  contact_number VARCHAR(20),
  estimated_volunteers_needed INT DEFAULT 1,
  volunteers_count INT DEFAULT 0,
  
  -- Soft Delete
  is_archived BOOLEAN DEFAULT FALSE,
  archived_at TIMESTAMP,
  
  CONSTRAINT valid_status CHECK (status IN ('ACTIVE', 'SUSPENDED', 'FULFILLED', 'CANCELLED'))
);

-- Indexes for common queries
CREATE INDEX idx_requests_pin_user_id ON requests(pin_user_id);
CREATE INDEX idx_requests_status ON requests(status);
CREATE INDEX idx_requests_category ON requests(category);
CREATE INDEX idx_requests_created_at ON requests(created_at DESC);
CREATE INDEX idx_requests_service_type ON requests(service_type);
```

### 2. **shortlist** Table (CSR Rep Shortlist)

```sql
CREATE TABLE shortlist (
  -- Primary & Relationship
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  csr_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  request_id UUID NOT NULL REFERENCES requests(id) ON DELETE CASCADE,
  
  -- Shortlist Metadata
  shortlisted_at TIMESTAMP DEFAULT NOW(),
  status VARCHAR(20) NOT NULL DEFAULT 'SHORTLISTED',  -- SHORTLISTED, IN_PROGRESS, COMPLETED, DECLINED
  notes TEXT,  -- CSR Rep's notes about this opportunity
  
  -- Fulfillment Tracking
  volunteered_hours DECIMAL(5,2),
  completion_date TIMESTAMP,
  feedback_from_pin TEXT,  -- Feedback from PIN
  
  -- Timestamps
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  
  CONSTRAINT valid_shortlist_status CHECK (status IN ('SHORTLISTED', 'IN_PROGRESS', 'COMPLETED', 'DECLINED')),
  CONSTRAINT unique_shortlist_per_csr_request UNIQUE(csr_user_id, request_id)
);

-- Indexes
CREATE INDEX idx_shortlist_csr_user_id ON shortlist(csr_user_id);
CREATE INDEX idx_shortlist_request_id ON shortlist(request_id);
CREATE INDEX idx_shortlist_status ON shortlist(status);
CREATE INDEX idx_shortlist_shortlisted_at ON shortlist(shortlisted_at DESC);
```

### 3. **request_categories** Table (Lookup)

```sql
CREATE TABLE request_categories (
  id SERIAL PRIMARY KEY,
  category_name VARCHAR(50) NOT NULL UNIQUE,
  description TEXT,
  icon_color VARCHAR(20),
  created_at TIMESTAMP DEFAULT NOW()
);

-- Seed data
INSERT INTO request_categories (category_name, description, icon_color) VALUES
('Food', 'Food assistance and meal provisions', 'orange'),
('Medical', 'Healthcare and medical supplies', 'red'),
('Housing', 'Shelter and housing needs', 'blue'),
('Transportation', 'Travel and transportation help', 'green'),
('Financial', 'Financial assistance and loans', 'purple'),
('Companionship', 'Social and emotional support', 'pink'),
('Education', 'Educational materials and tutoring', 'yellow'),
('Employment', 'Job seeking and career help', 'teal');
```

### 4. **service_types** Table (Lookup)

```sql
CREATE TABLE service_types (
  id SERIAL PRIMARY KEY,
  service_name VARCHAR(50) NOT NULL UNIQUE,
  description TEXT,
  category_id INT REFERENCES request_categories(id),
  created_at TIMESTAMP DEFAULT NOW()
);

-- Seed data examples
INSERT INTO service_types (service_name, description, category_id) VALUES
('Delivery', 'Deliver items to PIN', 1),
('In-person Help', 'Provide on-site assistance', 1),
('Accompaniment', 'Accompany PIN to appointments', 2),
('Companionship', 'Spend time and provide support', 6);
```

### 5. **request_status_history** Table (Audit Trail)

```sql
CREATE TABLE request_status_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  request_id UUID NOT NULL REFERENCES requests(id) ON DELETE CASCADE,
  old_status VARCHAR(20),
  new_status VARCHAR(20) NOT NULL,
  changed_by UUID REFERENCES users(id),  -- PIN or Admin
  changed_at TIMESTAMP DEFAULT NOW(),
  reason TEXT
);

CREATE INDEX idx_request_status_history_request_id ON request_status_history(request_id);
```

---

## 🔗 Relationships & ER Diagram

```
┌─────────────┐
│    users    │
│  (existing) │
└──────┬──────┘
       │
       │ (1:Many)
       │ pin_user_id
       │
       ↓
┌──────────────────┐         ┌────────────────────────┐
│   requests       │◄────────┤ request_status_history │
│  (NEW - Core)    │ 1:Many  │    (NEW - Audit)       │
└──────┬───────────┘         └────────────────────────┘
       │
       │ request_id
       │ (1:Many)
       │
       ↓
┌──────────────────┐
│   shortlist      │
│  (NEW - CSR)     │
│                  │
│ csr_user_id ─────┼──→ users(id)
└──────────────────┘


requests.category ──→ request_categories (Many:1)
requests.service_type ──→ service_types (Many:1)
```

---

## 📊 Data Model Diagram

```
requests
├─ id (PK)
├─ pin_user_id (FK) ─→ users
├─ title
├─ description
├─ category (FK) ─→ request_categories
├─ status (ACTIVE, SUSPENDED, FULFILLED, CANCELLED)
├─ priority
├─ location_city
├─ location_address
├─ service_type (FK) ─→ service_types
├─ requested_by_date
├─ created_at
├─ updated_at
├─ fulfilled_at
├─ suspended_at
└─ is_archived

shortlist
├─ id (PK)
├─ csr_user_id (FK) ─→ users
├─ request_id (FK) ─→ requests
├─ status (SHORTLISTED, IN_PROGRESS, COMPLETED, DECLINED)
├─ shortlisted_at
├─ notes
├─ volunteered_hours
├─ completion_date
└─ feedback_from_pin
```

---

## 🔄 Sequence Diagrams

### Scenario 1: PIN Creates a Request

```
PIN User          Frontend            Backend           Database
   │               (PIN Page)         (Controller)      (PostgreSQL)
   │                  │                   │                  │
   │  (1) Fill form    │                   │                  │
   ├─────────────────>│                   │                  │
   │  title, desc,    │                   │                  │
   │  category, etc   │                   │                  │
   │                  │                   │                  │
   │  (2) Submit      │                   │                  │
   │  (Validate)      │                   │                  │
   ├─────────────────>│                   │                  │
   │                  │  (3) API Call    │                  │
   │                  │  POST /requests  │                  │
   │                  ├──────────────────>│                  │
   │                  │                   │ (4) Validate    │
   │                  │                   │  - Check auth   │
   │                  │                   │  - Verify data  │
   │                  │                   │                  │
   │                  │                   │ (5) Call Entity │
   │                  │                   │  insert_request │
   │                  │                   ├─────────────────>│
   │                  │                   │                  │
   │                  │                   │ (6) INSERT INTO │
   │                  │                   │  requests table │
   │                  │                   │                  │
   │                  │                   │ (7) Return ID   │
   │                  │                   │<─────────────────┤
   │                  │                   │                  │
   │                  │  (8) 201 Created │                  │
   │                  │  {id, request}   │                  │
   │                  │<──────────────────┤                  │
   │                  │                   │                  │
   │  (9) Success msg │                   │                  │
   │<─────────────────┤                   │                  │
   │  "Request ID #1" │                   │                  │
   │  Created!        │                   │                  │
```

### Scenario 2: PIN Updates a Request

```
PIN User          Frontend            Backend           Database
   │               (Update Form)      (Controller)      (PostgreSQL)
   │                  │                   │                  │
   │  (1) Load existing request          │                  │
   ├─────────────────>│                   │                  │
   │  requestId: #1   │  (2) GET /requests/1               │
   │                  ├──────────────────>│                  │
   │                  │                   │ (3) Fetch      │
   │                  │                   ├─────────────────>│
   │                  │                   │                  │
   │                  │                   │ (4) SELECT ... │
   │                  │                   │                  │
   │                  │  (5) 200 OK      │                  │
   │                  │  {request data}   │                  │
   │                  │<──────────────────┤                  │
   │                  │                   │                  │
   │  (6) Populate form                   │                  │
   ├─────────────────>│                   │                  │
   │  Edit fields     │                   │                  │
   │                  │                   │                  │
   │  (7) Submit      │                   │                  │
   │  Updated data    │                   │                  │
   ├─────────────────>│                   │                  │
   │                  │  (8) API Call    │                  │
   │                  │  PUT /requests/1 │                  │
   │                  ├──────────────────>│                  │
   │                  │                   │ (9) Authorize  │
   │                  │                   │  Verify owner  │
   │                  │                   │                  │
   │                  │                   │ (10) Call Entity
   │                  │                   │   update_request│
   │                  │                   ├─────────────────>│
   │                  │                   │                  │
   │                  │                   │ (11) UPDATE ... │
   │                  │                   │                  │
   │                  │  (12) 200 OK     │                  │
   │                  │  {updated req}    │                  │
   │                  │<──────────────────┤                  │
   │                  │                   │                  │
   │  (13) Show success message           │                  │
   │<─────────────────┤                   │                  │
```

### Scenario 3: CSR Rep Searches and Shortlists Request

```
CSR Rep           Frontend            Backend           Database
   │               (CSR Page)         (Controller)      (PostgreSQL)
   │                  │                   │                  │
   │  (1) Search      │                   │                  │
   │  keyword: "food" │                   │                  │
   │  category: all   │                   │                  │
   ├─────────────────>│                   │                  │
   │  (2) Filter      │                   │                  │
   │  form submit     │                   │                  │
   ├─────────────────>│                   │                  │
   │                  │  (3) API Call    │                  │
   │                  │  GET /requests?  │                  │
   │                  │  search=food&... │                  │
   │                  ├──────────────────>│                  │
   │                  │                   │ (4) Query DB   │
   │                  │                   │  with filters  │
   │                  │                   ├─────────────────>│
   │                  │                   │                  │
   │                  │                   │ (5) SELECT ...  │
   │                  │                   │  WHERE status.. │
   │                  │                   │                  │
   │                  │  (6) 200 OK      │                  │
   │                  │  [requests array] │                  │
   │                  │<──────────────────┤                  │
   │                  │                   │                  │
   │  (7) Display results (5 requests)    │                  │
   │<─────────────────┤                   │                  │
   │  [Request 1]     │                   │                  │
   │  [Request 2]     │                   │                  │
   │  ...             │                   │                  │
   │                  │                   │                  │
   │  (8) Click "Shortlist" on Request 1  │                  │
   ├─────────────────>│                   │                  │
   │                  │  (9) API Call    │                  │
   │                  │  POST /shortlist │                  │
   │                  │  {request_id: 1} │                  │
   │                  ├──────────────────>│                  │
   │                  │                   │ (10) Authorize │
   │                  │                   │  Verify CSR    │
   │                  │                   │                  │
   │                  │                   │ (11) Call Entity
   │                  │                   │  add_to_shortlist
   │                  │                   ├─────────────────>│
   │                  │                   │                  │
   │                  │                   │ (12) INSERT INTO│
   │                  │                   │  shortlist      │
   │                  │                   │                  │
   │                  │  (13) 201 Created│                  │
   │                  │  {shortlist_id}   │                  │
   │                  │<──────────────────┤                  │
   │                  │                   │                  │
   │  (14) "Added to Shortlist"           │                  │
   │<─────────────────┤                   │                  │
```

### Scenario 4: PIN Suspends a Request

```
PIN User          Frontend            Backend           Database
   │               (My Requests)      (Controller)      (PostgreSQL)
   │                  │                   │                  │
   │  (1) View requests list              │                  │
   │  [Active Request 1]                  │                  │
   │  [Active Request 2]                  │                  │
   ├─────────────────>│                   │                  │
   │                  │                   │                  │
   │  (2) Click "Suspend" on Request 1    │                  │
   ├─────────────────>│                   │                  │
   │                  │  (3) Show confirm │                  │
   │                  │  "Are you sure?"  │                  │
   │                  │  [Yes] [Cancel]   │                  │
   │                  │                   │                  │
   │  (4) Confirm     │                   │                  │
   ├─────────────────>│                   │                  │
   │                  │  (5) API Call    │                  │
   │                  │  PUT /requests/1 │                  │
   │                  │  {status: SUSPENDED}               │
   │                  ├──────────────────>│                  │
   │                  │                   │ (6) Authorize  │
   │                  │                   │  Verify owner  │
   │                  │                   │                  │
   │                  │                   │ (7) Call Entity
   │                  │                   │  suspend_request
   │                  │                   ├─────────────────>│
   │                  │                   │                  │
   │                  │                   │ (8) UPDATE ...  │
   │                  │                   │  status=SUSPENDED
   │                  │                   │  suspended_at   │
   │                  │                   │                  │
   │                  │  (9) 200 OK      │                  │
   │                  │<──────────────────┤                  │
   │                  │                   │                  │
   │  (10) "Request suspended"            │                  │
   │<─────────────────┤                   │                  │
   │  Request moves to inactive list      │                  │
```

---

## 🏗️ BCE Class Diagram

### Layer Structure

```
┌──────────────────────────────────────────────────────────────┐
│ BOUNDARY LAYER (HTTP/Frontend Interface)                    │
│                                                              │
│  ┌─────────────────────┐    ┌──────────────────────────┐   │
│  │ PIN Dashboard       │    │ CSR Dashboard            │   │
│  │ (Frontend Component)│    │ (Frontend Component)     │   │
│  │                     │    │                          │   │
│  │ Features:          │    │ Features:                │   │
│  │ - Create request   │    │ - Search requests        │   │
│  │ - View requests    │    │ - View request details   │   │
│  │ - Update request   │    │ - Shortlist request      │   │
│  │ - Suspend request  │    │ - View shortlist         │   │
│  │ - Search requests  │    │ - Search shortlist       │   │
│  │ - Filter requests  │    │ - Filter shortlist       │   │
│  └─────────────────────┘    └──────────────────────────┘   │
│           │                           │                     │
│           │ HTTP Requests             │                     │
│           └───────────┬───────────────┘                     │
│                       │                                     │
│           ┌───────────▼────────────┐                       │
│           │ Request Controllers    │                       │
│           │ (BOUNDARY Layer)       │                       │
│           │                        │                       │
│           │ - Create Request       │                       │
│           │ - Get Requests         │                       │
│           │ - Update Request       │                       │
│           │ - Suspend Request      │                       │
│           │ - Search Requests      │                       │
│           │ - Filter Requests      │                       │
│           └───────────┬────────────┘                       │
│                       │                                     │
│           ┌───────────▼────────────┐                       │
│           │ Shortlist Controllers  │                       │
│           │ (BOUNDARY Layer)       │                       │
│           │                        │                       │
│           │ - Add to Shortlist     │                       │
│           │ - View Shortlist       │                       │
│           │ - Search Shortlist     │                       │
│           │ - Remove from Shortlist│                       │
│           │ - Filter Shortlist     │                       │
│           └───────────┬────────────┘                       │
│                       │                                     │
└───────────────────────┼─────────────────────────────────────┘
                        │ Delegates
                        │
┌───────────────────────▼─────────────────────────────────────┐
│ CONTROL LAYER (Business Logic)                             │
│                                                              │
│  ┌─────────────────────────┐  ┌──────────────────────────┐  │
│  │ Request (@staticmethod) │  │ Shortlist (@staticmethod)│  │
│  │                         │  │                          │  │
│  │ Methods:               │  │ Methods:                 │  │
│  │ + create_request()     │  │ + add_to_shortlist()     │  │
│  │ + get_user_requests()  │  │ + get_shortlist()        │  │
│  │ + update_request()     │  │ + search_shortlist()     │  │
│  │ + suspend_request()    │  │ + filter_shortlist()     │  │
│  │ + search_requests()    │  │ + remove_from_shortlist()│  │
│  │ + get_request_by_id()  │  │ + get_shortlist_stats()  │  │
│  │ + validate_request()   │  │ + mark_completed()       │  │
│  │                        │  │                          │  │
│  │ Logic:                │  │ Logic:                   │  │
│  │ - Verify PIN owns     │  │ - Verify CSR exists      │  │
│  │ - Validate data       │  │ - Check request exists   │  │
│  │ - Check permissions   │  │ - Prevent duplicates     │  │
│  │ - Enforce rules       │  │ - Track volunteering     │  │
│  │ - Format responses    │  │ - Update metrics         │  │
│  └─────────────────────────┘  └──────────────────────────┘  │
│                                                              │
└───────────┬──────────────────────────────────┬───────────────┘
            │ Calls Entity Methods             │
            │                                  │
┌───────────▼──────────────────────────────────▼───────────────┐
│ ENTITY LAYER (Database Operations)                          │
│                                                              │
│  ┌─────────────────────────────┐                            │
│  │ Request (ENTITY)            │                            │
│  │ Location: src/entity/       │                            │
│  │           request.py         │                            │
│  │                             │                            │
│  │ Database Methods:            │                            │
│  │ + insert_request(data)       │                            │
│  │ + get_request_by_id(id)      │                            │
│  │ + get_requests_by_user(uid)  │                            │
│  │ + update_request(id, data)   │                            │
│  │ + search_requests(filters)   │                            │
│  │ + get_all_active_requests()  │                            │
│  │ + mark_suspended(id)         │                            │
│  │                             │                            │
│  │ SQL Operations:              │                            │
│  │ - INSERT INTO requests       │                            │
│  │ - UPDATE requests            │                            │
│  │ - SELECT * FROM requests     │                            │
│  │ - WHERE with filters         │                            │
│  └─────────────────────────────┘                            │
│                                                              │
│  ┌─────────────────────────────┐                            │
│  │ Shortlist (ENTITY)          │                            │
│  │ Location: src/entity/       │                            │
│  │           shortlist.py       │                            │
│  │                             │                            │
│  │ Database Methods:            │                            │
│  │ + insert_shortlist(data)     │                            │
│  │ + get_shortlist_by_csr(uid)  │                            │
│  │ + check_duplicate(csr, req)  │                            │
│  │ + remove_shortlist(id)       │                            │
│  │ + search_shortlist(filters)  │                            │
│  │ + update_shortlist_status()  │                            │
│  │ + get_shortlist_by_status()  │                            │
│  │                             │                            │
│  │ SQL Operations:              │                            │
│  │ - INSERT INTO shortlist      │                            │
│  │ - DELETE FROM shortlist      │                            │
│  │ - SELECT * FROM shortlist    │                            │
│  │ - WHERE with filters         │                            │
│  └─────────────────────────────┘                            │
│                                                              │
└───────────┬──────────────────────────────────┬───────────────┘
            │ SQL Queries                      │
            │                                  │
            ▼                                  ▼
   ┌──────────────────────────────────────────────┐
   │   PostgreSQL Database (Supabase)             │
   │                                              │
   │ Tables:                                      │
   │  - requests (NEW)                            │
   │  - shortlist (NEW)                           │
   │  - request_categories (NEW - Lookup)         │
   │  - service_types (NEW - Lookup)              │
   │  - request_status_history (NEW - Audit)      │
   │  - users (EXISTING)                          │
   │                                              │
   └──────────────────────────────────────────────┘
```

---

## 📁 File Structure Plan

```
src/
├── controller/
│   ├── request/                    (NEW)
│   │   ├── __init__.py
│   │   ├── create_request_controller.py
│   │   ├── get_request_controller.py
│   │   ├── update_request_controller.py
│   │   ├── search_request_controller.py
│   │   └── suspend_request_controller.py
│   │
│   └── shortlist/                  (NEW)
│       ├── __init__.py
│       ├── create_shortlist_controller.py
│       ├── get_shortlist_controller.py
│       ├── search_shortlist_controller.py
│       └── remove_shortlist_controller.py
│
├── entity/
│   ├── request.py                  (NEW)
│   ├── shortlist.py                (NEW)
│   ├── request_category.py         (NEW)
│   ├── service_type.py             (NEW)
│   └── [existing files]
│
├── app/
│   ├── pin/
│   │   ├── page.js                 (NEW - PIN Dashboard)
│   │   └── [sub-pages]
│   │
│   ├── csr/
│   │   ├── page.js                 (EXISTING - Update to CSR Dashboard)
│   │   └── [sub-pages]
│   │
│   └── components/
│       ├── Header.js               (EXISTING)
│       ├── Alert.js                (EXISTING)
│       ├── RequestCard.js           (NEW)
│       ├── RequestForm.js           (NEW)
│       ├── ShortlistCard.js         (NEW)
│       ├── SearchBar.js             (NEW)
│       └── FilterPanel.js           (NEW)
│
└── utils/
    ├── validators.py               (EXISTING - Add request validators)
    └── request_helpers.py           (NEW)
```

---

## 🔑 Key Entities & Operations

### Request Entity

```
Request {
  id: UUID
  pin_user_id: UUID (FK)
  title: string
  description: string
  category: string (ENUM: Food, Medical, Housing, etc.)
  status: string (ENUM: ACTIVE, SUSPENDED, FULFILLED, CANCELLED)
  priority: string (ENUM: LOW, MEDIUM, HIGH, URGENT)
  location_city: string
  location_address: string
  service_type: string
  requested_by_date: date
  created_at: timestamp
  updated_at: timestamp
  fulfilled_at: timestamp (nullable)
  suspended_at: timestamp (nullable)
  contact_number: string
  is_archived: boolean
}

CRUD Operations:
✓ CREATE (PIN creates request)
✓ READ (PIN/CSR views requests)
✓ UPDATE (PIN updates own request)
✓ SUSPEND (PIN marks request as no longer relevant)
✓ SEARCH (PIN/CSR search by keyword/category)
✓ FILTER (PIN/CSR filter by status/priority)
```

### Shortlist Entity

```
Shortlist {
  id: UUID
  csr_user_id: UUID (FK)
  request_id: UUID (FK)
  status: string (ENUM: SHORTLISTED, IN_PROGRESS, COMPLETED, DECLINED)
  shortlisted_at: timestamp
  notes: text
  volunteered_hours: decimal
  completion_date: timestamp (nullable)
  feedback_from_pin: text (nullable)
  created_at: timestamp
  updated_at: timestamp
}

CRUD Operations:
✓ CREATE (CSR shortlists request)
✓ READ (CSR views shortlist)
✓ UPDATE (CSR updates status/notes)
✓ DELETE (CSR removes from shortlist)
✓ SEARCH (CSR searches shortlist)
✓ FILTER (CSR filters by service_type/date)
```

---

## 🔐 Authorization & Permissions

### PIN Permissions
- ✅ Create request (own data only)
- ✅ Read own requests
- ✅ Update own requests (if ACTIVE)
- ✅ Suspend own requests
- ✅ Cannot view other PIN's requests
- ❌ Cannot delete requests (only suspend/archive)
- ❌ Cannot access shortlist

### CSR Rep Permissions
- ✅ Search all ACTIVE requests
- ✅ View request details
- ✅ Shortlist requests
- ✅ View own shortlist
- ✅ Search own shortlist
- ✅ Update shortlist status
- ✅ Remove from shortlist
- ❌ Cannot create/update/delete requests
- ❌ Cannot view other CSR's shortlist

### Admin Permissions
- ✅ Full access to all requests
- ✅ Full access to all shortlists
- ✅ Delete requests
- ✅ View analytics/reports

---

## 🔍 Search & Filter Implementation

### PIN Search Requests
```
Query Parameters:
- keyword: string (searches title, description)
- category: string (exact match: Food, Medical, etc.)
- status: string (ACTIVE, SUSPENDED, FULFILLED)
- priority: string (LOW, MEDIUM, HIGH, URGENT)
- date_from: date
- date_to: date

Example: 
GET /api/requests?keyword=food&category=Food&status=ACTIVE
```

### CSR Search Requests
```
Query Parameters:
- keyword: string (searches title, description)
- category: string
- service_type: string (Delivery, Accompaniment, etc.)
- priority: string
- location_city: string
- sort_by: string (created_at, requested_by_date, priority)

Example:
GET /api/requests/available?keyword=help&category=Food&location_city=Bangkok
```

### CSR Filter Shortlist
```
Query Parameters:
- service_type: string
- date_from: date
- date_to: date
- status: string (SHORTLISTED, IN_PROGRESS, COMPLETED)

Example:
GET /api/shortlist?service_type=Delivery&date_from=2025-10-01&date_to=2025-10-31
```

---

## 🚀 Implementation Phases

### Phase 1: Backend Foundation
- [ ] Create database tables (requests, shortlist, lookups)
- [ ] Create Request entity class
- [ ] Create Shortlist entity class
- [ ] Create Request CRUD controllers
- [ ] Create Shortlist controllers
- [ ] Add validators and middleware

### Phase 2: PIN Features
- [ ] PIN dashboard page
- [ ] Create request form
- [ ] View requests page
- [ ] Update request form
- [ ] Suspend request functionality
- [ ] Search & filter requests

### Phase 3: CSR Features
- [ ] Update CSR dashboard
- [ ] Search volunteering opportunities
- [ ] View request details modal
- [ ] Shortlist functionality
- [ ] View shortlist page
- [ ] Filter & search shortlist

### Phase 4: Polish & Testing
- [ ] UI/UX improvements
- [ ] Unit tests
- [ ] Integration tests
- [ ] Performance optimization
- [ ] Documentation

---

## ⚠️ Important Notes

### Data Integrity
1. **Unique Shortlist**: CSR cannot shortlist same request twice (UNIQUE constraint)
2. **Ownership Verification**: Always verify PIN owns request before update
3. **Status Transitions**: Only certain status transitions allowed
4. **Soft Delete**: Archive requests instead of hard delete (data retention)

### Performance Considerations
1. **Indexes**: Created on frequently searched columns
2. **Pagination**: Implement for large result sets
3. **Caching**: Cache categories/service types lookup tables
4. **Query Optimization**: Use appropriate WHERE clauses with filters

### Security
1. **Row-Level Security**: Ensure users only access their own data
2. **SQL Injection**: Use parameterized queries
3. **Validation**: Validate all input data
4. **Authorization**: Check user role for each operation

---

## 📝 Questions & Clarifications

**Anything confusing?** Let me know:
1. Are category/service_type enums OK or should they be more flexible?
2. Should shortlist include feedback from CSR too (not just PIN)?
3. Should we track volunteer hours for metrics?
4. Is suspending different from fulfilling? (Currently separate statuses)
5. Should PINs be able to see who shortlisted them?
6. Need image uploads for requests?

---

**Status:** Design Complete - Ready for Implementation  
**Next Step:** Await feedback, then proceed to Phase 1 (Database Setup)
