import { InspectionReport } from '@/types/models';

export interface UploadResponse {
  report_id: string;
  data: InspectionReport;
} 