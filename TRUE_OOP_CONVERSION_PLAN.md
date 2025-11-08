# TRUE OOP Conversion Plan - Strategic Approach

## Lecturer's Requirement Analysis

> "At least the backend/middleware needs to be object oriented - the main code that controls/runs all application logic and hold data in memory"

**What this means:**
- ✅ Backend (Python entities + controllers) must be OOP
- ✅ Application logic must run through objects
- ✅ Data must be held in memory as object state (instance variables)
- ❌ Static methods for business logic = NOT OOP
- ❌ No objects holding state = NOT OOP

**Current state: DOES NOT MEET REQUIREMENT**
- Controllers: All static methods (no objects, no state)
- Entities: Static methods do all work (wrappers unused)

**Target state: MEETS REQUIREMENT**
- Controllers: Instance methods with state
- Entities: Instance methods do all work
- Data held in memory as objects

---

## Timeline: 3-4 Days

### Day 1: Entity Conversion (User, Role)
- Convert User entity to true OOP
- Convert Role entity to true OOP
- Test basic CRUD operations

### Day 2: Entity Conversion (Request, Shortlist, Profile)
- Convert Request entity to true OOP
- Convert Shortlist entity to true OOP
- Convert Profile entity to true OOP
- Test all entity operations

### Day 3: Controller Conversion (6-8 key controllers)
- Convert CreateUserAccountController
- Convert CreateNewPINRequestController
- Convert AddToShortlistController
- Convert UpdateUserAccountController
- Convert UpdatePINRequestController
- Convert LoginController
- Test all converted controllers

### Day 4: Integration Testing & Fixes
- Run all tests
- Test frontend integration
- Fix any bugs
- Verify everything works

---

## Phase 1: Entity Conversion Strategy

### Current Entity Structure (WRAPPER - NOT OOP)

```python
class User:
    # Lines 1-200: OOP wrapper (UNUSED)
    def __init__(self, user_id=None):
        self.id = user_id
        self.username = None
    
    def save(self):
        """WRAPPER - just calls static method"""
        return User.create_user(self.to_dict())  # ❌ Not real OOP
    
    # Lines 200-800: Static methods (DOING ALL WORK)
    @staticmethod
    def create_user(username, password, email, full_name, role_id):
        """❌ Static method - not OOP"""
        supabase = get_supabase()
        # ... 100 lines of actual logic
        result = supabase.table('users').insert({...}).execute()
        return result.data[0]
    
    @staticmethod
    def get_user_by_id(user_id):
        """❌ Static method - not OOP"""
        supabase = get_supabase()
        result = supabase.table('users').select('*').eq('id', user_id).execute()
        return result.data[0] if result.data else None
```

### Target Entity Structure (TRUE OOP)

```python
class User:
    """
    User Entity - TRUE OOP Implementation
    Holds user data in memory and performs operations on itself
    """
    
    def __init__(self, user_id=None):
        """Initialize user object - holds data in memory"""
        # Instance variables (data in memory)
        self.id = user_id
        self.username = None
        self.password = None
        self.email = None
        self.full_name = None
        self.role_id = None
        self.is_active = True
        self.last_login = None
        self.created_at = None
        self.role = None  # Related Role object
        
        # Load from database if ID provided
        if user_id:
            self._load_from_database()
    
    def _load_from_database(self):
        """Private method - load user data into memory"""
        supabase = get_supabase()
        result = supabase.table('users')\
            .select('*, roles(*)')\
            .eq('id', self.id)\
            .execute()
        
        if result.data:
            self._populate_from_dict(result.data[0])
    
    def _populate_from_dict(self, data):
        """Private method - populate instance variables"""
        self.id = data.get('id')
        self.username = data.get('username')
        self.password = data.get('password')
        self.email = data.get('email')
        self.full_name = data.get('full_name')
        self.role_id = data.get('role_id')
        self.is_active = data.get('is_active', True)
        self.last_login = data.get('last_login')
        self.created_at = data.get('created_at')
        
        # Load related role object
        if data.get('roles'):
            self.role = Role(role_data=data['roles'])
    
    def validate(self):
        """✅ Instance method - validate object state"""
        errors = []
        
        if not self.username or len(self.username) < 3:
            errors.append('Username must be at least 3 characters')
        
        if not self.email or '@' not in self.email:
            errors.append('Invalid email format')
        
        if not self.password or len(self.password) < 8:
            errors.append('Password must be at least 8 characters')
        
        if not self.full_name:
            errors.append('Full name is required')
        
        if not self.role_id:
            errors.append('Role is required')
        
        return len(errors) == 0, errors
    
    def check_uniqueness(self):
        """✅ Instance method - check if username/email exists"""
        supabase = get_supabase()
        
        # Check username (skip if updating existing user)
        query = supabase.table('users').select('id').eq('username', self.username)
        if self.id:
            query = query.neq('id', self.id)
        result = query.execute()
        if result.data:
            return False, 'Username already exists'
        
        # Check email
        query = supabase.table('users').select('id').eq('email', self.email)
        if self.id:
            query = query.neq('id', self.id)
        result = query.execute()
        if result.data:
            return False, 'Email already exists'
        
        return True, None
    
    def save(self):
        """✅ Instance method - DOES ALL THE WORK (not a wrapper!)"""
        # Validate
        is_valid, errors = self.validate()
        if not is_valid:
            raise ValueError('; '.join(errors))
        
        # Check uniqueness
        is_unique, error = self.check_uniqueness()
        if not is_unique:
            raise ValueError(error)
        
        supabase = get_supabase()
        
        if self.id:
            # Update existing user
            result = supabase.table('users').update({
                'username': self.username,
                'email': self.email,
                'full_name': self.full_name,
                'role_id': self.role_id,
                'is_active': self.is_active
            }).eq('id', self.id).execute()
        else:
            # Create new user
            hashed_password = hash_password(self.password)
            result = supabase.table('users').insert({
                'username': self.username,
                'password': hashed_password,
                'email': self.email,
                'full_name': self.full_name,
                'role_id': self.role_id,
                'is_active': self.is_active
            }).execute()
            
            if result.data:
                self.id = result.data[0]['id']
                self.created_at = result.data[0]['created_at']
        
        return True
    
    def delete(self):
        """✅ Instance method - delete this user"""
        if not self.id:
            raise ValueError('Cannot delete user without ID')
        
        supabase = get_supabase()
        result = supabase.table('users').delete().eq('id', self.id).execute()
        return bool(result.data)
    
    def deactivate(self):
        """✅ Instance method - deactivate this user"""
        self.is_active = False
        return self.save()
    
    def activate(self):
        """✅ Instance method - activate this user"""
        self.is_active = True
        return self.save()
    
    def update_last_login(self):
        """✅ Instance method - update last login timestamp"""
        if not self.id:
            return False
        
        supabase = get_supabase()
        result = supabase.table('users').update({
            'last_login': datetime.now().isoformat()
        }).eq('id', self.id).execute()
        
        if result.data:
            self.last_login = result.data[0]['last_login']
            return True
        return False
    
    def to_dict(self, include_password=False):
        """Convert object to dictionary"""
        user_dict = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role_id': self.role_id,
            'is_active': self.is_active,
            'last_login': self.last_login,
            'created_at': self.created_at
        }
        
        if include_password:
            user_dict['password'] = self.password
        
        if self.role:
            user_dict['role'] = self.role.to_dict()
        
        return user_dict
    
    # ========================================================================
    # FACTORY METHODS (Class methods that return objects)
    # ========================================================================
    
    @classmethod
    def find(cls, user_id):
        """✅ Factory method - returns User object"""
        return cls(user_id=user_id)
    
    @classmethod
    def find_by_username(cls, username):
        """✅ Factory method - returns User object"""
        supabase = get_supabase()
        result = supabase.table('users')\
            .select('*, roles(*)')\
            .eq('username', username)\
            .execute()
        
        if result.data:
            user = cls()
            user._populate_from_dict(result.data[0])
            return user
        return None
    
    @classmethod
    def find_by_email(cls, email):
        """✅ Factory method - returns User object"""
        supabase = get_supabase()
        result = supabase.table('users')\
            .select('*, roles(*)')\
            .eq('email', email)\
            .execute()
        
        if result.data:
            user = cls()
            user._populate_from_dict(result.data[0])
            return user
        return None
    
    @classmethod
    def all(cls, include_inactive=False):
        """✅ Factory method - returns list of User objects"""
        supabase = get_supabase()
        query = supabase.table('users').select('*, roles(*)')
        
        if not include_inactive:
            query = query.eq('is_active', True)
        
        result = query.execute()
        
        users = []
        for data in result.data:
            user = cls()
            user._populate_from_dict(data)
            users.append(user)
        
        return users
    
    @classmethod
    def by_role(cls, role_id):
        """✅ Factory method - returns list of User objects by role"""
        supabase = get_supabase()
        result = supabase.table('users')\
            .select('*, roles(*)')\
            .eq('role_id', role_id)\
            .execute()
        
        users = []
        for data in result.data:
            user = cls()
            user._populate_from_dict(data)
            users.append(user)
        
        return users
    
    # ========================================================================
    # AUTHENTICATION METHODS (Work with User objects)
    # ========================================================================
    
    def verify_password(self, password):
        """✅ Instance method - verify password for this user"""
        if not self.password:
            return False
        return verify_password(self.password, password)
    
    def set_password(self, new_password):
        """✅ Instance method - set new password for this user"""
        if len(new_password) < 8:
            raise ValueError('Password must be at least 8 characters')
        self.password = hash_password(new_password)
    
    @classmethod
    def authenticate(cls, username, password):
        """✅ Factory method - authenticate and return User object"""
        user = cls.find_by_username(username)
        if user and user.verify_password(password):
            user.update_last_login()
            return user
        return None
    
    # NO MORE @staticmethod FOR CRUD OPERATIONS!
    # All business logic goes through objects
```

---

## Phase 2: Controller Conversion Strategy

### Current Controller Structure (NOT OOP)

```python
class CreateUserAccountController:
    @staticmethod  # ❌ Not OOP - no state
    def create(data):
        """Static method - no object, no state in memory"""
        
        # Validation
        is_valid, error = validate_create_user_data(data)
        if not is_valid:
            return ResponseHelpers.error_response(error, 400)
        
        # Sanitize
        sanitized = Sanitizers.sanitize_user_data(data)
        
        # Call static method (not OOP)
        result = User.create_user(  # ❌ Static call
            username=sanitized['username'],
            password=sanitized['password'],
            email=sanitized['email'],
            full_name=sanitized['full_name'],
            role_id=sanitized['role_id']
        )
        
        # Return
        if result and 'data' in result:
            return ResponseHelpers.success_response(result['data'], 201)
        else:
            return ResponseHelpers.error_response('Failed', 400)
```

### Target Controller Structure (TRUE OOP)

```python
class CreateUserAccountController:
    """
    Create User Account Controller - TRUE OOP
    Holds request data in memory and orchestrates user creation
    """
    
    def __init__(self, request_data):
        """✅ Constructor - holds data in memory"""
        self.request_data = request_data
        self.user = None
        self.errors = []
        self.sanitized_data = {}
    
    def validate(self):
        """✅ Instance method - validate request data"""
        if not self.request_data:
            self.errors.append('Request body is required')
            return False
        
        # Check required fields
        required = ['username', 'password', 'email', 'full_name', 'role_id']
        for field in required:
            if field not in self.request_data:
                self.errors.append(f'Missing field: {field}')
        
        if self.errors:
            return False
        
        # Validate formats
        username = self.request_data['username'].strip()
        if len(username) < 3:
            self.errors.append('Username must be at least 3 characters')
        
        password = self.request_data['password']
        if len(password) < 8:
            self.errors.append('Password must be at least 8 characters')
        
        email = self.request_data['email'].strip()
        if '@' not in email:
            self.errors.append('Invalid email format')
        
        return len(self.errors) == 0
    
    def sanitize(self):
        """✅ Instance method - sanitize input data"""
        self.sanitized_data = {
            'username': self.request_data['username'].strip().lower(),
            'password': self.request_data['password'],
            'email': self.request_data['email'].strip().lower(),
            'full_name': self.request_data['full_name'].strip(),
            'role_id': int(self.request_data['role_id'])
        }
    
    def create_user_object(self):
        """✅ Instance method - create User object"""
        self.user = User()
        self.user.username = self.sanitized_data['username']
        self.user.password = self.sanitized_data['password']
        self.user.email = self.sanitized_data['email']
        self.user.full_name = self.sanitized_data['full_name']
        self.user.role_id = self.sanitized_data['role_id']
    
    def execute(self):
        """✅ Instance method - main execution logic"""
        try:
            # Step 1: Validate
            if not self.validate():
                return ResponseHelpers.error_response(
                    '; '.join(self.errors), 400
                )
            
            # Step 2: Sanitize
            self.sanitize()
            
            # Step 3: Create User object (holds data in memory)
            self.create_user_object()
            
            # Step 4: Save user (User object does the work)
            self.user.save()
            
            # Step 5: Return response
            return ResponseHelpers.success_response(
                self.user.to_dict(), 201
            )
            
        except ValueError as e:
            return ResponseHelpers.error_response(str(e), 400)
        except Exception as e:
            print(f"[ERROR] Create user failed: {str(e)}")
            return ResponseHelpers.error_response(
                'Internal server error', 500
            )
```

---

## Phase 3: API Route Updates

### Current API Route (NOT OOP)

```python
@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    
    # Static call - no objects
    response, status = CreateUserAccountController.create(data)
    
    return jsonify(response), status
```

### Target API Route (TRUE OOP)

```python
@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    
    # Create controller object (holds data in memory)
    controller = CreateUserAccountController(data)
    
    # Execute (controller orchestrates, entities do work)
    response, status = controller.execute()
    
    return jsonify(response), status
```

---

## Files to Convert

### Priority 1: Core Entities (Day 1-2)
1. ✅ `src/entity/user.py` (861 lines) - **CRITICAL**
2. ✅ `src/entity/role.py` (348 lines) - **CRITICAL**
3. ✅ `src/entity/request.py` (940 lines) - **CRITICAL**
4. ✅ `src/entity/shortlist.py` (602 lines) - **CRITICAL**
5. ✅ `src/entity/profile.py` (295 lines) - **IMPORTANT**

### Priority 2: Key Controllers (Day 2-3)
1. ✅ `src/controller/userAccount/create_user_account_controller.py`
2. ✅ `src/controller/userAccount/update_user_account_controller.py`
3. ✅ `src/controller/request/create_new_pin_request_controller.py`
4. ✅ `src/controller/request/update_pin_request_controller.py`
5. ✅ `src/controller/shortlist/add_to_shortlist_controller.py`
6. ✅ `src/controller/auth/login_controller.py`

### Priority 3: Other Controllers (Keep as-is initially)
- Can use factory methods from entities
- Convert later if time permits
- Will still work with new entity structure

---

## Testing Strategy

### Day 1-2: Entity Tests
```python
# Test User entity
user = User()
user.username = 'testuser'
user.email = 'test@example.com'
user.password = 'password123'
user.full_name = 'Test User'
user.role_id = 2
user.save()  # Should work

# Test factory methods
user2 = User.find_by_username('testuser')
assert user2.email == 'test@example.com'

# Test instance methods
user2.full_name = 'Updated Name'
user2.save()  # Should update
```

### Day 3: Controller Tests
```python
# Test controller
controller = CreateUserAccountController({
    'username': 'newuser',
    'password': 'password123',
    'email': 'new@example.com',
    'full_name': 'New User',
    'role_id': 2
})

response, status = controller.execute()
assert status == 201
assert response['success'] == True
```

### Day 4: Integration Tests
- Test all API endpoints
- Test frontend integration
- Verify existing functionality works

---

## Risk Mitigation

### Backup Strategy
1. Create backup branch before starting
2. Commit after each entity conversion
3. Commit after each controller conversion
4. Can rollback if needed

### Incremental Approach
1. Convert one entity at a time
2. Test before moving to next
3. Keep factory methods for backward compatibility
4. Convert controllers gradually

### Fallback Plan
If time runs out:
- At minimum, convert User, Request, and 2 controllers
- This demonstrates OOP understanding
- Remaining code can use factory methods

---

## Success Criteria

### What Your Lecturer Will See

**Entities:**
```python
class User:
    def __init__(self):
        self.username = None  # ✅ Data in memory
        self.email = None     # ✅ Data in memory
    
    def save(self):  # ✅ Instance method
        # Does actual work
        supabase.table('users').insert({...})
```

**Controllers:**
```python
class CreateUserAccountController:
    def __init__(self, data):
        self.data = data  # ✅ Data in memory
        self.user = None  # ✅ Holds objects
    
    def execute(self):  # ✅ Instance method
        self.user = User()  # ✅ Creates objects
        self.user.save()    # ✅ Uses objects
```

**API Routes:**
```python
controller = CreateUserAccountController(data)  # ✅ Creates objects
response = controller.execute()  # ✅ Uses objects
```

**Result:** ✅ Backend holds data in memory as objects and runs logic through objects

---

## Next Steps

Ready to start? I can:

1. **Option A: Full Conversion** - Convert all 5 entities + 6 controllers (3-4 days)
2. **Option B: Minimal Conversion** - Convert 2 entities + 2 controllers (1-2 days)
3. **Option C: Show me one example first** - Convert just User entity + CreateUserAccountController so you can see the pattern

Which approach do you want to take?

