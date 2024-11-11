import { InspectionReport } from '@/types/models';

export interface Certificate {
  title: string | null;
  issuing_authority: string | null;
  issue_date: string | null;
  expiry_date: string | null;
}

export interface Deficiency {
  code: string | null;
  description: string | null;
  action_taken: string | null;
  action_code: string | null;
  deadline: string | null;
  rectified_date: string | null;
}

export interface UploadResponse {
  report_id: string;
  data: {
    certificates: Certificate[];
    deficiencies: Deficiency[];
  };
} 