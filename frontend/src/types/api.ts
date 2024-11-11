import { InspectionReport } from '@/types/models';

export interface Ship {
  name: string | null;
  imo_number: string | null;
  flag: string | null;
  ship_type: string | null;
  gross_tonnage: number | null;
  call_sign: string | null;
  deadweight: number | null;
  company: string | null;
  registered_owner: string | null;
}

export interface Inspector {
  name: string | null;
  id: string | null;
  authority: string | null;
  office: string | null;
  contact: string | null;
}

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
  remarks: string | null;
}

export interface ParsedData {
  ship: Ship;
  inspector: Inspector;
  inspection_date: string | null;
  port_name: string | null;
  inspection_type: string | null;
  areas_inspected: string[];
  operational_controls: string[];
  certificates: Certificate[];
  deficiencies: Deficiency[];
  last_port: string | null;
  next_port: string | null;
  detained: boolean | null;
}

export interface UploadResponse {
  data: ParsedData;
} 