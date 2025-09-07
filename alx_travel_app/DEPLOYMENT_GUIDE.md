# ALX Travel App - Deployment Guide

This guide provides comprehensive instructions for deploying the ALX Travel App with Celery and Swagger documentation to various cloud platforms.

## 🎯 Deployment Objectives

- ✅ Deploy application to cloud server (Render, PythonAnywhere)
- ✅ Configure environment variables correctly
- ✅ Run Celery worker on server
- ✅ Make Swagger documentation publicly accessible at `/swagger/`
- ✅ Test all endpoints including email notifications

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Server    │    │   Database      │    │   Message       │
│   (Django +     │    │   (PostgreSQL)  │    │   Broker        │
│    Gunicorn)    │    │                 │    │   (Redis)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Celery        │    │   Static Files  │    │   API           │
│   Worker        │    │   (WhiteNoise)  │    │   Documentation │
│   (Background   │    │                 │    │   (Swagger)     │
│    Tasks)       │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Option 1: Automated Deployment Script

```bash
cd alx_travel_app
./deploy.sh
```

### Option 2: Manual Deployment

Follow the platform-specific instructions below.

## 📋 Prerequisites

- Python 3.11+
- PostgreSQL database
- Redis server
- Cloud platform account (Render/PythonAnywhere)
- Domain name (optional)

## 🌐 Platform-Specific Deployments

### 1. Render Deployment (Recommended)

#### Step 1: Prepare Repository
1. Push your code to GitHub
2. Ensure all configuration files are in place:
   - `render.yaml`
   - `Procfile`
   - `requirements.txt`
   - `runtime.txt`

#### Step 2: Create Services on Render
1. **Web Service**:
   - Connect GitHub repository
   - Use `render.yaml` configuration
   - Set environment variables

2. **Worker Service**:
   - Create background worker
   - Use same repository
   - Set worker-specific environment variables

3. **Database**:
   - Create PostgreSQL database
   - Note connection string

4. **Redis**:
   - Create Redis instance
   - Note connection string

#### Step 3: Environment Variables
Set these in Render dashboard:

```bash
# Django Configuration
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-app.onrender.com

# Database
DATABASE_URL=postgresql://user:pass@host:port/db

# Celery
CELERY_BROKER_URL=redis://user:pass@host:port/0
CELERY_RESULT_BACKEND=redis://user:pass@host:port/0

# Chapa API
CHAPA_SECRET_KEY=your-chapa-secret
CHAPA_WEBHOOK_SECRET=your-webhook-secret

# Email
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

#### Step 4: Deploy
1. Render will automatically build and deploy
2. Monitor logs for any issues
3. Test endpoints after deployment

### 2. PythonAnywhere Deployment

#### Step 1: Upload Code
1. Upload your project to PythonAnywhere
2. Extract to your home directory

#### Step 2: Set Up Virtual Environment
```bash
# Create virtual environment
python3.10 -m venv myenv
source myenv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Step 3: Configure Web App
1. Go to Web tab in PythonAnywhere dashboard
2. Create new web app
3. Choose "Manual configuration"
4. Select Python 3.10

#### Step 4: Configure WSGI
Edit the WSGI file:
```python
import os
import sys

path = '/home/yourusername/alx_travel_app'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'alx_travel_app.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

#### Step 5: Set Up Database
```bash
python3.10 manage.py migrate
python3.10 manage.py collectstatic --noinput
```

#### Step 6: Configure Celery Worker
1. Go to Tasks tab
2. Create new task
3. Set command: `celery -A alx_travel_app worker --loglevel=info`
4. Set working directory: `/home/yourusername/alx_travel_app`

#### Step 7: Environment Variables
Set in Web app configuration:
```bash
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=yourusername.pythonanywhere.com
DATABASE_URL=sqlite:///db.sqlite3
CELERY_BROKER_URL=redis://localhost:6379/0
```

### 3. Docker Deployment

#### Step 1: Build and Run
```bash
# Build image
docker build -t alx-travel-app .

# Run with Docker Compose
docker-compose up -d
```

#### Step 2: Access Application
- Web: http://localhost:8000
- API Docs: http://localhost:8000/swagger/
- Admin: http://localhost:8000/admin/

## 🔧 Configuration Details

### Environment Variables

#### Required Variables
```bash
SECRET_KEY=your-django-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com
DATABASE_URL=postgresql://user:pass@host:port/db
CELERY_BROKER_URL=redis://host:port/0
CELERY_RESULT_BACKEND=redis://host:port/0
```

#### Optional Variables
```bash
# Email Configuration
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_DEFAULT_FROM_EMAIL=noreply@your-domain.com

# Chapa API
CHAPA_SECRET_KEY=your-chapa-secret
CHAPA_WEBHOOK_SECRET=your-webhook-secret

# Security
SECURE_SSL_REDIRECT=True
SECURE_PROXY_SSL_HEADER=('HTTP_X_FORWARDED_PROTO', 'https')
```

### Database Configuration

#### PostgreSQL (Production)
```python
DATABASES = {
    'default': dj_database_url.parse(os.getenv('DATABASE_URL'))
}
```

#### SQLite (Development)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### Celery Configuration

#### Production Settings
```python
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
CELERY_TASK_ALWAYS_EAGER = False
```

## 📊 API Documentation

### Swagger UI
- **URL**: `https://your-domain.com/swagger/`
- **Features**: Interactive API testing, request/response examples
- **Authentication**: Public access (no authentication required)

### ReDoc
- **URL**: `https://your-domain.com/redoc/`
- **Features**: Clean, readable API documentation

### OpenAPI Schema
- **URL**: `https://your-domain.com/api/schema/`
- **Format**: JSON schema for API integration

## 🧪 Testing Deployment

### 1. Health Check
```bash
curl https://your-domain.com/admin/
```

### 2. API Documentation
```bash
curl https://your-domain.com/swagger/
```

### 3. Test Booking Creation
```bash
curl -X POST https://your-domain.com/api/booking/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "destination": "Paris, France",
    "travel_date": "2024-06-15",
    "total_amount": "150000.00"
  }'
```

### 4. Test Payment Initiation
```bash
curl -X POST https://your-domain.com/api/payment/initiate/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "booking_reference": "BK12345678",
    "amount": "150000.00",
    "currency": "NGN",
    "email": "test@example.com",
    "first_name": "Test",
    "last_name": "User"
  }'
```

### 5. Test Email Notifications
1. Create a booking
2. Check Celery worker logs
3. Verify email delivery (check console/logs)

## 🔍 Monitoring and Debugging

### Logs
- **Web Server**: Check platform logs (Render/PythonAnywhere)
- **Celery Worker**: Monitor worker logs for task execution
- **Database**: Check database connection and queries

### Common Issues

#### 1. Static Files Not Loading
```bash
python manage.py collectstatic --noinput
```

#### 2. Database Connection Issues
- Check `DATABASE_URL` format
- Verify database credentials
- Ensure database is accessible

#### 3. Celery Worker Not Starting
- Check `CELERY_BROKER_URL`
- Verify Redis connection
- Check worker logs

#### 4. Email Not Sending
- Verify email configuration
- Check Celery worker logs
- Test email backend

### Performance Optimization

#### 1. Database
- Use connection pooling
- Optimize queries
- Add database indexes

#### 2. Static Files
- Use CDN for static files
- Enable compression
- Cache static files

#### 3. Celery
- Scale workers based on load
- Use task routing
- Monitor queue length

## 🔒 Security Considerations

### Production Security
1. **Environment Variables**: Never commit secrets to version control
2. **HTTPS**: Always use HTTPS in production
3. **Database**: Use strong passwords and restrict access
4. **CORS**: Configure CORS properly
5. **Rate Limiting**: Implement API rate limiting

### Security Headers
```python
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
```

## 📈 Scaling Considerations

### Horizontal Scaling
1. **Load Balancer**: Use multiple web server instances
2. **Database**: Set up read replicas
3. **Celery**: Scale workers based on queue length
4. **Caching**: Implement Redis caching

### Vertical Scaling
1. **Resources**: Increase CPU/memory
2. **Database**: Upgrade database instance
3. **Storage**: Increase storage capacity

## 🆘 Troubleshooting

### Common Error Messages

#### 1. "DisallowedHost" Error
```bash
# Add your domain to ALLOWED_HOSTS
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
```

#### 2. "Database Connection" Error
```bash
# Check DATABASE_URL format
DATABASE_URL=postgresql://user:password@host:port/database
```

#### 3. "Celery Worker" Error
```bash
# Check Redis connection
CELERY_BROKER_URL=redis://host:port/0
```

### Debug Mode
```bash
# Enable debug mode for troubleshooting
DEBUG=True
```

## 📞 Support

### Documentation
- **Django**: https://docs.djangoproject.com/
- **Celery**: https://docs.celeryproject.org/
- **Render**: https://render.com/docs
- **PythonAnywhere**: https://help.pythonanywhere.com/

### Community
- **Django Forum**: https://forum.djangoproject.com/
- **Stack Overflow**: Tag with `django`, `celery`, `deployment`

---

**Deployment Status**: ✅ Ready for Production  
**Last Updated**: January 2025  
**Version**: 1.0.0
