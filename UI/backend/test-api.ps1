# BiasLens Backend API Tests for Windows PowerShell

$API_URL = "http://localhost:3001"
$ErrorActionPreference = "Continue"

Write-Host "========================================" -ForegroundColor Blue
Write-Host "BiasLens Backend API Tests" -ForegroundColor Blue
Write-Host "========================================" -ForegroundColor Blue
Write-Host ""

# Test 1: Health Check
Write-Host "Test 1: Health Check" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$API_URL/health" -Method Get
    $response | ConvertTo-Json
} catch {
    Write-Host "Failed to reach server: $_" -ForegroundColor Red
}
Write-Host ""

# Test 2: Register User
Write-Host "Test 2: Register New User" -ForegroundColor Yellow
$registerBody = @{
    name = "Test User"
    email = "test@example.com"
    password = "TestPassword123!"
    code = "BIASLENS2025"
} | ConvertTo-Json

try {
    $registerResponse = Invoke-RestMethod -Uri "$API_URL/api/auth/register" `
        -Method Post `
        -ContentType "application/json" `
        -Body $registerBody
    $registerResponse | ConvertTo-Json
    $token = $registerResponse.token
} catch {
    Write-Host "Registration failed (user may already exist), trying login..." -ForegroundColor Yellow
    
    $loginBody = @{
        email = "test@example.com"
        password = "TestPassword123!"
    } | ConvertTo-Json
    
    try {
        $loginResponse = Invoke-RestMethod -Uri "$API_URL/api/auth/login" `
            -Method Post `
            -ContentType "application/json" `
            -Body $loginBody
        $loginResponse | ConvertTo-Json
        $token = $loginResponse.token
    } catch {
        Write-Host "Login also failed: $_" -ForegroundColor Red
        exit 1
    }
}
Write-Host ""

if (-not $token) {
    Write-Host "Warning: Could not obtain token" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Token obtained: $($token.Substring(0, 20))..." -ForegroundColor Green
Write-Host ""

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

# Test 3: Get Current User
Write-Host "Test 3: Get Current User (Protected Route)" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$API_URL/api/auth/me" -Method Get -Headers $headers
    $response | ConvertTo-Json
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}
Write-Host ""

# Test 4: Create Conversation
Write-Host "Test 4: Create Conversation" -ForegroundColor Yellow
$convBody = @{
    title = "First Analysis"
} | ConvertTo-Json

try {
    $convResponse = Invoke-RestMethod -Uri "$API_URL/api/conversations" `
        -Method Post `
        -Headers $headers `
        -Body $convBody
    $convResponse | ConvertTo-Json
    $convId = $convResponse.id
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}
Write-Host ""

if (-not $convId) {
    Write-Host "Warning: Could not create conversation" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Conversation ID: $convId" -ForegroundColor Green
Write-Host ""

# Test 5: Save Chat Message (User)
Write-Host "Test 5: Save Chat Message (User)" -ForegroundColor Yellow
$userMsgBody = @{
    conversationId = $convId
    role = "user"
    text = "This is a test message to check for bias."
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$API_URL/api/chats" `
        -Method Post `
        -Headers $headers `
        -Body $userMsgBody
    $response | ConvertTo-Json
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}
Write-Host ""

# Test 6: Save Chat Message (Assistant with Bias Data)
Write-Host "Test 6: Save Chat Message (Assistant with Bias Data)" -ForegroundColor Yellow
$biasData = @{
    summary = "This text contains some bias indicators."
    overall = "medium"
    biases = @(
        @{type = "Gender"; score = 35; note = "Some gender-related language"},
        @{type = "Political"; score = 20; note = "Minimal political bias"},
        @{type = "Racial"; score = 15; note = "No racial bias detected"},
        @{type = "Sentiment"; score = 45; note = "Some negative sentiment"}
    )
}

$assistantMsgBody = @{
    conversationId = $convId
    role = "assistant"
    text = "This text contains some bias indicators."
    biasData = $biasData
} | ConvertTo-Json -Depth 10

try {
    $response = Invoke-RestMethod -Uri "$API_URL/api/chats" `
        -Method Post `
        -Headers $headers `
        -Body $assistantMsgBody
    $response | ConvertTo-Json
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}
Write-Host ""

# Test 7: Get Conversation with Chats
Write-Host "Test 7: Get Conversation with Chats" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$API_URL/api/conversations/$convId" `
        -Method Get `
        -Headers $headers
    $response | ConvertTo-Json
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}
Write-Host ""

# Test 8: Get All Chats in Conversation
Write-Host "Test 8: Get All Chats in Conversation" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$API_URL/api/chats/$convId" `
        -Method Get `
        -Headers $headers
    $response | ConvertTo-Json
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}
Write-Host ""

# Test 9: List Conversations
Write-Host "Test 9: List All Conversations" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$API_URL/api/conversations" `
        -Method Get `
        -Headers $headers
    $response | ConvertTo-Json
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}
Write-Host ""

# Test 10: Update Conversation Title
Write-Host "Test 10: Update Conversation Title" -ForegroundColor Yellow
$updateBody = @{
    title = "Updated Analysis Title"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$API_URL/api/conversations/$convId" `
        -Method Patch `
        -Headers $headers `
        -Body $updateBody
    $response | ConvertTo-Json
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Blue
Write-Host "✓ All tests completed!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Blue
