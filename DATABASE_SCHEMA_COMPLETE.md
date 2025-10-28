# 📊 Complete Database Schema with PIN/CSR Relationships

**Last Updated:** October 28, 2025  
**Status:** Active in Supabase PostgreSQL

---

## 🔵 CURRENT TABLES (Existing)

### 1. ROLES Table
**Purpose:** Stores available user roles in the system  
**Location:** Supabase PostgreSQL  
**Record Count:** 4 roles  

```sql
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL,        -- e.g., "User Admin", "PIN", "CSR Rep"
    role_code VARCHAR(20) UNIQUE,                 -- e.g., "USER_ADMIN", "PIN", "CSR_REP"
    description TEXT,                             -- Role description
    dashboard_route VARCHAR(100),                 -- Route: "/admin", "/pin", "/csr", "/platform"
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Current Roles:**
| id | role_name | role_code | dashboard_route | Description |
|----|-----------|-----------|-----------------|-------------|
| 1 | User Admin | USER_ADMIN | /admin | System administrator |
| 2 | PIN | PIN | /pin | Person in need user |
| 3 | CSR Rep | CSR_REP | /csr | Customer service representative |
| 4 | Platform Management | PLATFORM_MGMT | /platform | Platform administrator |

**Used By:** Users table (foreign key)

---

### 2. USERS Table
**Purpose:** Stores all user accounts and authentication data  
**Location:** Supabase PostgreSQL  
**Relationship:** ❌ **NOT** referenced by user_details (doesn't exist)  

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,        -- e.g., "admin1"
    password VARCHAR(255) NOT NULL,              -- Hashed with werkzeug
    email VARCHAR(100) UNIQUE NOT NULL,          -- User email
    full_name VARCHAR(100),                      -- User's full name
    role_id INTEGER NOT NULL,                    -- Foreign key → roles.id
    is_active BOOLEAN DEFAULT TRUE,              -- Account status
    last_login TIMESTAMP,                        -- Last login timestamp
    created_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_user_role FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
);
```

**Sample Data:**
| id | username | email | full_name | role_id | is_active | created_at |
|----|----|-----|----------|---------|-----------|-----------|
| 1 | admin1 | admin@example.com | Admin User | 1 | true | 2024-01-15 |
| 2 | pin_user1 | pin@example.com | PIN User 1 | 2 | true | 2024-01-20 |
| 3 | csr_rep1 | csr@example.com | CSR Rep 1 | 3 | true | 2024-01-22 |
| 4 | platform_admin | platform@example.com | Platform Admin | 4 | true | 2024-01-25 |

**Fields Explanation:**
- `id`: Auto-incremented primary key (unique identifier)
- `username`: Must be unique across system
- `email`: Must be unique across system
- `role_id`: Links to `roles.id` (1=Admin, 2=PIN, 3=CSR, 4=Platform)
- `is_active`: Can suspend accounts by setting to false
- `last_login`: Auto-updated on successful authentication
- `password`: Hashed using werkzeug.security (never stored plaintext)

**Foreign Key Constraint:**
```
❌ ON DELETE CASCADE → If role is deleted, all users with that role are deleted
```

---

### 3. USER_DETAILS Table ❌
**Status:** DOES NOT EXIST (mentioned in docs but not in database)

---

## 🔴 NEW TABLES (PIN/CSR System)

### 4. REQUESTS Table
**Purpose:** Stores PIN requests for help/services  
**Owner:** PIN users can create/update their own requests  
**Accessed By:** CSR reps can search and view available requests  

```sql
CREATE TABLE requests (
    id SERIAL PRIMARY KEY,
    pin_user_id INTEGER NOT NULL,                -- FK → users.id (PIN role owner)
    title VARCHAR(255) NOT NULL,                 -- Request title
    description TEXT NOT NULL,                   -- Detailed description
    category VARCHAR(50),                        -- e.g., "Food", "Medical", "Housing"
    service_type VARCHAR(50),                    -- e.g., "Delivery", "In-person Help"
    priority VARCHAR(20) DEFAULT 'MEDIUM',       -- LOW, MEDIUM, HIGH, URGENT
    location_city VARCHAR(100),                  -- City/location where help needed
    location_detail TEXT,                        -- Detailed location description
    status VARCHAR(20) DEFAULT 'ACTIVE',         -- ACTIVE, SUSPENDED, FULFILLED, CANCELLED
    requested_by_date DATE,                      -- When help is needed by
    fulfilled_at TIMESTAMP,                      -- When request was fulfilled
    suspended_at TIMESTAMP,                      -- When request was suspended
    is_archived BOOLEAN DEFAULT FALSE,           -- For soft deletes
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_request_pin_user FOREIGN KEY (pin_user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT check_status CHECK (status IN ('ACTIVE', 'SUSPENDED', 'FULFILLED', 'CANCELLED')),
    CONSTRAINT check_priority CHECK (priority IN ('LOW', 'MEDIUM', 'HIGH', 'URGENT'))
);

-- Indexes for performance
CREATE INDEX idx_requests_pin_user_id ON requests(pin_user_id);
CREATE INDEX idx_requests_status ON requests(status);
CREATE INDEX idx_requests_category ON requests(category);
CREATE INDEX idx_requests_created_at ON requests(created_at DESC);
CREATE INDEX idx_requests_service_type ON requests(service_type);
```

**ER Relationship:**
```
┌─────────────┐
│   USERS     │
│   id (PK)   │
│   ...       │
│   role_id   │ ──→ [PIN = role_id 2]
└─────────────┘
      ▲
      │ FK: pin_user_id
      │
┌─────────────┐
│  REQUESTS   │
│  id (PK)    │
│  pin_user_id│ ┐
│  ...        │ ├── Only created by PIN users (role_id = 2)
└─────────────┘ ┘
```

**Sample Data:**
| id | pin_user_id | title | category | status | priority | created_at |
|----|----|-----|---------|---------|---------|-----------|
| 1 | 2 | Need grocery delivery | Food | ACTIVE | HIGH | 2024-10-20 |
| 2 | 2 | Medical appointment transport | Medical | ACTIVE | URGENT | 2024-10-21 |

---

### 5. SHORTLIST Table
**Purpose:** CSR reps save/shortlist PIN requests they want to help with  
**Owner:** CSR reps add requests to their shortlist  

```sql
CREATE TABLE shortlist (
    id SERIAL PRIMARY KEY,
    csr_user_id INTEGER NOT NULL,                -- FK → users.id (CSR role owner)
    request_id INTEGER NOT NULL,                 -- FK → requests.id
    status VARCHAR(20) DEFAULT 'SHORTLISTED',   -- SHORTLISTED, IN_PROGRESS, COMPLETED, DECLINED
    notes TEXT,                                  -- CSR's notes about the request
    volunteered_hours DECIMAL(5, 2),            -- Hours volunteered
    completion_date TIMESTAMP,                   -- When help was provided
    feedback_from_pin TEXT,                      -- PIN feedback to CSR
    shortlisted_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_shortlist_csr_user FOREIGN KEY (csr_user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_shortlist_request FOREIGN KEY (request_id) REFERENCES requests(id) ON DELETE CASCADE,
    CONSTRAINT unique_csr_request UNIQUE(csr_user_id, request_id),  -- One shortlist per CSR+Request
    CONSTRAINT check_shortlist_status CHECK (status IN ('SHORTLISTED', 'IN_PROGRESS', 'COMPLETED', 'DECLINED'))
);

-- Indexes for performance
CREATE INDEX idx_shortlist_csr_user_id ON shortlist(csr_user_id);
CREATE INDEX idx_shortlist_request_id ON shortlist(request_id);
CREATE INDEX idx_shortlist_status ON shortlist(status);
CREATE INDEX idx_shortlist_shortlisted_at ON shortlist(shortlisted_at DESC);
CREATE INDEX idx_shortlist_csr_request ON shortlist(csr_user_id, request_id);
```

**ER Relationship:**
```
┌─────────────┐
│   USERS     │
│   id (PK)   │
│   ...       │
│   role_id   │ ──→ [CSR = role_id 3]
└─────────────┘
      ▲
      │ FK: csr_user_id
      │
┌──────────────────┐
│   SHORTLIST      │
│   id (PK)        │
│   csr_user_id    │ ┐
│   request_id     │ ├── CSR saves/tracks requests
│   status         │ │   they want to help with
│   ...            │ ┘
└──────────────────┘
      │
      │ FK: request_id
      ▼
┌─────────────┐
│  REQUESTS   │
│  id (PK)    │
│  ...        │
└─────────────┘
```

**Sample Data:**
| id | csr_user_id | request_id | status | shortlisted_at | volunteered_hours |
|----|----|----|----|----------|-------|
| 1 | 3 | 1 | IN_PROGRESS | 2024-10-20 15:30:00 | 2.5 |
| 2 | 3 | 2 | COMPLETED | 2024-10-21 09:00:00 | 1.0 |

---

### 6. REQUEST_CATEGORIES Table (Lookup)
**Purpose:** Reference table for request categories  

```sql
CREATE TABLE request_categories (
    id SERIAL PRIMARY KEY,
    category_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    icon VARCHAR(50),                            -- For UI display
    created_at TIMESTAMP DEFAULT NOW()
);

-- Sample data
INSERT INTO request_categories (category_name, description) VALUES
('Food', 'Food and grocery assistance'),
('Medical', 'Medical services and support'),
('Housing', 'Housing and accommodation help'),
('Transportation', 'Transport and travel assistance'),
('Financial', 'Financial guidance and support'),
('Companionship', 'Social and emotional support'),
('Education', 'Education and tutoring services'),
('Employment', 'Job and employment assistance');
```

---

### 7. SERVICE_TYPES Table (Lookup)
**Purpose:** Reference table for service types  

```sql
CREATE TABLE service_types (
    id SERIAL PRIMARY KEY,
    service_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Sample data
INSERT INTO service_types (service_name, description) VALUES
('Delivery', 'Item or package delivery'),
('In-person Help', 'On-site physical assistance'),
('Accompaniment', 'Going with person to location'),
('Companionship', 'Social interaction and presence'),
('Consultation', 'Advice and guidance'),
('Professional Service', 'Specialized professional help');
```

---

### 8. REQUEST_STATUS_HISTORY Table (Audit)
**Purpose:** Track all status changes for audit trail and analytics  

```sql
CREATE TABLE request_status_history (
    id SERIAL PRIMARY KEY,
    request_id INTEGER NOT NULL,                 -- FK → requests.id
    old_status VARCHAR(20),                      -- Previous status
    new_status VARCHAR(20) NOT NULL,             -- New status
    changed_by INTEGER,                          -- FK → users.id (who changed it)
    reason TEXT,                                 -- Why was it changed
    changed_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_history_request FOREIGN KEY (request_id) REFERENCES requests(id) ON DELETE CASCADE,
    CONSTRAINT fk_history_changed_by FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_request_status_history_request_id ON request_status_history(request_id);
CREATE INDEX idx_request_status_history_changed_at ON request_status_history(changed_at DESC);
```

---

## 🔗 Complete Relationship Diagram

```
                        ┌──────────────┐
                        │    ROLES     │
                        │  id (PK)     │
                        │  role_name   │
                        │  created_at  │
                        └──────────────┘
                               ▲
                               │ (FK)
                               │
                        ┌──────────────┐
                        │    USERS     │
                        │  id (PK)     │
                        │  username    │
                        │  role_id     │
                        │  email       │
                        │  is_active   │
                        └──────────────┘
                         ▲      ▲      ▲
                   ┌─────┘      │      └─────┐
            (FK)   │            │            │   (FK)
                   │            │            │
        ┌────────────────┐  ┌──────────────┐  ┌──────────────┐
        │   REQUESTS     │  │ REQUEST_     │  │  SHORTLIST   │
        │  id (PK)       │  │ STATUS_      │  │  id (PK)     │
        │  pin_user_id   │◄─┤ HISTORY      │  │  csr_user_id │
        │  title         │  │  id (PK)     │  │  request_id  │
        │  category      │  │  request_id  │  │  status      │
        │  status        │  │  new_status  │  │  notes       │
        │  created_at    │  │  changed_by  │  │  created_at  │
        └────────────────┘  │  changed_at  │  └──────────────┘
                            └──────────────┘
                                   ▲
                                   │
                         ┌─────────┴──────────┐
                         │                    │
            ┌─────────────────────┐  ┌────────────────────┐
            │REQUEST_CATEGORIES   │  │  SERVICE_TYPES     │
            │  id (PK)            │  │  id (PK)           │
            │  category_name      │  │  service_name      │
            └─────────────────────┘  └────────────────────┘
                   ▲                         ▲
                   │                         │
         (indexed on)               (indexed on)
                   │                         │
            REQUESTS.category    REQUESTS.service_type
```

---

## 🔐 Authorization & Foreign Key Constraints

### PIN User (role_id = 2)
```sql
-- Can only create requests where pin_user_id = their_user_id
SELECT * FROM requests 
WHERE pin_user_id = {authenticated_user_id} 
AND status IN ('ACTIVE', 'SUSPENDED', 'FULFILLED')

-- Update own request
UPDATE requests 
SET title = ?, description = ?, category = ?
WHERE id = {request_id} 
AND pin_user_id = {authenticated_user_id}
AND status = 'ACTIVE'  -- Can only edit ACTIVE requests

-- Suspend own request
UPDATE requests 
SET status = 'SUSPENDED', suspended_at = NOW()
WHERE id = {request_id}
AND pin_user_id = {authenticated_user_id}
```

### CSR Rep (role_id = 3)
```sql
-- Search all ACTIVE requests
SELECT * FROM requests 
WHERE status = 'ACTIVE'
ORDER BY priority DESC, created_at DESC

-- Add to shortlist (prevents duplicates via UNIQUE constraint)
INSERT INTO shortlist (csr_user_id, request_id, status)
VALUES ({csr_user_id}, {request_id}, 'SHORTLISTED')
-- Fails if already shortlisted by this CSR

-- View own shortlist
SELECT s.*, r.* FROM shortlist s
JOIN requests r ON s.request_id = r.id
WHERE s.csr_user_id = {authenticated_user_id}
ORDER BY s.shortlisted_at DESC
```

---

## 📊 Query Examples with Relationships

### 1. PIN User Views Their Requests
```sql
SELECT 
    r.id,
    r.title,
    r.description,
    r.category,
    r.status,
    COUNT(s.id) AS csr_volunteers_count
FROM requests r
LEFT JOIN shortlist s ON r.id = s.request_id 
    AND s.status IN ('IN_PROGRESS', 'COMPLETED')
WHERE r.pin_user_id = 2
AND r.status IN ('ACTIVE', 'SUSPENDED')
GROUP BY r.id
ORDER BY r.created_at DESC
```

### 2. CSR Rep Views Available Requests
```sql
SELECT 
    r.id,
    r.title,
    r.description,
    u.full_name AS pin_name,
    u.email AS pin_email,
    r.category,
    r.priority,
    r.service_type,
    CASE 
        WHEN s.id IS NOT NULL THEN 'Already Shortlisted'
        ELSE 'Available'
    END AS shortlist_status
FROM requests r
JOIN users u ON r.pin_user_id = u.id
LEFT JOIN shortlist s ON r.id = s.request_id 
    AND s.csr_user_id = 3
WHERE r.status = 'ACTIVE'
AND u.is_active = TRUE
ORDER BY r.priority DESC, r.created_at DESC
```

### 3. CSR Rep Views Their Shortlist with Progress
```sql
SELECT 
    s.id AS shortlist_id,
    r.id AS request_id,
    r.title,
    u.full_name AS pin_name,
    r.category,
    s.status,
    s.volunteered_hours,
    s.shortlisted_at,
    s.completion_date,
    sh.new_status AS latest_status_change,
    sh.changed_at AS status_changed_at
FROM shortlist s
JOIN requests r ON s.request_id = r.id
JOIN users u ON r.pin_user_id = u.id
LEFT JOIN request_status_history sh ON r.id = sh.request_id
WHERE s.csr_user_id = 3
ORDER BY 
    CASE s.status 
        WHEN 'IN_PROGRESS' THEN 1
        WHEN 'SHORTLISTED' THEN 2
        WHEN 'COMPLETED' THEN 3
        WHEN 'DECLINED' THEN 4
    END,
    s.shortlisted_at DESC
```

### 4. Admin Views System Statistics
```sql
SELECT 
    'Requests' AS metric,
    COUNT(*) AS total,
    SUM(CASE WHEN status = 'ACTIVE' THEN 1 ELSE 0 END) AS active,
    SUM(CASE WHEN status = 'FULFILLED' THEN 1 ELSE 0 END) AS fulfilled,
    SUM(CASE WHEN status = 'SUSPENDED' THEN 1 ELSE 0 END) AS suspended
FROM requests

UNION ALL

SELECT 
    'Shortlists' AS metric,
    COUNT(*) AS total,
    SUM(CASE WHEN status = 'IN_PROGRESS' THEN 1 ELSE 0 END) AS active,
    SUM(CASE WHEN status = 'COMPLETED' THEN 1 ELSE 0 END) AS fulfilled,
    SUM(CASE WHEN status = 'DECLINED' THEN 1 ELSE 0 END) AS suspended
FROM shortlist
```

---

## 📋 Summary of Relationships

| From Table | To Table | Foreign Key | Relationship | On Delete |
|-----------|----------|-----------|-------------|-----------|
| users | roles | role_id → id | Many-to-One | CASCADE |
| requests | users | pin_user_id → id | Many-to-One | CASCADE |
| requests | request_categories | category | Indexed lookup | None |
| requests | service_types | service_type | Indexed lookup | None |
| shortlist | users | csr_user_id → id | Many-to-One | CASCADE |
| shortlist | requests | request_id → id | Many-to-One | CASCADE |
| request_status_history | requests | request_id → id | Many-to-One | CASCADE |
| request_status_history | users | changed_by → id | Many-to-One | SET NULL |

---

## ✅ Data Integrity Checks

```python
# Python validation before insert
def validate_request_creation(data, authenticated_user_id):
    """Validate request creation"""
    errors = []
    
    # 1. User must be PIN role
    user = User.get_user_by_id(authenticated_user_id)
    if user['role_id'] != 2:  # PIN role_id = 2
        errors.append("Only PIN users can create requests")
    
    # 2. Title and description required
    if not data.get('title'):
        errors.append("Title is required")
    if not data.get('description'):
        errors.append("Description is required")
    
    # 3. Category must exist
    category = check_category_exists(data.get('category'))
    if not category:
        errors.append(f"Category '{data.get('category')}' does not exist")
    
    # 4. Service type must exist (if provided)
    if data.get('service_type'):
        service = check_service_type_exists(data.get('service_type'))
        if not service:
            errors.append(f"Service type '{data.get('service_type')}' does not exist")
    
    # 5. Priority must be valid
    if data.get('priority') not in ['LOW', 'MEDIUM', 'HIGH', 'URGENT']:
        errors.append("Priority must be LOW, MEDIUM, HIGH, or URGENT")
    
    return len(errors) == 0, errors
```

---

## 🔄 Cascade Delete Behavior

**Scenario: If a PIN user is deleted (or their account suspended):**
```
1. DELETE FROM users WHERE id = 2 (PIN user)
   ↓
2. ALL requests created by this PIN user are deleted (CASCADE)
   ↓
3. ALL shortlist entries pointing to those requests are deleted (CASCADE)
   ↓
4. ALL request_status_history records for those requests are deleted (CASCADE)
```

**Scenario: If a CSR user is deleted:**
```
1. DELETE FROM users WHERE id = 3 (CSR user)
   ↓
2. ALL shortlist entries created by this CSR are deleted (CASCADE)
   ↓
3. Requests remain (CSR didn't create them, just shortlisted)
   ↓
4. request_status_history for changes by this CSR gets changed_by = NULL
```

---

## 🚀 Next Steps

**Phase 1 - Database Setup:**
- [ ] Create requests table with indexes
- [ ] Create shortlist table with UNIQUE constraint
- [ ] Create lookup tables (categories, service_types)
- [ ] Create audit table (request_status_history)
- [ ] Test CASCADE deletes
- [ ] Seed lookup tables with sample data

**Phase 2 - Backend Implementation:**
- [ ] Create Request entity class with all CRUD methods
- [ ] Create Shortlist entity class with all CRUD methods
- [ ] Create request controllers (create, get, update, search, suspend)
- [ ] Create shortlist controllers (add, remove, search, filter)
- [ ] Add authorization checks in each controller
- [ ] Add validators for all inputs

**Phase 3 - Frontend Implementation:**
- [ ] Create PIN dashboard to view/create/update requests
- [ ] Create CSR dashboard to search requests and shortlist
- [ ] Create request detail view
- [ ] Create shortlist management interface
- [ ] Add search and filter functionality

**Phase 4 - Testing & Polish:**
- [ ] Test all CRUD operations
- [ ] Test CASCADE deletes
- [ ] Test authorization (PIN vs CSR)
- [ ] Test search and filters
- [ ] Performance optimization
- [ ] Error handling

---

**Ready to proceed with Phase 1 database creation?** 🚀
