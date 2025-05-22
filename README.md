# E-Commerce Application

## Overview
This is a Python Flask e-commerce application with the following core functionalities:
- User registration and authentication with OTP verification
- Password management (change password, forgot password)
- Product catalog with images and descriptions
- Shopping cart functionality
- Checkout and payment processing with Stripe integration

## Features

### User Authentication
- Registration with email and password
- Login with username/password + OTP verification
- Change password functionality
- Forgot password with email reset link

### Product Management
- Browse product catalog with pagination
- View detailed product information
- Product images and descriptions
- Admin interface for product management

### Shopping Experience
- Add products to cart
- Update quantities or remove items
- View cart contents and total
- Secure checkout process

### Payment Processing
- Integration with Stripe payment gateway
- Order history tracking
- Payment confirmation

## Installation

1. Clone the repository:
```
git clone <repository-url>
cd e-commerce-app
```

2. Create and activate a virtual environment:
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```
pip install -r requirements.txt
```

4. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Update the values in `.env` with your configuration

5. Run the application:
```
python run.py
```

6. Access the application at http://localhost:5000

## Project Structure
```
app/
├── __init__.py          # Application factory
├── models/              # Database models
│   ├── user.py
│   ├── product.py
│   ├── cart.py
│   └── order.py
├── routes/              # Route handlers
│   ├── auth.py
│   ├── main.py
│   ├── products.py
│   └── cart.py
├── static/              # Static assets
│   ├── css/
│   ├── js/
│   ├── images/
│   └── product_images/
├── templates/           # HTML templates
│   ├── auth/
│   ├── main/
│   ├── products/
│   ├── cart/
│   └── admin/
└── utils/               # Utility functions
    └── auth_utils.py
```

## Technologies Used
- Python 3.8+
- Flask web framework
- SQLAlchemy ORM
- Flask-Login for authentication
- PyOTP for OTP generation
- Stripe for payment processing
- Bootstrap 5 for frontend styling