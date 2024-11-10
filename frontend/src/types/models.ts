export interface Ship {
  name: string;
  imo_number: string;
  flag: string;
  ship_type: string;
  gross_tonnage: number;
  call_sign: string;
  deadweight: number;
  company: string;
  registered_owner: string;
}

export interface Inspector {
  name: string;
  id: string | null;
  authority: string;
  office: string;
  contact: string;
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
}

export interface InspectionReport {
  ship: Ship;
  inspector: Inspector;
  inspection_date: string;
  port_name: string;
  inspection_type: string;
  areas_inspected: string[];
  operational_controls: string[];
  certificates: Certificate[];
  deficiencies: Deficiency[];
  last_port: string | null;
  next_port: string | null;
  detained: boolean;
} 