# Vector Nova - Knowledge Base Query System

A comprehensive FastAPI application for intelligent document search and query processing using vector embeddings and hybrid search capabilities.

## 🚀 Features

- **Document Management**: Upload, process, and manage various document types (PDF, TXT, DOCX, MD)
- **Vector Search**: Semantic search using embeddings and vector similarity
- **Hybrid Search**: Combine semantic and keyword-based search for better results
- **User Authentication**: JWT-based authentication and authorization
- **Query History**: Track and manage user search queries
- **Web Scraping**: Extract content from web pages for knowledge base expansion
- **LLM Integration**: Generate responses and summaries using language models
- **Rate Limiting**: API protection with configurable rate limits
- **Caching**: Redis-based caching for improved performance

## 🏗️ Architecture

```
knowledge_base/
├── app/
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py              # Configuration management
│   ├── database.py            # Database connections
│   ├── dependencies.py        # Common dependencies
│   └── core/
│       ├── security.py        # Authentication/authorization
│       ├── rate_limiting.py   # Rate limiting middleware
│       └── logging.py         # Logging configuration
├── app/api/
│   ├── auth.py               # Authentication routes
│   ├── documents.py          # Document management
│   ├── query.py              # Query/search endpoints
│   └── users.py              # User management
├── app/models/
│   ├── user.py               # User SQLAlchemy models
│   ├── document.py           # Document models
│   └── query.py              # Query history models
├── app/services/
│   ├── document_processor.py # Document ingestion service
│   ├── vector_service.py     # Vector operations
│   ├── search_service.py     # Hybrid search implementation
│   ├── cache_service.py      # Caching logic
│   └── llm_service.py        # LLM integration
├── app/utils/
│   ├── chunking.py           # Text chunking utilities
│   ├── embeddings.py         # Embedding generation
│   └── web_scraper.py        # Web crawling utilities
├── docker-compose.yml        # Local development setup
├── requirements.txt
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Docker
- Docker Compose

### Running the Application

1. **Build and start the application:**
   ```bash
   docker-compose up --build
   ```

2. **Run in background:**
   ```bash
   docker-compose up -d --build
   ```

3. **Stop the application:**
   ```bash
   docker-compose down
   ```

## 📚 API Documentation

Once the application is running, you can access:

- **Interactive API Docs (Swagger UI):** http://localhost:8000/docs
- **Alternative API Docs (ReDoc):** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health
- **Root Endpoint:** http://localhost:8000/

## 🔧 API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `GET /api/v1/auth/me` - Get current user info

### Users
- `GET /api/v1/users/` - Get all users (admin only)
- `GET /api/v1/users/{user_id}` - Get user by ID
- `PUT /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Delete user (admin only)

### Documents
- `POST /api/v1/documents/upload` - Upload document
- `GET /api/v1/documents/` - Get user's documents
- `GET /api/v1/documents/{document_id}` - Get specific document
- `DELETE /api/v1/documents/{document_id}` - Delete document

### Query
- `POST /api/v1/query/search` - Search documents
- `GET /api/v1/query/history` - Get query history
- `GET /api/v1/query/suggestions` - Get search suggestions
- `POST /api/v1/query/feedback` - Submit search feedback

## 🔧 Development

### Environment Variables

Create a `.env` file in the root directory:

```env
# Application
DEBUG=True
SECRET_KEY=your-secret-key-change-in-production

# Database
DATABASE_URL=sqlite:///./vector_nova.db

# Vector Database
VECTOR_DB_URL=http://localhost:6333
VECTOR_DB_API_KEY=

# LLM Settings
LLM_PROVIDER=openai
LLM_API_KEY=your-openai-api-key
LLM_MODEL=gpt-3.5-turbo

# Embeddings
EMBEDDING_MODEL=text-embedding-ada-002
EMBEDDING_DIMENSION=1536

# Cache
REDIS_URL=redis://localhost:6379
CACHE_TTL=3600

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
```

### Database Setup

The application uses SQLite by default. For production, consider using PostgreSQL:

```yaml
# In docker-compose.yml
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: vector_nova
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
```

### Vector Database

The application is designed to work with vector databases like Qdrant, Pinecone, or Weaviate. Update the `vector_service.py` to integrate with your preferred vector database.

## 🐳 Docker Commands

### Build the image manually:
```bash
docker build -t vector-nova .
```

### Run the container manually:
```bash
docker run -p 8000:8000 vector-nova
```

### View logs:
```bash
docker-compose logs -f app
```

### Access container shell:
```bash
docker-compose exec app bash
```

## 🔄 Development Workflow

1. **Make changes** to your Python files
2. **Docker will automatically reload** the application (thanks to the volume mount and `--reload` flag)
3. **No need to rebuild** unless you change `requirements.txt` or `Dockerfile`

## 🗄️ Adding Services

### Vector Database (Qdrant)
```yaml
# In docker-compose.yml
services:
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage
```

### Redis Cache
```yaml
# In docker-compose.yml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
```

## 🚀 Production Deployment

For production, consider:

1. **Remove `--reload`** from the Dockerfile CMD
2. **Use a production WSGI server** like Gunicorn
3. **Add proper environment variables** for configuration
4. **Use a reverse proxy** like Nginx
5. **Implement proper logging** and monitoring
6. **Set up SSL/TLS** certificates
7. **Configure backup strategies** for databases

## 🛠️ Troubleshooting

### Port already in use:
```bash
# Check what's using port 8000
lsof -i :8000

# Use a different port in docker-compose.yml
ports:
  - "8001:8000"
```

### Container won't start:
```bash
# Check logs
docker-compose logs app

# Rebuild from scratch
docker-compose down
docker system prune -f
docker-compose up --build
```

### Permission issues:
```bash
# On Linux/Mac, you might need to fix file permissions
sudo chown -R $USER:$USER .
```

## 🎯 Next Steps

- [ ] Implement actual vector database integration (Qdrant, Pinecone)
- [ ] Add real LLM integration (OpenAI, Anthropic)
- [ ] Implement PDF and DOCX text extraction
- [ ] Add document preprocessing and cleaning
- [ ] Implement advanced search filters
- [ ] Add document versioning
- [ ] Set up automated testing
- [ ] Add monitoring and analytics
- [ ] Implement document sharing and collaboration
- [ ] Add API rate limiting per user
- [ ] Set up CI/CD pipeline

## 📝 License

This project is licensed under the MIT License.

---

**Happy coding! 🎉**
