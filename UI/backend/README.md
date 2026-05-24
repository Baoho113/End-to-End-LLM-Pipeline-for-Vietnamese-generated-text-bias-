# BiasLens Backend API

Backend API for BiasLens built with Express, Prisma, and PostgreSQL.

## Setup

### Prerequisites
- Node.js 18+
- PostgreSQL 14+

### Installation

1. Install dependencies:
```bash
npm install
```

2. Copy `.env.example` to `.env` and configure your database:
```bash
cp .env.example .env
```

3. Set up Prisma:
```bash
npx prisma generate
npx prisma migrate dev --name init
```

### Development

Start the development server:
```bash
npm run dev
```

The server will run on `http://localhost:3001`

### Database

View and manage your database with Prisma Studio:
```bash
npm run prisma:studio
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
  - Body: `{ name, email, password, code }`
  - Returns: `{ token, user }`

- `POST /api/auth/login` - Login user
  - Body: `{ email, password }`
  - Returns: `{ token, user }`

- `GET /api/auth/me` - Get current user (requires auth header)
  - Returns: `{ id, name, email, createdAt }`

### Conversations
- `POST /api/conversations` - Create conversation (requires auth)
  - Body: `{ title? }`
  - Returns: `{ id, userId, title, createdAt, updatedAt }`

- `GET /api/conversations` - List user's conversations (requires auth)
  - Returns: `[{ id, title, userId, createdAt, _count: { chats } }, ...]`

- `GET /api/conversations/:id` - Get conversation with all chats (requires auth)
  - Returns: `{ id, title, chats: [...] }`

- `PATCH /api/conversations/:id` - Update conversation (requires auth)
  - Body: `{ title }`
  - Returns: `{ id, title, ... }`

- `DELETE /api/conversations/:id` - Delete conversation (requires auth)
  - Returns: `{ message }`

### Chats
- `POST /api/chats` - Save chat message (requires auth)
  - Body: `{ conversationId, role, text, biasData? }`
  - Returns: `{ id, conversationId, userId, role, text, biasData, createdAt }`

- `GET /api/chats/:conversationId` - Get all chats in conversation (requires auth)
  - Returns: `[{ id, conversationId, role, text, biasData, createdAt }, ...]`

- `DELETE /api/chats/:id` - Delete chat (requires auth)
  - Returns: `{ message }`

## Authentication

Include JWT token in request headers:
```
Authorization: Bearer <token>
```

## Building for Production

```bash
npm run build
npm start
```

## Database Migrations

Create a new migration:
```bash
npx prisma migrate dev --name <migration_name>
```

Deploy migrations to production:
```bash
npx prisma migrate deploy
```

## Project Structure

```
backend/
├── prisma/
│   ├── schema.prisma       # Database schema
│   └── migrations/         # Migration files
├── src/
│   ├── server.ts           # Express server
│   ├── routes/             # API route handlers
│   ├── controllers/        # Business logic
│   ├── middleware/         # Express middleware
│   └── utils/              # Utility functions
├── package.json
├── tsconfig.json
├── .env
└── README.md
```
