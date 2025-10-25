"""
BOUNDARY-CONTROL-ENTITY (BCE) ARCHITECTURE EXPLANATION

A comprehensive guide to understanding the three-layer architecture pattern
used in the CSR Application.
"""

# ==============================================================================
# 1. LAYER OVERVIEW
# ==============================================================================

"""
┌─────────────────────────────────────────────────────────────────┐
│                      BOUNDARY LAYER                              │
│  (HTTP Requests/Responses - API Endpoints)                      │
│  Location: src/controller/*controller.py                         │
│  Responsibility: Accept HTTP requests, validate input           │
│                                                                   │
│  ↓ Passes cleaned data ↓                                         │
│                                                                   │
├─────────────────────────────────────────────────────────────────┤
│                      CONTROL LAYER                               │
│  (Business Logic - Controllers)                                 │
│  Location: src/controller/*controller.py (class methods)        │
│  Responsibility: Orchestrate operations, enforce business rules │
│                                                                   │
│  ↓ Calls entity methods ↓                                        │
│                                                                   │
├─────────────────────────────────────────────────────────────────┤
│                      ENTITY LAYER                                │
│  (Domain Objects - Business Entities)                           │
│  Location: src/entity/*.py (User, Role, etc.)                  │
│  Responsibility: Database operations, data persistence          │
│                                                                   │
│  ↓ Returns domain objects ↓                                      │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
"""

# ==============================================================================
# 2. USE CASE: CREATE USER ACCOUNT
# ==============================================================================

"""
FLOW: User Admin creates a new user account

┌────────────────────────────────────────────────────────────────────┐
│ BOUNDARY: POST /api/userAccount (HTTP Request)                    │
├────────────────────────────────────────────────────────────────────┤

Location: src/controller/userAccount/create_user_account_controller.py

@create_user_account_blueprint.route('/', methods=['POST'])
@require_role(Role.USER_ADMIN)  # ← Authorization check
def create():
    # BOUNDARY LAYER: Extract and validate HTTP input
    data = request.json
    
    # Validate required fields
    if not all([data.get('username'), data.get('password'), 
                data.get('email'), data.get('full_name'), data.get('role_id')]):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    
    # ↓ Call CONTROL LAYER (business logic)
    try:
        result = User.create_user(
            username=data['username'],
            password=data['password'],
            email=data['email'],
            full_name=data['full_name'],
            role_id=data['role_id']
        )
        
        # BOUNDARY LAYER: Format response for HTTP client
        if result:
            return jsonify({
                'success': True,
                'data': result,
                'message': 'User created successfully'
            }), 201
        else:
            return jsonify({'success': False, 'message': 'Failed to create user'}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

┌────────────────────────────────────────────────────────────────────┐
│ CONTROL: User.create_user() - Business Logic                      │
├────────────────────────────────────────────────────────────────────┤

Location: src/entity/user.py

class User:
    @staticmethod
    def create_user(username: str, password: str, email: str, 
                   full_name: str, role_id: int) -> Optional[Dict]:
        """Create a new user account with business rule validation"""
        
        supabase = get_supabase()
        
        # CONTROL LAYER: Apply business rules
        
        # Rule 1: Username must be unique
        existing = User.get_user_by_username(username)
        if existing:
            raise ValueError(f"Username '{username}' already exists")
        
        # Rule 2: Password must be hashed for security
        hashed_password = generate_password_hash(password)
        
        # Rule 3: Email must be unique
        existing_email = supabase.table('users').select('*').eq('email', email).execute()
        if existing_email.data:
            raise ValueError(f"Email '{email}' already exists")
        
        # Rule 4: Role must exist
        role = Role.get_role_by_id(role_id)
        if not role:
            raise ValueError(f"Role with ID {role_id} does not exist")
        
        # ↓ Call ENTITY LAYER (data persistence)
        new_user = supabase.table('users').insert({
            'username': username,
            'password': hashed_password,
            'email': email,
            'full_name': full_name,
            'role_id': role_id,
            'is_active': True,
            'created_at': datetime.now().isoformat()
        }).execute()
        
        # ↓ Call ENTITY LAYER (return entity data)
        return User.get_user_by_id(new_user.data[0]['id'])

┌────────────────────────────────────────────────────────────────────┐
│ ENTITY: Database Operations (Persistence)                         │
├────────────────────────────────────────────────────────────────────┤

Location: src/entity/user.py (helper methods)

class User:
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[Dict]:
        """Retrieve user from database"""
        supabase = get_supabase()
        response = supabase.table('users').select('*').eq('id', user_id).execute()
        return response.data[0] if response.data else None
    
    @staticmethod
    def get_user_by_username(username: str) -> Optional[Dict]:
        """Check if username exists in database"""
        supabase = get_supabase()
        response = supabase.table('users').select('*').eq('username', username).execute()
        return response.data[0] if response.data else None

DATABASE FLOW:
Users Table in Supabase:
┌─────────────────────────────────────────────────────────────────┐
│ id | username | email        | password (hashed) | role_id | ... │
├─────────────────────────────────────────────────────────────────┤
│ 1  | admin1   | admin@...    | $2b$12$abc...    | 1       | ... │
│ 2  | pin_user | pin@...      | $2b$12$xyz...    | 2       | ... │
│ 3  | NEW_USER | new@...      | $2b$12$NEW...    | 1       | ... │ ← Created
└─────────────────────────────────────────────────────────────────┘
"""

# ==============================================================================
# 3. USE CASE: VIEW ALL USER ACCOUNTS
# ==============================================================================

"""
FLOW: User Admin views list of all users

┌────────────────────────────────────────────────────────────────────┐
│ BOUNDARY: GET /api/userAccount (HTTP Request)                     │
├────────────────────────────────────────────────────────────────────┤

Location: src/controller/userAccount/view_user_account_controller.py

@view_user_account_blueprint.route('/', methods=['GET'])
@require_role(Role.USER_ADMIN)
def get_all():
    """Retrieve all user accounts"""
    try:
        # BOUNDARY: Accept HTTP GET request (no body validation needed)
        
        # ↓ Call CONTROL LAYER
        result = User.get_all_users()
        
        # BOUNDARY: Format response as JSON
        if result:
            return jsonify({
                'success': True,
                'data': result,
                'message': f'Retrieved {len(result)} users'
            }), 200
        else:
            return jsonify({
                'success': True,
                'data': [],
                'message': 'No users found'
            }), 200
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

┌────────────────────────────────────────────────────────────────────┐
│ CONTROL: User.get_all_users() - Business Logic                    │
├────────────────────────────────────────────────────────────────────┤

Location: src/entity/user.py

class User:
    @staticmethod
    def get_all_users() -> List[Dict]:
        """Get all users with business rule application"""
        
        # CONTROL: Call entity layer to fetch data
        supabase = get_supabase()
        response = supabase.table('users').select('*').execute()
        
        users = response.data if response.data else []
        
        # CONTROL: Apply business rules (e.g., hide passwords, format dates)
        safe_users = []
        for user in users:
            safe_users.append({
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'full_name': user['full_name'],
                'role_id': user['role_id'],
                'is_active': user['is_active'],
                # Note: 'password' field NEVER returned to client
                'created_at': user.get('created_at')
            })
        
        return safe_users

DATABASE RESULT:
┌─────────────────────────────────────────────────────┐
│ GET /api/userAccount                                │
│ Returns JSON:                                       │
│ {                                                   │
│   "success": true,                                  │
│   "data": [                                         │
│     {                                               │
│       "id": 1,                                      │
│       "username": "admin1",                         │
│       "email": "admin@...",                         │
│       "full_name": "Admin User",                    │
│       "role_id": 1,                                 │
│       "is_active": true                             │
│     },                                              │
│     {                                               │
│       "id": 2,                                      │
│       "username": "pin_user1",                      │
│       "email": "pin@...",                           │
│       "full_name": "PIN User",                      │
│       "role_id": 2,                                 │
│       "is_active": true                             │
│     }                                               │
│   ]                                                 │
│ }                                                   │
└─────────────────────────────────────────────────────┘
"""

# ==============================================================================
# 4. USE CASE: UPDATE USER ACCOUNT
# ==============================================================================

"""
FLOW: User Admin updates a user's email and full name

┌────────────────────────────────────────────────────────────────────┐
│ BOUNDARY: PUT /api/userAccount/<id> (HTTP Request)                │
├────────────────────────────────────────────────────────────────────┤

Location: src/controller/userAccount/update_user_account_controller.py

@update_user_account_blueprint.route('/<int:user_id>', methods=['PUT'])
@require_role(Role.USER_ADMIN)
def update(user_id):
    """Update user account details"""
    try:
        data = request.json
        
        # BOUNDARY: Validate input
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        
        # Only allow certain fields to be updated (security)
        allowed_fields = {'email', 'full_name', 'role_id'}
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        
        if not update_data:
            return jsonify({'success': False, 'message': 'No valid fields to update'}), 400
        
        # ↓ Call CONTROL LAYER
        result = User.update_user(user_id, update_data)
        
        if result:
            return jsonify({
                'success': True,
                'data': result,
                'message': 'User updated successfully'
            }), 200
        else:
            return jsonify({'success': False, 'message': 'User not found'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

┌────────────────────────────────────────────────────────────────────┐
│ CONTROL: User.update_user() - Business Logic                      │
├────────────────────────────────────────────────────────────────────┤

Location: src/entity/user.py

class User:
    @staticmethod
    def update_user(user_id: int, update_data: Dict) -> Optional[Dict]:
        """Update user with business rule validation"""
        
        # CONTROL LAYER: Business rules
        
        # Rule 1: User must exist
        existing_user = User.get_user_by_id(user_id)
        if not existing_user:
            raise ValueError(f"User with ID {user_id} not found")
        
        # Rule 2: If email is being updated, check uniqueness
        if 'email' in update_data:
            email_check = supabase.table('users').select('*').eq('email', update_data['email']).execute()
            if email_check.data and email_check.data[0]['id'] != user_id:
                raise ValueError(f"Email '{update_data['email']}' already exists")
        
        # Rule 3: If role is being updated, verify role exists
        if 'role_id' in update_data:
            role = Role.get_role_by_id(update_data['role_id'])
            if not role:
                raise ValueError(f"Role with ID {update_data['role_id']} does not exist")
        
        # ↓ Call ENTITY LAYER (database update)
        supabase = get_supabase()
        supabase.table('users').update(update_data).eq('id', user_id).execute()
        
        # ↓ Call ENTITY LAYER (return updated user)
        return User.get_user_by_id(user_id)

DATABASE RESULT:
Before:
│ id | username | email    | full_name     | role_id │
├────┼──────────┼──────────┼───────────────┼─────────┤
│ 5  | testuser | old@...  | Old Name      | 1       │

After UPDATE:
│ id | username | email    | full_name     | role_id │
├────┼──────────┼──────────┼───────────────┼─────────┤
│ 5  | testuser | new@...  | Updated Name  | 2       │ ← Updated
"""

# ==============================================================================
# 5. USE CASE: SUSPEND USER ACCOUNT
# ==============================================================================

"""
FLOW: User Admin suspends a user (deactivates account)

┌────────────────────────────────────────────────────────────────────┐
│ BOUNDARY: PUT /api/userAccount/<id>/suspend (HTTP Request)        │
├────────────────────────────────────────────────────────────────────┤

Location: src/controller/userAccount/suspend_user_account_controller.py

@suspend_user_account_blueprint.route('/<int:user_id>/suspend', methods=['PUT'])
@require_role(Role.USER_ADMIN)
def suspend(user_id):
    """Suspend a user account (set is_active to False)"""
    try:
        # BOUNDARY: Parse URL parameter (user_id)
        
        # ↓ Call CONTROL LAYER
        result = User.update_user(user_id, {'is_active': False})
        
        if result:
            return jsonify({
                'success': True,
                'data': result,
                'message': 'User account suspended successfully'
            }), 200
        else:
            return jsonify({'success': False, 'message': 'Failed to suspend user account'}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

┌────────────────────────────────────────────────────────────────────┐
│ CONTROL: User.update_user() - Business Logic                      │
├────────────────────────────────────────────────────────────────────┤

Same as UPDATE use case, but with specific update_data: {'is_active': False}

┌────────────────────────────────────────────────────────────────────┐
│ ENTITY: Database Persistence                                       │
├────────────────────────────────────────────────────────────────────┤

UPDATE users SET is_active = false WHERE id = <user_id>

DATABASE RESULT:
Before:
│ id | username | email    | is_active │
├────┼──────────┼──────────┼───────────┤
│ 2  | pin_user | pin@...  | true      │

After SUSPEND:
│ id | username | email    | is_active │
├────┼──────────┼──────────┼───────────┤
│ 2  | pin_user | pin@...  | false     │ ← Suspended
"""

# ==============================================================================
# 6. USE CASE: ACTIVATE USER ACCOUNT
# ==============================================================================

"""
FLOW: User Admin reactivates a suspended user

┌────────────────────────────────────────────────────────────────────┐
│ BOUNDARY: PUT /api/userAccount/<id>/activate (HTTP Request)       │
├────────────────────────────────────────────────────────────────────┤

Location: src/controller/userAccount/suspend_user_account_controller.py

@suspend_user_account_blueprint.route('/<int:user_id>/activate', methods=['PUT'])
@require_role(Role.USER_ADMIN)
def activate(user_id):
    """Activate a suspended user account (set is_active to True)"""
    try:
        # BOUNDARY: Parse URL parameter
        
        # ↓ Call CONTROL LAYER
        result = User.update_user(user_id, {'is_active': True})
        
        if result:
            return jsonify({
                'success': True,
                'data': result,
                'message': 'User account activated successfully'
            }), 200
        else:
            return jsonify({'success': False, 'message': 'Failed to activate user account'}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

DATABASE RESULT:
Before:
│ id | username | is_active │
├────┼──────────┼───────────┤
│ 2  | pin_user | false     │

After ACTIVATE:
│ id | username | is_active │
├────┼──────────┼───────────┤
│ 2  | pin_user | true      │ ← Activated
"""

# ==============================================================================
# 7. USE CASE: DELETE USER ACCOUNT
# ==============================================================================

"""
FLOW: User Admin permanently deletes a user

┌────────────────────────────────────────────────────────────────────┐
│ BOUNDARY: DELETE /api/userAccount/<id>/delete (HTTP Request)      │
├────────────────────────────────────────────────────────────────────┤

Location: src/controller/userAccount/suspend_user_account_controller.py

@suspend_user_account_blueprint.route('/<int:user_id>/delete', methods=['DELETE'])
@require_role(Role.USER_ADMIN)
def delete(user_id):
    """Permanently delete a user account"""
    try:
        # BOUNDARY: Parse URL parameter
        
        # ↓ Call CONTROL LAYER
        # Rule: User must exist before deletion
        user = User.get_user_by_id(user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': 'User account not found'
            }), 404
        
        # ↓ Call ENTITY LAYER (delete from database)
        from src.entity.supabase_config import supabase
        supabase.table('users').delete().eq('id', user_id).execute()
        
        return jsonify({
            'success': True,
            'message': 'User account deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

DATABASE RESULT:
Before:
│ id | username | email     │
├────┼──────────┼───────────┤
│ 5  | testuser | test@...  │
│ 6  | delme    | del@...   │

After DELETE (id=6):
│ id | username | email     │
├────┼──────────┼───────────┤
│ 5  | testuser | test@...  │
(User with id=6 completely removed)
"""

# ==============================================================================
# 8. USE CASE: SEARCH USER ACCOUNTS
# ==============================================================================

"""
FLOW: User Admin searches for users by keyword

┌────────────────────────────────────────────────────────────────────┐
│ BOUNDARY: POST /api/userAccount/search (HTTP Request)             │
├────────────────────────────────────────────────────────────────────┤

Location: src/controller/userAccount/search_user_account_controller.py

@search_user_account_blueprint.route('/search', methods=['POST'])
@require_role(Role.USER_ADMIN)
def search():
    """Search for users by criteria"""
    try:
        data = request.json
        
        # BOUNDARY: Validate search input
        search_term = data.get('search_term', '').strip().lower()
        
        if not search_term or len(search_term) < 2:
            return jsonify({
                'success': False,
                'message': 'Search term must be at least 2 characters'
            }), 400
        
        # ↓ Call CONTROL LAYER
        results = User.search_users(search_term)
        
        return jsonify({
            'success': True,
            'data': results,
            'message': f'Found {len(results)} matching users'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

┌────────────────────────────────────────────────────────────────────┐
│ CONTROL: User.search_users() - Business Logic                     │
├────────────────────────────────────────────────────────────────────┤

Location: src/entity/user.py

class User:
    @staticmethod
    def search_users(search_term: str) -> List[Dict]:
        """Search users by username, email, or full name"""
        
        # CONTROL: Get all users and apply search logic
        supabase = get_supabase()
        all_users = supabase.table('users').select('*').execute()
        
        # CONTROL: Apply search filtering (case-insensitive)
        search_term_lower = search_term.lower()
        results = [
            user for user in all_users.data
            if search_term_lower in user['username'].lower()
            or search_term_lower in user['email'].lower()
            or search_term_lower in user['full_name'].lower()
        ]
        
        return results

DATABASE RESULT:
POST /api/userAccount/search
Body: { "search_term": "admin" }

Returns:
{
  "success": true,
  "data": [
    {
      "id": 1,
      "username": "admin1",
      "email": "admin@...",
      "full_name": "Admin User",
      "role_id": 1,
      "is_active": true
    }
  ],
  "message": "Found 1 matching users"
}
"""

# ==============================================================================
# 9. USE CASE: CREATE USER PROFILE (ROLE)
# ==============================================================================

"""
FLOW: User Admin creates a new user profile/role

┌────────────────────────────────────────────────────────────────────┐
│ BOUNDARY: POST /api/userProfile (HTTP Request)                    │
├────────────────────────────────────────────────────────────────────┤

Location: src/controller/userProfile/create_user_profile_controller.py

@create_user_profile_blueprint.route('/', methods=['POST'])
@require_role(Role.USER_ADMIN)
def create():
    """Create a new user profile"""
    try:
        data = request.json
        
        # BOUNDARY: Validate input
        if not all([data.get('role_name'), data.get('role_code')]):
            return jsonify({
                'success': False,
                'message': 'role_name and role_code are required'
            }), 400
        
        # ↓ Call CONTROL LAYER
        result = Role.create_role(
            role_name=data['role_name'],
            role_code=data['role_code'],
            description=data.get('description', '')
        )
        
        if result:
            return jsonify({
                'success': True,
                'data': result,
                'message': 'Profile created successfully'
            }), 201
        else:
            return jsonify({'success': False, 'message': 'Failed to create profile'}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

┌────────────────────────────────────────────────────────────────────┐
│ CONTROL: Role.create_role() - Business Logic                      │
├────────────────────────────────────────────────────────────────────┤

Location: src/entity/role.py

class Role:
    @staticmethod
    def create_role(role_name: str, role_code: str, description: str = '') -> Optional[Dict]:
        """Create a new role with validation"""
        
        supabase = get_supabase()
        
        # CONTROL: Apply business rules
        
        # Rule 1: role_code must be unique
        existing = Role.get_role_by_code(role_code)
        if existing:
            raise ValueError(f"Role code '{role_code}' already exists")
        
        # Rule 2: role_name must be unique
        existing_name = supabase.table('roles').select('*').eq('role_name', role_name).execute()
        if existing_name.data:
            raise ValueError(f"Role name '{role_name}' already exists")
        
        # ↓ Call ENTITY LAYER (persist to database)
        new_role = supabase.table('roles').insert({
            'role_name': role_name,
            'role_code': role_code,
            'description': description,
            'created_at': datetime.now().isoformat()
        }).execute()
        
        return Role.get_role_by_id(new_role.data[0]['id'])

DATABASE RESULT:
Roles Table:
┌─────────────────────────────────────────────────────────┐
│ id | role_name         | role_code        | description │
├─────────────────────────────────────────────────────────┤
│ 1  | User Admin        | USER_ADMIN       | Admin user  │
│ 2  | PIN               | PIN              | PIN user    │
│ 3  | NEW_PROFILE       | NEW_PROFILE_CODE | New role... │ ← Created
└─────────────────────────────────────────────────────────┘
"""

# ==============================================================================
# 10. CASCADE DELETE USE CASE (Advanced)
# ==============================================================================

"""
FLOW: Deleting a role automatically deletes all users with that role

┌────────────────────────────────────────────────────────────────────┐
│ BOUNDARY: DELETE /api/userProfile/<id>/delete (HTTP Request)      │
├────────────────────────────────────────────────────────────────────┤

Location: src/controller/userProfile/suspend_user_profile_controller.py

@suspend_user_profile_blueprint.route('/<int:profile_id>/delete', methods=['DELETE'])
@require_role(Role.USER_ADMIN)
def delete(profile_id):
    """Delete a profile (role) - triggers CASCADE DELETE"""
    try:
        # BOUNDARY: Parse URL parameter
        
        # ↓ Call CONTROL LAYER
        # Rule: Profile must exist
        profile = Role.get_role_by_id(profile_id)
        if not profile:
            return jsonify({
                'success': False,
                'message': 'Profile not found'
            }), 404
        
        # ↓ Call ENTITY LAYER
        from src.entity.supabase_config import supabase
        supabase.table('roles').delete().eq('id', profile_id).execute()
        
        # Note: Database CASCADE constraint automatically deletes related users
        
        return jsonify({
            'success': True,
            'message': 'Profile deleted successfully. All associated users were also deleted.'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

CASCADE DELETE FLOW:

Before DELETE:
Roles Table:
│ id | role_name    │
├────┼──────────────┤
│ 5  | TEST_ROLE    │

Users Table:
│ id | username | role_id │
├────┼──────────┼─────────┤
│ 10 | user1    | 5       │
│ 11 | user2    | 5       │
│ 12 | user3    | 5       │

DELETE /api/userProfile/5/delete

After DELETE (DATABASE CASCADE CONSTRAINT ACTIVATES):
Roles Table:
│ id | role_name    │
├────┼──────────────┤
(Role 5 deleted)

Users Table:
│ id | username | role_id │
├────┼──────────┼─────────┤
(Users 10, 11, 12 automatically deleted by CASCADE constraint)

CASCADE FLOW DIAGRAM:
┌─────────────────────────┐
│ DELETE role_id = 5      │
│ (Boundary)              │
└────────────┬────────────┘
             │
             ↓
┌─────────────────────────┐
│ Role.get_role_by_id(5)  │
│ (Control validation)    │
└────────────┬────────────┘
             │
             ↓
┌─────────────────────────┐
│ supabase.delete WHERE   │
│ id = 5 on roles table   │
│ (Entity persistence)    │
└────────────┬────────────┘
             │
             ↓
┌─────────────────────────┐
│ DATABASE CASCADE        │
│ CONSTRAINT TRIGGERS     │
│ (Foreign Key CASCADE)   │
└────────────┬────────────┘
             │
             ↓
┌─────────────────────────┐
│ DELETE all users with   │
│ role_id = 5             │
│ (Automatic)             │
└─────────────────────────┘
"""

# ==============================================================================
# SUMMARY: BCE ARCHITECTURE PATTERN
# ==============================================================================

"""
KEY CONCEPTS:

1. SEPARATION OF CONCERNS
   - Boundary: Handles HTTP protocol
   - Control: Handles business logic
   - Entity: Handles data persistence

2. DATA FLOW (Always same direction):
   HTTP Request → Boundary → Control → Entity → Database
   Database → Entity → Control → Boundary → HTTP Response

3. VALIDATION AT EACH LAYER:
   Boundary:  Input validation (type, format, presence)
   Control:   Business rule validation (uniqueness, relationships)
   Entity:    Data persistence validation (constraints, types)

4. SECURITY:
   - Each layer enforces authorization (@require_role)
   - Sensitive data filtered at Boundary layer
   - Database constraints prevent invalid data
   - Passwords hashed at Control layer

5. ERROR HANDLING:
   - Try/catch at Boundary for HTTP error responses
   - Exceptions propagate upward
   - Each layer can add context to errors

6. REUSABILITY:
   - Entity methods used by multiple controllers
   - Control logic independent of HTTP
   - Business rules defined once in Control layer

BENEFITS:
✅ Clean separation of concerns
✅ Easy to test (mock each layer)
✅ Business logic not tied to HTTP
✅ Database operations centralized
✅ Consistent error handling
✅ Single responsibility principle
"""
