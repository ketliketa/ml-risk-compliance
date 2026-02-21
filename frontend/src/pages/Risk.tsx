import { useEffect, useState } from 'react';
import api from '../lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';

interface RiskScore {
  document_id: string;
  score: number;
  factors: string[];
}

interface RiskDashboard {
  total_documents: number;
  high_risk_count: number;
  medium_risk_count: number;
  low_risk_count: number;
  average_score: number;
  scores: RiskScore[];
}

export default function Risk() {
  const [dashboard, setDashboard] = useState<RiskDashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchRiskData();
  }, []);

  const fetchRiskData = async () => {
    try {
      setLoading(true);
      const res = await api.get('/risk/dashboard');
      setDashboard(res.data);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Dështoi ngarkimi i të dhënave të rrezikut');
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (score: number) => {
    if (score >= 70) return 'text-red-600 bg-red-50 border-red-200';
    if (score >= 40) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    return 'text-green-600 bg-green-50 border-green-200';
  };

  const getRiskLabel = (score: number) => {
    if (score >= 70) return 'Rrezik i Lartë';
    if (score >= 40) return 'Rrezik Mesatar';
    return 'Rrezik i Ulët';
  };

  if (loading) {
    return <div className="text-center py-12">Po ngarkohen të dhënat e rrezikut...</div>;
  }

  if (error) {
    return <div className="text-center py-12 text-red-600">Gabim: {error}</div>;
  }

  return (
    <div>
      <h2 className="text-3xl font-bold text-gray-900 mb-6">Paneli i Rrezikut</h2>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Dokumente Gjithsej</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboard?.total_documents || 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Rrezik i Lartë</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{dashboard?.high_risk_count || 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Rrezik Mesatar</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{dashboard?.medium_risk_count || 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Rrezik i Ulët</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{dashboard?.low_risk_count || 0}</div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Rezultatet e Rrezikut</CardTitle>
          <CardDescription>
            Rezultati Mesatar i Rrezikut: {dashboard?.average_score ? dashboard.average_score.toFixed(1) : '0.0'}/100
          </CardDescription>
        </CardHeader>
        <CardContent>
          {!dashboard || !dashboard.scores || dashboard.scores.length === 0 ? (
            <p className="text-center py-8 text-gray-500">Nuk ka rezultate të rrezikut të disponueshme</p>
          ) : (
            <div className="space-y-4">
              {dashboard.scores.map((score) => (
                <div
                  key={score.document_id}
                  className={`p-4 border rounded-md ${getRiskColor(score.score)}`}
                >
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <div className="font-medium">Dokumenti: {score.document_id}</div>
                      <div className="text-sm mt-1">Niveli i Rrezikut: {getRiskLabel(score.score)}</div>
                    </div>
                    <div className="text-2xl font-bold">{score.score}/100</div>
                  </div>
                  {score.factors.length > 0 && (
                    <div className="mt-3 pt-3 border-t">
                      <div className="text-sm font-medium mb-2">Faktorët e Rrezikut:</div>
                      <ul className="list-disc list-inside text-sm space-y-1">
                        {score.factors.map((factor, idx) => (
                          <li key={idx}>{factor}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
