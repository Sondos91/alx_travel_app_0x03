#!/bin/bash

# ALX Travel App - Deployment Script
# This script helps deploy the application to various platforms

set -e

echo "🚀 ALX Travel App - Deployment Script"
echo "====================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required commands exist
check_requirements() {
    print_status "Checking requirements..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 is not installed"
        exit 1
    fi
    
    print_success "Requirements check passed"
}

# Install dependencies
install_dependencies() {
    print_status "Installing dependencies..."
    pip3 install -r requirements.txt
    print_success "Dependencies installed"
}

# Run database migrations
run_migrations() {
    print_status "Running database migrations..."
    python3 manage.py makemigrations
    python3 manage.py migrate
    print_success "Database migrations completed"
}

# Collect static files
collect_static() {
    print_status "Collecting static files..."
    python3 manage.py collectstatic --noinput
    print_success "Static files collected"
}

# Create superuser
create_superuser() {
    print_status "Creating superuser..."
    echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin123')" | python3 manage.py shell
    print_success "Superuser created (username: admin, password: admin123)"
}

# Test the application
test_application() {
    print_status "Testing application..."
    python3 manage.py check
    print_success "Application tests passed"
}

# Deploy to Render
deploy_render() {
    print_status "Deploying to Render..."
    
    if [ ! -f "render.yaml" ]; then
        print_error "render.yaml not found"
        exit 1
    fi
    
    print_warning "Make sure you have:"
    print_warning "1. Created a Render account"
    print_warning "2. Connected your GitHub repository"
    print_warning "3. Set up environment variables in Render dashboard"
    print_warning "4. Created PostgreSQL and Redis services"
    
    read -p "Press Enter to continue..."
    
    print_success "Render deployment configuration ready"
    print_status "Visit https://dashboard.render.com to deploy"
}

# Deploy with Docker
deploy_docker() {
    print_status "Deploying with Docker..."
    
    if [ ! -f "Dockerfile" ]; then
        print_error "Dockerfile not found"
        exit 1
    fi
    
    print_status "Building Docker image..."
    docker build -t alx-travel-app .
    
    print_status "Starting services with Docker Compose..."
    docker-compose up -d
    
    print_success "Docker deployment completed"
    print_status "Application available at: http://localhost:8000"
    print_status "API Documentation: http://localhost:8000/swagger/"
}

# Deploy to PythonAnywhere
deploy_pythonanywhere() {
    print_status "Deploying to PythonAnywhere..."
    
    print_warning "Manual deployment steps for PythonAnywhere:"
    echo "1. Upload your code to PythonAnywhere"
    echo "2. Install dependencies: pip3.10 install --user -r requirements.txt"
    echo "3. Set up environment variables in the Web app configuration"
    echo "4. Configure static files mapping"
    echo "5. Set up a separate worker process for Celery"
    echo "6. Configure your domain and SSL"
    
    print_success "PythonAnywhere deployment instructions provided"
}

# Main menu
show_menu() {
    echo ""
    echo "🎯 Choose deployment option:"
    echo "1. Local development setup"
    echo "2. Deploy to Render"
    echo "3. Deploy with Docker"
    echo "4. Deploy to PythonAnywhere"
    echo "5. Run tests only"
    echo "6. Exit"
    echo ""
}

# Local development setup
local_setup() {
    print_status "Setting up local development environment..."
    
    check_requirements
    install_dependencies
    run_migrations
    collect_static
    create_superuser
    test_application
    
    print_success "Local development setup completed!"
    print_status "Start the server: python3 manage.py runserver"
    print_status "Start Celery worker: celery -A alx_travel_app worker --loglevel=info"
    print_status "API Documentation: http://localhost:8000/swagger/"
}

# Main execution
main() {
    while true; do
        show_menu
        read -p "Enter your choice (1-6): " choice
        
        case $choice in
            1)
                local_setup
                ;;
            2)
                deploy_render
                ;;
            3)
                deploy_docker
                ;;
            4)
                deploy_pythonanywhere
                ;;
            5)
                test_application
                ;;
            6)
                print_status "Goodbye!"
                exit 0
                ;;
            *)
                print_error "Invalid choice. Please try again."
                ;;
        esac
        
        echo ""
        read -p "Press Enter to continue..."
    done
}

# Run main function
main
