import { InspectionReport } from './models';

export interface UploadResponse {
  report_id: string;
  data: InspectionReport;
} 