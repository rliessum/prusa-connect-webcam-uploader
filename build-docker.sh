#!/bin/bash

# Docker Build Script for Prusa Connect Webcam Uploader
# This script helps build and tag the Docker image for various deployment scenarios

set -e

# Configuration
IMAGE_NAME="rliessum/prusa-webcam-uploader"
VERSION="1.0.0"
REGISTRY=""  # Set to your registry URL if pushing to a registry

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

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help          Show this help message"
    echo "  -b, --build         Build Docker image"
    echo "  -p, --push          Push to registry (requires REGISTRY to be set)"
    echo "  -t, --tag TAG       Custom tag (default: latest)"
    echo "  -r, --registry URL  Registry URL for pushing"
    echo "  --no-cache          Build without cache"
    echo "  --platform ARCH     Target platform (e.g., linux/amd64,linux/arm64)"
    echo ""
    echo "Examples:"
    echo "  $0 --build                           # Build with latest tag"
    echo "  $0 --build --tag v1.0.0             # Build with custom tag"
    echo "  $0 --build --push --registry myregistry.com"
    echo "  $0 --build --platform linux/amd64,linux/arm64  # Multi-platform build"
}

# Default values
BUILD=false
PUSH=false
TAG="latest"
NO_CACHE=""
PLATFORM=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        -b|--build)
            BUILD=true
            shift
            ;;
        -p|--push)
            PUSH=true
            shift
            ;;
        -t|--tag)
            TAG="$2"
            shift 2
            ;;
        -r|--registry)
            REGISTRY="$2"
            shift 2
            ;;
        --no-cache)
            NO_CACHE="--no-cache"
            shift
            ;;
        --platform)
            PLATFORM="--platform $2"
            shift 2
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main execution
main() {
    print_status "Starting Docker build process..."
    
    # Check if Docker is available
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    # Check if we're in the correct directory
    if [[ ! -f "Dockerfile" ]]; then
        print_error "Dockerfile not found. Please run this script from the project root."
        exit 1
    fi
    
    if [[ "$BUILD" == "true" ]]; then
        build_image
    fi
    
    if [[ "$PUSH" == "true" ]]; then
        if [[ -z "$REGISTRY" ]]; then
            print_error "Registry URL is required for pushing. Use --registry option."
            exit 1
        fi
        push_image
    fi
    
    if [[ "$BUILD" == "false" && "$PUSH" == "false" ]]; then
        print_warning "No action specified. Use --build or --push."
        show_usage
        exit 1
    fi
}

# Function to build Docker image
build_image() {
    print_status "Building Docker image..."
    
    # Construct full image name
    if [[ -n "$REGISTRY" ]]; then
        FULL_IMAGE_NAME="${REGISTRY}/${IMAGE_NAME}:${TAG}"
    else
        FULL_IMAGE_NAME="${IMAGE_NAME}:${TAG}"
    fi
    
    print_status "Image name: $FULL_IMAGE_NAME"
    
    # Build command
    BUILD_CMD="docker build $NO_CACHE $PLATFORM -t $FULL_IMAGE_NAME ."
    
    print_status "Running: $BUILD_CMD"
    
    if eval $BUILD_CMD; then
        print_success "Docker image built successfully: $FULL_IMAGE_NAME"
        
        # Also tag as latest if not already
        if [[ "$TAG" != "latest" ]]; then
            LATEST_TAG="${REGISTRY:+${REGISTRY}/}${IMAGE_NAME}:latest"
            docker tag "$FULL_IMAGE_NAME" "$LATEST_TAG"
            print_success "Also tagged as: $LATEST_TAG"
        fi
        
        # Show image info
        print_status "Image details:"
        docker images "$FULL_IMAGE_NAME" --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.Size}}\t{{.CreatedAt}}"
    else
        print_error "Docker build failed"
        exit 1
    fi
}

# Function to push Docker image
push_image() {
    print_status "Pushing Docker image to registry..."
    
    FULL_IMAGE_NAME="${REGISTRY}/${IMAGE_NAME}:${TAG}"
    
    print_status "Pushing: $FULL_IMAGE_NAME"
    
    if docker push "$FULL_IMAGE_NAME"; then
        print_success "Image pushed successfully: $FULL_IMAGE_NAME"
        
        # Push latest tag if not already
        if [[ "$TAG" != "latest" ]]; then
            LATEST_TAG="${REGISTRY}/${IMAGE_NAME}:latest"
            if docker push "$LATEST_TAG"; then
                print_success "Latest tag pushed: $LATEST_TAG"
            fi
        fi
    else
        print_error "Docker push failed"
        exit 1
    fi
}

# Run main function
main 