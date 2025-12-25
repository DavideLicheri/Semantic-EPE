# EURING Code Recognition System - Project Structure

## Overview

This document describes the complete project structure for the EURING Code Recognition System, including all directories, key files, and their purposes.

## Directory Structure

```
euring-code-recognition/
├── .kiro/                          # Kiro specifications
│   └── specs/
│       └── euring-code-recognition/
│           ├── requirements.md     # System requirements (EARS format)
│           ├── design.md          # System design document
│           └── tasks.md           # Implementation task list
│
├── backend/                        # Python FastAPI backend
│   ├── app/                       # Application code
│   │   ├── __init__.py
│   │   ├── api/                   # API endpoints
│   │   │   └── __init__.py
│   │   ├── models/                # Data models
│   │   │   ├── __init__.py
│   │   │   └── euring_models.py  # Core EURING data models
│   │   ├── services/              # Business logic
│   │   │   ├── __init__.py
│   │   │   └── interfaces.py     # Service interfaces
│   │   └── repositories/          # Data access layer
│   │       └── __init__.py
│   ├── tests/                     # Test suite
│   │   ├── __init__.py
│   │   └── conftest.py           # Pytest configuration & fixtures
│   ├── main.py                    # FastAPI application entry point
│   ├── requirements.txt           # Python dependencies
│   └── pytest.ini                 # Pytest configuration
│
├── frontend/                       # React TypeScript frontend
│   ├── src/
│   │   ├── components/            # React components
│   │   │   └── __init__.ts
│   │   └── types/                 # TypeScript definitions
│   │       ├── __init__.ts
│   │       └── euring-types.ts   # Core type definitions
│   ├── package.json               # Node.js dependencies
│   ├── vite.config.ts            # Vite build configuration
│   ├── tsconfig.json             # TypeScript configuration
│   └── tsconfig.node.json        # TypeScript Node configuration
│
├── README.md                       # Project documentation
├── PROJECT_STRUCTURE.md           # This file
├── setup.sh                       # Setup script
└── .gitignore                     # Git ignore rules
```

## Key Components

### Backend Components

#### Models (`backend/app/models/euring_models.py`)
Core data models including:
- `EuringVersion`: Represents a specific version of the EURING code
- `FieldDefinition`: Defines fields within a version
- `ConversionMapping`: Maps conversions between versions
- `RecognitionResult`: Results from version recognition
- `ConversionResult`: Results from version conversion
- `BillingInfo`: Billing and quota information
- `UserSession`: User session data

#### Services (`backend/app/services/interfaces.py`)
Service interfaces for:
- `RecognitionEngine`: Version recognition logic
- `SKOSManager`: SKOS model management
- `ConversionService`: Version conversion logic
- `BillingService`: Billing and quota management

#### Tests (`backend/tests/conftest.py`)
Testing infrastructure including:
- Hypothesis configuration for property-based testing
- Test data generators for EURING strings
- Fixtures for sample data
- Custom strategies for generating test cases

### Frontend Components

#### Types (`frontend/src/types/euring-types.ts`)
TypeScript interfaces matching backend models:
- All core data types
- API request/response types
- Component prop types
- Enums for status values

## Technology Stack

### Backend
- **Framework**: FastAPI 0.104.1
- **Testing**: pytest 7.4.3, Hypothesis 6.92.1
- **Validation**: Pydantic 2.5.0
- **Authentication**: python-jose, passlib
- **Database**: SQLAlchemy 2.0.23, PostgreSQL

### Frontend
- **Framework**: React 18.2.0
- **Language**: TypeScript 5.0.0
- **Build Tool**: Vite 4.4.0
- **HTTP Client**: Axios 1.6.0
- **Routing**: React Router 6.8.0

## Setup and Installation

### Quick Setup
Run the setup script:
```bash
./setup.sh
```

### Manual Setup

#### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Frontend
```bash
cd frontend
npm install
```

## Running the Application

### Backend
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python main.py
```
API available at: http://localhost:8000

### Frontend
```bash
cd frontend
npm run dev
```
UI available at: http://localhost:3000

## Testing

### Backend Tests
```bash
cd backend
source venv/bin/activate
pytest                    # Run all tests
pytest -m property       # Run property-based tests only
pytest -m unit          # Run unit tests only
```

### Property-Based Testing
The system uses Hypothesis for property-based testing with:
- Minimum 100 iterations per test
- Custom generators for EURING strings
- Strategies for batch processing
- Credential generators for authentication tests

## API Documentation

When the backend is running:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development Workflow

1. **Requirements**: Defined in `.kiro/specs/euring-code-recognition/requirements.md`
2. **Design**: Detailed in `.kiro/specs/euring-code-recognition/design.md`
3. **Tasks**: Implementation plan in `.kiro/specs/euring-code-recognition/tasks.md`
4. **Implementation**: Follow task list sequentially
5. **Testing**: Write tests alongside implementation
6. **Validation**: Run test suite to verify correctness

## Next Steps

After completing this setup task, the next tasks in the implementation plan are:
1. Implement SKOS model and version management (Task 2)
2. Implement recognition engine (Task 3)
3. Implement conversion service (Task 5)
4. And so on...

Refer to `.kiro/specs/euring-code-recognition/tasks.md` for the complete task list.