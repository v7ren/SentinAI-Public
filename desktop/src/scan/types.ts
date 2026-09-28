export type ScanEvent = {
  type: string;
  msg?: string;
  filename?: string;
  count?: number;
  files_scanned?: number;
  total_files?: number;
  scan_id?: string;
  error?: string;
  issues?: Array<{
    type?: string;
    severity?: string;
    line?: number;
    description?: string;
  }>;
};

export type FindingRow = {
  file: string;
  type: string;
  severity: string;
  line: number;
  description: string;
};
