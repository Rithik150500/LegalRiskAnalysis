import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Documents from './pages/Documents';
import Analyses from './pages/Analyses';
import AnalysisDetail from './pages/AnalysisDetail';
import NewAnalysis from './pages/NewAnalysis';

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/documents" element={<Documents />} />
        <Route path="/analyses" element={<Analyses />} />
        <Route path="/analyses/new" element={<NewAnalysis />} />
        <Route path="/analyses/:analysisId" element={<AnalysisDetail />} />
      </Routes>
    </Layout>
  );
}

export default App;
