# Geocaching Adventure App

A full-stack web application that lets users explore a virtual world of monsters and riddles.
The project uses a **FastAPI** backend with a **React** frontend, served through **Docker** containers for production deployment.

### Note from Dor:
Hey guys, welcome to my game :) <br>
This is a work in progress. 
As much as I really want to turn it into an actual game, I'm working on it alone and with no budget (using only free-version ChatGPT), 
so it currently is at a showcasing-my-abilities level.
To keep it free, I'm "deploying" it locally and access it using ngrok, so at this point it's up only while my computer is on.
If you want to try, either clone the repo, or contact me so I run it.<br>
Enjoy!

## ⚙️ Tech Stack
### 🧠 Backend

FastAPI — modern async Python web framework

SQLAlchemy — ORM for PostgreSQL

Alembic — database migrations

PostgreSQL — persistent data storage

JWT Authentication — access + HttpOnly refresh tokens

Gunicorn + Uvicorn — production WSGI server

### 💎 Frontend

React (CRA)

React Router DOM — client-side routing

Leaflet / Google Maps API — interactive map

Context API — Auth & Location management

Nginx — static file serving for production

### 🐳 Deployment

Docker Compose — orchestrates backend, frontend, and database

Nginx reverse proxy — single entry point for requests

Ready for deployment to AWS EC2 / Oracle Cloud / Google Cloud

## 🏗️ Project Structure
```
project-root/
│
├── src/
│   ├── backend/
│   │   ├── main.py
│   │   ├── models/
│   │   ├── routes/
│   │   ├── services/
│   │   ├── database.py
│   │   ├── auth/
│   │   └── enemies/
│   │
│   └── frontend/
│       ├── src/
│       ├── public/
│       ├── package.json
│       └── nginx.conf
│
├── Dockerfile.backend
├── Dockerfile.frontend
├── docker-compose.yml
├── nginx.conf
└── README.md
```

## 🚀 Deploying the game
1. Clone the repository
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>

2. Environment variables
Use .env.example to generate a .env, and place it in the project root.
Create a copy of this .env and place it in /src/frontend
(I know, I know, uniting them is on the to-do list).

3. Build & run all services
docker compose up -d --build

## Other stuff

### Database migrations
This app uses Alembic for database migrations.
The backend validates SQLAlchemy models against the actual database on startup, 
and will prevent you from starting the service if there's a mismatch.


To generate a migration plan:
alembic revision --autogenerate -m "Migration message here"

To execute the migration:
alembic upgrade head

### Services:

🧠 backend → http://localhost:8000

💎 frontend → http://localhost

🐘 Postgres → http://localhost:5432

### Rebuild only one service
docker compose build frontend

### View logs
docker compose logs -f backend

## 🧰 Backend Development

To run locally (without Docker):

Build the database service:
docker compose build db


Run the backend with uvicorn:
cd src/backend
uvicorn main:app --reload

### Interactive docs:

Swagger UI → http://localhost:8000/docs

ReDoc → http://localhost:8000/redoc

## Run database migrations:

alembic upgrade head

## 🎨 Frontend Development

Run locally:

cd src/frontend
npm install
npm start


Frontend dev server → http://localhost:3000

(connected to FastAPI backend at port 8000)

## 🧙‍♂️ Developer Notes

The app supports both logged-in users (for riddles & rewards)
and guests (map exploration).

Enemies appear dynamically and expire after 24h.

Backend is stateless and easy to scale horizontally.

Designed for minimal EC2 footprint (≈300–500 MB total image size).