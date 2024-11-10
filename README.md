<div align="center">
  <img src="frontend/public/container.png" alt="PSC Report Parser Banner" width="100%" height="300px" style="object-fit: cover; border-radius: 10px;"/>
</div>

<h1 align="center">PSC Report Parser</h1>

<p align="center">
  A full-stack application for parsing and analyzing Port State Control (PSC) inspection reports using AI.
</p>

<p align="center">
  <a href="#about">About</a> •
  <a href="#features">Features</a> •
  <a href="#tech-stack">Tech Stack</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> 
</p>

## About

Port State Control (PSC) is a ship inspection program where foreign vessels are inspected to verify their compliance with international maritime regulations. These inspections result in detailed reports that document vessel conditions, deficiencies, and compliance status.

### The Challenge
PSC reports are typically provided as PDFs with varying formats, making it difficult to:
- Extract structured data consistently
- Analyze trends across multiple inspections
- Track deficiencies and their rectification
- Generate insights about vessel compliance

### The Solution
This application uses AI to:
- Automatically extract structured data from PSC report PDFs
- Store information in a searchable database
- Present data in an organized, user-friendly interface
- Enable tracking and analysis of inspection results

## Features

- 📄 Parse PSC inspection reports from PDF format
- 🤖 AI-powered data extraction using LlamaParse
- 💾 Persistent storage with Supabase
- 📊 Interactive UI for viewing inspection details
- 🔍 Detailed deficiency analysis
- 📋 Certificate management
- 🚢 Comprehensive ship information tracking

## Tech Stack

### Backend
- FastAPI (Python web framework)
- LlamaParse (PDF parsing)
- Groq (LLM for data extraction)
- Supabase (Database)
- Pydantic (Data validation)

### Frontend
- Next.js 14
- TypeScript
- Tailwind CSS
- Shadcn UI

## Installation

### Prerequisites
- Python 3.9+
- Node.js 18+
- npm or yarn
- Supabase account
- Groq API key
- LlamaParse API key

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/psc-report-parser.git
cd psc-report-parser

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p data logs

# Set up environment variables
cp .env.example .env

# Edit .env with your credentials:
GROQ_API_KEY=your_groq_api_key            # Get from https://console.groq.com
LLAMA_CLOUD_API_KEY=your_llama_api_key    # Get from https://cloud.llamaindex.ai
SUPABASE_URL=your_supabase_url            # Get from Supabase project settings
SUPABASE_KEY=your_supabase_key            # Get from Supabase project settings

# Start the backend server
python run.py
```

The server will start on http://localhost:8000. You can verify it's running by visiting http://localhost:8000/docs for the Swagger documentation.

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with:
NEXT_PUBLIC_API_URL=http://localhost:8000

# Run the development server
npm run dev
```

### Database Setup

1. Create a Supabase project at https://supabase.com
2. Go to SQL Editor in your Supabase dashboard
3. Run the following SQL to create the necessary tables:

```sql
-- Create the inspection_reports table
CREATE TABLE inspection_reports (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    ship_name TEXT,
    imo_number TEXT,
    flag TEXT,
    inspection_date TIMESTAMP WITH TIME ZONE,
    port_name TEXT,
    detained BOOLEAN,
    raw_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create the deficiencies table
CREATE TABLE deficiencies (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    report_id UUID REFERENCES inspection_reports(id),
    code TEXT,
    description TEXT,
    action_taken TEXT,
    action_code TEXT,
    deadline TIMESTAMP WITH TIME ZONE,
    rectified_date TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX idx_inspection_reports_imo ON inspection_reports(imo_number);
CREATE INDEX idx_inspection_reports_ship_name ON inspection_reports(ship_name);
CREATE INDEX idx_deficiencies_report_id ON deficiencies(report_id);
```

## Usage

1. Start the backend server:
```bash
# From project root
source venv/bin/activate  # On Windows: venv\Scripts\activate
python run.py
```

2. Start the frontend development server:
```bash
# From frontend directory
npm run dev
```

3. Navigate to http://localhost:3000
4. Upload a PSC inspection report PDF
5. View the extracted data and analysis

## API Endpoints

The backend provides the following endpoints:

- `POST /upload`: Upload and parse a PSC report PDF
  - Request: Multipart form data with 'file' field containing the PDF
  - Response: JSON containing parsed report data and database ID

Example response structure:
```json
{
  "report_id": "uuid-string",
  "data": {
    "ship": {
      "name": "VESSEL NAME",
      "imo_number": "1234567"
    },
    "inspector": {
      "name": "INSPECTOR NAME"
    }
  }
}
```

## Error Handling

The backend implements comprehensive error handling for:
- Invalid file formats
- PDF parsing failures
- Data extraction issues
- Database connection problems
- Validation errors

All errors return appropriate HTTP status codes and descriptive error messages.

## Logging

Logs are stored in the `logs` directory with the following structure:
- `app.log`: General application logs
- Error logs include timestamps and stack traces for debugging

You can adjust the log level in `app/logger.py` (defaults to INFO in production, DEBUG in development).

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.