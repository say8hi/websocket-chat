# Chat Application
![Logo](./logo.jpg)

This is a real-time chat application built using FastAPI for the backend and React for the frontend. The application supports WebSocket communication for real-time messaging, with PostgreSQL for data storage and Redis for caching.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Environment Variables](#environment-variables)
- [Docker Setup](#docker-setup)
- [Usage](#usage)
- [License](#license)

## Features

- Real-time messaging using WebSockets
- User registration and authentication
- Message history retrieval
- Caching of messages using Redis
- Telegram bot integration for notifications
- Migrations with alembic

## Architecture

The application consists of several components:

- **Backend (FastAPI)**: Handles API requests, manages WebSocket connections, and interacts with the database.
- **Frontend (NodeJs)**: Provides the user interface for users to send and receive messages.
- **Database (PostgreSQL)**: Stores user data and chat messages.
- **Redis**: Caches messages for faster retrieval.
- **Nginx**: Serves as a reverse proxy for the frontend and backend services.
- **Celery**: Handles asynchronous tasks, such as sending notifications or processing messages.
- **Telegram Bot**: Notifies users of new messages or events.

## Getting Started

### Prerequisites

- Docker
- Docker Compose

### Clone the Repository

```bash
git clone https://github.com/say8hi/websocket-chat.git
cd websocket-chat
```
### Setup Environment Variables

Rename a `.env.example` to `.env` in the root directory and set the following variables::

```env
# Postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_USER=db_user
POSTGRES_PASSWORD=db_pass
POSTGRES_DB=db_name

# Redis
REDIS_HOST=redis
REDIS_PORT=4030
REDIS_PASSWORD=redis_pass

# Tg bot
BOT_TOKEN=bot_token
ADMINS=admin_id,admin_id
BOT_USERNAME=username_bot

# Secrets
AUTH_SECRET=secret_key
```

### Docker Setup

To run the application using Docker, execute the following command in the project root directory:

```bash
docker-compose up -d --build
```
This command will:
- Build all the services defined in `docker-compose.yml`.
- Start the backend, frontend, database, Redis cache, Nginx, Celery worker, and Telegram bot.

## Project Structure
```
/websocket-chat
│
├── backend                        # FastAPI backend code
│   ├── api                        # API routers for chat and user management
│   │   ├── chat.py                # Chat-related API endpoints
│   │   ├── __init__.py            # Package initializer
│   │   └── users.py               # User-related API endpoints
│   ├── config.py                  # Application configuration
│   ├── database                   # Database models and ORM setup
│   │   ├── database.py            # Database connection logic
│   │   ├── models.py              # SQLAlchemy models for users and messages
│   │   └── orm.py                 # Async ORM operations
│   ├── Dockerfile                 # Dockerfile for the backend
│   ├── main.py                    # Application entry point
│   ├── misc                       # Miscellaneous utilities
│   │   └── connection_manager.py  # WebSocket connection manager
│   ├── requirements.txt           # Python dependencies
│   ├── schemas                    # Pydantic models for request and response validation
│   │   ├── messages.py            # Message-related Pydantic models
│   │   ├── users.py               # User-related Pydantic models
│   └── utils                      # Utility functions for authentication and caching
│       ├── auth.py                # Functions for user authentication
│       └── cache.py               # Functions for caching with Redis
│
├── celery                         # Celery worker code for asynchronous tasks
│   ├── app.py                     # Celery application setup
│   ├── tasks.py                   # Task definitions
│   ├── Dockerfile                 # Dockerfile for the Celery worker
│   └── requirements.txt           # Python dependencies for Celery
│
├── frontend                       # React frontend code
│   ├── Dockerfile                 # Dockerfile for the frontend
│   ├── package.json               # Node.js dependencies
│   ├── public                     # Static files for React
│   │   ├── index.html             # Main HTML file
│   │   ├── script.js              # JavaScript entry point
│   │   └── style.css              # Stylesheet
│   └── server.js                  # Express server for the frontend
│
├── nginx                          # Nginx configuration for reverse proxy
│   ├── default.conf               # Nginx configuration file
│   └── Dockerfile                 # Dockerfile for Nginx
│
├── tg_bot                         # Telegram bot code
│   ├── bot.py                     # Main bot logic
│   ├── config.py                  # Bot configuration
│   ├── Dockerfile                 # Dockerfile for the bot
│   ├── filters                    # Filters for processing messages
│   ├── handlers                   # Handlers for various bot commands
│   ├── keyboards                  # Custom keyboards for Telegram interactions
│   ├── middlewares                # Middleware for bot processing
│   ├── requirements.txt           # Python dependencies for the bot
│   ├── states                     # State management for bot conversation
│   └── utils                      # Utility functions for bot operations
│
├── migrations                     # Database migration scripts
│   ├── env.py                     # Migration environment setup
│   ├── versions                   # Individual migration versions
│   └── script.py.mako             # Migration script template
│
├── alembic.ini                    # Alembic configuration for database migrations
├── docker-compose.yml             # Docker Compose configuration
├── README.md                      # Project documentation
└── .env                           # Environment variables
```
## Environment Variables

The application relies on the following environment variables defined in the `.env` file:

- `POSTGRES_HOST`: Name of the PostgreSQL database service in the `docker-compose.yml`.
- `POSTGRES_PORT`: Port of the PostgreSQL database service in the `docker-compose.yml`.
- `POSTGRES_DB`: Name of the PostgreSQL database.
- `POSTGRES_USER`: PostgreSQL user.
- `POSTGRES_PASSWORD`: PostgreSQL password.
- `REDIS_HOST`: Name of the Redis service in the `docker-compose.yml`.
- `REDIS_PORT`: Port of the Redis service in the `docker-compose.yml`.
- `REDIS_PASSWORD`: Password for Redis.
- `BOT_TOKEN`: Bot token from the [@botfather](https://t.me/botfather).
- `ADMINS`: Telegram ids of admins for the bot.
- `BOT_USERNAME`: Username of the bot (for creating links like https://t.me/{bot_username}).
- `AUTH_SECRET`: Secret key for JWT authentication.

## Usage

Once the services are up and running, you can access the application at:
- **Nginx**: [http://localhost:80](http://localhost:80)

Without proxy:
- **Frontend**: [http://localhost:3000](http://localhost:3000)
- **Backend API**: [http://localhost:8000](http://localhost:8000)

### Accessing the Database

You can connect to the PostgreSQL database using a client like pgAdmin or any SQL client using the following credentials:

- **Host**: `localhost`
- **Port**: `<port_from_the_docker_compose.yml (5432 by default)>`
- **Database**: `<your_db_name>`
- **User**: `<your_db_user>`
- **Password**: `<your_db_password>`

### Interacting with the API

Also all endpoints can be found here: [http://localhost:8000/docs](http://localhost:8000/docs)
The backend API supports several endpoints for user management and messaging. Here are some key endpoints:

#### User Registration

- **Endpoint**: `POST /users/register`
- **Body**: 
    ```json
    {
        "username": "your_username",
        "password": "your_password"
    }
    ```
- **Response**: 
    ```json
    {
        "status": "string status"
        "data": {
            "token": "jwt token"
            "user_id": "user_id"
        }
    }
    ```

#### User Login

- **Endpoint**: `POST /users/login`
- **Body**: 
    ```json
    {
        "username": "your_username",
        "password": "your_password"
    }
    ```
- **Response**: 
    ```json
    {
        "status": "string status"
        "data": {
            "token": "jwt token"
            "user_id": "user_id"
        }
    }
    ```
#### Get all users

- **Endpoint**: `GET /users/`
- **Headers**:
  ```json
  {
    "Authorization": "Bearer {jwt_token}",
  }
  ```
- **Body**: 
    ```json
    {
        "username": "your_username",
        "password": "your_password"
    }
    ```
- **Response**: 
    ```json
    {
      [
        {"id": 1, "username": "username"...},
        {"id": 2, "username": "username2"...}
      ]
    }
    ```
#### Connect telegram account

- **Endpoint**: `POST /users/connect-tg`
- **Body**: 
    ```json
      {
        "user_id": 0,
        "tg_user_id": 0
      }
    ```
- **Response**: 
    ```json
    {
      "status": "string",
      "data": {}
    }
    ```
#### Websocket for live-chatting
- **Endpoint**: `/chat/ws/{sender_id}/{receiver_id}`

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
