# Library Management System

This project is a comprehensive library management system implemented using Django REST Framework, which allows users to manage books, borrowings, payments, and notifications within a library.

## Setup Instructions

1. **Clone the repository:**
```bash
git clone https://github.com/EugeneProtsenko/libarary_mate_project
cd library-management-system
```

2. **Create and activate a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate # Unix/Mac
venv\Scripts\activate # Windows
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**

- Create a `.env` file in the project root directory.
- Add the required environment variables, such as `SECRET_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_PUBLIC_KEY`, `TELEGRAM_CHAT_ID` and `TELEGRAM_API_TOKEN`.

5. **Run database migrations:**
```bash
python manage.py migrate
```

6. **Start the Django development server:**
```bash
python manage.py runserver
```

7. **Access the application at `http://localhost:8000`.**

## Using Celery with Docker

To use Celery for task scheduling, follow these steps:

1. **Build the Docker image:**
```bash
docker-compose build
```

2. **Start the Docker containers:**
```bash
docker-compose up -d
```

3. **Celery worker and beat services will be started along with the Django application.**

## API Endpoints

- **Books**: `/api/books/`
- GET: Retrieve all books
- POST: Create a new book
- **Users**: `/api/users/`
- GET: Retrieve user details
- POST: Create a new user
- **Borrowings**: `/api/borrowings/`
- GET: Retrieve all borrowings
- POST: Create a new borrowing
- **Payments**: `/api/payments/`
- GET: Retrieve all payments
- POST: Create a new payment

## Testing

To run tests, use the following command:
```bash
python manage.py test
```
