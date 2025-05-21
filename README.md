# Spectre Clothing: Clothing Boutique Inventory and Order Management System

A comprehensive inventory and order management system designed for a clothing boutique.

## Overview

Spectre Clothing is a web-based application designed to help a small to medium-sized clothing boutique efficiently manage its product catalog, inventory levels, customer orders, and supplier information. The system aims to replace manual processes, reduce errors, improve operational efficiency, and provide better insights for business decision-making.

## Features

- **User Management**: Role-based access control (Admin, Stock Manager, Sales Staff)
- **Product Management**: CRUD operations for products with categories and images
- **Inventory Management**: Track stock levels for product variants (size/color)
- **Order Management**: Create and process customer orders
- **Supplier Management**: Manage supplier information
- **Reporting & Dashboard**: Sales reports and analytics

## Technology Stack

- **Backend**: Python with Django framework
- **Database**: MySQL
- **Frontend**: HTML, Tailwind CSS, JavaScript

## Installation and Setup

### Prerequisites

- Python 3.8 or higher
- MySQL server
- Node.js and npm (for Tailwind CSS)

### Setup Instructions

1. Clone the repository
2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Set up the MySQL database:
   - Create a database named `spectre_clothing_db`
   - Configure database connection in `settings.py`
5. Apply migrations:
   ```
   python manage.py migrate
   ```
6. Initialize data:
   ```
   python manage.py initialize_data
   ```
7. Start the development server:
   ```
   python manage.py runserver
   ```

## Default Users

After running the initialize_data command, you'll have access to these users:

- **Admin**: Username: `admin`, Password: `admin123`
- **Owner**: Username: `jeanny`, Password: `jeanny123`
- **Stock Manager**: Username: `joven`, Password: `joven123`
- **Sales Staff**: Username: `villy`, Password: `villy123`

## Project Structure

```
spectre_clothing/
├── accounts/         # User management and authentication
├── dashboard/        # Dashboard and reporting
├── inventory/        # Inventory management
├── orders/           # Order processing
├── products/         # Product catalog
├── suppliers/        # Supplier information
├── static/           # Static files (CSS, JS)
├── templates/        # HTML templates
├── media/            # Uploaded images
└── spectre_clothing/ # Project settings
```

## License

This project is for educational purposes only.

## Contributors

- [Your Team Name/Second-Year Students]
