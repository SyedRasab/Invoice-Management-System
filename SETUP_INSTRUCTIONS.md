# Setup Instructions - Invoice Management System

This guide will help you set up and run the Invoice Management System on your local machine.

## Prerequisites

Before you begin, ensure you have the following installed:

1. **Python 3.8 or higher**
   - Download from: https://www.python.org/downloads/
   - During installation, check "Add Python to PATH"

2. **Modern Web Browser**
   - Google Chrome, Mozilla Firefox, or Microsoft Edge

## Step-by-Step Setup

### Step 1: Verify Python Installation

Open Command Prompt (Windows) or Terminal (Mac/Linux) and run:

```bash
python --version
```

You should see something like `Python 3.8.x` or higher.

### Step 2: Navigate to Project Directory

```bash
cd C:\Users\rasab\OneDrive\Desktop\demoooo
```

### Step 3: Install Backend Dependencies

Navigate to the backend folder:

```bash
cd backend
```

Install required Python packages:

```bash
pip install -r requirements.txt
```

This will install:
- Flask (web framework)
- Flask-CORS (cross-origin requests)
- SQLAlchemy (database)
- ReportLab (PDF generation)
- Pandas (data processing)
- OpenPyXL (Excel export)

**Note**: Installation may take 2-5 minutes depending on your internet connection.

### Step 4: Initialize the Database

The database will be created automatically when you first run the application. To manually initialize:

```bash
python database.py
```

You should see: `Database initialized successfully!`

### Step 5: Start the Backend Server

```bash
python app.py
```

You should see:

```
==================================================
Invoice Management System - Backend Server
==================================================
Server running at: http://0.0.0.0:5000
API Documentation:
  - GET  /api/customers
  - POST /api/customers
  ...
==================================================
```

**Important**: Keep this terminal window open! The server must be running for the application to work.

### Step 6: Open the Frontend

1. Open a new File Explorer window
2. Navigate to: `C:\Users\rasab\OneDrive\Desktop\demoooo\frontend`
3. Double-click `index.html`

The application should open in your default web browser!

## Using the Application

### First Time Setup

1. **Create Your First Customer**
   - Click "Create New Invoice"
   - Enter customer name and contact
   - Fill in invoice details
   - Click "Generate Invoice"

2. **View Generated Invoice**
   - After creating an invoice, you'll see a preview
   - Click "Download PDF" to save the invoice

3. **Explore Other Features**
   - View all customers
   - Browse invoices
   - Export data to Excel

## Common Issues and Solutions

### Issue 1: "pip is not recognized"

**Solution**: Python was not added to PATH during installation.

**Fix**:
1. Reinstall Python
2. Check "Add Python to PATH" during installation
3. Or manually add Python to PATH

### Issue 2: "Port 5000 is already in use"

**Solution**: Another application is using port 5000.

**Fix**:
1. Open `backend/config.py`
2. Change `PORT = 5000` to `PORT = 5001`
3. Open `frontend/js/app.js`
4. Change `const API_BASE_URL = 'http://localhost:5000/api'` to `http://localhost:5001/api`
5. Restart the backend server

### Issue 3: Frontend can't connect to backend

**Symptoms**: 
- Dashboard shows "0" for all statistics
- Creating invoice shows error

**Solution**:
1. Ensure backend server is running (check terminal)
2. Open browser console (Press F12)
3. Look for error messages
4. Verify the backend URL in `frontend/js/app.js`

### Issue 4: PDF download doesn't work

**Solution**:
1. Check if ReportLab is installed: `pip install reportlab`
2. Ensure the `data/customers` folder exists
3. Check browser's download settings

### Issue 5: Excel export fails

**Solution**:
1. Ensure pandas and openpyxl are installed
2. Check if `data` folder exists
3. Verify write permissions

## File Locations

### Database
- Location: `backend/invoice_system.db`
- This file stores all your data

### Customer Data
- Location: `data/customers/`
- Each customer has a folder with their invoices

### Invoice PDFs
- Location: `data/customers/{customer_id}/invoices/`

### Excel Exports
- Location: `data/`
- Named: `export_YYYYMMDD_HHMMSS.xlsx`

## Stopping the Application

1. **Stop Backend Server**:
   - Go to the terminal where the server is running
   - Press `Ctrl + C`

2. **Close Frontend**:
   - Simply close the browser tab

## Restarting the Application

1. Open terminal in `backend` folder
2. Run: `python app.py`
3. Open `frontend/index.html` in browser

## Backup Your Data

To backup your data:

1. **Database**: Copy `backend/invoice_system.db`
2. **Customer Files**: Copy entire `data/customers/` folder
3. **Exports**: Copy any Excel files from `data/` folder

## Upgrading to Production

For production deployment:

1. **Change Database**: Migrate to MySQL or PostgreSQL
2. **Add Security**: Implement user authentication
3. **Use Web Server**: Deploy with Gunicorn + Nginx
4. **Enable HTTPS**: Use SSL certificates
5. **Cloud Storage**: Store PDFs in cloud storage

## Getting Help

If you encounter issues:

1. Check this guide first
2. Review error messages in terminal
3. Check browser console (F12) for frontend errors
4. Verify all dependencies are installed
5. Ensure Python version is 3.8+

## System Requirements

### Minimum Requirements
- **OS**: Windows 10, macOS 10.14, or Linux
- **RAM**: 2 GB
- **Storage**: 500 MB free space
- **Python**: 3.8 or higher

### Recommended Requirements
- **OS**: Windows 11, macOS 12+, or Linux
- **RAM**: 4 GB or more
- **Storage**: 1 GB free space
- **Python**: 3.10 or higher

## Next Steps

Once the system is running:

1. Create a few test invoices
2. Explore customer management
3. Try filtering invoices
4. Export data to Excel
5. Customize company information in `backend/config.py`

---

**Congratulations! Your Invoice Management System is ready to use!** 🎉
