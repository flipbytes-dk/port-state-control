from supabase import create_client
import os
from dotenv import load_dotenv
from .models import InspectionReport
from .logger import setup_logger

logger = setup_logger(__name__)

load_dotenv()

class Database:
    def __init__(self):
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("Supabase credentials not found in environment variables")
        
        self.client = create_client(supabase_url, supabase_key)

    async def store_inspection_report(self, report: InspectionReport):
        try:
            # Convert the report to a dictionary
            report_dict = report.model_dump()
            
            # Store the main report data
            response = self.client.table('inspection_reports').insert({
                'ship_name': report_dict['ship']['name'],
                'imo_number': report_dict['ship']['imo_number'],
                'flag': report_dict['ship']['flag'],
                'inspection_date': report_dict['inspection_date'],
                'port_name': report_dict['port_name'],
                'detained': report_dict['detained'],
                'raw_data': report_dict  # Store the complete JSON for future reference
            }).execute()

            report_id = response.data[0]['id']
            
            # Store deficiencies separately for better querying
            if report_dict['deficiencies']:
                deficiencies = [
                    {
                        'report_id': report_id,
                        'code': d['code'],
                        'description': d['description'],
                        'action_taken': d['action_taken'],
                        'action_code': d['action_code'],
                        'deadline': d['deadline'],
                        'rectified_date': d['rectified_date']
                    }
                    for d in report_dict['deficiencies']
                ]
                
                self.client.table('deficiencies').insert(deficiencies).execute()

            return report_id

        except Exception as e:
            logger.error(f"Error storing inspection report: {str(e)}")
            raise 