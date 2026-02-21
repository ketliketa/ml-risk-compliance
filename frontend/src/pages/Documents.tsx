import { useEffect, useState, useRef } from 'react';
import api from '../lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Upload, FileText, Calendar, Hash, AlertTriangle, TrendingUp, Trash2 } from 'lucide-react';
import { useAutoDeleteOnRefresh } from '../hooks/useAutoDelete';

interface Document {
  document_id: string;
  filename: string;
  uploaded_at: string;
  text_length: number;
  file_type: string;
  analysis?: {
    summary: string;
    key_findings: string[];
    keywords: string[];
  };
  csv_anomalies?: {
    has_anomalies: boolean;
    anomalies: any[];
    total_rows: number;
    total_columns: number;
    analysis: string;
    anomaly_count: number;
  };
  document_anomalies?: {
    has_anomalies: boolean;
    anomalies: any[];
    analysis: string;
    anomaly_count: number;
    high_severity_count: number;
    medium_severity_count: number;
    low_severity_count: number;
  };
}

export default function Documents() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedDoc, setSelectedDoc] = useState<Document | null>(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Auto-delete documents on page refresh
  useAutoDeleteOnRefresh();

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      const res = await api.get('/documents');
      setDocuments(res.data);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to load documents');
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      setUploading(true);
      setError(null);
      const formData = new FormData();
      formData.append('file', file);

      const uploadRes = await api.post('/documents/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      // Refresh documents list
      await fetchDocuments();
      
      // Auto-select the newly uploaded document
      if (uploadRes.data.document_id) {
        await handleViewDetails(uploadRes.data.document_id);
      }
      
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (err: any) {
      setError(err.message || 'Failed to upload document');
    } finally {
      setUploading(false);
    }
  };

  const handleViewDetails = async (docId: string) => {
    try {
      const res = await api.get(`/documents/${docId}`);
      setSelectedDoc(res.data);
    } catch (err: any) {
      setError(err.message || 'Failed to load document details');
    }
  };

  const handleDeleteDocument = async (docId: string) => {
    if (!confirm('A jeni të sigurt që dëshironi ta fshini këtë dokument?')) {
      return;
    }

    try {
      await api.delete(`/documents/${docId}`);
      if (selectedDoc?.document_id === docId) {
        setSelectedDoc(null);
      }
      await fetchDocuments();
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to delete document');
    }
  };

  // Auto-delete documents on page refresh/unload
  useEffect(() => {
    const handleBeforeUnload = () => {
      // Delete all documents when page is refreshed
      documents.forEach(async (doc) => {
        try {
          await api.delete(`/documents/${doc.document_id}`);
        } catch (err) {
          // Ignore errors during cleanup
        }
      });
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [documents]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-600 mb-4"></div>
          <p className="text-gray-600">Po ngarkohen dokumentet...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2">
            Dokumentet
          </h1>
          <p className="text-gray-600">Menaxhoni dhe analizoni dokumentet tuaja</p>
        </div>
        <div className="flex gap-3">
          <input
            ref={fileInputRef}
            type="file"
            onChange={handleUpload}
            className="hidden"
            id="file-upload"
            accept=".pdf,.docx,.txt,.md,.xlsx,.csv"
          />
          <Button
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
            className="px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 shadow-lg shadow-blue-500/30 transition-all"
          >
            <Upload className="w-5 h-5 mr-2" />
            {uploading ? 'Po ngarkohet...' : 'Ngarko Dokument'}
          </Button>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border-l-4 border-red-500 rounded-lg text-red-700 animate-fadeIn">
          {error}
        </div>
      )}

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Documents List */}
        <div className="lg:col-span-1">
          <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
            <CardHeader className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-t-lg border-b">
              <CardTitle className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-blue-600" />
                Biblioteka e Dokumenteve
              </CardTitle>
              <CardDescription>
                {documents.length} {documents.length === 1 ? 'dokument' : 'dokumente'} të ngarkuar
              </CardDescription>
            </CardHeader>
            <CardContent className="p-4">
              {documents.length === 0 ? (
                <div className="text-center py-12">
                  <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500 mb-4">Ende nuk ka dokumente të ngarkuar</p>
                  <Button
                    onClick={() => fileInputRef.current?.click()}
                    variant="outline"
                    className="mx-auto"
                  >
                    Ngarko Dokumentin tënd të Parë
                  </Button>
                </div>
              ) : (
                <div className="space-y-3 max-h-[600px] overflow-y-auto">
                  {documents.map((doc) => (
                    <div
                      key={doc.document_id}
                      className={`
                        p-4 rounded-xl border-2 transition-all duration-200
                        ${selectedDoc?.document_id === doc.document_id
                          ? 'border-blue-500 bg-blue-50 shadow-md'
                          : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50 hover:shadow-sm'
                        }
                      `}
                    >
                      <div 
                        className="cursor-pointer"
                        onClick={() => handleViewDetails(doc.document_id)}
                      >
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex-1 min-w-0">
                            <div className="font-semibold text-gray-900 truncate mb-1">
                              {doc.filename}
                            </div>
                            <div className="flex items-center gap-3 text-xs text-gray-500">
                              <span className="flex items-center gap-1">
                                <Calendar className="w-3 h-3" />
                                {new Date(doc.uploaded_at).toLocaleDateString()}
                              </span>
                              <span className="flex items-center gap-1">
                                <Hash className="w-3 h-3" />
                                {doc.text_length.toLocaleString()} chars
                              </span>
                            </div>
                          </div>
                        </div>
                        {doc.analysis?.keywords && doc.analysis.keywords.length > 0 && (
                          <div className="flex flex-wrap gap-1 mt-2">
                            {doc.analysis.keywords.slice(0, 3).map((keyword, idx) => (
                              <span
                                key={idx}
                                className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded-md text-xs font-medium"
                              >
                                {keyword}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                      <div className="mt-3 pt-3 border-t">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeleteDocument(doc.document_id);
                          }}
                          className="w-full text-red-600 hover:text-red-700 hover:bg-red-50"
                        >
                          <Trash2 className="w-4 h-4 mr-1" />
                          Fshi Dokumentin
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Document Details */}
        <div className="lg:col-span-2 space-y-6">
          {selectedDoc ? (
            <>
              {/* Document Details */}
              <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
                <CardHeader className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-t-lg border-b">
                  <div>
                    <CardTitle className="flex items-center gap-2">
                      <FileText className="w-5 h-5 text-purple-600" />
                      Analiza e Dokumentit
                    </CardTitle>
                    <CardDescription className="mt-1">{selectedDoc.filename}</CardDescription>
                  </div>
                </CardHeader>
                <CardContent className="p-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                    <div className="space-y-1">
                      <div className="text-sm font-medium text-gray-500 flex items-center gap-2">
                        <Calendar className="w-4 h-4" />
                        Ngarkuar
                      </div>
                      <div className="text-gray-900 font-medium">
                        {new Date(selectedDoc.uploaded_at).toLocaleString()}
                      </div>
                    </div>
                    <div className="space-y-1">
                      <div className="text-sm font-medium text-gray-500 flex items-center gap-2">
                        <FileText className="w-4 h-4" />
                        Lloji i Skedarit
                      </div>
                      <div className="text-gray-900 font-medium">{selectedDoc.file_type}</div>
                    </div>
                    <div className="space-y-1">
                      <div className="text-sm font-medium text-gray-500 flex items-center gap-2">
                        <Hash className="w-4 h-4" />
                        Gjatësia e Tekstit
                      </div>
                      <div className="text-gray-900 font-medium">
                        {selectedDoc.text_length.toLocaleString()} karaktere
                      </div>
                    </div>
                  </div>

                  {selectedDoc.analysis && (
                    <div className="space-y-6 pt-6 border-t">
                      {selectedDoc.analysis.summary && (
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900 mb-3">Përmbledhje</h3>
                          <p className="text-gray-700 leading-relaxed bg-gray-50 p-4 rounded-lg">
                            {selectedDoc.analysis.summary}
                          </p>
                        </div>
                      )}
                      {selectedDoc.analysis.key_findings && selectedDoc.analysis.key_findings.length > 0 && (
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900 mb-3">Gjetjet Kryesore</h3>
                          <ul className="space-y-2">
                            {selectedDoc.analysis.key_findings.map((finding, idx) => (
                              <li
                                key={idx}
                                className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg border-l-4 border-blue-500"
                              >
                                <Hash className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
                                <span className="text-gray-700">{finding}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {selectedDoc.analysis.keywords && selectedDoc.analysis.keywords.length > 0 && (
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900 mb-3">Fjalët Kyçe</h3>
                          <div className="flex flex-wrap gap-2">
                            {selectedDoc.analysis.keywords.map((keyword, idx) => (
                              <span
                                key={idx}
                                className="px-3 py-1.5 bg-gradient-to-r from-blue-100 to-purple-100 text-blue-800 rounded-full text-sm font-medium shadow-sm"
                              >
                                {keyword}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Document Anomalies Section (for all file types) */}
                  {selectedDoc.document_anomalies && (
                    <div className="space-y-6 pt-6 border-t">
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                          <AlertTriangle className="w-5 h-5 text-red-600" />
                          Zbulimi i Anomalive të Dokumentit
                        </h3>
                        <div className={`p-4 rounded-lg border-l-4 mb-4 ${
                          selectedDoc.document_anomalies.has_anomalies
                            ? 'bg-gradient-to-r from-red-50 to-orange-50 border-red-500'
                            : 'bg-gradient-to-r from-green-50 to-emerald-50 border-green-500'
                        }`}>
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-semibold text-gray-900">
                              {selectedDoc.document_anomalies.has_anomalies 
                                ? `${selectedDoc.document_anomalies.anomaly_count} Anomali të Zbuluara`
                                : 'Nuk u Gjetën Anomali'}
                            </span>
                            {selectedDoc.document_anomalies.has_anomalies && (
                              <div className="flex gap-2">
                                {selectedDoc.document_anomalies.high_severity_count > 0 && (
                                  <span className="px-2 py-1 bg-red-200 text-red-800 rounded text-xs font-bold">
                                    {selectedDoc.document_anomalies.high_severity_count} E Lartë
                                  </span>
                                )}
                                {selectedDoc.document_anomalies.medium_severity_count > 0 && (
                                  <span className="px-2 py-1 bg-yellow-200 text-yellow-800 rounded text-xs font-bold">
                                    {selectedDoc.document_anomalies.medium_severity_count} Mesatare
                                  </span>
                                )}
                                {selectedDoc.document_anomalies.low_severity_count > 0 && (
                                  <span className="px-2 py-1 bg-blue-200 text-blue-800 rounded text-xs font-bold">
                                    {selectedDoc.document_anomalies.low_severity_count} E Ulët
                                  </span>
                                )}
                              </div>
                            )}
                          </div>
                          <p className="text-sm text-gray-600">{selectedDoc.document_anomalies.analysis}</p>
                        </div>

                        {selectedDoc.document_anomalies.has_anomalies && selectedDoc.document_anomalies.anomalies.length > 0 && (
                          <div className="space-y-3 max-h-[400px] overflow-y-auto">
                            {selectedDoc.document_anomalies.anomalies.slice(0, 20).map((anomaly: any, idx: number) => (
                              <div
                                key={idx}
                                className={`p-4 rounded-lg border-l-4 ${
                                  anomaly.severity === 'high'
                                    ? 'bg-red-50 border-red-500'
                                    : anomaly.severity === 'medium'
                                    ? 'bg-yellow-50 border-yellow-500'
                                    : 'bg-blue-50 border-blue-500'
                                }`}
                              >
                                <div className="flex items-start justify-between mb-2">
                                  <div className="flex-1">
                                    <div className="font-semibold text-gray-900 mb-1 flex items-center gap-2">
                                      {anomaly.anomaly_type?.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase()).replace('Anomaly', 'Anomali')}
                                      <span className={`px-2 py-0.5 rounded text-xs font-bold ${
                                        anomaly.severity === 'high'
                                          ? 'bg-red-200 text-red-800'
                                          : anomaly.severity === 'medium'
                                          ? 'bg-yellow-200 text-yellow-800'
                                          : 'bg-blue-200 text-blue-800'
                                      }`}>
                                        {anomaly.severity?.toUpperCase() || 'UNKNOWN'}
                                      </span>
                                    </div>
                                    {anomaly.description && (
                                      <div className="text-sm text-gray-700 mb-2">
                                        {anomaly.description}
                                      </div>
                                    )}
                                    {anomaly.keyword && (
                                      <div className="text-sm text-gray-700">
                                        <span className="font-medium">Fjalë Kyçe:</span> {anomaly.keyword}
                                        {anomaly.count && ` (${anomaly.count} herë)`}
                                      </div>
                                    )}
                                    {anomaly.context && (
                                      <div className="text-xs text-gray-600 mt-2 bg-white/60 p-2 rounded italic border-l-2 border-gray-300">
                                        "{anomaly.context.substring(0, 200)}{anomaly.context.length > 200 ? '...' : ''}"
                                      </div>
                                    )}
                                    {anomaly.phrase && (
                                      <div className="text-sm text-gray-700 mt-1">
                                        <span className="font-medium">Fraza:</span> "{anomaly.phrase}"
                                      </div>
                                    )}
                                  </div>
                                </div>
                              </div>
                            ))}
                            {selectedDoc.document_anomalies.anomalies.length > 20 && (
                              <p className="text-sm text-gray-500 text-center py-2">
                                Duke shfaqur 20 të parat nga {selectedDoc.document_anomalies.anomalies.length} anomalitë
                              </p>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* CSV Anomalies Section (specific to CSV files) */}
                  {selectedDoc.csv_anomalies && (
                    <div className="space-y-6 pt-6 border-t">
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                          <TrendingUp className="w-5 h-5 text-orange-600" />
                          Zbulimi i Anomalive të të Dhënave CSV
                        </h3>
                        <div className={`p-4 rounded-lg border-l-4 mb-4 ${
                          selectedDoc.csv_anomalies.has_anomalies
                            ? 'bg-gradient-to-r from-orange-50 to-yellow-50 border-orange-500'
                            : 'bg-gradient-to-r from-green-50 to-emerald-50 border-green-500'
                        }`}>
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-semibold text-gray-900">
                              {selectedDoc.csv_anomalies.has_anomalies 
                                ? `${selectedDoc.csv_anomalies.anomaly_count} Anomali të Zbuluara`
                                : 'Nuk u Gjetën Anomali'}
                            </span>
                            {selectedDoc.csv_anomalies.has_anomalies && (
                              <AlertTriangle className="w-5 h-5 text-orange-600" />
                            )}
                          </div>
                          <p className="text-sm text-gray-700 mb-2">
                            Skedari: {selectedDoc.csv_anomalies.total_rows} rreshta × {selectedDoc.csv_anomalies.total_columns} kolona
                          </p>
                          <p className="text-sm text-gray-600">{selectedDoc.csv_anomalies.analysis}</p>
                        </div>

                        {selectedDoc.csv_anomalies.has_anomalies && selectedDoc.csv_anomalies.anomalies.length > 0 && (
                          <div className="space-y-3 max-h-[400px] overflow-y-auto">
                            {selectedDoc.csv_anomalies.anomalies.slice(0, 20).map((anomaly: any, idx: number) => (
                              <div
                                key={idx}
                                className="p-4 bg-red-50 border-l-4 border-red-500 rounded-lg"
                              >
                                <div className="flex items-start justify-between mb-2">
                                  <div className="flex-1">
                                    <div className="font-semibold text-gray-900 mb-1">
                                      {anomaly.anomaly_type}
                                    </div>
                                    <div className="text-sm text-gray-700">
                                      <span className="font-medium">Kolona:</span> {anomaly.column}
                                      {anomaly.row_index >= 0 && (
                                        <> • <span className="font-medium">Rreshti:</span> {anomaly.row_index + 1}</>
                                      )}
                                      {anomaly.value !== null && anomaly.value !== undefined && (
                                        <> • <span className="font-medium">Vlera:</span> {anomaly.value}</>
                                      )}
                                    </div>
                                    {anomaly.z_score !== undefined && (
                                      <div className="text-xs text-gray-600 mt-1">
                                        Z-Score: {anomaly.z_score.toFixed(2)}
                                      </div>
                                    )}
                                  </div>
                                </div>
                              </div>
                            ))}
                            {selectedDoc.csv_anomalies.anomalies.length > 20 && (
                              <p className="text-sm text-gray-500 text-center py-2">
                                Duke shfaqur 20 të parat nga {selectedDoc.csv_anomalies.anomalies.length} anomalitë
                              </p>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

            </>
          ) : (
            <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
              <CardContent className="py-20">
                <div className="text-center">
                  <FileText className="w-20 h-20 text-gray-300 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-gray-700 mb-2">
                    Zgjidh një Dokument
                  </h3>
                  <p className="text-gray-500">
                    Zgjidh një dokument nga lista për të parë detajet dhe për të biseduar me asistentin AI
                  </p>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
