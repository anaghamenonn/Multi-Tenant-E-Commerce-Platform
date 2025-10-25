# ﻿🛍️ Multi-Tenant-E-Commerce-Platform

## Overview

A fully functional **multi-tenant e-commerce backend** built using **Django REST Framework**, supporting role-based access, JWT authentication, and PostgreSQL database, deployed on **Render (Free Tier)**.

## Features

### 🌐 Multi-Tenant Architecture
- Custom middleware (`TenantMiddleware`) to identify tenant via:
  - Authenticated user's vendor
  - Request header `X-Tenant-ID`
- Data isolation between vendors.

### 👥 Role-Based Access Control
- Custom `User` model with roles:
  - `admin` – Platform-level access  
  - `owner` – Vendor-level owner  
  - `staff` – Vendor employee  
  - `customer` – Customer linked to a vendor

### 🔐 JWT Authentication
- Implemented using `rest_framework_simplejwt`
- Custom token includes:
  - `role`
  - `tenant_id`
  - `username`

### 🧩 Core Entities
- **Vendor** – Represents a store or tenant  
- **User** – Custom user model with role and vendor link  
- **Product** – Linked to vendor and assigned staff  
- **Customer** – Linked to vendor and user  
- **Order** / **OrderItem** – Linked to customer and vendor  

### 🛠️ API Endpoints

All endpoints can be tested via the included **Postman Collection** (`Multi-Tenant E-Commerce.postman_collection.json`).  
Replace `{{base_url}}` with the deployed URL and login first to obtain `{{token}}` for authorization.

| Endpoint | Method | Description | Access Role |
|----------|--------|-------------|-------------|
| `/api/auth/register/` | POST | Register new user | All |
| `/api/auth/login/` | POST | Obtain JWT token | All |
| `/vendors/` | GET/POST | Manage vendors | Admin only |
| `/products/` | CRUD | Manage products | Owner / Staff |
| `/orders/` | CRUD | Manage orders | Owner / Staff / Customer |
| `/orders/place/` | POST | Place a new order | Customer |

> **Note:** Staff can only view products assigned to them. Owners can view all products under their vendor. Customers can place orders linked to their vendor.


## Tech Stack

- **Backend:** Django, Django REST Framework  
- **Database:** PostgreSQL  
- **Authentication:** JWT (SimpleJWT)  
- **Hosting:** Render (Free Tier)  
- **Static Files:** WhiteNoise  
- **Environment Variables:** python-dotenv  
- **Migrations & Build:** Automated via `build.sh`  

---

## Setup Instructions (Local Development)

### 1. Clone the Repository
```bash
git clone https://github.com/anaghamenonn/Multi-Tenant-E-Commerce-Platform.git
cd Multi-Tenant-E-Commerce-Platform
```
### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```
### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
### 4. Configure Environment Variables
Create a .env file in the project root:
```bash
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=postgresql://<user>:<password>@<host>:<port>/<dbname>
ALLOWED_HOSTS=localhost,127.0.0.1
```
### 5. Run Migrations & Start Server
```bash
python manage.py migrate
python manage.py runserver
```

## Deployment (Render)
- build.sh handles installation, migration, and static file collection.
- **Hosting:** Render (Free Tier)  
- PostgreSQL database configured on Render (Free Tier).
- Environment variables set in the Render Dashboard.
- Live API URL: https://multi-tenant-e-commerce-platform.onrender.com

## Testing Instructions
- Import the Postman Collection in Postman(Json file is in root dir)
- Replace {{base_url}} with the live deployment URL.
- Register and login users to obtain {{token}} for authorized requests.
- Test all endpoints using the collection; it covers:
   - Vendor creation (Admin)
   - Owner, Staff, Customer registration
   - Product management
   - Order placement and listing
All endpoints and example requests are fully documented in the collection.

## Author
Anagha P H
Software Developer  
📧 Email: anaghamenon7377@gmail.com
