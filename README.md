# 💎 Premium Invoice Management System

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-green?style=for-the-badge&logo=flask&logoColor=white)
![Javascript](https://img.shields.io/badge/JavaScript-ES6-yellow?style=for-the-badge&logo=javascript&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen?style=for-the-badge)

> **An Enterprise-Grade, High-Performance Invoice Management Solution.**

This system is engineered for **silver trading businesses** and high-velocity retail environments. It combines a robust **Flask** backend with a stunning **Premium Glass UI** to deliver a seamless, intuitive, and visually captivating experience. Designed for reliability, speed, and modern aesthetics.

---

## ✨ Key Features

### 🔹 Advanced Customer CRM
*   **Centralized Profiles**: Create and manage detailed customer profiles with ease.
*   **Transaction History**: View complete purchase and payment history at a glance.
*   **Smart Search**: Instantly find customers and invoices with real-time filtering.

### 🔹 Intelligent Invoicing Engine
*   **Dual Calculation Modes**:
    *   **⚖️ Ready Mode**: Precision calculation based on Silver Weight × Market Rate.
    *   **⚒️ Mazduri Mode**: Labor-based calculation (Piece Count × Labor Rate).
*   **Real-Time Math**: Prices, totals, and balances update instantly as you type—no page reloads.
*   **Auto-Numbering**: Smart invoice ID generation ensures organized record-keeping.

### 🔹 Financial Management
*   **Multi-Payment Support**: Accept Cash, Bank Transfer, Cheque, and Mobile Wallets.
*   **Partial Payments**: Flexible payment tracking with advanced handling of deposits and remaining balances.
*   **Audit Logging**: comprehensive security logs track every system action for full accountability.

### 🔹 Premium User Experience
*   **Glassmorphism UI**: A visually stunning, translucent interface with blur effects and ambient lighting.
*   **Responsive Design**: Flawless experience across Desktop, Tablet, and Mobile devices.
*   **Interactive Dashboard**: dynamic charts and quick-action widgets for instant business insights.

### 🔹 Reporting & Export
*   **📄 PDF Generation**: Professional, branded invoices generated instantly for printing or sharing.
*   **📊 Excel Export**: One-click full database export for offline analysis and backup.

---

## 📸 Visual Tour

| **Executive Dashboard** | **Smart Invoice Creation** |
|:---:|:---:|
| <img src="screenshots/dashboard.png?raw=true" alt="Executive Dashboard" width="450"/> | <img src="screenshots/create_invoice.png?raw=true" alt="Invoice Creation" width="450"/> |
| *Real-time insights and quick actions* | *Instant calculations with dual-mode support* |

| **Glass Login Interface** | **Data Management** |
|:---:|:---:|
| <img src="screenshots/login.png?raw=true" alt="Glass Login" width="450"/> | <img src="screenshots/tables.png?raw=true" alt="Smart Tables" width="450"/> |
| *Secure, aesthetic access point* | *Filterable, sortable data grids* |

---

## 📂 Project Structure

A clean, modular architecture ensures maintainability and scalability.

```
premium-invoice-management-system/
├── backend/                # 🧠 Application Logic (Flask)
│   ├── app.py              # Main Application Entry Point
│   ├── models.py           # Database Models (SQLAlchemy)
│   ├── routes/             # API Endpoints & Blueprint Controllers
│   ├── utils.py            # Financial Calculations & Helpers
│   └── pdf_generator.py    # ReportLab PDF Generation Engine
├── frontend/               # 💎 Presentation Layer (Glass UI)
│   ├── css/theme.css       # Custom Glassmorphism Styles
│   ├── js/api.js           # Frontend-Backend Communication
│   └── index.html          # Main Dashboard Interface
├── data/                   # 💾 Persistence Layer
│   └── invoice.db          # SQLite Database (Auto-generated)
└── requirements.txt        # 📦 Dependency Definitions
```

---

## 🚀 Installation & Setup

Get up and running in minutes.

### Prerequisites
*   **Python 3.10+** installed on your system.
*   **Git** for version control.

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/premium-invoice-management-system.git
cd premium-invoice-management-system
```

### 2. Set Up Virtual Environment
Isolate dependencies to keep your system clean.

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 4. Launch the Application
**Option A: One-Click (Windows)**
Double-click the `start_server.bat` file included in the root directory.

**Option B: Manual Start**
```bash
python app.py
```

Access the system at: `http://localhost:5000`

---

## 📖 Usage Guide

### 1. Create a Customer
Navigate to **"Customers"** > **"Add New"**. Enter the client's details. This creates a profile that will be linked to all their future invoices.

### 2. Generate an Invoice
Go to **"New Invoice"**. Select the customer, choose the billing mode (**Ready** or **Mazduri**), and add items. The system calculates totals automatically. Click **"Save & Generate PDF"** to finalize.

### 3. Record Payments
In the **"Invoices"** view, select an unpaid invoice and click **"Add Payment"**. Enter the amount and method (e.g., Cash, Bank). The balance updates instantly.

### 4. Export Data
Use the **"Export Data"** button on the Dashboard to download the full database as an Excel file for reporting or backup.

---

## 🔮 Future Roadmap

We are constantly improving. Upcoming features include:

*   [ ] **Multi-User Role Management** (Admin/Staff access levels)
*   [ ] **Inventory Tracking Integration** (Auto-deduct stock)
*   [ ] **Dark/Light Mode Toggle**
*   [ ] **Automated Email Notifications** for invoices and receipts

---

## 📝 License

This project is licensed under the **MIT License**. You are free to use, modify, and distribute this software. See the [LICENSE](LICENSE) file for details.

---

## 👤 Author & Contact

**Developed by Syed Rasab Ul Haque**

*   📧 **Email**: rasab1781@gmail.com
*   💼 **LinkedIn**: [www.linkedin.com/in/rasab3922](https://www.linkedin.com/in/rasab3922)

---

<p align="center">
  <i>Built with ❤️ using <b>Flask</b>, <b>SQLite</b>, and <b>Glassmorphism Design</b>.</i>
</p>
