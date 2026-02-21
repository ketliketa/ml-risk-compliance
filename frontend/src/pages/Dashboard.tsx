import { useEffect, useState } from 'react';
import api from '../lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { AlertCircle, FileText, Shield, TrendingUp } from 'lucide-react';

interface DashboardData {
  totalDocuments: number;
  highRiskCount: number;
  mediumRiskCount: number;
  lowRiskCount: number;
  averageScore: number;
  totalAlerts: number;
  totalAnomalies: number;
}

export default function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [riskRes, alertsRes, anomaliesRes, docsRes] = await Promise.all([
          api.get('/risk/dashboard'),
          api.get('/alerts'),
          api.get('/anomalies'),
          api.get('/documents'),
        ]);

        const riskData = riskRes.data || {};
        setData({
          totalDocuments: riskData.total_documents || (docsRes.data ? docsRes.data.length : 0),
          highRiskCount: riskData.high_risk_count || 0,
          mediumRiskCount: riskData.medium_risk_count || 0,
          lowRiskCount: riskData.low_risk_count || 0,
          averageScore: riskData.average_score || 0,
          totalAlerts: (alertsRes.data && alertsRes.data.total) ? alertsRes.data.total : 0,
          totalAnomalies: (anomaliesRes.data && anomaliesRes.data.total) ? anomaliesRes.data.total : 0,
        });
        setError(null);
      } catch (err: any) {
        setError(err.message || 'Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-600 mb-4"></div>
          <p className="text-gray-600">Po ngarkohet paneli...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-red-50 border-l-4 border-red-500 rounded-lg text-red-700">
        Error: {error}
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fadeIn">
      <div>
        <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2">
          Paneli Kryesor
        </h1>
        <p className="text-gray-600">Përmbledhje e metrikave të rrezikut dhe përputhjes</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="shadow-xl border-0 bg-gradient-to-br from-blue-50 to-blue-100 hover:shadow-2xl transition-all duration-300">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-700">Dokumente Gjithsej</CardTitle>
            <div className="p-2 bg-blue-500 rounded-lg">
              <FileText className="h-5 w-5 text-white" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-blue-700">{data?.totalDocuments || 0}</div>
            <p className="text-xs text-gray-600 mt-1">Të gjitha skedarët e ngarkuar</p>
          </CardContent>
        </Card>

        <Card className="shadow-xl border-0 bg-gradient-to-br from-red-50 to-red-100 hover:shadow-2xl transition-all duration-300">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-700">Rrezik i Lartë</CardTitle>
            <div className="p-2 bg-red-500 rounded-lg">
              <Shield className="h-5 w-5 text-white" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-red-700">{data?.highRiskCount || 0}</div>
            <p className="text-xs text-gray-600 mt-1">Kërkon vëmendje</p>
          </CardContent>
        </Card>

        <Card className="shadow-xl border-0 bg-gradient-to-br from-yellow-50 to-yellow-100 hover:shadow-2xl transition-all duration-300">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-700">Sinjalizime Aktive</CardTitle>
            <div className="p-2 bg-yellow-500 rounded-lg">
              <AlertCircle className="h-5 w-5 text-white" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-yellow-700">{data?.totalAlerts || 0}</div>
            <p className="text-xs text-gray-600 mt-1">Njoftimet e sistemit</p>
          </CardContent>
        </Card>

        <Card className="shadow-xl border-0 bg-gradient-to-br from-orange-50 to-orange-100 hover:shadow-2xl transition-all duration-300">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-700">Anomalitë</CardTitle>
            <div className="p-2 bg-orange-500 rounded-lg">
              <TrendingUp className="h-5 w-5 text-white" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-orange-700">{data?.totalAnomalies || 0}</div>
            <p className="text-xs text-gray-600 mt-1">Vlera ekstreme të zbuluara</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
        <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
          <CardHeader className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-t-lg border-b">
            <CardTitle>Përmbledhje e Rrezikut</CardTitle>
            <CardDescription>Shpërndarja e niveleve të rrezikut</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm">Rrezik i Lartë</span>
                  <span className="text-sm font-medium">{data?.highRiskCount || 0}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-red-600 h-2 rounded-full"
                    style={{ width: `${((data?.highRiskCount || 0) / (data?.totalDocuments || 1)) * 100}%` }}
                  ></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm">Rrezik Mesatar</span>
                  <span className="text-sm font-medium">{data?.mediumRiskCount || 0}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-yellow-500 h-2 rounded-full"
                    style={{ width: `${((data?.mediumRiskCount || 0) / (data?.totalDocuments || 1)) * 100}%` }}
                  ></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm">Rrezik i Ulët</span>
                  <span className="text-sm font-medium">{data?.lowRiskCount || 0}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-green-500 h-2 rounded-full"
                    style={{ width: `${((data?.lowRiskCount || 0) / (data?.totalDocuments || 1)) * 100}%` }}
                  ></div>
                </div>
              </div>
            </div>
            <div className="mt-4 pt-4 border-t">
              <div className="flex justify-between">
                <span className="text-sm font-medium">Rezultati Mesatar i Rrezikut</span>
                <span className="text-lg font-bold">{data?.averageScore ? data.averageScore.toFixed(1) : '0.0'}/100</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
          <CardHeader className="bg-gradient-to-r from-indigo-50 to-blue-50 rounded-t-lg border-b">
            <CardTitle>Statistika të Shpejta</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span>Dokumente Gjithsej</span>
                <span className="font-semibold">{data?.totalDocuments || 0}</span>
              </div>
              <div className="flex justify-between">
                <span>Dokumente me Rrezik të Lartë</span>
                <span className="font-semibold text-red-600">{data?.highRiskCount || 0}</span>
              </div>
              <div className="flex justify-between">
                <span>Sinjalizime Aktive</span>
                <span className="font-semibold text-yellow-600">{data?.totalAlerts || 0}</span>
              </div>
              <div className="flex justify-between">
                <span>Anomalitë të Zbuluara</span>
                <span className="font-semibold text-orange-600">{data?.totalAnomalies || 0}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
