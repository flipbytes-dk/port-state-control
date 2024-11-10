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
import { AlertTriangle, CheckCircle2 } from "lucide-react";

interface Deficiency {
  code: string | null;
  description: string | null;
  action_taken: string | null;
  action_code: string | null;
  deadline: string | null;
  rectified_date: string | null;
}

interface DeficiencyTableProps {
  deficiencies: Deficiency[];
}

export default function DeficiencyTable({ deficiencies }: DeficiencyTableProps) {
  // Helper function to check if a deficiency is empty (all values are null or N/A)
  const isEmptyDeficiency = (deficiency: Deficiency): boolean => {
    return Object.values(deficiency).every(value => 
      value === null || 
      value === 'N/A' || 
      value === '' || 
      value === undefined
    );
  };

  // Helper function to check if the entire deficiencies array is effectively empty
  const isEmptyDeficienciesList = (deficiencies: Deficiency[]): boolean => {
    if (!deficiencies || deficiencies.length === 0) return true;
    return deficiencies.every(isEmptyDeficiency);
  };

  // Filter out empty deficiencies
  const validDeficiencies = deficiencies.filter(def => !isEmptyDeficiency(def));

  if (isEmptyDeficienciesList(deficiencies)) {
    return (
      <Card>
        <CardHeader className="flex flex-row items-center space-x-4">
          <CheckCircle2 className="h-6 w-6 text-green-500" />
          <div>
            <CardTitle>No Deficiencies Found</CardTitle>
            <p className="text-sm text-muted-foreground mt-1">
              This vessel has passed inspection with no reported deficiencies
            </p>
          </div>
        </CardHeader>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center space-x-4">
        <AlertTriangle className="h-6 w-6 text-red-500" />
        <div>
          <div className="flex items-center gap-3">
            <CardTitle>Deficiencies</CardTitle>
            <span className="inline-flex items-center justify-center px-2.5 py-0.5 rounded-full text-sm font-medium bg-red-100 text-red-800">
              Total: {validDeficiencies.length}
            </span>
          </div>
          <p className="text-sm text-muted-foreground mt-1">
            The following deficiencies were identified during inspection
          </p>
        </div>
      </CardHeader>
      <CardContent>
        <div className="relative overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Code</TableHead>
                <TableHead>Description</TableHead>
                <TableHead>Action Code</TableHead>
                <TableHead>Action Taken</TableHead>
                <TableHead>Deadline</TableHead>
                <TableHead>Rectified Date</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {validDeficiencies.map((deficiency, index) => (
                <TableRow key={index}>
                  <TableCell className="font-medium">{deficiency.code || 'N/A'}</TableCell>
                  <TableCell>{deficiency.description || 'N/A'}</TableCell>
                  <TableCell>{deficiency.action_code || 'N/A'}</TableCell>
                  <TableCell>{deficiency.action_taken || 'N/A'}</TableCell>
                  <TableCell>{deficiency.deadline || 'N/A'}</TableCell>
                  <TableCell>{deficiency.rectified_date || 'N/A'}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
} 