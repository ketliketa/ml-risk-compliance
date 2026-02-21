import { useEffect, useState } from 'react';
import api from '../lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { AlertCircle } from 'lucide-react';

interface Alert {
  alert_id: string;
  type: string;
  severity: string;
  message: string;
  timestamp: string;
  document_id?: string;
}

interface AlertsResponse {
  alerts: Alert[];
  total: number;
}

export default function Alerts() {
  const [data, setData] = useState<AlertsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchAlerts();
  }, []);

  const fetchAlerts = async () => {
    try {
      setLoading(true);
      const res = await api.get('/alerts');
      setData(res.data);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Dështoi ngarkimi i sinjalizimeve');
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    if (severity === 'high') return 'border-red-300 bg-red-50';
    if (severity === 'medium') return 'border-yellow-300 bg-yellow-50';
    return 'border-blue-300 bg-blue-50';
  };

  const getSeverityBadgeColor = (severity: string) => {
    if (severity === 'high') return 'bg-red-200 text-red-800';
    if (severity === 'medium') return 'bg-yellow-200 text-yellow-800';
    return 'bg-blue-200 text-blue-800';
  };

  if (loading) {
    return <div className="text-center py-12">Po ngarkohen sinjalizimet...</div>;
  }

  if (error) {
    return <div className="text-center py-12 text-red-600">Gabim: {error}</div>;
  }

  return (
    <div>
      <h2 className="text-3xl font-bold text-gray-900 mb-6">Sinjalizimet</h2>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Përmbledhje</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{data?.total || 0} sinjalizime aktive</div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Sinjalizime Aktive</CardTitle>
          <CardDescription>Sinjalizimet dhe njoftimet aktuale të sistemit</CardDescription>
        </CardHeader>
        <CardContent>
          {!data || !data.alerts || data.alerts.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <AlertCircle className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <p>Nuk ka sinjalizime aktive</p>
            </div>
          ) : (
            <div className="space-y-4">
              {data.alerts.map((alert) => (
                <div
                  key={alert.alert_id}
                  className={`p-4 border rounded-md ${getSeverityColor(alert.severity)}`}
                >
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex-1">
                      <div className="font-medium mb-1">{alert.message}</div>
                      <div className="text-sm text-gray-600">
                        Lloji: {alert.type} • {alert.timestamp ? new Date(alert.timestamp).toLocaleString() : 'N/A'}
                      </div>
                      {alert.document_id && (
                        <div className="text-sm text-gray-600 mt-1">
                          ID e Dokumentit: {alert.document_id}
                        </div>
                      )}
                    </div>
                    <span
                      className={`px-2 py-1 rounded text-xs font-medium ${getSeverityBadgeColor(
                        alert.severity
                      )}`}
                    >
                      {alert.severity.toUpperCase()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
