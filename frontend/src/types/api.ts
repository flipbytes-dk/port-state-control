import { InspectionReport } from '@/types/models';

export interface UploadResponse {
  report_id: string;
  data: InspectionReport;
}

export interface Deficiency {
  code: string | null;
  description: string | null;
  action_taken: string | null;
  action_code: string | null;
  deadline: string | null;
  rectified_date: string | null;
  remarks: string | null;
} 