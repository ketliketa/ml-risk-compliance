import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Documents from './pages/Documents';
import Compliance from './pages/Compliance';
import Risk from './pages/Risk';
import Anomalies from './pages/Anomalies';
import Reports from './pages/Reports';
import Alerts from './pages/Alerts';
import Chat from './pages/Chat';
import { 
  LayoutDashboard, 
  FileText, 
  Shield, 
  AlertTriangle, 
  TrendingUp, 
  FileBarChart, 
  Bell,
  MessageSquare
} from 'lucide-react';

function NavLink({ to, children, icon: Icon }: { to: string; children: React.ReactNode; icon: React.ComponentType<{ className?: string }> }) {
  const location = useLocation();
  const isActive = location.pathname === to;
  
  return (
    <Link
      to={to}
      className={`
        group relative flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200
        ${isActive 
          ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-lg shadow-blue-500/30' 
          : 'text-gray-700 hover:bg-gray-100 hover:text-blue-600'
        }
      `}
    >
      <Icon className={`w-5 h-5 ${isActive ? 'text-white' : 'text-gray-500 group-hover:text-blue-600'}`} />
      <span className="font-medium">{children}</span>
      {isActive && (
        <div className="absolute right-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-white rounded-l-full" />
      )}
    </Link>
  );
}

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
        <nav className="bg-white/80 backdrop-blur-lg border-b border-gray-200/50 shadow-sm sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-20">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center shadow-lg">
                  <FileText className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                    Projekti ML
                  </h1>
                  <p className="text-xs text-gray-500">Rreziku & Përputhja</p>
                </div>
              </div>
            </div>
          </div>
        </nav>

        <div className="flex">
          <aside className="w-64 min-h-screen bg-white/60 backdrop-blur-lg border-r border-gray-200/50 p-6 sticky top-20">
            <nav className="space-y-2">
              <NavLink to="/" icon={LayoutDashboard}>Paneli Kryesor</NavLink>
              <NavLink to="/documents" icon={FileText}>Dokumentet</NavLink>
              <NavLink to="/compliance" icon={Shield}>Përputhja</NavLink>
              <NavLink to="/risk" icon={AlertTriangle}>Rreziku</NavLink>
              <NavLink to="/anomalies" icon={TrendingUp}>Anomalitë</NavLink>
              <NavLink to="/reports" icon={FileBarChart}>Raportet</NavLink>
              <NavLink to="/alerts" icon={Bell}>Sinjalizimet</NavLink>
              <NavLink to="/chat" icon={MessageSquare}>Biseda</NavLink>
            </nav>
          </aside>

          <main className="flex-1 p-8">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/documents" element={<Documents />} />
              <Route path="/compliance" element={<Compliance />} />
              <Route path="/risk" element={<Risk />} />
              <Route path="/anomalies" element={<Anomalies />} />
              <Route path="/reports" element={<Reports />} />
              <Route path="/alerts" element={<Alerts />} />
              <Route path="/chat" element={<Chat />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
}

export default App;
