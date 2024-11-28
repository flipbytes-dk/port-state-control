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
from .database import Database

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

# Update CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",    # Local frontend
        "http://127.0.0.1:3000",    # Alternative local frontend URL
        "http://localhost:8000",    # Local backend
        "https://port-state-control.vercel.app",  # Production frontend
        "https://port-state-control.onrender.com"  # Production backend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
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
    Process all pages of the document and combine the information into a single coherent output. Names might appear on rubber stamped pages, so be sure to extract them from all pages. 
    """,
    premium_mode=True 
)

# Initialize Groq LLM
llm = Groq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.2-11b-vision-preview"
)

# Add this after FastAPI initialization
db = Database()

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
            Your task is to extract structured information from the report and return it in JSON format. It is very important that you extract all the information from the report, especially the deficiencies and the action code/action taken for these deficiencies. If all values in deficiencies are null, then there are no deficiencies. Sometimes `action taken` field might be preceeded by a number, be sure to extract the action taken code or text. Sometimes in `action_taken` you might find a number that preceeds the text. That number can be entered in the `action_code`. This will typically be a 2 digit number. When extracting port names, look for mentions across all pages and then use the one that is most likely to be the correct port. If there are two or more mentions of last port of call, then compare both and use the one that is most likely to be the correct port, based on your vast knowledge of the world and port names. 
            
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
                        "rectified_date": "string or null",
                        "remarks": "string or null"
                    }
                ],
                "last_port": "string or null",
                "next_port": "string or null",
                "detained": boolean or null
            }

            Process all information from all pages. If the same type of information appears on multiple pages,
            combine it appropriately. For certificates and deficiencies, include all entries found throughout the document. Bear in mind that sometimes in deficiencies, non-conformities are marked as "x" and "-" means conformity. Read the report thoroughly to figure this out. Also remeber that for deficiencies if you find the values of `code`, `action_taken` and `action_code` to be null, then perhaps there are no deficiencies. In the section on deficiencies, if you find columns like `additional comments`, `remarks` or something similar to this, be sure to club them all together in `remarks` column. You MUST NOT leave any information out especially when it comes to deficiencies. extract all of them.
            
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
            
            # After successfully creating structured_data, store it in the database
            try:
                report_id = await db.store_inspection_report(structured_data)
                logger.info(f"Stored report in database with ID: {report_id}")
                
                # Return both the structured data and the report ID
                return {
                    "report_id": report_id,
                    "data": structured_data
                }
                
            except Exception as e:
                logger.error(f"Error storing report in database: {str(e)}")
                raise HTTPException(
                    status_code=500, 
                    detail=f"Failed to store report in database: {str(e)}"
                )

        except Exception as e:
            logger.error(f"Error in data extraction: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Data extraction failed: {str(e)}")

    except Exception as e:
        logger.error(f"Error processing upload: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
