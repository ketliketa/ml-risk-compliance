import { useEffect, useState } from 'react';
import api from '../lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { FileText, Shield, CheckCircle, XCircle, Calendar, Hash } from 'lucide-react';

interface Violation {
  requirement_id: string;
  requirement_text: string;
  evidence: string;
  severity: string;
}

interface ComplianceCheck {
  document_id: string;
  violations: Violation[];
  total_violations: number;
}

interface Document {
  document_id: string;
  filename: string;
  uploaded_at: string;
  text_length: number;
  file_type: string;
}

export default function Compliance() {
  const [documentId, setDocumentId] = useState('');
  const [complianceCheck, setComplianceCheck] = useState<ComplianceCheck | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loadingDocuments, setLoadingDocuments] = useState(true);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      setLoadingDocuments(true);
      const res = await api.get('/documents');
      setDocuments(res.data);
    } catch (err: any) {
      console.error('Failed to load documents:', err);
    } finally {
      setLoadingDocuments(false);
    }
  };

  const handleCheck = async () => {
    if (!documentId.trim()) {
      setError('Ju lutem shkruani ose zgjidhni ID e dokumentit');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const res = await api.post(`/compliance/check/${documentId}`);
      setComplianceCheck(res.data);
    } catch (err: any) {
      setError(err.message || 'Dështoi kontrolli i përputhjes');
      setComplianceCheck(null);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectDocument = (docId: string) => {
    setDocumentId(docId);
    setError(null);
    setComplianceCheck(null);
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2">
          Kontrolli i Përputhjes
        </h1>
        <p className="text-gray-600">Verifikoni dokumentet kundrejt kërkesave rregullatore</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Document Selection */}
        <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
          <CardHeader className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-t-lg border-b">
            <CardTitle className="flex items-center gap-2">
              <Shield className="w-5 h-5 text-blue-600" />
              Zgjidh Dokument
            </CardTitle>
            <CardDescription>
              Zgjidh një dokument për të kontrolluar shkeljet e përputhjes
            </CardDescription>
          </CardHeader>
          <CardContent className="p-6 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                ID e Dokumentit
              </label>
              <div className="flex gap-2">
                <Input
                  placeholder="Shkruaj ose zgjidh ID e dokumentit"
                  value={documentId}
                  onChange={(e) => {
                    setDocumentId(e.target.value);
                    setError(null);
                    setComplianceCheck(null);
                  }}
                  className="flex-1"
                />
                <Button 
                  onClick={handleCheck} 
                  disabled={loading || !documentId.trim()}
                  className="px-6 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800"
                >
                  {loading ? 'Po kontrollohet...' : 'Kontrollo'}
                </Button>
              </div>
            </div>

            {documents.length > 0 && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Ose zgjidh nga dokumentet e ngarkuara:
                </label>
                <div className="space-y-2 max-h-[400px] overflow-y-auto">
                  {documents.map((doc) => (
                    <div
                      key={doc.document_id}
                      onClick={() => handleSelectDocument(doc.document_id)}
                      className={`
                        p-4 rounded-xl border-2 cursor-pointer transition-all duration-200
                        ${documentId === doc.document_id
                          ? 'border-blue-500 bg-blue-50 shadow-md'
                          : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50'
                        }
                      `}
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
                      <div className="text-xs font-mono text-gray-400 bg-gray-100 px-2 py-1 rounded mt-2">
                        ID: {doc.document_id}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {loadingDocuments && (
              <div className="text-center py-8 text-gray-500">
                Po ngarkohen dokumentet...
              </div>
            )}

            {!loadingDocuments && documents.length === 0 && (
              <div className="text-center py-8">
                <FileText className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                <p className="text-gray-500 mb-2">Ende nuk ka dokumente të ngarkuar</p>
                <p className="text-sm text-gray-400">
                  Shkoni te faqja Dokumentet për të ngarkuar një dokument fillimisht
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Compliance Results */}
        <div>
          {error && (
            <Card className="mb-6 shadow-xl border-0 bg-red-50 border-l-4 border-red-500">
              <CardContent className="p-4">
                <div className="flex items-center gap-2 text-red-700">
                  <XCircle className="w-5 h-5" />
                  <span className="font-medium">{error}</span>
                </div>
              </CardContent>
            </Card>
          )}

          {complianceCheck && (
            <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
              <CardHeader className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-t-lg border-b">
                <CardTitle className="flex items-center gap-2">
                  {complianceCheck.total_violations === 0 ? (
                    <CheckCircle className="w-5 h-5 text-green-600" />
                  ) : (
                    <XCircle className="w-5 h-5 text-red-600" />
                  )}
                  Rezultatet e Përputhjes
                </CardTitle>
                <CardDescription>
                  ID e Dokumentit: <span className="font-mono text-xs">{complianceCheck.document_id}</span>
                  {' • '}
                  Shkelje Gjithsej: 
                  <span className={`font-semibold ml-1 ${
                    complianceCheck.total_violations === 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {complianceCheck.total_violations}
                  </span>
                </CardDescription>
              </CardHeader>
              <CardContent className="p-6">
                {complianceCheck.violations.length === 0 ? (
                  <div className="text-center py-12">
                    <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <CheckCircle className="w-8 h-8 text-green-600" />
                    </div>
                    <h3 className="text-xl font-semibold text-green-700 mb-2">
                      Nuk ka Shkelje të Përputhjes
                    </h3>
                    <p className="text-gray-600">
                      Ky dokument duket se është në përputhje me të gjitha rregullat.
                    </p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="p-4 bg-red-50 border-l-4 border-red-500 rounded-lg">
                      <div className="flex items-center gap-2 mb-2">
                        <XCircle className="w-5 h-5 text-red-600" />
                        <span className="font-semibold text-red-900">
                          {complianceCheck.total_violations} Shkelje{complianceCheck.total_violations !== 1 ? '' : ''} të Gjetura
                        </span>
                      </div>
                      <p className="text-sm text-red-700">
                        Ky dokument kërkon vëmendje për të adresuar çështjet e përputhjes.
                      </p>
                    </div>

                    {complianceCheck.violations.map((violation, idx) => (
                      <div
                        key={idx}
                        className={`p-5 rounded-xl border-2 ${
                          violation.severity === 'high'
                            ? 'border-red-300 bg-red-50'
                            : 'border-yellow-300 bg-yellow-50'
                        }`}
                      >
                        <div className="flex justify-between items-start mb-3">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <Shield className={`w-4 h-4 ${
                                violation.severity === 'high' ? 'text-red-600' : 'text-yellow-600'
                              }`} />
                              <span className="font-semibold text-gray-900">
                                Kërkesa: {violation.requirement_id}
                              </span>
                            </div>
                            <div className="text-sm text-gray-700 mt-1 bg-white/60 p-3 rounded-lg">
                              {violation.requirement_text}
                            </div>
                          </div>
                          <span
                            className={`px-3 py-1 rounded-lg text-xs font-bold ${
                              violation.severity === 'high'
                                ? 'bg-red-200 text-red-800'
                                : 'bg-yellow-200 text-yellow-800'
                            }`}
                          >
                            {violation.severity.toUpperCase()}
                          </span>
                        </div>
                        <div className="mt-4 pt-4 border-t border-gray-300">
                          <div className="text-sm font-semibold text-gray-700 mb-2">Dëshmi:</div>
                          <div className="text-sm text-gray-600 bg-white/60 p-3 rounded-lg italic border-l-4 border-gray-400">
                            "{violation.evidence}"
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {!complianceCheck && !error && (
            <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
              <CardContent className="py-20">
                <div className="text-center">
                  <Shield className="w-20 h-20 text-gray-300 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-gray-700 mb-2">
                    Gati për Kontrollin e Përputhjes
                  </h3>
                  <p className="text-gray-500">
                    Zgjidh një dokument nga lista ose shkruaj ID e dokumentit për të kontrolluar shkeljet e përputhjes
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
