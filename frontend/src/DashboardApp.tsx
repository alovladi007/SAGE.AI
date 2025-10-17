import React, { useState, useEffect, useCallback } from 'react';
import { Upload, FileText, AlertTriangle, Shield, BarChart3, Search, Users, Settings, ChevronDown, Eye, Download, X, CheckCircle, Clock, AlertCircle, TrendingUp, FileCheck, Database, Activity, Image, Network, MessageSquare, Brain, Layers, GitBranch, Target, Zap, Filter, Calendar, Hash, PieChart, LineChart, Play, RefreshCw, Send, UserPlus, Flag } from 'lucide-react';
import api, { handleApiError, Paper, Statistics } from './services/api';

// @ts-ignore - Environment variable from Vite
const API_URL = import.meta.env.REACT_APP_API_URL || 'http://localhost:8001';

// Main App Component
const AcademicIntegrityPlatform = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [papers, setPapers] = useState<Paper[]>([]);
  const [statistics, setStatistics] = useState<Statistics | null>(null);
  const [selectedPaper, setSelectedPaper] = useState<Paper | null>(null);

  useEffect(() => {
    fetchStatistics();
    fetchRecentPapers();
  }, []);

  const fetchStatistics = async () => {
    try {
      const data = await api.statistics.getOverview();
      setStatistics(data);
    } catch (error) {
      console.error('Failed to fetch statistics:', error);
      // Set mock data as fallback for demo purposes
      setStatistics({
        total_papers: 0,
        processed_papers: 0,
        processing_rate: 0,
        total_anomalies_detected: 0,
        high_risk_papers: 0,
        average_processing_time: 'N/A',
        last_updated: new Date().toISOString()
      });
    }
  };

  const fetchRecentPapers = async () => {
    try {
      const data = await api.papers.search({ limit: 10 });
      setPapers(data.results || []);
    } catch (error) {
      console.error('Failed to fetch papers:', error);
      setPapers([]);
    }
  };

  const renderContent = () => {
    switch(activeTab) {
      case 'dashboard':
        return <Dashboard statistics={statistics} papers={papers} />;
      case 'upload':
        return <UploadSection onUploadSuccess={fetchRecentPapers} />;
      case 'search':
        return <SearchSection papers={papers} setPapers={setPapers} setSelectedPaper={setSelectedPaper} />;
      case 'analysis':
        return <AnalysisSection selectedPaper={selectedPaper} />;
      case 'images':
        return <ImageForensicsSection selectedPaper={selectedPaper} />;
      case 'statistics':
        return <StatisticalTestsSection selectedPaper={selectedPaper} />;
      case 'citations':
        return <CitationNetworkSection selectedPaper={selectedPaper} />;
      case 'explainability':
        return <ExplainabilitySection selectedPaper={selectedPaper} />;
      case 'collaboration':
        return <CollaborationSection selectedPaper={selectedPaper} />;
      case 'batch':
        return <BatchProcessingSection />;
      case 'reports':
        return <ReportsSection papers={papers} />;
      default:
        return <Dashboard statistics={statistics} papers={papers} />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Shield className="w-8 h-8 text-indigo-600" />
              <h1 className="text-2xl font-bold text-gray-900">Academic Integrity Platform</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">Institution: Demo University</span>
              <button className="p-2 rounded-lg hover:bg-gray-100">
                <Settings className="w-5 h-5 text-gray-600" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b">
        <div className="px-6">
          <div className="flex space-x-6 overflow-x-auto">
            {[
              { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
              { id: 'upload', label: 'Upload', icon: Upload },
              { id: 'search', label: 'Search', icon: Search },
              { id: 'analysis', label: 'Analysis', icon: FileCheck },
              { id: 'images', label: 'Image Forensics', icon: Image },
              { id: 'statistics', label: 'Statistical Tests', icon: Hash },
              { id: 'citations', label: 'Citation Network', icon: Network },
              { id: 'explainability', label: 'AI Explainability', icon: Brain },
              { id: 'collaboration', label: 'Collaboration', icon: Users },
              { id: 'batch', label: 'Batch Processing', icon: Layers },
              { id: 'reports', label: 'Reports', icon: FileText }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-1 py-4 border-b-2 transition-colors whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'border-indigo-600 text-indigo-600'
                    : 'border-transparent text-gray-600 hover:text-gray-900'
                }`}
              >
                <tab.icon className="w-5 h-5" />
                <span className="font-medium text-sm">{tab.label}</span>
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="p-6">
        {renderContent()}
      </main>
    </div>
  );
};

// Dashboard Component
const Dashboard = ({ statistics, papers }) => {
  const stats = statistics || {
    total_papers: 0,
    processed_papers: 0,
    processing_rate: 0,
    total_anomalies_detected: 0,
    high_risk_papers: 0
  };

  const getRiskColor = (score) => {
    if (score >= 0.7) return 'text-red-600 bg-red-100';
    if (score >= 0.4) return 'text-yellow-600 bg-yellow-100';
    return 'text-green-600 bg-green-100';
  };

  const getRiskLabel = (score) => {
    if (score >= 0.7) return 'High Risk';
    if (score >= 0.4) return 'Medium Risk';
    return 'Low Risk';
  };

  return (
    <div className="space-y-6">
      {/* Statistics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Papers"
          value={stats.total_papers}
          icon={Database}
          color="blue"
        />
        <StatCard
          title="Processed"
          value={stats.processed_papers}
          icon={CheckCircle}
          color="green"
        />
        <StatCard
          title="Anomalies Detected"
          value={stats.total_anomalies_detected}
          icon={AlertTriangle}
          color="yellow"
        />
        <StatCard
          title="High Risk Papers"
          value={stats.high_risk_papers}
          icon={AlertCircle}
          color="red"
        />
      </div>

      {/* Processing Overview */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Processing Overview</h2>
        <div className="space-y-4">
          <div>
            <div className="flex justify-between text-sm mb-2">
              <span>Processing Rate</span>
              <span>{(stats.processing_rate * 100).toFixed(1)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-indigo-600 h-2 rounded-full transition-all duration-500"
                style={{ width: `${stats.processing_rate * 100}%` }}
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4 mt-4">
            <div className="flex items-center space-x-2">
              <Activity className="w-5 h-5 text-gray-400" />
              <span className="text-sm text-gray-600">Avg. Processing Time: 2.3 min</span>
            </div>
            <div className="flex items-center space-x-2">
              <Clock className="w-5 h-5 text-gray-400" />
              <span className="text-sm text-gray-600">Last Update: Just now</span>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Papers */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b">
          <h2 className="text-lg font-semibold">Recent Papers</h2>
        </div>
        <div className="divide-y">
          {papers.slice(0, 5).map((paper, index) => (
            <div key={index} className="px-6 py-4 hover:bg-gray-50 transition-colors">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="font-medium text-gray-900">{paper.title}</h3>
                  <p className="text-sm text-gray-600 mt-1">
                    {paper.authors?.join(', ')}
                  </p>
                  <div className="flex items-center space-x-4 mt-2">
                    <span className="text-xs text-gray-500">{paper.journal || 'No journal'}</span>
                    <span className="text-xs text-gray-500">
                      {paper.publication_date ? new Date(paper.publication_date).toLocaleDateString() : 'No date'}
                    </span>
                  </div>
                </div>
                <div className="ml-4">
                  <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getRiskColor(paper.risk_score || 0)}`}>
                    {getRiskLabel(paper.risk_score || 0)}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Statistics Card Component
const StatCard = ({ title, value, icon: Icon, color }) => {
  const colorClasses = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    yellow: 'bg-yellow-100 text-yellow-600',
    red: 'bg-red-100 text-red-600'
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-600">{title}</p>
          <p className="text-2xl font-bold mt-1">{value.toLocaleString()}</p>
        </div>
        <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
    </div>
  );
};

// Upload Section Component
const UploadSection = ({ onUploadSuccess }) => {
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [jobStatus, setJobStatus] = useState(null);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setUploading(true);
    setUploadedFile(file);
    setUploadProgress(0);

    const formData = new FormData();
    formData.append('file', file);

    try {
      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      const response = await fetch(`${API_URL}/api/papers/upload`, {
        method: 'POST',
        body: formData
      });

      clearInterval(progressInterval);
      setUploadProgress(100);

      const data = await response.json();
      setJobStatus(data);

      if (data.job_id) {
        pollJobStatus(data.job_id);
      }

      if (onUploadSuccess) {
        onUploadSuccess();
      }
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const pollJobStatus = async (jobId) => {
    const interval = setInterval(async () => {
      try {
        const response = await fetch(`${API_URL}/api/jobs/${jobId}/status`);
        const data = await response.json();

        setJobStatus(data);

        if (data.status === 'completed' || data.status === 'failed') {
          clearInterval(interval);
        }
      } catch (error) {
        console.error('Failed to fetch job status:', error);
        clearInterval(interval);
      }
    }, 2000);
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-lg shadow-lg p-8">
        <h2 className="text-2xl font-bold mb-6">Upload Paper for Analysis</h2>

        {/* Upload Area */}
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center hover:border-indigo-500 transition-colors">
          <Upload className="w-16 h-16 mx-auto text-gray-400 mb-4" />
          <h3 className="text-lg font-medium mb-2">Drop your PDF here or click to browse</h3>
          <p className="text-gray-600 mb-4">Supports PDF and TXT files up to 50MB</p>

          <input
            type="file"
            accept=".pdf,.txt"
            onChange={handleFileUpload}
            className="hidden"
            id="file-upload"
            disabled={uploading}
          />
          <label
            htmlFor="file-upload"
            className="inline-flex items-center px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 cursor-pointer transition-colors"
          >
            Select File
          </label>
        </div>

        {/* Upload Progress */}
        {uploading && (
          <div className="mt-6">
            <div className="flex items-center justify-between text-sm mb-2">
              <span className="font-medium">{uploadedFile?.name}</span>
              <span>{uploadProgress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-indigo-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
          </div>
        )}

        {/* Job Status */}
        {jobStatus && (
          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                {jobStatus.status === 'completed' ? (
                  <CheckCircle className="w-5 h-5 text-green-600" />
                ) : jobStatus.status === 'failed' ? (
                  <AlertCircle className="w-5 h-5 text-red-600" />
                ) : (
                  <Clock className="w-5 h-5 text-yellow-600 animate-pulse" />
                )}
                <div>
                  <p className="font-medium">
                    {jobStatus.status === 'completed' ? 'Analysis Complete' :
                     jobStatus.status === 'failed' ? 'Analysis Failed' :
                     'Processing...'}
                  </p>
                  <p className="text-sm text-gray-600">
                    Paper ID: {jobStatus.paper_id}
                  </p>
                </div>
              </div>
              {jobStatus.status === 'completed' && (
                <button className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">
                  View Results
                </button>
              )}
            </div>
          </div>
        )}

        {/* Recent Uploads */}
        <div className="mt-8">
          <h3 className="font-semibold mb-4">Processing Queue</h3>
          <div className="space-y-2">
            {[
              { name: 'Research_Paper_2024.pdf', status: 'processing', progress: 65 },
              { name: 'Thesis_Chapter_3.pdf', status: 'queued', progress: 0 },
              { name: 'Literature_Review.pdf', status: 'completed', progress: 100 }
            ].map((item, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <FileText className="w-5 h-5 text-gray-400" />
                  <span className="text-sm font-medium">{item.name}</span>
                </div>
                <div className="flex items-center space-x-2">
                  {item.status === 'completed' ? (
                    <CheckCircle className="w-5 h-5 text-green-600" />
                  ) : item.status === 'processing' ? (
                    <div className="flex items-center space-x-2">
                      <div className="w-24 bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full"
                          style={{ width: `${item.progress}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-600">{item.progress}%</span>
                    </div>
                  ) : (
                    <span className="text-xs text-gray-600">Queued</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// Search Section Component
const SearchSection = ({ papers, setPapers, setSelectedPaper }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState({
    author: '',
    journal: '',
    minRisk: 0,
    startDate: '',
    endDate: ''
  });
  const [searching, setSearching] = useState(false);

  const handleSearch = async () => {
    setSearching(true);

    try {
      const params = new URLSearchParams();
      if (searchQuery) params.append('query', searchQuery);
      if (filters.author) params.append('author', filters.author);
      if (filters.journal) params.append('journal', filters.journal);
      if (filters.minRisk > 0) params.append('min_risk_score', filters.minRisk);
      if (filters.startDate) params.append('start_date', filters.startDate);
      if (filters.endDate) params.append('end_date', filters.endDate);

      const response = await fetch(`${API_URL}/api/papers/search?${params}`);
      const data = await response.json();
      setPapers(data.results || []);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setSearching(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Search Bar */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="space-y-4">
          <div className="flex space-x-4">
            <div className="flex-1">
              <input
                type="text"
                placeholder="Search papers by title, abstract, or content..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <button
              onClick={handleSearch}
              disabled={searching}
              className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
            >
              {searching ? 'Searching...' : 'Search'}
            </button>
          </div>

          {/* Filters */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <input
              type="text"
              placeholder="Author"
              value={filters.author}
              onChange={(e) => setFilters({...filters, author: e.target.value})}
              className="px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <input
              type="text"
              placeholder="Journal"
              value={filters.journal}
              onChange={(e) => setFilters({...filters, journal: e.target.value})}
              className="px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <select
              value={filters.minRisk}
              onChange={(e) => setFilters({...filters, minRisk: parseFloat(e.target.value)})}
              className="px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="0">All Risk Levels</option>
              <option value="0.3">Low Risk & Above</option>
              <option value="0.6">Medium Risk & Above</option>
              <option value="0.8">High Risk Only</option>
            </select>
          </div>
        </div>
      </div>

      {/* Search Results */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b">
          <h2 className="text-lg font-semibold">
            Search Results ({papers.length} papers found)
          </h2>
        </div>
        <div className="divide-y max-h-96 overflow-y-auto">
          {papers.map((paper, index) => (
            <div
              key={index}
              className="px-6 py-4 hover:bg-gray-50 cursor-pointer transition-colors"
              onClick={() => setSelectedPaper(paper)}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="font-medium text-gray-900">{paper.title}</h3>
                  <p className="text-sm text-gray-600 mt-1">
                    {paper.authors?.join(', ')}
                  </p>
                  {paper.abstract && (
                    <p className="text-sm text-gray-500 mt-2 line-clamp-2">
                      {paper.abstract}
                    </p>
                  )}
                  <div className="flex items-center space-x-4 mt-2">
                    <span className="text-xs text-gray-500">{paper.journal || 'No journal'}</span>
                    <span className="text-xs text-gray-500">
                      {paper.publication_date ? new Date(paper.publication_date).toLocaleDateString() : 'No date'}
                    </span>
                  </div>
                </div>
                <div className="ml-4 flex flex-col items-end space-y-2">
                  <RiskBadge score={paper.risk_score || 0} />
                  <button className="text-indigo-600 hover:text-indigo-800 text-sm font-medium">
                    View Details →
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Analysis Section Component
const AnalysisSection = ({ selectedPaper }) => {
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeAnalysisTab, setActiveAnalysisTab] = useState('overview');

  useEffect(() => {
    if (selectedPaper) {
      fetchAnalysisData();
    }
  }, [selectedPaper]);

  const fetchAnalysisData = async () => {
    if (!selectedPaper?.paper_id) return;

    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/papers/${selectedPaper.paper_id}/analyze`);
      const data = await response.json();
      setAnalysisData(data);
    } catch (error) {
      console.error('Failed to fetch analysis:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!selectedPaper) {
    return (
      <div className="bg-white rounded-lg shadow p-12 text-center">
        <FileCheck className="w-16 h-16 mx-auto text-gray-400 mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No Paper Selected</h3>
        <p className="text-gray-600">Select a paper from the search results to view detailed analysis</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-12 text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">Loading analysis...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Paper Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-bold mb-2">{selectedPaper.title}</h2>
        <p className="text-gray-600 mb-4">{selectedPaper.authors?.join(', ')}</p>
        <div className="flex items-center space-x-6">
          <RiskMeter score={analysisData?.overall_risk_score || 0} />
          <div className="flex space-x-4">
            <button className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">
              <Download className="w-4 h-4 inline mr-2" />
              Download Report
            </button>
            <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
              <Eye className="w-4 h-4 inline mr-2" />
              View PDF
            </button>
          </div>
        </div>
      </div>

      {/* Analysis Tabs */}
      <div className="bg-white rounded-lg shadow">
        <div className="border-b">
          <div className="px-6 flex space-x-8">
            {['overview', 'similarity', 'anomalies', 'recommendations'].map(tab => (
              <button
                key={tab}
                onClick={() => setActiveAnalysisTab(tab)}
                className={`py-4 px-1 border-b-2 font-medium text-sm capitalize transition-colors ${
                  activeAnalysisTab === tab
                    ? 'border-indigo-600 text-indigo-600'
                    : 'border-transparent text-gray-600 hover:text-gray-900'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>

        <div className="p-6">
          {activeAnalysisTab === 'overview' && (
            <AnalysisOverview analysisData={analysisData} />
          )}
          {activeAnalysisTab === 'similarity' && (
            <SimilarityFindings findings={analysisData?.similarity_findings || []} />
          )}
          {activeAnalysisTab === 'anomalies' && (
            <AnomalyFindings findings={analysisData?.anomaly_findings || []} />
          )}
          {activeAnalysisTab === 'recommendations' && (
            <Recommendations recommendations={analysisData?.recommendations || []} />
          )}
        </div>
      </div>
    </div>
  );
};

// Analysis Overview Component
const AnalysisOverview = ({ analysisData }) => {
  if (!analysisData) return null;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-3 gap-6">
        <div className="text-center">
          <p className="text-sm text-gray-600 mb-2">Overall Risk Score</p>
          <p className="text-3xl font-bold text-indigo-600">
            {(analysisData.overall_risk_score * 100).toFixed(1)}%
          </p>
        </div>
        <div className="text-center">
          <p className="text-sm text-gray-600 mb-2">Similar Papers Found</p>
          <p className="text-3xl font-bold text-gray-900">
            {analysisData.similarity_findings?.length || 0}
          </p>
        </div>
        <div className="text-center">
          <p className="text-sm text-gray-600 mb-2">Anomalies Detected</p>
          <p className="text-3xl font-bold text-gray-900">
            {analysisData.anomaly_findings?.length || 0}
          </p>
        </div>
      </div>

      <div className="border-t pt-6">
        <h3 className="font-semibold mb-4">Key Findings</h3>
        <ul className="space-y-2">
          {analysisData.recommendations?.map((rec, index) => (
            <li key={index} className="flex items-start">
              <AlertTriangle className="w-5 h-5 text-yellow-500 mr-2 flex-shrink-0 mt-0.5" />
              <span className="text-sm text-gray-700">{rec}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

// Similarity Findings Component
const SimilarityFindings = ({ findings }) => {
  return (
    <div className="space-y-4">
      {findings.length === 0 ? (
        <p className="text-gray-600">No similar papers found.</p>
      ) : (
        findings.map((finding, index) => (
          <div key={index} className="border rounded-lg p-4 hover:bg-gray-50">
            <div className="flex items-start justify-between">
              <div>
                <h4 className="font-medium">{finding.title}</h4>
                <p className="text-sm text-gray-600 mt-1">{finding.authors?.join(', ')}</p>
                <div className="flex items-center space-x-4 mt-2">
                  <span className="text-xs text-gray-500">
                    Text Similarity: {(finding.text_similarity * 100).toFixed(1)}%
                  </span>
                  <span className="text-xs text-gray-500">
                    Semantic Similarity: {(finding.semantic_similarity * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
              <div className="text-right">
                <span className="text-lg font-bold text-indigo-600">
                  {(finding.overall_similarity * 100).toFixed(1)}%
                </span>
                <p className="text-xs text-gray-500 mt-1">Overall Match</p>
              </div>
            </div>
          </div>
        ))
      )}
    </div>
  );
};

// Anomaly Findings Component
const AnomalyFindings = ({ findings }) => {
  const getSeverityColor = (severity) => {
    switch(severity) {
      case 'critical': return 'text-red-600 bg-red-100';
      case 'high': return 'text-orange-600 bg-orange-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'low': return 'text-blue-600 bg-blue-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="space-y-4">
      {findings.length === 0 ? (
        <p className="text-gray-600">No anomalies detected.</p>
      ) : (
        findings.map((anomaly, index) => (
          <div key={index} className="border rounded-lg p-4">
            <div className="flex items-start justify-between">
              <div>
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getSeverityColor(anomaly.severity)}`}>
                    {anomaly.severity.toUpperCase()}
                  </span>
                  <span className="font-medium">{anomaly.type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
                </div>
                <p className="text-sm text-gray-700 mt-2">{anomaly.description}</p>
              </div>
              <div className="text-right">
                <span className="text-sm text-gray-500">
                  Confidence: {(anomaly.confidence * 100).toFixed(0)}%
                </span>
              </div>
            </div>
          </div>
        ))
      )}
    </div>
  );
};

// Recommendations Component
const Recommendations = ({ recommendations }) => {
  return (
    <div className="space-y-4">
      {recommendations.length === 0 ? (
        <p className="text-gray-600">No specific recommendations at this time.</p>
      ) : (
        <div className="space-y-3">
          {recommendations.map((rec, index) => (
            <div key={index} className="flex items-start space-x-3">
              <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-gray-700">{rec}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// Reports Section Component
const ReportsSection = ({ papers }) => {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-bold mb-6">Generate Reports</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="border rounded-lg p-6 hover:border-indigo-500 transition-colors cursor-pointer">
            <FileText className="w-12 h-12 text-indigo-600 mb-4" />
            <h3 className="font-semibold mb-2">Institutional Report</h3>
            <p className="text-sm text-gray-600 mb-4">
              Comprehensive analysis of all papers from your institution
            </p>
            <button className="text-indigo-600 font-medium text-sm">
              Generate Report →
            </button>
          </div>

          <div className="border rounded-lg p-6 hover:border-indigo-500 transition-colors cursor-pointer">
            <TrendingUp className="w-12 h-12 text-indigo-600 mb-4" />
            <h3 className="font-semibold mb-2">Trend Analysis</h3>
            <p className="text-sm text-gray-600 mb-4">
              Identify patterns and trends in academic integrity issues
            </p>
            <button className="text-indigo-600 font-medium text-sm">
              View Trends →
            </button>
          </div>
        </div>
      </div>

      {/* Recent Reports */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b">
          <h3 className="font-semibold">Recent Reports</h3>
        </div>
        <div className="divide-y">
          {[
            { name: 'Q4 2024 Integrity Report', date: '2024-12-01', type: 'Quarterly' },
            { name: 'Computer Science Department Review', date: '2024-11-15', type: 'Department' },
            { name: 'High Risk Papers Summary', date: '2024-11-10', type: 'Risk Analysis' }
          ].map((report, index) => (
            <div key={index} className="px-6 py-4 flex items-center justify-between hover:bg-gray-50">
              <div className="flex items-center space-x-3">
                <FileText className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="font-medium">{report.name}</p>
                  <p className="text-sm text-gray-600">{report.type} • {report.date}</p>
                </div>
              </div>
              <button className="text-indigo-600 hover:text-indigo-800">
                <Download className="w-5 h-5" />
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Risk Badge Component
const RiskBadge = ({ score }) => {
  const getRiskLevel = () => {
    if (score >= 0.7) return { label: 'High', color: 'bg-red-100 text-red-700' };
    if (score >= 0.4) return { label: 'Medium', color: 'bg-yellow-100 text-yellow-700' };
    return { label: 'Low', color: 'bg-green-100 text-green-700' };
  };

  const risk = getRiskLevel();

  return (
    <span className={`px-2 py-1 text-xs font-medium rounded-full ${risk.color}`}>
      {risk.label} Risk
    </span>
  );
};

// Risk Meter Component
const RiskMeter = ({ score }) => {
  const percentage = score * 100;
  const rotation = (percentage / 100) * 180 - 90;

  return (
    <div className="flex items-center space-x-4">
      <div className="relative w-32 h-16">
        <svg className="w-32 h-16" viewBox="0 0 120 60">
          <path
            d="M 10 60 A 50 50 0 0 1 110 60"
            fill="none"
            stroke="#e5e7eb"
            strokeWidth="8"
          />
          <path
            d="M 10 60 A 50 50 0 0 1 110 60"
            fill="none"
            stroke={percentage > 70 ? '#dc2626' : percentage > 40 ? '#f59e0b' : '#10b981'}
            strokeWidth="8"
            strokeDasharray={`${percentage * 1.57} 157`}
          />
        </svg>
        <div className="absolute inset-0 flex items-end justify-center pb-2">
          <span className="text-2xl font-bold">{percentage.toFixed(1)}%</span>
        </div>
      </div>
      <div>
        <p className="text-sm text-gray-600">Risk Score</p>
        <p className="font-semibold">
          {score >= 0.7 ? 'High Risk' : score >= 0.4 ? 'Medium Risk' : 'Low Risk'}
        </p>
      </div>
    </div>
  );
};

// Image Forensics Section
const ImageForensicsSection = ({ selectedPaper }) => {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
          <Image className="w-6 h-6 text-pink-600" />
          Image Manipulation Detection & Forensics
        </h2>
        {selectedPaper ? (
          <div className="space-y-6">
            <div className="grid grid-cols-3 gap-4">
              <div className="p-4 bg-pink-50 rounded-lg">
                <p className="text-sm text-gray-600">Images Analyzed</p>
                <p className="text-2xl font-bold text-pink-600">8</p>
              </div>
              <div className="p-4 bg-red-50 rounded-lg">
                <p className="text-sm text-gray-600">Manipulated</p>
                <p className="text-2xl font-bold text-red-600">2</p>
              </div>
              <div className="p-4 bg-orange-50 rounded-lg">
                <p className="text-sm text-gray-600">Duplicates Found</p>
                <p className="text-2xl font-bold text-orange-600">1</p>
              </div>
            </div>

            <div className="border-t pt-4">
              <h3 className="font-semibold mb-3">Detection Results</h3>
              <div className="grid grid-cols-2 gap-4">
                {[
                  { name: 'Figure 3A', status: 'Manipulation Detected', confidence: 0.92, type: 'danger' },
                  { name: 'Figure 5B', status: 'Duplicate Found', confidence: 0.88, type: 'warning' },
                  { name: 'Figure 1', status: 'Clean', confidence: 0.95, type: 'success' },
                  { name: 'Figure 2', status: 'Clean', confidence: 0.97, type: 'success' }
                ].map((img, idx) => (
                  <div key={idx} className={`p-4 border-2 rounded-lg ${
                    img.type === 'danger' ? 'border-red-300 bg-red-50' :
                    img.type === 'warning' ? 'border-orange-300 bg-orange-50' :
                    'border-green-300 bg-green-50'
                  }`}>
                    <div className="aspect-video bg-gray-200 rounded mb-2 flex items-center justify-center">
                      <Image className="w-12 h-12 text-gray-400" />
                    </div>
                    <p className="font-medium">{img.name}</p>
                    <p className="text-sm text-gray-600">{img.status}</p>
                    <p className="text-xs text-gray-500 mt-1">Confidence: {(img.confidence * 100).toFixed(1)}%</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center py-12 text-gray-500">
            <Image className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p>Select a paper to view image forensics analysis</p>
          </div>
        )}
      </div>
    </div>
  );
};

// Statistical Tests Section
const StatisticalTestsSection = ({ selectedPaper }) => {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
          <Hash className="w-6 h-6 text-orange-600" />
          Statistical Anomaly Detection
        </h2>
        {selectedPaper ? (
          <div className="space-y-6">
            {/* GRIM Test */}
            <div className="border rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold flex items-center gap-2">
                  <Hash className="w-4 h-4" />
                  GRIM Test (Granularity Check)
                </h3>
                <span className="px-3 py-1 bg-red-100 text-red-700 text-sm font-medium rounded-full">
                  3 Issues Found
                </span>
              </div>
              <p className="text-sm text-gray-600 mb-3">
                Tests if reported means are mathematically possible given the sample size
              </p>
              <div className="space-y-2">
                {[
                  { table: 'Table 2', mean: '3.45', n: 23, possible: false },
                  { table: 'Table 5', mean: '7.89', n: 15, possible: false },
                  { table: 'Table 7', mean: '4.33', n: 12, possible: false }
                ].map((test, idx) => (
                  <div key={idx} className="p-3 bg-red-50 rounded flex items-center justify-between">
                    <div>
                      <p className="font-medium">{test.table}</p>
                      <p className="text-sm text-gray-600">Mean: {test.mean}, N = {test.n}</p>
                    </div>
                    <span className="text-sm font-semibold text-red-600">Impossible</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Benford's Law */}
            <div className="border rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold flex items-center gap-2">
                  <PieChart className="w-4 h-4" />
                  Benford's Law Analysis
                </h3>
                <span className="px-3 py-1 bg-yellow-100 text-yellow-700 text-sm font-medium rounded-full">
                  Deviation Detected
                </span>
              </div>
              <p className="text-sm text-gray-600 mb-3">
                Tests if the distribution of leading digits follows the expected natural pattern
              </p>
              <div className="grid grid-cols-9 gap-1 mb-3">
                {[30.1, 17.6, 12.5, 9.7, 7.9, 6.7, 5.8, 5.1, 4.6].map((expected, idx) => {
                  const observed = idx === 0 ? 45.2 : idx === 1 ? 25.3 : expected + (Math.random() * 2 - 1);
                  const deviation = Math.abs(observed - expected);
                  return (
                    <div key={idx} className="text-center">
                      <div className="h-16 bg-gray-200 rounded relative overflow-hidden">
                        <div
                          className="absolute bottom-0 left-0 right-0 bg-blue-500"
                          style={{ height: `${expected * 2}%` }}
                        />
                        <div
                          className={`absolute bottom-0 left-0 right-0 ${deviation > 5 ? 'bg-red-500' : 'bg-green-500'} opacity-70`}
                          style={{ height: `${observed * 2}%` }}
                        />
                      </div>
                      <p className="text-xs mt-1">{idx + 1}</p>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* P-value Distribution */}
            <div className="border rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold flex items-center gap-2">
                  <LineChart className="w-4 h-4" />
                  P-value Distribution (P-hacking Detection)
                </h3>
                <span className="px-3 py-1 bg-yellow-100 text-yellow-700 text-sm font-medium rounded-full">
                  Suspicious Pattern
                </span>
              </div>
              <p className="text-sm text-gray-600 mb-3">
                Excessive p-values just below 0.05 may indicate selective reporting
              </p>
              <div className="h-32 bg-gray-50 rounded flex items-end justify-around p-2">
                {[
                  { range: '<0.01', count: 2 },
                  { range: '0.01-0.02', count: 3 },
                  { range: '0.02-0.03', count: 4 },
                  { range: '0.03-0.04', count: 5 },
                  { range: '0.04-0.05', count: 12 },
                  { range: '0.05-0.10', count: 1 }
                ].map((bar, idx) => (
                  <div key={idx} className="flex flex-col items-center gap-1 flex-1">
                    <div className="text-xs font-semibold">{bar.count}</div>
                    <div
                      className={`w-full rounded-t ${idx === 4 ? 'bg-red-500' : 'bg-blue-500'}`}
                      style={{ height: `${(bar.count / 12) * 100}%` }}
                    />
                    <div className="text-xs text-gray-600">{bar.range}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center py-12 text-gray-500">
            <BarChart3 className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p>Select a paper to view statistical tests</p>
          </div>
        )}
      </div>
    </div>
  );
};

// Citation Network Section
const CitationNetworkSection = ({ selectedPaper }) => {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
          <Network className="w-6 h-6 text-cyan-600" />
          Citation Network Analysis
        </h2>
        {selectedPaper ? (
          <div className="space-y-6">
            <div className="grid grid-cols-4 gap-4">
              <div className="p-4 bg-cyan-50 rounded-lg">
                <p className="text-sm text-gray-600">Total Citations</p>
                <p className="text-2xl font-bold text-cyan-600">47</p>
              </div>
              <div className="p-4 bg-blue-50 rounded-lg">
                <p className="text-sm text-gray-600">Self-Citations</p>
                <p className="text-2xl font-bold text-blue-600">12 (25.5%)</p>
              </div>
              <div className="p-4 bg-purple-50 rounded-lg">
                <p className="text-sm text-gray-600">Citation Rings</p>
                <p className="text-2xl font-bold text-purple-600">2</p>
              </div>
              <div className="p-4 bg-red-50 rounded-lg">
                <p className="text-sm text-gray-600">Predatory Journals</p>
                <p className="text-2xl font-bold text-red-600">3</p>
              </div>
            </div>

            {/* Network Visualization */}
            <div className="border rounded-lg p-6">
              <h3 className="font-semibold mb-4">Citation Network Graph</h3>
              <div className="aspect-video bg-gray-100 rounded flex items-center justify-center relative">
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="relative w-full h-full p-8">
                    {[
                      { x: 50, y: 50, label: 'This Paper', type: 'main' },
                      { x: 20, y: 30, label: 'Paper A', type: 'cite' },
                      { x: 80, y: 30, label: 'Paper B', type: 'cite' },
                      { x: 35, y: 70, label: 'Paper C', type: 'self' },
                      { x: 65, y: 70, label: 'Paper D', type: 'cite' },
                      { x: 50, y: 15, label: 'Paper E', type: 'ring' }
                    ].map((node, idx) => (
                      <div
                        key={idx}
                        className={`absolute w-12 h-12 rounded-full flex items-center justify-center text-xs font-semibold ${
                          node.type === 'main' ? 'bg-indigo-600 text-white ring-4 ring-indigo-200' :
                          node.type === 'self' ? 'bg-blue-500 text-white' :
                          node.type === 'ring' ? 'bg-purple-500 text-white' :
                          'bg-gray-400 text-white'
                        }`}
                        style={{ left: `${node.x}%`, top: `${node.y}%`, transform: 'translate(-50%, -50%)' }}
                      >
                        {idx + 1}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Issues */}
            <div className="border-t pt-4">
              <h3 className="font-semibold mb-3">Detected Issues</h3>
              <div className="space-y-2">
                <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <div className="flex items-start gap-2">
                    <AlertTriangle className="w-5 h-5 text-yellow-600 mt-0.5" />
                    <div>
                      <p className="font-medium text-yellow-900">High Self-Citation Rate</p>
                      <p className="text-sm text-yellow-700">25.5% of citations are self-citations (threshold: 20%)</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center py-12 text-gray-500">
            <Network className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p>Select a paper to view citation network analysis</p>
          </div>
        )}
      </div>
    </div>
  );
};

// AI Explainability Section
const ExplainabilitySection = ({ selectedPaper }) => {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
          <Brain className="w-6 h-6 text-indigo-600" />
          AI Explainability & Model Interpretability
        </h2>

        {selectedPaper ? (
          <div className="space-y-6">
            {/* LIME Explanation */}
            <div className="border rounded-lg p-4">
              <h3 className="font-semibold mb-3 flex items-center gap-2">
                <Target className="w-5 h-5 text-green-600" />
                LIME (Local Interpretable Model-Agnostic Explanations)
              </h3>
              <p className="text-sm text-gray-600 mb-4">
                Highlights which text segments most influenced the similarity detection
              </p>
              <div className="p-4 bg-gray-50 rounded font-mono text-sm space-y-2">
                <p>
                  The <span className="bg-red-200 px-1">experimental methodology employed in this study</span> was
                  designed to <span className="bg-yellow-200 px-1">minimize potential confounding variables</span> while
                  ensuring <span className="bg-red-200 px-1">robust statistical analysis</span> of the collected data.
                </p>
              </div>
            </div>

            {/* SHAP Values */}
            <div className="border rounded-lg p-4">
              <h3 className="font-semibold mb-3 flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-blue-600" />
                SHAP (SHapley Additive exPlanations)
              </h3>
              <p className="text-sm text-gray-600 mb-4">
                Shows the contribution of each feature to the final risk score
              </p>
              <div className="space-y-3">
                {[
                  { feature: 'Text Similarity Score', value: 0.35, impact: 'positive' },
                  { feature: 'Statistical Anomalies', value: 0.28, impact: 'positive' },
                  { feature: 'Citation Network Issues', value: 0.18, impact: 'positive' },
                  { feature: 'Image Manipulation', value: 0.12, impact: 'positive' },
                  { feature: 'Author Reputation', value: -0.08, impact: 'negative' },
                  { feature: 'Journal Impact Factor', value: -0.05, impact: 'negative' }
                ].map((item, idx) => (
                  <div key={idx} className="flex items-center gap-3">
                    <div className="w-48 text-sm text-gray-700">{item.feature}</div>
                    <div className="flex-1 h-6 bg-gray-200 rounded relative">
                      <div
                        className={`absolute h-full rounded ${item.impact === 'positive' ? 'bg-red-500' : 'bg-green-500'}`}
                        style={{
                          width: `${Math.abs(item.value) * 100}%`,
                          left: item.impact === 'negative' ? `${50 - Math.abs(item.value) * 50}%` : '50%'
                        }}
                      />
                      <div className="absolute left-1/2 top-0 bottom-0 w-0.5 bg-gray-400"></div>
                    </div>
                    <div className={`w-16 text-sm font-semibold text-right ${item.impact === 'positive' ? 'text-red-600' : 'text-green-600'}`}>
                      {item.value > 0 ? '+' : ''}{item.value.toFixed(2)}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center py-12 text-gray-500">
            <Brain className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p>Select a paper to view AI explainability analysis</p>
          </div>
        )}
      </div>
    </div>
  );
};

// Collaboration Section
const CollaborationSection = ({ selectedPaper }) => {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold flex items-center gap-2">
            <Users className="w-6 h-6 text-indigo-600" />
            Multi-Reviewer Collaboration
          </h2>
          <button className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">
            <UserPlus className="w-4 h-4" />
            Assign Reviewer
          </button>
        </div>

        {selectedPaper ? (
          <div className="space-y-6">
            {/* Review Status */}
            <div className="grid grid-cols-4 gap-4">
              <div className="p-4 bg-blue-50 rounded-lg">
                <p className="text-sm text-gray-600">Total Reviewers</p>
                <p className="text-2xl font-bold text-blue-600">3</p>
              </div>
              <div className="p-4 bg-green-50 rounded-lg">
                <p className="text-sm text-gray-600">Completed Reviews</p>
                <p className="text-2xl font-bold text-green-600">2</p>
              </div>
              <div className="p-4 bg-yellow-50 rounded-lg">
                <p className="text-sm text-gray-600">Pending</p>
                <p className="text-2xl font-bold text-yellow-600">1</p>
              </div>
              <div className="p-4 bg-purple-50 rounded-lg">
                <p className="text-sm text-gray-600">Consensus Score</p>
                <p className="text-2xl font-bold text-purple-600">85%</p>
              </div>
            </div>

            {/* Comments & Discussion */}
            <div className="border rounded-lg">
              <div className="bg-gray-50 px-4 py-3 border-b flex items-center justify-between">
                <h3 className="font-semibold flex items-center gap-2">
                  <MessageSquare className="w-5 h-5" />
                  Review Comments & Discussion
                </h3>
                <span className="text-sm text-gray-600">5 comments</span>
              </div>
              <div className="p-4 space-y-4 max-h-96 overflow-y-auto">
                {[
                  { author: 'Dr. Sarah Johnson', time: '2 hours ago', comment: 'The statistical anomalies in Table 3 are concerning.', type: 'critical' },
                  { author: 'Prof. Michael Chen', time: '1 hour ago', comment: 'I agree. Additionally, the image analysis shows manipulation in Figure 2A.', type: 'critical' }
                ].map((comment, idx) => (
                  <div key={idx} className="p-3 rounded-lg border bg-red-50 border-red-200">
                    <div className="flex items-start justify-between mb-2">
                      <span className="font-medium text-sm">{comment.author}</span>
                      <span className="text-xs text-gray-500">{comment.time}</span>
                    </div>
                    <p className="text-sm text-gray-700">{comment.comment}</p>
                  </div>
                ))}
              </div>
              <div className="p-4 border-t">
                <div className="flex gap-2">
                  <input
                    type="text"
                    placeholder="Add a comment..."
                    className="flex-1 px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                  <button className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center gap-2">
                    <Send className="w-4 h-4" />
                    Send
                  </button>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center py-12 text-gray-500">
            <Users className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p>Select a paper to view collaboration features</p>
          </div>
        )}
      </div>
    </div>
  );
};

// Batch Processing Section
const BatchProcessingSection = () => {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold flex items-center gap-2">
            <Layers className="w-6 h-6 text-indigo-600" />
            Batch Processing Management
          </h2>
          <button className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">
            <Play className="w-4 h-4" />
            New Batch Job
          </button>
        </div>

        <div className="space-y-6">
          <div className="grid grid-cols-4 gap-4">
            <div className="p-4 bg-blue-50 rounded-lg">
              <p className="text-sm text-gray-600">Active Jobs</p>
              <p className="text-2xl font-bold text-blue-600">2</p>
            </div>
            <div className="p-4 bg-green-50 rounded-lg">
              <p className="text-sm text-gray-600">Completed Today</p>
              <p className="text-2xl font-bold text-green-600">8</p>
            </div>
            <div className="p-4 bg-yellow-50 rounded-lg">
              <p className="text-sm text-gray-600">Queued</p>
              <p className="text-2xl font-bold text-yellow-600">5</p>
            </div>
            <div className="p-4 bg-purple-50 rounded-lg">
              <p className="text-sm text-gray-600">Papers Processed</p>
              <p className="text-2xl font-bold text-purple-600">127</p>
            </div>
          </div>

          {/* Job List */}
          <div className="border rounded-lg overflow-hidden">
            <div className="bg-gray-50 px-4 py-3 border-b">
              <h3 className="font-semibold">Recent Batch Jobs</h3>
            </div>
            <div className="divide-y">
              {[
                { id: 'batch-2024-001', name: 'CS Department Q4 Analysis', papers: 45, status: 'running', progress: 67 },
                { id: 'batch-2024-002', name: 'Journal Submission Review', papers: 23, status: 'running', progress: 34 },
                { id: 'batch-2024-003', name: 'Thesis Archive Scan', papers: 89, status: 'queued', progress: 0 }
              ].map((job, idx) => (
                <div key={idx} className="p-4 hover:bg-gray-50">
                  <div className="flex items-center justify-between mb-2">
                    <div>
                      <p className="font-medium">{job.name}</p>
                      <p className="text-sm text-gray-600">{job.id} • {job.papers} papers</p>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                      job.status === 'running' ? 'bg-blue-100 text-blue-700' : 'bg-yellow-100 text-yellow-700'
                    }`}>
                      {job.status === 'running' ? (
                        <span className="flex items-center gap-1">
                          <RefreshCw className="w-3 h-3 animate-spin" />
                          Running
                        </span>
                      ) : 'Queued'}
                    </span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="flex-1 bg-gray-200 rounded-full h-2">
                      <div className="bg-blue-500 h-2 rounded-full" style={{ width: `${job.progress}%` }} />
                    </div>
                    <span className="text-sm text-gray-600 w-12 text-right">{job.progress}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Scheduled Jobs */}
          <div className="border rounded-lg">
            <div className="bg-gray-50 px-4 py-3 border-b flex items-center justify-between">
              <h3 className="font-semibold flex items-center gap-2">
                <Calendar className="w-5 h-5" />
                Scheduled Jobs
              </h3>
            </div>
            <div className="divide-y">
              {[
                { name: 'Daily New Submissions Scan', frequency: 'Daily at 00:00', nextRun: '2024-11-17 00:00', enabled: true },
                { name: 'Weekly Department Review', frequency: 'Weekly (Monday)', nextRun: '2024-11-18 08:00', enabled: true }
              ].map((schedule, idx) => (
                <div key={idx} className="p-4 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Clock className="w-5 h-5 text-gray-400" />
                    <div>
                      <p className="font-medium">{schedule.name}</p>
                      <p className="text-sm text-gray-600">{schedule.frequency}</p>
                      <p className="text-xs text-gray-500 mt-1">Next run: {schedule.nextRun}</p>
                    </div>
                  </div>
                  <span className="px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-700">
                    Active
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AcademicIntegrityPlatform;
