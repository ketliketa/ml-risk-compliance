import { useEffect, useState } from 'react';
import api from '../lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';

interface Anomaly {
  transaction_id: string;
  amount: number;
  date: string;
  customer_id: string;
  anomaly_type: string;
  z_score: number;
}

interface AnomaliesResponse {
  anomalies: Anomaly[];
  total: number;
}

export default function Anomalies() {
  const [data, setData] = useState<AnomaliesResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchAnomalies();
  }, []);

  const fetchAnomalies = async () => {
    try {
      setLoading(true);
      const res = await api.get('/anomalies');
      setData(res.data);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Dështoi ngarkimi i anomalive');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center py-12">Po ngarkohen anomalitë...</div>;
  }

  if (error) {
    return <div className="text-center py-12 text-red-600">Gabim: {error}</div>;
  }

  return (
    <div>
      <h2 className="text-3xl font-bold text-gray-900 mb-6">Zbulimi i Anomalive</h2>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Përmbledhje</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{data?.total || 0} anomalitë të zbuluara</div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Anomalitë të Zbuluara</CardTitle>
          <CardDescription>Transaksionet të shënuara si vlera ekstreme</CardDescription>
        </CardHeader>
        <CardContent>
          {data?.anomalies.length === 0 ? (
            <p className="text-center py-8 text-gray-500">Nuk u zbuluan anomalitë</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      ID e Transaksionit
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      ID e Klientit
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Shuma
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Data
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Lloji
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Rezultati Z
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {data?.anomalies.map((anomaly, idx) => (
                    <tr key={idx} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {anomaly.transaction_id}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {anomaly.customer_id}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-medium">
                        ${anomaly.amount ? anomaly.amount.toFixed(2) : '0.00'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {anomaly.date || 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {anomaly.anomaly_type || 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {anomaly.z_score !== undefined ? anomaly.z_score.toFixed(2) : '0.00'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
