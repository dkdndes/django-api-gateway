# Google Sheets API Documentation

This document provides detailed information about the API endpoints available for the Google Sheets integration.

## Authentication

All API endpoints require authentication. You can authenticate using:

1. Session authentication (for web browser access)
2. Token authentication (for programmatic access)

For token authentication, include the token in the Authorization header:

```
Authorization: Token your_token_here
```

## Endpoints

### Google Sheets

#### List Google Sheets

```
GET /sheets/api/sheets/
```

Returns a list of Google Sheets that the authenticated user has access to.

**Response:**

```json
[
  {
    "id": 1,
    "name": "My Sheet",
    "sheet_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
    "description": "This is my Google Sheet",
    "user": {
      "id": 1,
      "username": "user1",
      "email": "user1@example.com"
    },
    "created_at": "2025-05-10T12:00:00Z",
    "updated_at": "2025-05-10T12:00:00Z"
  }
]
```

#### Create Google Sheet

```
POST /sheets/api/sheets/
```

Creates a new Google Sheet connection.

**Request:**

```json
{
  "name": "My Sheet",
  "sheet_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
  "description": "This is my Google Sheet"
}
```

**Response:**

```json
{
  "id": 1,
  "name": "My Sheet",
  "sheet_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
  "description": "This is my Google Sheet",
  "user": {
    "id": 1,
    "username": "user1",
    "email": "user1@example.com"
  },
  "created_at": "2025-05-10T12:00:00Z",
  "updated_at": "2025-05-10T12:00:00Z"
}
```

#### Get Google Sheet

```
GET /sheets/api/sheets/{id}/
```

Returns details of a specific Google Sheet.

**Response:**

```json
{
  "id": 1,
  "name": "My Sheet",
  "sheet_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
  "description": "This is my Google Sheet",
  "user": {
    "id": 1,
    "username": "user1",
    "email": "user1@example.com"
  },
  "created_at": "2025-05-10T12:00:00Z",
  "updated_at": "2025-05-10T12:00:00Z"
}
```

#### Update Google Sheet

```
PUT /sheets/api/sheets/{id}/
```

Updates a specific Google Sheet.

**Request:**

```json
{
  "name": "Updated Sheet Name",
  "description": "Updated description"
}
```

**Response:**

```json
{
  "id": 1,
  "name": "Updated Sheet Name",
  "sheet_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
  "description": "Updated description",
  "user": {
    "id": 1,
    "username": "user1",
    "email": "user1@example.com"
  },
  "created_at": "2025-05-10T12:00:00Z",
  "updated_at": "2025-05-10T12:30:00Z"
}
```

#### Delete Google Sheet

```
DELETE /sheets/api/sheets/{id}/
```

Deletes a specific Google Sheet.

**Response:**

```
204 No Content
```

#### Sync Google Sheet Data

```
POST /sheets/api/sheets/{id}/sync/
```

Syncs data from the Google Sheet to the database.

**Response:**

```json
{
  "success": true,
  "message": "Successfully synced 10 rows of data"
}
```

### Sheet Data

#### List Sheet Data

```
GET /sheets/api/sheets/{sheet_id}/data/
```

Returns a list of data rows from a specific Google Sheet.

**Response:**

```json
[
  {
    "id": 1,
    "sheet": 1,
    "row_number": 1,
    "row_data": {
      "column1": "value1",
      "column2": "value2"
    },
    "created_at": "2025-05-10T12:00:00Z",
    "updated_at": "2025-05-10T12:00:00Z"
  }
]
```

#### Get Sheet Data Row

```
GET /sheets/api/sheets/{sheet_id}/data/{id}/
```

Returns a specific data row from a Google Sheet.

**Response:**

```json
{
  "id": 1,
  "sheet": 1,
  "row_number": 1,
  "row_data": {
    "column1": "value1",
    "column2": "value2"
  },
  "created_at": "2025-05-10T12:00:00Z",
  "updated_at": "2025-05-10T12:00:00Z"
}
```

## Error Responses

### Authentication Error

```json
{
  "detail": "Authentication credentials were not provided."
}
```

### Permission Error

```json
{
  "detail": "You do not have permission to perform this action."
}
```

### Not Found Error

```json
{
  "detail": "Not found."
}
```

### Validation Error

```json
{
  "field_name": [
    "Error message"
  ]
}
```

### Google API Error

```json
{
  "error": "Error message from Google API"
}
```