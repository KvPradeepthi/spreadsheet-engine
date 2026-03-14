# Backend Spreadsheet Engine with Formula Parsing and Dependency Graph

A RESTful API service for a spreadsheet engine that supports formula parsing, cell dependencies, and automated recalculation.

## Features

- **Formula Parsing**: Parse arithmetic expressions with cell references
- **Cell Dependencies**: Automatic tracking of cell dependencies using a directed acyclic graph (DAG)
- **Recalculation**: Automatic recalculation of dependent cells when values change
- **Error Handling**: Comprehensive error handling with specific error types (#DIV/0!, #REF!, #CYCLE!)
- **Docker Containerized**: Fully containerized application with health checks
- **RESTful API**: Clean REST endpoints for cell operations

## Supported Operations

- Arithmetic operators: `+`, `-`, `*`, `/`
- Cell references: `A1`, `B2`, `AZ100`, etc.
- Parentheses for grouping: `(A1 + B1) * 2`
- Formula format: `=expression`

## Project Structure

```
.
├── app.py                 # Flask application with API endpoints
├── parser.py              # Formula parsing logic
├── graph_manager.py       # Dependency graph management
├── evaluator.py           # Cell evaluation engine
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker container configuration
├── docker-compose.yml     # Docker Compose orchestration
├── .env.example           # Environment variable template
└── README.md              # This file
```

## Setup and Installation

### Prerequisites
- Docker and Docker Compose
- Python 3.8+ (for local development)

### Using Docker Compose

1. Clone the repository
2. Copy `.env.example` to `.env` and update variables as needed
3. Run the application:

```bash
docker-compose up --build
```

The API will be available at `http://localhost:8080`

### Health Check

The application includes a health check endpoint:

```bash
curl http://localhost:8080/health
```

Expected response: `{"status": "healthy"}`

## API Endpoints

### Set Cell Value

**Request:**
```
PUT /api/sheets/{sheet_id}/cells/{cell_id}
Content-Type: application/json

{"value": 123}
```

For formulas:
```
{"value": "=A1+B1"}
```

**Response:** `200 OK`

### Get Cell Value

**Request:**
```
GET /api/sheets/{sheet_id}/cells/{cell_id}
```

**Response:**
```json
{"value": 123}
```

## Error Handling

- `#DIV/0!` - Division by zero
- `#REF!` - Reference to non-existent cell
- `#CYCLE!` - Circular dependency detected

Errors are propagated to all dependent cells.

## Core Components

### Parser
Recursive descent parser for arithmetic expressions with cell references.

### Graph Manager
Manages the dependency graph:
- Tracks cell dependencies
- Detects circular references using DFS
- Maintains topological order for recalculation

### Evaluator
Evaluates cell formulas:
- Handles arithmetic operations
- Resolves cell references
- Propagates errors to dependents
- Manages recalculation order

## Configuration

Environment variables (see `.env.example`):
- `API_PORT`: Port for the API server (default: 8080)
- `FLASK_ENV`: Flask environment (development/production)
- `FLASK_DEBUG`: Debug mode flag

## Testing

Example API calls:

```bash
# Set cell A1 to 10
curl -X PUT http://localhost:8080/api/sheets/test/cells/A1 \
  -H "Content-Type: application/json" \
  -d '{"value": 10}'

# Set cell B1 to 20
curl -X PUT http://localhost:8080/api/sheets/test/cells/B1 \
  -H "Content-Type: application/json" \
  -d '{"value": 20}'

# Set cell C1 to formula =A1+B1
curl -X PUT http://localhost:8080/api/sheets/test/cells/C1 \
  -H "Content-Type: application/json" \
  -d '{"value": "=A1+B1"}'

# Get cell C1 value (should be 30)
curl http://localhost:8080/api/sheets/test/cells/C1
```

## Development

For local development without Docker:

```bash
pip install -r requirements.txt
export API_PORT=8080
python app.py
```

## Architecture

- **API Layer**: Flask application handling HTTP requests
- **Formula Parser**: Converts formula strings to evaluatable expressions
- **Dependency Manager**: Maintains DAG of cell dependencies
- **Evaluation Engine**: Computes cell values and handles recalculation
- **In-Memory Storage**: Stores sheet and cell data

## License

MIT License
