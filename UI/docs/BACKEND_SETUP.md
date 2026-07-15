# 🚀 BiasLens Backend - Quick Start

## What's Been Created

✅ **Complete Prisma Backend** with:
- User authentication (register, login, JWT)
- Conversation management
- Chat storage with bias analysis data
- PostgreSQL database schema
- Express API server
- TypeScript + security best practices

## File Structure

```
backend/
├── prisma/
│   └── schema.prisma          ← Database schema
├── src/
│   ├── server.ts              ← Main Express server
│   ├── routes/
│   │   ├── auth.ts            ← Auth endpoints
│   │   ├── conversations.ts   ← Conversation CRUD
│   │   └── chats.ts           ← Chat storage
│   ├── controllers/           ← Business logic
│   ├── middleware/
│   │   └── auth.ts            ← JWT verification
│   └── utils/
│       ├── password.ts        ← Bcrypt hashing
│       └── jwt.ts             ← JWT generation
├── .env                       ← Environment config
└── package.json
```

## Prerequisites

- PostgreSQL 14+ running locally or remote
- Node.js 18+

## Step 1: Configure Database

### Local PostgreSQL Setup (Windows):

1. **Install PostgreSQL** from https://www.postgresql.org/download/windows/

2. **Create database**:
```sql
CREATE DATABASE biaslens_db;
```

3. **Update `.env`**:
```env
DATABASE_URL="postgresql://postgres:YOUR_PASSWORD@localhost:5432/biaslens_db"
```

### Or Use Remote (e.g., Heroku PostgreSQL, Render, Railway):

Just update `DATABASE_URL` in `.env` with your remote connection string.

## Step 2: Install & Setup Backend

```bash
cd backend
npm install
npx prisma generate
npx prisma migrate dev --name init
```

This will:
- Install all dependencies
- Generate Prisma client
- Create database tables

## Step 3: Start Backend Server

```bash
npm run dev
```

You should see:
```
✅ Database connected
🚀 Server running on http://localhost:3001
```

## Step 4: Test API

### Register User:
```bash
curl -X POST http://localhost:3001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "Password123!",
    "code": "BIASLENS2025"
  }'
```

Response:
```json
{
  "message": "User registered successfully",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "clkz5j8kp00001h6z7z8z8z8z",
    "name": "Test User",
    "email": "test@example.com"
  }
}
```

### Login:
```bash
curl -X POST http://localhost:3001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Password123!"
  }'
```

### Get Current User:
```bash
curl -X GET http://localhost:3001/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Step 5: Integrate with Frontend

See [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md) for:
- Creating API client
- Updating hooks
- Running both services together

## Available API Endpoints

### Auth
- `POST /api/auth/register` - Register
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user

### Conversations
- `POST /api/conversations` - Create
- `GET /api/conversations` - List all
- `GET /api/conversations/:id` - Get one with chats
- `PATCH /api/conversations/:id` - Update title
- `DELETE /api/conversations/:id` - Delete

### Chats
- `POST /api/chats` - Save message
- `GET /api/chats/:conversationId` - Get all in conversation
- `DELETE /api/chats/:id` - Delete message

All endpoints except `/auth/register` and `/auth/login` require:
```
Authorization: Bearer <token>
```

## Useful Commands

```bash
# View database in UI
npm run prisma:studio

# Create new migration
npm run prisma:migrate

# Build for production
npm run build
npm start

# Check database schema
npx prisma introspect
```

## Database Schema

**Users** (stores account info)
- id, email (unique), name, password (hashed), createdAt, updatedAt

**Conversations** (chat sessions)
- id, userId, title, createdAt, updatedAt

**Chats** (individual messages)
- id, conversationId, userId, role (user/assistant), text, biasData (JSON), createdAt, updatedAt

## Frontend Integration

Once backend is running:

1. Copy `INTEGRATION_GUIDE.md` guide
2. Update frontend `.env.local`:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:3001
   ```
3. Run frontend: `npm run dev` (port 3000)

## Production Deployment

### Heroku Example:

```bash
# Add Heroku remote
heroku create your-biaslens-backend

# Add PostgreSQL add-on
heroku addons:create heroku-postgresql:mini

# Set environment
heroku config:set JWT_SECRET="your_secret_32_chars_min"

# Deploy
git push heroku main
```

### Railway Example:

1. Connect GitHub repo
2. Add PostgreSQL plugin
3. Set environment variables
4. Deploy automatically

## Troubleshooting

### "Database connection failed"
- Check PostgreSQL is running
- Verify DATABASE_URL is correct
- Test with: `psql postgresql://user:password@localhost:5432/biaslens_db`

### "Prisma client not found"
```bash
npx prisma generate
```

### "Migration failed"
```bash
npx prisma migrate reset  # ⚠️ Deletes all data
```

## Next Steps

- ✅ Backend created
- ⬜ Integration Guide
- ⬜ Frontend hooks updated
- ⬜ Deploy to production
- ⬜ Add email verification
- ⬜ Add refresh tokens
- ⬜ Add rate limiting
