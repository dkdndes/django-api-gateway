# Google Sheets Models Documentation

This document provides detailed information about the models used in the Google Sheets integration app.

## GoogleSheet

The `GoogleSheet` model represents a connection to a Google Sheet.

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `user` | ForeignKey | The user who owns this Google Sheet connection |
| `name` | CharField | A user-friendly name for the Google Sheet |
| `sheet_id` | CharField | The Google Sheet ID (from the URL) |
| `description` | TextField | Optional description of the Google Sheet |
| `created_at` | DateTimeField | When the connection was created |
| `updated_at` | DateTimeField | When the connection was last updated |

### Methods

#### `sync_data()`

Fetches data from the Google Sheet and stores it in the database.

**Returns:** A tuple containing (success_status, message)

#### `get_sheet_data()`

Retrieves the sheet data from the database.

**Returns:** A list of dictionaries representing the sheet data

## SheetData

The `SheetData` model represents a row of data from a Google Sheet.

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `sheet` | ForeignKey | The GoogleSheet this data belongs to |
| `row_number` | IntegerField | The row number in the Google Sheet |
| `row_data` | JSONField | The data from the row as a JSON object |
| `created_at` | DateTimeField | When the row data was created |
| `updated_at` | DateTimeField | When the row data was last updated |

### Methods

#### `get_headers()`

Returns a list of column headers for the sheet.

**Returns:** A list of strings representing the column headers

#### `get_value(column_name)`

Gets the value for a specific column in this row.

**Parameters:**
- `column_name` (str): The name of the column

**Returns:** The value for the specified column, or None if not found