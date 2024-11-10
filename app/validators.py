from typing import Dict, Any, Optional
import json
from datetime import datetime
import re
from .logger import setup_logger
from dateutil import parser

logger = setup_logger(__name__)

class ResponseValidator:
    @staticmethod
    def is_valid_date(date_str: Optional[str]) -> bool:
        """Validate if string is a proper ISO date format."""
        if not date_str:
            return True  # None is acceptable
        try:
            datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return True
        except (ValueError, AttributeError):
            return False

    @staticmethod
    def is_valid_imo(imo: Optional[str]) -> bool:
        """Validate IMO number format with more flexible rules."""
        if not imo:
            return True  # None is acceptable
        # Remove any non-digit characters
        imo_digits = ''.join(filter(str.isdigit, str(imo)))
        # Accept if it has 7 digits anywhere in the string
        return len(imo_digits) == 7

    @staticmethod
    def is_valid_deficiency_code(code: Optional[str]) -> bool:
        """Validate deficiency code format with more flexible rules."""
        if not code:
            return True  # None is acceptable
        # Remove any non-digit characters
        code_digits = ''.join(filter(str.isdigit, str(code)))
        # Accept if it has 4-6 digits (some PSC authorities use different formats)
        return 4 <= len(code_digits) <= 6

    @staticmethod
    def validate_ship_data(ship: Dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate ship section of the response with more flexible rules."""
        errors = []
        
        # Only validate IMO number if it's present and not empty
        if ship.get('imo_number') and str(ship['imo_number']).strip():
            if not ResponseValidator.is_valid_imo(ship['imo_number']):
                # Convert to warning instead of error
                logger.warning(f"Non-standard IMO number format: {ship['imo_number']}")
        
        # More flexible number validation
        for field in ['gross_tonnage', 'deadweight']:
            if ship.get(field) is not None:
                try:
                    # Try to convert to float if it's a string
                    if isinstance(ship[field], str):
                        ship[field] = float(ship[field].replace(',', ''))
                    elif not isinstance(ship[field], (int, float)):
                        errors.append(f"{field.replace('_', ' ').title()} must be a number")
                except (ValueError, TypeError):
                    errors.append(f"Invalid {field.replace('_', ' ').title()} format")
        
        return len(errors) == 0, errors

    @staticmethod
    def validate_deficiencies(deficiencies: list) -> tuple[bool, list[str]]:
        """Validate deficiencies section of the response with more flexible rules."""
        errors = []
        
        for idx, deficiency in enumerate(deficiencies):
            # Validate code format if present and not empty
            if deficiency.get('code') and str(deficiency['code']).strip():
                if not ResponseValidator.is_valid_deficiency_code(deficiency['code']):
                    # Convert to warning instead of error
                    logger.warning(f"Non-standard deficiency code format at index {idx}: {deficiency['code']}")
            
            # More flexible date validation
            for date_field in ['deadline', 'rectified_date']:
                if deficiency.get(date_field) and str(deficiency[date_field]).strip():
                    try:
                        # Try to parse various date formats
                        parsed_date = ResponseValidator.parse_flexible_date(deficiency[date_field])
                        if parsed_date:
                            deficiency[date_field] = parsed_date.isoformat()
                        else:
                            logger.warning(f"Non-standard date format for {date_field} at index {idx}")
                    except Exception:
                        logger.warning(f"Could not parse date for {date_field} at index {idx}")
        
        return len(errors) == 0, errors

    @staticmethod
    def parse_flexible_date(date_str: str) -> Optional[datetime]:
        """Parse dates in various formats."""
        if not date_str:
            return None
        
        try:
            # Try different date formats
            for fmt in [
                "%Y-%m-%d",
                "%d/%m/%Y",
                "%m/%d/%Y",
                "%d-%m-%Y",
                "%Y/%m/%d",
                "%d.%m.%Y",
                "%Y.%m.%d"
            ]:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            # Try parsing with dateutil as a fallback
            return parser.parse(date_str)
        except Exception:
            return None

    @classmethod
    def validate_response(cls, response_str: str) -> tuple[bool, list[str], Optional[Dict]]:
        """Validate the complete response with more flexible rules."""
        errors = []
        cleaned_data = None

        try:
            # Clean up the response string
            cleaned_response = response_str.strip()
            if cleaned_response.startswith(("'", '"')) and cleaned_response.endswith(("'", '"')):
                cleaned_response = cleaned_response[1:-1]
            
            # Handle potential JSON formatting issues
            if not cleaned_response.startswith("{"):
                cleaned_response = "{" + cleaned_response.split("{", 1)[1]
            if not cleaned_response.endswith("}"):
                cleaned_response = cleaned_response.rsplit("}", 1)[0] + "}"
            
            data = json.loads(cleaned_response)
            
            # Ensure all sections exist with default values
            data['ship'] = data.get('ship', {})
            data['inspector'] = data.get('inspector', {})
            data['areas_inspected'] = data.get('areas_inspected', [])
            data['operational_controls'] = data.get('operational_controls', [])
            data['certificates'] = data.get('certificates', [])
            data['deficiencies'] = data.get('deficiencies', [])

            # Convert potential string values to proper types
            if isinstance(data.get('detained'), str):
                data['detained'] = data['detained'].lower() in ['true', 'yes', '1']

            # Validate with more flexible rules
            if data.get('ship'):
                is_valid, ship_errors = cls.validate_ship_data(data['ship'])
                errors.extend(ship_errors)

            if data.get('deficiencies'):
                if not isinstance(data['deficiencies'], list):
                    data['deficiencies'] = [data['deficiencies']]
                is_valid, deficiency_errors = cls.validate_deficiencies(data['deficiencies'])
                errors.extend(deficiency_errors)

            # Store cleaned data even if there are some non-critical errors
            cleaned_data = data

            return True, errors, cleaned_data  # Always return the data, use errors as warnings

        except json.JSONDecodeError as e:
            return False, [f"JSON parsing error: {str(e)}"], None
        except Exception as e:
            return False, [f"Validation error: {str(e)}"], None