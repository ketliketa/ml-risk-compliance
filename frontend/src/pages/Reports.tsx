import { useState } from 'react';
import api from '../lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';

export default function Reports() {
  const [generating, setGenerating] = useState(false);
  const [report, setReport] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    try {
      setGenerating(true);
      setError(null);
      const res = await api.post('/reports/generate');
      setReport(res.data);
    } catch (err: any) {
      setError(err.message || 'Dështoi gjenerimi i raportit');
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div>
      <h2 className="text-3xl font-bold text-gray-900 mb-6">Raportet</h2>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Gjenero Raport</CardTitle>
          <CardDescription>Gjenero raporte PDF dhe Excel me të dhënat aktuale</CardDescription>
        </CardHeader>
        <CardContent>
          <Button onClick={handleGenerate} disabled={generating}>
            {generating ? 'Po gjenerohet...' : 'Gjenero Raport'}
          </Button>
        </CardContent>
      </Card>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md text-red-700">
          {error}
        </div>
      )}

      {report && (
        <Card>
          <CardHeader>
            <CardTitle>Raporti u Gjenerua</CardTitle>
            <CardDescription>ID e Raportit: {report.report_id}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <div className="text-sm font-medium text-gray-500">Raporti PDF</div>
                <div className="text-sm text-gray-900">{report.pdf_path}</div>
              </div>
              <div>
                <div className="text-sm font-medium text-gray-500">Raporti Excel</div>
                <div className="text-sm text-gray-900">{report.excel_path}</div>
              </div>
              <div className="p-4 bg-green-50 border border-green-200 rounded-md text-green-700">
                {report.message}
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
