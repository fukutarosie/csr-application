# CSR App - Customer Service Request Management System

A full-stack application built with Flask (Backend) and Next.js (Frontend) for managing customer service requests with role-based access control.

## Features

- **Authentication & Authorization**
  - Secure login with username and password
  - Role-based access control (4 roles)
  - JWT session token management
  - Protected API endpoints

- **User Roles**
  - User Admin
  - PIN (Partner Information Network)
  - CSR Rep (Customer Service Representative)
  - Platform Management

## Prerequisites

- Python 3.8+
- Node.js 14+
- npm or yarn
- Supabase account (already configured)

## Setup Instructions

### 1. Backend Setup (Flask)

#### Install Python Dependencies

```bash
# Navigate to project root
cd csr_app

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Configure Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. The `.env` file is already configured with your Supabase credentials. Review it to ensure everything is correct.

#### Run Flask Backend

```bash
python app.py
```

The backend will start at `http://localhost:5000`

### 2. Frontend Setup (Next.js)

#### Install Node Dependencies

```bash
# Navigate to frontend directory (if separate)
npm install
# or
yarn install
```

#### Run Next.js Development Server

```bash
npm run dev
# or
yarn dev
```

The frontend will start at `http://localhost:3000`

## Project Structure

```
csr_app/
├── src/
│   ├── app/                 # Next.js frontend
│   │   ├── page.js         # Login page
│   │   ├── layout.js       # Root layout
│   │   └── globals.css     # Global styles
│   ├── config/
│   │   └── supabase.py     # Supabase configuration
│   ├── controller/
│   │   └── auth/
│   │       ├── auth_controller.py    # Authentication endpoints
│   │       └── auth_middleware.py    # Role-based access middleware
│   └── entity/
│       ├── role.py         # Role model
│       ├── user.py         # User model
│       └── __init__.py     # Entity exports
├── app.py                   # Flask app entry point
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (local)
├── .env.example            # Environment variables (template)
└── tailwind.config.js      # Tailwind CSS configuration
```

## API Endpoints

### Authentication

- **POST** `/api/auth/login`
  - Login with username, password, and role
  - Returns: JWT token and user data

- **POST** `/api/auth/logout`
  - Logout and invalidate session
  - Requires: Authorization header with Bearer token

- **GET** `/api/auth/verify`
  - Verify session token validity
  - Requires: Authorization header with Bearer token

### User Management (User Admin Only)

- **GET** `/api/users`
  - Get all users
  - Requires: User Admin role

- **GET** `/api/users/<user_id>`
  - Get specific user
  - Requires: User Admin role

- **POST** `/api/users/create`
  - Create a new user
  - Requires: User Admin role
  - Body: `{ username, password, email, full_name, role_id }`

- **PUT** `/api/users/<user_id>`
  - Update user details
  - Requires: User Admin role
  - Body: `{ email, full_name, role_id }`

- **PUT** `/api/users/<user_id>/suspend`
  - Suspend a user account
  - Requires: User Admin role

- **PUT** `/api/users/<user_id>/activate`
  - Activate a suspended user
  - Requires: User Admin role

- **POST** `/api/users/search`
  - Search users by criteria
  - Requires: User Admin role
  - Body: `{ username, email, full_name }`

### Roles

- **GET** `/api/roles`
  - Get all roles
  - Requires: User Admin role

- **GET** `/api/roles/<role_id>`
  - Get specific role
  - Requires: User Admin role

## Environment Variables

Key environment variables configured:

```
# Supabase
SUPABASE_URL=https://gfmghhgmcvgiuqkapzkv.supabase.co
SUPABASE_KEY=your_anon_key

# Flask
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_PORT=5000

# JWT
JWT_SECRET_KEY=your_jwt_secret
JWT_ACCESS_TOKEN_EXPIRES=3600

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:5000
```

## Testing

Run tests with pytest:

```bash
pytest
```

## Development Workflow

### Option 1: Using Batch File (Easiest - Windows)

Simply run the batch file which automatically sets up and starts both services:

```bash
run.bat
```

This will:
- Create a Python virtual environment (if needed)
- Install all Python dependencies
- Install Node.js dependencies
- Start both Flask backend and Next.js frontend in separate windows

### Option 2: Using PowerShell Script (Windows)

Run the PowerShell script:

```powershell
.\run.ps1
```

**Note:** If you get a permission error, run PowerShell as Administrator first, then:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Option 3: Manual Setup

1. Start the Flask backend:
   ```bash
   python app.py
   ```

2. In a new terminal, start the Next.js frontend:
   ```bash
   npm run dev
   ```

3. Open browser to `http://localhost:3000`

4. Login with your Supabase user credentials

## Security Notes

⚠️ **Important:**

- Never commit `.env` file to version control
- Change `SECRET_KEY` and `JWT_SECRET_KEY` in production
- Use environment-specific configurations
- Keep Supabase keys secure

## Troubleshooting

### Backend won't start
- Check if port 5000 is available
- Verify environment variables in `.env`
- Check Python version compatibility

### Frontend can't connect to backend
- Ensure backend is running on port 5000
- Check CORS configuration in `app.py`
- Verify `NEXT_PUBLIC_API_URL` in `.env`

### Database connection issues
- Verify Supabase credentials in `.env`
- Check Supabase project status
- Ensure tables exist in Supabase

## Support

For issues or questions, check the project documentation or contact the development team.

## License

Proprietary - CSR App Development Team