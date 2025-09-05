# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Presenton is an open-source AI presentation generator that runs locally on your device. It supports multiple LLM providers (OpenAI, Google, Anthropic, Ollama, custom OpenAI-compatible APIs) and various image generation services. The application can generate presentations from prompts or uploaded documents and export to PowerPoint (PPTX) and PDF formats.

## Architecture

This is a multi-server architecture with two main components:

### FastAPI Backend (`servers/fastapi/`)
- **Python-based REST API** using FastAPI with async support
- **Database layer** with SQLModel for ORM, supports SQLite, MySQL, and PostgreSQL
- **LLM Integration** with provider-specific endpoints and unified client interface
- **Presentation Generation** pipeline with outline → slides → export workflow
- **MCP Server** for Model Context Protocol support
- **Image Generation** services supporting multiple providers
- **Document Processing** with docling for various file formats

### Next.js Frontend (`servers/nextjs/`)
- **React/Next.js application** with TypeScript
- **Component architecture** using Radix UI components and Tailwind CSS
- **State management** with Redux Toolkit
- **Page structure**:
  - `/dashboard` - presentation management
  - `/outline` - outline editing and template selection
  - `/presentation` - slide editing interface
  - `/custom-template` - template creation from PPTX files
  - `/settings` - configuration management

## Development Commands

### Backend (FastAPI)
```bash
# Navigate to backend directory
cd servers/fastapi

# Install dependencies (requires Python 3.11-3.12)
pip install -r requirements.txt

# Run development server
python server.py

# Run tests
pytest

# Run MCP server
python mcp_server.py
```

### Frontend (Next.js)
```bash
# Navigate to frontend directory
cd servers/nextjs

# Install dependencies
npm install

# Development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Lint code
npm run lint
```

### Docker Deployment
```bash
# Build and run with Docker
docker run -it --name presenton -p 5000:80 -v "./app_data:/app_data" ghcr.io/presenton/presenton:latest

# With GPU support for Ollama
docker run -it --name presenton --gpus=all -p 5000:80 -e LLM="ollama" -e OLLAMA_MODEL="llama3.2:3b" -v "./app_data:/app_data" ghcr.io/presenton/presenton:latest
```

## Key Architecture Patterns

### Presentation Generation Pipeline
1. **Outline Generation** - LLM generates presentation structure
2. **Template Selection** - Choose from built-in or custom HTML/CSS templates  
3. **Slide Generation** - Individual slides created with content and layout
4. **Export Processing** - Convert to PPTX/PDF using puppeteer and python-pptx

### LLM Provider Abstraction
- **Unified Client Interface** (`services/llm_client.py`) handles all providers
- **Provider-specific endpoints** in `api/v1/ppt/endpoints/` for each service
- **Tool calling support** with automatic fallback to JSON schema for unsupported models

### Template System
- **HTML/CSS templates** stored in database with Tailwind CSS styling
- **Dynamic template generation** from existing PPTX files
- **Layout components** with structured content areas (titles, bullets, images, charts)

### Database Schema
- **Presentations** - metadata and configuration
- **Slides** - individual slide content and layout references
- **Templates** - HTML/CSS template definitions
- **Image Assets** - cached image references

## Environment Configuration

Key environment variables for deployment:
- `LLM` - Provider selection (openai/google/anthropic/ollama/custom)
- `*_API_KEY` - API keys for respective providers
- `IMAGE_PROVIDER` - Image generation service
- `CAN_CHANGE_KEYS` - Allow runtime API key modification
- `DISABLE_ANONYMOUS_TELEMETRY` - Privacy control

## API Structure

Main API endpoints:
- `POST /api/v1/ppt/presentation/generate` - Generate complete presentations
- `/api/v1/ppt/outlines/` - Outline management
- `/api/v1/ppt/slides/` - Individual slide operations
- `/api/v1/ppt/images/` - Image generation and management
- `/api/v1/ppt/layouts/` - Template and layout operations