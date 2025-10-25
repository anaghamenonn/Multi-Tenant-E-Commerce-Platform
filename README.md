# ﻿🛍️ Multi-Tenant-E-Commerce-Platform

## Overview

This project is a multi-tenant e-commerce backend where multiple vendors can host their stores on a shared platform. Each vendor manages its own products, orders, and customers independently using role-based access control.

## ⚙️ Tech Stack

Django 5.x
Django REST Framework
SimpleJWT for authentication
MySQL (via XAMPP)
Python 3.10+

## 🧩 Setup Instructions

### 1. Clone repo
git clone https://github.com/anaghamenonn/Multi-Tenant-E-Commerce-Platform.git  
cd multi-tenant-ecommerce

### 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # on Windows

### 3. Install dependencies
pip install -r requirements.txt

### 4. Configure database in settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ecommerce',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}

### 5. Run migrations
python manage.py makemigrations
python manage.py migrate

### 6. Run server
python manage.py runserver

