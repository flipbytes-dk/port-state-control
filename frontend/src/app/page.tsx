'use client';

import React from "react";
import { useState } from 'react';
import axios from 'axios';
import { Upload, FileText, AlertCircle, Loader2 } from 'lucide-react';
import InfoCard from '@/components/InfoCard';
import DeficiencyTable from '@/components/DeficiencyTable';
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import CertificateTable from '@/components/CertificateTable';
import Image from 'next/image';
import type { UploadResponse } from '@/types/api';

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [parsedData, setParsedData] = useState<UploadResponse['data'] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post<UploadResponse>(
        `${process.env.NEXT_PUBLIC_API_URL}/upload`, 
        formData, 
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          withCredentials: false
        }
      );
      setParsedData(response.data.data);
      setError(null);
    } catch (err) {
      if (axios.isAxiosError(err)) {
        if (err.response) {
          setError(`Error: ${err.response.data.detail || 'Failed to parse file'}`);
        } else if (err.request) {
          setError('No response from server. Please check if the server is running.');
        } else {
          setError('Error setting up the request.');
        }
      } else {
        setError('An unexpected error occurred.');
      }
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="relative">
        <div className="absolute inset-0 h-[500px] w-full overflow-hidden">
          <Image
            src="/container.png"
            alt="Container ship background"
            fill
            className="object-cover opacity-95"
            priority
          />
          <div className="absolute inset-0 bg-gradient-to-b from-background/10 to-background" />
        </div>

        <div className="relative pt-8 px-4 sm:px-6 lg:px-8">
          <div className="max-w-7xl mx-auto">
            <div className="text-center mb-8 bg-white/95 backdrop-blur-sm py-6 rounded-lg shadow-lg max-w-2xl mx-auto">
              <h1 className="text-4xl font-bold text-foreground">
                PSC Report Parser
              </h1>
              <p className="mt-2 text-muted-foreground">
                Upload your PSC report PDF to extract and analyze the data
              </p>
            </div>

            <Card className="max-w-xl mx-auto mb-8 bg-background/95 backdrop-blur-sm">
              <CardContent className="pt-6">
                <div className="flex items-center justify-center w-full">
                  <label className="flex flex-col items-center justify-center w-full h-64 border-2 border-dashed rounded-lg cursor-pointer hover:bg-accent hover:bg-opacity-50 border-border">
                    <div className="flex flex-col items-center justify-center pt-5 pb-6">
                      <Upload className="w-12 h-12 mb-4 text-muted-foreground" />
                      <p className="mb-2 text-sm text-muted-foreground">
                        <span className="font-semibold">Click to upload</span> or drag and drop
                      </p>
                      <p className="text-xs text-muted-foreground">PDF files only</p>
                    </div>
                    <input
                      type="file"
                      className="hidden"
                      accept=".pdf"
                      onChange={handleFileChange}
                    />
                  </label>
                </div>

                {file && (
                  <div className="mt-4 flex items-center gap-2 text-sm text-muted-foreground">
                    <FileText className="w-4 h-4" />
                    <span>{file.name}</span>
                  </div>
                )}

                {error && (
                  <Alert variant="destructive" className="mt-4">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                )}

                <Button
                  onClick={handleUpload}
                  disabled={loading}
                  className="mt-4 w-full"
                >
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Processing...
                    </>
                  ) : (
                    'Parse Report'
                  )}
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      <div className="px-4 sm:px-6 lg:px-8 pb-8">
        <div className="max-w-7xl mx-auto">
          {parsedData && (
            <div className="space-y-8">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <InfoCard
                  type="ship"
                  title="Ship Information"
                  data={{
                    'Ship Name': parsedData.ship.name,
                    'IMO Number': parsedData.ship.imo_number,
                    'Flag': parsedData.ship.flag,
                    'Ship Type': parsedData.ship.ship_type,
                    'Gross Tonnage': parsedData.ship.gross_tonnage,
                    'Call Sign': parsedData.ship.call_sign,
                    'Deadweight': parsedData.ship.deadweight,
                    'Company': parsedData.ship.company,
                    'Registered Owner': parsedData.ship.registered_owner,
                  }}
                />
                <InfoCard
                  type="inspection"
                  title="Inspection Details"
                  data={{
                    'Port Name': parsedData.port_name,
                    'Date of Inspection': parsedData.inspection_date,
                    'Type of Inspection': parsedData.inspection_type,
                    'Last Port': parsedData.last_port || 'N/A',
                    'Next Port': parsedData.next_port || 'N/A',
                    'Detained': parsedData.detained ? 'Yes' : 'No',
                  }}
                />
                <InfoCard
                  type="authority"
                  title="Inspector Information"
                  data={{
                    'Name': parsedData.inspector.name,
                    'Authority': parsedData.inspector.authority,
                    'Office': parsedData.inspector.office,
                    'Contact': parsedData.inspector.contact,
                  }}
                />
              </div>

              <CertificateTable certificates={parsedData.certificates} />
              <DeficiencyTable deficiencies={parsedData.deficiencies} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
} 