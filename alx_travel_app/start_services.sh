#!/bin/bash

# ALX Travel App - Service Startup Script
# This script helps start all required services for the application

echo "🚀 Starting ALX Travel App Services..."
echo "======================================"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a service is running
service_running() {
    if command_exists systemctl; then
        systemctl is-active --quiet "$1"
    else
        pgrep -f "$1" >/dev/null
    fi
}

# Check if Python is installed
if ! command_exists python3; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if Django is installed
if ! python3 -c "import django" 2>/dev/null; then
    echo "❌ Django is not installed. Installing dependencies..."
    pip3 install -r requirements.txt
else
    echo "✅ Django is installed"
fi

# Check if RabbitMQ is running
echo "🔍 Checking RabbitMQ status..."
if command_exists rabbitmqctl; then
    if rabbitmqctl status >/dev/null 2>&1; then
        echo "✅ RabbitMQ is running"
    else
        echo "⚠️  RabbitMQ is not running. Starting RabbitMQ..."
        if command_exists systemctl; then
            sudo systemctl start rabbitmq-server
        elif command_exists brew; then
            brew services start rabbitmq
        else
            echo "❌ Cannot start RabbitMQ automatically. Please start it manually:"
            echo "   - Ubuntu/Debian: sudo systemctl start rabbitmq-server"
            echo "   - macOS: brew services start rabbitmq"
            echo "   - Or run: rabbitmq-server"
        fi
    fi
else
    echo "❌ RabbitMQ is not installed. Please install RabbitMQ first:"
    echo "   - Ubuntu/Debian: sudo apt-get install rabbitmq-server"
    echo "   - macOS: brew install rabbitmq"
    exit 1
fi

# Check if database exists and run migrations
echo "🔍 Checking database..."
if [ ! -f "db.sqlite3" ]; then
    echo "📊 Database not found. Running migrations..."
    python3 manage.py makemigrations
    python3 manage.py migrate
    echo "✅ Database setup complete"
else
    echo "✅ Database exists"
fi

# Function to start Celery worker
start_celery_worker() {
    echo "🐰 Starting Celery worker..."
    if [ -z "$1" ]; then
        # Start in background
        nohup celery -A travel_project worker --loglevel=info > celery_worker.log 2>&1 &
        echo "✅ Celery worker started in background (PID: $!)"
        echo "📝 Logs are being written to celery_worker.log"
    else
        # Start in foreground
        celery -A travel_project worker --loglevel=info
    fi
}

# Function to start Django server
start_django_server() {
    echo "🌐 Starting Django development server..."
    if [ -z "$1" ]; then
        # Start in background
        nohup python3 manage.py runserver > django_server.log 2>&1 &
        echo "✅ Django server started in background (PID: $!)"
        echo "📝 Logs are being written to django_server.log"
        echo "🌍 Server running at: http://127.0.0.1:8000/"
    else
        # Start in foreground
        python3 manage.py runserver
    fi
}

# Main menu
echo ""
echo "🎯 Choose an option:"
echo "1. Start all services in background"
echo "2. Start all services in foreground"
echo "3. Start only Celery worker"
echo "4. Start only Django server"
echo "5. Check service status"
echo "6. Stop all services"
echo "7. Exit"
echo ""

read -p "Enter your choice (1-7): " choice

case $choice in
    1)
        echo "🚀 Starting all services in background..."
        start_celery_worker background
        sleep 2
        start_django_server background
        echo ""
        echo "✅ All services started in background!"
        echo "📝 Check logs:"
        echo "   - Celery: tail -f celery_worker.log"
        echo "   - Django: tail -f django_server.log"
        echo ""
        echo "🌍 Access your app at: http://127.0.0.1:8000/"
        echo "🐰 Celery worker is running in background"
        ;;
    2)
        echo "🚀 Starting all services in foreground..."
        echo "⚠️  Press Ctrl+C to stop all services"
        echo ""
        # Start Celery in background first
        start_celery_worker background
        sleep 2
        # Start Django in foreground
        start_django_server foreground
        ;;
    3)
        start_celery_worker
        ;;
    4)
        start_django_server
        ;;
    5)
        echo "🔍 Checking service status..."
        echo ""
        
        # Check Django
        if pgrep -f "manage.py runserver" >/dev/null; then
            echo "✅ Django server is running"
        else
            echo "❌ Django server is not running"
        fi
        
        # Check Celery
        if pgrep -f "celery.*worker" >/dev/null; then
            echo "✅ Celery worker is running"
        else
            echo "❌ Celery worker is not running"
        fi
        
        # Check RabbitMQ
        if rabbitmqctl status >/dev/null 2>&1; then
            echo "✅ RabbitMQ is running"
        else
            echo "❌ RabbitMQ is not running"
        fi
        ;;
    6)
        echo "🛑 Stopping all services..."
        
        # Stop Django
        pkill -f "manage.py runserver"
        echo "✅ Django server stopped"
        
        # Stop Celery
        pkill -f "celery.*worker"
        echo "✅ Celery worker stopped"
        
        echo "✅ All services stopped"
        ;;
    7)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "📚 For more information, check the README.md file"
echo "🐛 For troubleshooting, check the logs or run: ./start_services.sh 5"
