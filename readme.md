# PDF Genie 🧞‍♂️

## Overview

PDF Genie is a web application that transforms boring PDFs into entertaining, meme-style explanations. Users can upload various types of documents (manuals, legal docs, textbooks, policies) and receive fun, engaging summaries that make complex content easier to understand and more enjoyable to read.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Single-page application** built with vanilla HTML, CSS, and JavaScript
- **Tailwind CSS** for styling with custom animations and drag-and-drop visual feedback
- **File upload interface** with drag-and-drop functionality for PDF files
- **Responsive design** optimized for both desktop and mobile devices

### Backend Architecture
- **FastAPI framework** providing RESTful API endpoints for PDF processing
- **Asynchronous processing** for handling file uploads and AI transformations
- **Modular design** with separate functions for PDF text extraction and AI processing
- **CORS middleware** enabled for cross-origin requests from the frontend

### PDF Processing Pipeline
- **PyPDF2 library** for extracting text content from uploaded PDF files
- **BytesIO streams** for efficient in-memory file handling without disk storage
- **Page-by-page text extraction** to handle multi-page documents

### AI Integration
- **Google Gemini AI** integration for transforming extracted text into meme-style explanations
- **Environment-based configuration** for secure API key management
- **Fallback handling** for missing or invalid API credentials

## External Dependencies

### Core Libraries
- **FastAPI**: Web framework for building the API backend
- **PyPDF2**: PDF text extraction and parsing
- **python-dotenv**: Environment variable management

### AI Services
- **Google Gemini AI**: Large language model for content transformation and meme-style text generation

### Frontend Dependencies
- **Tailwind CSS**: Utility-first CSS framework delivered via CDN

### Development Tools
- **CORS middleware**: Cross-origin resource sharing for frontend-backend communication
- **Static file serving**: FastAPI's built-in static file handling capabilities