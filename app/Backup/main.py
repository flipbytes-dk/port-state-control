import os
from fastapi import FastAPI, UploadFile, HTTPException, File
from fastapi.middleware.cors import CORSMiddleware
from llama_parse import LlamaParse
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.core.program import FunctionCallingProgram
from llama_index.llms.groq import Groq
from dotenv import load_dotenv
import nest_asyncio
from .models import InspectionReport
from .logger import setup_logger
from pathlib import Path
import json
from .validators import ResponseValidator
from llama_index.core.response_synthesizers import ResponseMode
from llama_index.core.prompts import PromptTemplate

# Apply nest_asyncio
nest_asyncio.apply()

# Set up logger
logger = setup_logger(__name__)

# Load environment variables
load_dotenv()

# Create data directory in project root
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize LlamaParse with specific PSC parsing instructions
parser = LlamaParse(
    api_key=os.getenv("LLAMA_CLOUD_API_KEY"),
    result_type="markdown",
    parsing_instructions="""
    This is a Port State Control (PSC) inspection report. Please pay special attention to:
    
    1. Ship Particulars section:
        - Ship's Name
        - IMO Number
        - MMSI Number (if available)
        - Flag State
        - Ship Type
        - Gross Tonnage
    
    2. Inspection Details:
        - Date of Inspection
        - Port of Inspection
        - Country of Inspection
    
    3. Inspector Information:
        - Inspector's Name
        - Inspector's ID/Badge Number (if available)
        - Authority (e.g., Port State Control Authority name)
    
    4. Deficiencies Section:
        - Deficiency Code (usually in format XXXXX)
        - Detailed Description of the Deficiency
        - Action Taken Code (this could be two numbers separated by a '/')
        - Action Taken Description
        - Deadline for Rectification
        - Date of Rectification (if available)
    
    5. Additional Important Fields:
        - Type of Inspection
        - Nature of Inspection
        - Any detention information
        
    Please maintain the hierarchical structure and relationships between different sections.
    Preserve all numerical values, dates, and codes exactly as they appear in the document.
    Process all pages of the document and combine the information into a single coherent output.
    """,
    premium_mode=True,
    max_items_per_page=50,  # Increase items per page
    include_page_breaks=True,  # Include page break information
    collapse_bullets_and_numbering=False,  # Preserve bullet points and numbering
    language="en"  # Specify language
)

# Initialize Groq LLM
llm = Groq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.2-11b-text-preview"
)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        logger.info(f"Received file upload: {file.filename}")
        
        # Verify file is PDF
        if not file.filename.endswith('.pdf'):
            logger.error(f"Invalid file format: {file.filename}")
            raise HTTPException(status_code=400, detail="File must be a PDF")
        
        # Save uploaded file temporarily
        temp_path = PROJECT_ROOT / f"temp_{file.filename}"
        logger.debug(f"Saving temporary file: {temp_path}")
        
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Parse PDF to markdown using LlamaParse
        try:
            logger.info("Starting PDF parsing with LlamaParse")
            documents = await parser.aload_data(str(temp_path))
            
            # Combine all pages into a single markdown document
            markdown_text = "\n\n---\n\n".join(doc.text for doc in documents)
            logger.info(f"Parsed {len(documents)} pages from PDF")
            
            # Save markdown to data directory
            markdown_path = DATA_DIR / "temp.md"
            logger.info(f"Attempting to save markdown to: {markdown_path}")
            
            try:
                markdown_path.write_text(markdown_text, encoding="utf-8")
                logger.info(f"Successfully saved parsed markdown to {markdown_path}")
            except Exception as e:
                logger.error(f"Error saving markdown file: {str(e)}")
            
            logger.info("Successfully parsed PDF to markdown")
            
        except Exception as e:
            logger.error(f"Error parsing PDF: {str(e)}")
            raise
        finally:
            # Clean up temp PDF file
            if temp_path.exists():
                temp_path.unlink()
                logger.debug(f"Cleaned up temporary file: {temp_path}")
        
        # Create extraction prompt
        extraction_prompt = PromptTemplate(
            """You are a specialized Port State Control (PSC) inspection report analyzer.
            Your task is to extract structured information from the report and return it in JSON format. It is very important that you extract all the information from the report, especially the deficiencies and the action code/action taken for these deficiencies.
            
            Return ONLY a valid JSON object with the following structure, no additional text:
            {
                "ship": {
                    "name": "string or null",
                    "imo_number": "string or null",
                    "flag": "string or null",
                    "ship_type": "string or null",
                    "gross_tonnage": number or null,
                    "call_sign": "string or null",
                    "deadweight": number or null,
                    "company": "string or null",
                    "registered_owner": "string or null"
                },
                "inspector": {
                    "name": "string or null",
                    "id": "string or null",
                    "authority": "string or null",
                    "office": "string or null",
                    "contact": "string or null"
                },
                "inspection_date": "ISO date string or null",
                "port_name": "string or null",
                "inspection_type": "string or null",
                "areas_inspected": ["string"],
                "operational_controls": ["string"],
                "certificates": [
                    {
                        "title": "string or null",
                        "issuing_authority": "string or null",
                        "issue_date": "ISO date string or null",
                        "expiry_date": "ISO date string or null"
                    }
                ],
                "deficiencies": [
                    {
                        "code": "string or null",
                        "description": "string or null",
                        "action_taken": "string or null",
                        "action_code": "string or null",
                        "deadline": "ISO date string or null",
                        "rectified_date": "string or null"
                    }
                ],
                "last_port": "string or null",
                "next_port": "string or null",
                "detained": boolean or null
            }

            Process all information from all pages. If the same type of information appears on multiple pages,
            combine it appropriately. For certificates and deficiencies, include all entries found throughout the document.
            
            Report content:
            {report_content}
            
            Return ONLY the JSON object, no other text or explanation."""
        )
        
        # Extract structured data
        logger.info("Extracting structured data from markdown")
        try:
            # Get raw completion from LLM
            response = llm.complete(
                extraction_prompt.format(report_content=markdown_text)
            )
            raw_response = response.text
            logger.info("Raw response received from LLM")
            logger.debug(f"Raw response: {raw_response}")
            
            # Validate response format
            is_valid, validation_errors, cleaned_data = ResponseValidator.validate_response(raw_response)
            
            if not is_valid:
                error_msg = "; ".join(validation_errors)
                logger.error(f"Response validation failed: {error_msg}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Invalid response format: {error_msg}"
                )
            
            try:
                structured_data = InspectionReport(**cleaned_data)
            except Exception as e:
                logger.error(f"Error creating InspectionReport: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Error creating report structure: {str(e)}"
                )

            # Validate the structured data
            if not structured_data:
                raise HTTPException(status_code=500, detail="Empty response from LLM")
            
            logger.info(f"Successfully processed report")
            if structured_data.ship and structured_data.ship.name:
                logger.info(f"Vessel name: {structured_data.ship.name}")
            logger.info(f"Number of deficiencies: {len(structured_data.deficiencies or [])}")
            
            return structured_data
            
        except Exception as e:
            logger.error(f"Error in data extraction: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Data extraction failed: {str(e)}")

    except Exception as e:
        logger.error(f"Error processing upload: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/debug/raw-response/")
async def debug_raw_response(file: UploadFile):
    """Debug endpoint to see raw LLM response"""
    try:
        # ... (same file handling code as upload_inspection_report) ...
        
        raw_response = llm.complete(
            extraction_prompt.format(report_content=markdown_text)
        )
        return {
            "raw_response": raw_response.text,
            "response_type": str(type(raw_response)),
            "response_preview": str(raw_response.text)[:500] if isinstance(raw_response, str) else None
        }
    except Exception as e:
        logger.error(f"Debug endpoint error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))