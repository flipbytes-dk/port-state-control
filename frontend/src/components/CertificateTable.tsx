import React from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollText } from "lucide-react";

interface Certificate {
  title: string | null;
  issuing_authority: string | null;
  issue_date: string | null;
  expiry_date: string | null;
}

interface CertificateTableProps {
  certificates: Certificate[];
}

export default function CertificateTable({ certificates }: CertificateTableProps) {
  if (!certificates || certificates.length === 0 || !certificates[0].title) {
    return (
      <Card>
        <CardContent className="text-center py-8 text-muted-foreground">
          No certificates found
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center space-x-4">
        <ScrollText className="h-6 w-6 text-blue-500" />
        <CardTitle>Certificates</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="relative overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Title</TableHead>
                <TableHead>Issuing Authority</TableHead>
                <TableHead>Issue Date</TableHead>
                <TableHead>Expiry Date</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {certificates.map((cert, index) => (
                <TableRow key={index}>
                  <TableCell className="font-medium">{cert.title || 'N/A'}</TableCell>
                  <TableCell>{cert.issuing_authority || 'N/A'}</TableCell>
                  <TableCell>{cert.issue_date || 'N/A'}</TableCell>
                  <TableCell>{cert.expiry_date || 'N/A'}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
} 