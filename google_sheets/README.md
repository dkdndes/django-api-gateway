# Google Sheets Integration for Django API Gateway

This app provides integration with Google Sheets for the Django API Gateway project. It allows users to connect to their Google Sheets, fetch data, and display it in a web interface.

## Features

- Connect to Google Sheets using OAuth2 authentication
- View and manage connected Google Sheets
- Fetch and display data from Google Sheets
- RESTful API for programmatic access to Google Sheets data

## Setup Instructions

### 1. Install Required Packages

```bash
pip install django-allauth google-auth google-api-python-client drf-nested-routers
```

### 2. Create Google OAuth2 Credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Navigate to "APIs & Services" > "Credentials"
4. Click "Create Credentials" > "OAuth client ID"
5. Select "Web application" as the application type
6. Add the following authorized redirect URIs:
   - `http://localhost:8000/accounts/google/login/callback/`
   - `https://yourdomain.com/accounts/google/login/callback/` (for production)
7. Click "Create" and note your Client ID and Client Secret

### 3. Configure Django Settings

Update your `settings.py` file with the following:

```python
# Google OAuth2 Settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive',
        ],
        'AUTH_PARAMS': {
            'access_type': 'offline',
        },
        'APP': {
            'client_id': 'YOUR_GOOGLE_CLIENT_ID',
            'secret': 'YOUR_GOOGLE_CLIENT_SECRET',
            'key': ''
        }
    }
}
```

Replace `YOUR_GOOGLE_CLIENT_ID` and `YOUR_GOOGLE_CLIENT_SECRET` with the values from the Google Cloud Console.

### 4. Configure Django Admin

1. Log in to the Django admin interface
2. Go to "Sites" and update the domain name to your actual domain (e.g., `localhost:8000` for development)
3. Go to "Social applications" and add a new application:
   - Provider: Google
   - Name: Google
   - Client ID: Your Google Client ID
   - Secret key: Your Google Client Secret
   - Sites: Add your site from the available sites

### 5. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Start the Development Server

```bash
python manage.py runserver
```

## Usage

1. Navigate to `/sheets/` to access the Google Sheets interface
2. Click "Login with Google" to authenticate with your Google account
3. Once authenticated, you can add Google Sheets by providing the Sheet ID
4. View and manage your connected sheets from the dashboard

## API Endpoints

- `GET /sheets/api/sheets/` - List all Google Sheets
- `POST /sheets/api/sheets/` - Add a new Google Sheet
- `GET /sheets/api/sheets/{id}/` - Get details of a specific Google Sheet
- `PUT /sheets/api/sheets/{id}/` - Update a Google Sheet
- `DELETE /sheets/api/sheets/{id}/` - Delete a Google Sheet
- `POST /sheets/api/sheets/{id}/sync/` - Sync data from Google Sheets
- `GET /sheets/api/sheets/{id}/data/` - Get data from a specific Google Sheet

## Troubleshooting

### Common Issues

1. **Authentication Failed**: Make sure your Google OAuth credentials are correctly configured in both the Google Cloud Console and Django admin.

2. **Permission Denied**: Ensure that the Google account you're using has access to the Google Sheets you're trying to connect to.

3. **Invalid Sheet ID**: The Sheet ID is the part of the URL after `spreadsheets/d/` and before `/edit`. Make sure you're using the correct ID.

4. **API Quota Exceeded**: Google API has usage limits. If you're making too many requests, you might hit these limits. Consider implementing caching to reduce API calls.

### Getting Help

If you encounter any issues, please check the Django and Google API documentation, or open an issue in the project repository.