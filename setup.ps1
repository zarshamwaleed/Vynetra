# Vynetra Setup Script
Write-Host "Setting up Vynetra..." -ForegroundColor Cyan

# 1. Create directory structure
Write-Host "Creating directory structure..." -ForegroundColor Yellow
$dirs = @(
    "backend\app\api",
    "backend\app\api\v1\endpoints",
    "backend\app\core",
    "backend\app\models",
    "backend\app\services",
    "backend\app\utils",
    "backend\app\agents",
    "backend\app\mcp",
    "backend\alembic\versions",
    "backend\tests",
    "backend\scripts",
    "frontend\src\app",
    "frontend\src\components",
    "frontend\src\lib",
    "frontend\src\styles",
    "frontend\src\types",
    "frontend\src\utils",
    "frontend\src\app\api",
    "frontend\public",
    "docker\nginx",
    "docker\postgres",
    "docker\redis",
    "scripts",
    "docs",
    ".github\workflows",
    "generated\ppt",
    "generated\pdf",
    "generated\notes",
    "generated\animations",
    "generated\diagrams",
    "generated\manim",
    "generated\images"
)

foreach ($dir in $dirs) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
}
Write-Host "Directory structure created" -ForegroundColor Green

# 2. Create .env file
Write-Host "Creating .env file..." -ForegroundColor Yellow
$envContent = @"
# Project
PROJECT_NAME=Vynetra
PROJECT_VERSION=1.0.0
ENVIRONMENT=development
DEBUG=True

# Backend
BACKEND_PORT=8000
BACKEND_HOST=0.0.0.0
SECRET_KEY=dev-secret-key-change-in-production-12345

# Frontend
FRONTEND_PORT=3000
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# Database
DATABASE_URL=postgresql+asyncpg://vynetra:vynetra123@postgres:5432/vynetra
POSTGRES_USER=vynetra
POSTGRES_PASSWORD=vynetra123
POSTGRES_DB=vynetra

# Redis
REDIS_URL=redis://redis:6379/0

# LLM Configuration
LLM_PROVIDER=GROQ
GROQ_API_KEY=your-groq-api-key-here
GOOGLE_API_KEY=your-google-api-key-here
OLLAMA_BASE_URL=http://ollama:11434
OPENROUTER_API_KEY=your-openrouter-api-key-here

# MCP Servers
MCP_FILESYSTEM_PORT=8001
MCP_MANIM_PORT=8002
MCP_POWERPOINT_PORT=8003
MCP_PDF_PORT=8004
MCP_BROWSER_PORT=8005

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Storage
STORAGE_PATH=./generated
ASSETS_PATH=./assets

# Security
CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
ALLOWED_HOSTS=["localhost","127.0.0.1"]
"@
$envContent | Out-File -FilePath .env -Encoding utf8
Write-Host ".env file created" -ForegroundColor Green

# 3. Create docker-compose.yml
Write-Host "Creating docker-compose.yml..." -ForegroundColor Yellow
$composeContent = @"
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
      target: development
    container_name: vynetra-backend
    ports:
      - "${BACKEND_PORT:-8000}:8000"
    environment:
      - ENVIRONMENT=${ENVIRONMENT:-development}
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - GROQ_API_KEY=${GROQ_API_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - OLLAMA_BASE_URL=${OLLAMA_BASE_URL}
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
      - SECRET_KEY=${SECRET_KEY}
      - STORAGE_PATH=/app/generated
      - CORS_ORIGINS=${CORS_ORIGINS}
    volumes:
      - ./backend:/app
      - ./generated:/app/generated
      - ./assets:/app/assets
      - /app/__pycache__
      - /app/.pytest_cache
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - vynetra-network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      target: development
    container_name: vynetra-frontend
    ports:
      - "${FRONTEND_PORT:-3000}:3000"
    environment:
      - NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL:-http://localhost:8000/api/v1}
    volumes:
      - ./frontend:/app
      - /app/node_modules
      - /app/.next
    depends_on:
      - backend
    networks:
      - vynetra-network

  postgres:
    image: postgres:16-alpine
    container_name: vynetra-postgres
    environment:
      - POSTGRES_USER=${POSTGRES_USER:-vynetra}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-vynetra123}
      - POSTGRES_DB=${POSTGRES_DB:-vynetra}
      - PGDATA=/var/lib/postgresql/data/pgdata
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - vynetra-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: vynetra-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - vynetra-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  ollama:
    image: ollama/ollama:latest
    container_name: vynetra-ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    environment:
      - OLLAMA_HOST=0.0.0.0
      - OLLAMA_ORIGINS=*
    networks:
      - vynetra-network

networks:
  vynetra-network:
    driver: bridge

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
  ollama_data:
    driver: local
"@
$composeContent | Out-File -FilePath docker-compose.yml -Encoding utf8
Write-Host "docker-compose.yml created" -ForegroundColor Green

# 4. Create backend files
Write-Host "Creating backend files..." -ForegroundColor Yellow

# backend/Dockerfile
$backendDockerfile = @"
FROM python:3.11-slim AS base

RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    g++ \
    graphviz \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

FROM base AS development

COPY requirements-dev.txt .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements-dev.txt

COPY . .

RUN mkdir -p /app/generated /app/assets /app/logs

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
"@
$backendDockerfile | Out-File -FilePath backend\Dockerfile -Encoding utf8

# backend/requirements.txt
$requirements = @"
fastapi==0.115.6
uvicorn[standard]==0.34.0
pydantic==2.10.4
pydantic-settings==2.6.1
python-dotenv==1.0.1
sqlalchemy==2.0.36
alembic==1.14.1
psycopg2-binary==2.9.10
asyncpg==0.30.0
redis==5.2.1
python-pptx==1.0.2
reportlab==4.2.5
markdown==3.7
httpx==0.28.1
aiofiles==24.1.0
python-multipart==0.0.20
"@
$requirements | Out-File -FilePath backend\requirements.txt -Encoding utf8

# backend/requirements-dev.txt
$requirementsDev = @"
-r requirements.txt
black==24.10.0
isort==5.13.2
flake8==7.1.1
pytest==8.3.4
pytest-asyncio==0.24.0
pytest-cov==6.0.0
httpx==0.28.1
"@
$requirementsDev | Out-File -FilePath backend\requirements-dev.txt -Encoding utf8

# backend/app/main.py
$mainPy = @"
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import setup_logging
from app.api.v1.api import api_router

setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Vynetra...")
    yield
    logger.info("Shutting down Vynetra...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="AI Presentation Creator using Multi-Agent AI and MCP",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"name": settings.PROJECT_NAME, "version": settings.PROJECT_VERSION, "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "services": {"api": "ok"}}
"@
$mainPy | Out-File -FilePath backend\app\main.py -Encoding utf8

# backend/app/core/config.py
$configPy = @"
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True)
    
    PROJECT_NAME: str = "Vynetra"
    PROJECT_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    BACKEND_PORT: int = 8000
    SECRET_KEY: str = Field(default="dev-secret-key", min_length=32)
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    DATABASE_URL: str = "postgresql+asyncpg://vynetra:vynetra123@postgres:5432/vynetra"
    REDIS_URL: str = "redis://redis:6379/0"
    LLM_PROVIDER: str = "GROQ"
    GROQ_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    OLLAMA_BASE_URL: str = "http://ollama:11434"
    STORAGE_PATH: str = "./generated"
    LOG_LEVEL: str = "INFO"
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

settings = Settings()
"@
$configPy | Out-File -FilePath backend\app\core\config.py -Encoding utf8

# backend/app/core/logging.py
$loggingPy = @"
import logging
import sys
from app.core.config import settings

def setup_logging():
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    logging.info("Logging configured")
"@
$loggingPy | Out-File -FilePath backend\app\core\logging.py -Encoding utf8

# backend/app/api/v1/api.py
$apiPy = @"
from fastapi import APIRouter
from app.api.v1.endpoints import health

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
"@
$apiPy | Out-File -FilePath backend\app\api\v1\api.py -Encoding utf8

# backend/app/api/v1/endpoints/health.py
$healthPy = @"
from fastapi import APIRouter
router = APIRouter()

@router.get("")
async def health_check():
    return {"status": "healthy", "services": {"api": "ok"}}

@router.get("/ping")
async def ping():
    return {"ping": "pong"}
"@
$healthPy | Out-File -FilePath backend\app\api\v1\endpoints\health.py -Encoding utf8

# backend/app/core/database.py
$databasePy = @"
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
Base = declarative_base()
"@
$databasePy | Out-File -FilePath backend\app\core\database.py -Encoding utf8

# backend/app/services/mcp_manager.py
$mcpPy = @"
class MCPManager:
    def __init__(self):
        self.servers = {}
        self._initialized = False
    
    async def start_all(self):
        if not self._initialized:
            self.servers = {"filesystem": {"status": "running"}, "manim": {"status": "running"}}
            self._initialized = True
    
    async def stop_all(self):
        self._initialized = False
    
    async def health_check(self):
        return {name: info["status"] == "running" for name, info in self.servers.items()}

mcp_manager = MCPManager()
"@
$mcpPy | Out-File -FilePath backend\app\services\mcp_manager.py -Encoding utf8

Write-Host "Backend files created" -ForegroundColor Green

# 5. Create frontend files
Write-Host "Creating frontend files..." -ForegroundColor Yellow

# frontend/Dockerfile
$frontendDockerfile = @"
FROM node:20-alpine AS base
RUN apk add --no-cache libc6-compat
WORKDIR /app

FROM base AS development
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev"]
"@
$frontendDockerfile | Out-File -FilePath frontend\Dockerfile -Encoding utf8

# frontend/package.json
$packageJson = @"
{
  "name": "vynetra-frontend",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  },
  "dependencies": {
    "next": "14.2.5",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "framer-motion": "^11.13.1",
    "lucide-react": "^0.344.0"
  },
  "devDependencies": {
    "@types/node": "^20.10.0",
    "@types/react": "^18.3.0",
    "@types/react-dom": "^18.3.0",
    "autoprefixer": "^10.4.16",
    "tailwindcss": "^3.3.6",
    "typescript": "^5.3.0"
  }
}
"@
$packageJson | Out-File -FilePath frontend\package.json -Encoding utf8

# frontend/next.config.js
$nextConfig = @"
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  output: 'standalone',
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.NEXT_PUBLIC_API_URL + '/:path*',
      },
    ];
  },
};
module.exports = nextConfig;
"@
$nextConfig | Out-File -FilePath frontend\next.config.js -Encoding utf8

# frontend/tailwind.config.js
$tailwindConfig = @"
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: { extend: {} },
  plugins: [],
}
"@
$tailwindConfig | Out-File -FilePath frontend\tailwind.config.js -Encoding utf8

# frontend/src/app/layout.tsx
$layoutTsx = @"
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Vynetra - AI Presentation Creator',
  description: 'One Prompt. A Complete Presentation.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  );
}
"@
$layoutTsx | Out-File -FilePath frontend\src\app\layout.tsx -Encoding utf8

# frontend/src/app/globals.css
$globalsCss = @"
@tailwind base;
@tailwind components;
@tailwind utilities;
"@
$globalsCss | Out-File -FilePath frontend\src\app\globals.css -Encoding utf8

# frontend/src/app/page.tsx
$pageTsx = @"
'use client';
import { useState } from 'react';
import { motion } from 'framer-motion';
import { Sparkles } from 'lucide-react';

export default function Home() {
  const [prompt, setPrompt] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;
    setIsLoading(true);
    try {
      const response = await fetch('/api/v1/presentations/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt, slides: 10 }),
      });
      const data = await response.json();
      console.log('Generation started:', data);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="container mx-auto px-4 py-16">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-5xl font-bold text-white mb-4">
            <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
              Vynetra
            </span>
          </h1>
          <p className="text-xl text-gray-300">One Prompt. A Complete Presentation.</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="max-w-4xl mx-auto"
        >
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20">
            <form onSubmit={handleSubmit}>
              <div className="relative">
                <textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="Enter your presentation topic or prompt..."
                  className="w-full h-32 bg-white/5 border border-white/20 rounded-xl p-4 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none"
                  disabled={isLoading}
                />
                <button
                  type="submit"
                  disabled={isLoading || !prompt.trim()}
                  className="absolute bottom-4 right-4 bg-gradient-to-r from-purple-500 to-pink-500 text-white px-6 py-2 rounded-lg font-medium hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  {isLoading ? 'Generating...' : 'Generate'}
                </button>
              </div>
            </form>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
            <div className="bg-white/5 rounded-xl p-6 border border-white/10 text-center">
              <h3 className="text-white font-semibold mb-2">Smart Content</h3>
              <p className="text-gray-400 text-sm">AI-generated structured slides</p>
            </div>
            <div className="bg-white/5 rounded-xl p-6 border border-white/10 text-center">
              <h3 className="text-white font-semibold mb-2">Animations</h3>
              <p className="text-gray-400 text-sm">Automated Manim animations</p>
            </div>
            <div className="bg-white/5 rounded-xl p-6 border border-white/10 text-center">
              <h3 className="text-white font-semibold mb-2">Diagrams</h3>
              <p className="text-gray-400 text-sm">AI-generated flowcharts</p>
            </div>
          </div>
        </motion.div>

        <div className="mt-16 max-w-4xl mx-auto">
          <div className="bg-white/5 rounded-xl p-4 border border-white/10">
            <div className="flex items-center justify-between text-sm text-gray-400">
              <span className="flex items-center gap-2">
                <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                System Status: Ready
              </span>
              <span>v1.0.0</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
"@
$pageTsx | Out-File -FilePath frontend\src\app\page.tsx -Encoding utf8

Write-Host "Frontend files created" -ForegroundColor Green

# 6. Create .gitignore
Write-Host "Creating .gitignore..." -ForegroundColor Yellow
$gitignore = @"
__pycache__/
*.pyc
venv/
env/
node_modules/
.next/
generated/
.env
*.log
.vscode/
.idea/
.DS_Store
"@
$gitignore | Out-File -FilePath .gitignore -Encoding utf8
Write-Host ".gitignore created" -ForegroundColor Green

# 7. Final message
Write-Host ""
Write-Host "Vynetra setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Make sure Docker Desktop is running" -ForegroundColor White
Write-Host "2. Run: docker-compose up --build" -ForegroundColor White
Write-Host "3. Access: http://localhost:3000 (Frontend)" -ForegroundColor White
Write-Host "4. Access: http://localhost:8000/docs (API Docs)" -ForegroundColor White
Write-Host ""