# 🚀 Testing the Backend API

This guide shows how to test the BiasLens backend API implementation.

## Prerequisites

✅ Backend running on `http://localhost:3001`
✅ Database initialized with `npx prisma migrate dev --name init`

## Quick Test (Windows PowerShell)

### Step 1: Start Backend

```bash
cd backend
npm run dev
```

You should see:
```
✅ Database connected
🚀 Server running on http://localhost:3001
```

### Step 2: Run Test Script

In a new PowerShell terminal:

```powershell
cd backend
.\test-api.ps1
```

This will test all 10 API endpoints:
1. ✅ Health check
2. ✅ Register user
3. ✅ Get current user (protected)
4. ✅ Create conversation
5. ✅ Save chat (user message)
6. ✅ Save chat (assistant message with bias data)
7. ✅ Get conversation with chats
8. ✅ Get all chats in conversation
9. ✅ List all conversations
10. ✅ Update conversation title

## Manual Testing with cURL

### 1. Check Health

```bash
curl http://localhost:3001/health
```

Expected response:
```json
{
  "status": "ok",
  "timestamp": "2026-05-23T20:00:00.000Z"
}
```

### 2. Register New User

```bash
curl -X POST http://localhost:3001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "code": "BIASLENS2025"
  }'
```

Expected response:
```json
{
  "message": "User registered successfully",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "clkz5j8kp00001h6z7z8z8z8z",
    "name": "John Doe",
    "email": "john@example.com"
  }
}
```

### 3. Login

```bash
curl -X POST http://localhost:3001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'
```

Save the `token` from response for next steps.

### 4. Get Current User (with JWT)

```bash
curl -X GET http://localhost:3001/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 5. Create Conversation

```bash
curl -X POST http://localhost:3001/api/conversations \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"title": "First Analysis"}'
```

Save the `id` from response.

### 6. Save Chat (User Message)

```bash
curl -X POST http://localhost:3001/api/chats \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "conversationId": "CONVERSATION_ID",
    "role": "user",
    "text": "This text might have some bias in it."
  }'
```

### 7. Save Chat (Assistant Response with Bias Data)

```bash
curl -X POST http://localhost:3001/api/chats \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "conversationId": "CONVERSATION_ID",
    "role": "assistant",
    "text": "Analysis complete.",
    "biasData": {
      "summary": "This text contains moderate bias indicators.",
      "overall": "medium",
      "biases": [
        {"type": "Gender", "score": 45, "note": "Gender-related language detected"},
        {"type": "Political", "score": 20, "note": "Minor political bias"},
        {"type": "Racial", "score": 10, "note": "No significant racial bias"},
        {"type": "Sentiment", "score": 35, "note": "Negative sentiment present"}
      ]
    }
  }'
```

### 8. Get Conversation with All Chats

```bash
curl -X GET http://localhost:3001/api/conversations/CONVERSATION_ID \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 9. Get All Chats in Conversation

```bash
curl -X GET http://localhost:3001/api/chats/CONVERSATION_ID \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 10. List All Conversations

```bash
curl -X GET http://localhost:3001/api/conversations \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 11. Update Conversation Title

```bash
curl -X PATCH http://localhost:3001/api/conversations/CONVERSATION_ID \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Title"}'
```

### 12. Delete Chat

```bash
curl -X DELETE http://localhost:3001/api/chats/CHAT_ID \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 13. Delete Conversation

```bash
curl -X DELETE http://localhost:3001/api/conversations/CONVERSATION_ID \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Testing with Postman

1. **Import Collection**: Create a new collection in Postman
2. **Set Base URL**: `http://localhost:3001`
3. **Add Variable**: `token` - Update after login
4. **Create Requests**:
   - POST `/api/auth/register`
   - POST `/api/auth/login`
   - GET `/api/auth/me` (add `Authorization: Bearer {{token}}` header)
   - POST `/api/conversations` (with token)
   - POST `/api/chats` (with token)
   - GET `/api/conversations` (with token)

## Expected Results

### Success Status Codes
- ✅ 201 - Created (register, create conversation, save chat)
- ✅ 200 - OK (login, get, list, update)
- ✅ 204 - No Content (delete)

### Error Status Codes
- ❌ 400 - Bad Request (missing fields)
- ❌ 401 - Unauthorized (invalid token)
- ❌ 403 - Forbidden (invalid code)
- ❌ 404 - Not Found (wrong ID)
- ❌ 409 - Conflict (email already exists)

## Frontend Integration

Once backend is tested, test with frontend:

```bash
# In frontend root
npm run dev
```

Then:
1. Navigate to http://localhost:3000
2. Register new account (code: `BIASLENS2025`)
3. Login
4. Send bias analysis
5. Check database with: `npm run prisma:studio` in backend

## Debugging

### View Database

```bash
cd backend
npm run prisma:studio
# Opens http://localhost:5555
```

### Check Backend Logs

Look at the terminal where `npm run dev` is running

### Clear Database (SQLite)

```bash
cd backend
rm dev.db
npx prisma migrate dev --name init
npm run dev
```

### Clear Database (PostgreSQL)

```bash
npx prisma migrate reset
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Connection refused | Backend not running: `cd backend && npm run dev` |
| "Invalid token" | Token expired or incorrect, login again |
| "Email already exists" | Use different email or clear database |
| CORS error | Check CORS_ORIGIN in .env matches frontend URL |
| Database error | Run `npx prisma migrate dev --name init` |

---

**Status: Ready for Testing! ✅**
