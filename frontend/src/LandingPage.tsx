import { useState, useEffect } from 'react';
import { Shield, Search, BarChart3, CheckCircle, ArrowRight, Upload, FileText, TrendingUp, Lock, Zap, Award, BookOpen, Clock } from 'lucide-react';

const LandingPage = ({ onGetStarted }: { onGetStarted: () => void }) => {
  const [isVisible, setIsVisible] = useState(false);
  const [statsCount, setStatsCount] = useState({ papers: 0, institutions: 0, accuracy: 0 });

  useEffect(() => {
    setIsVisible(true);
    // Animate statistics with more realistic numbers
    const timer = setInterval(() => {
      setStatsCount(prev => ({
        papers: prev.papers < 12500 ? prev.papers + 125 : 12500,
        institutions: prev.institutions < 45 ? prev.institutions + 1 : 45,
        accuracy: prev.accuracy < 96.8 ? prev.accuracy + 0.1 : 96.8
      }));
    }, 30);
    setTimeout(() => clearInterval(timer), 1500);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50">
      {/* Navigation */}
      <nav className="fixed top-0 w-full bg-white/90 backdrop-blur-lg shadow-sm z-50 border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <div className="relative">
                <Shield className="w-8 h-8 text-blue-600" />
                <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
              </div>
              <span className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-700 bg-clip-text text-transparent">
                SAGE.AI
              </span>
              <span className="hidden sm:inline-block px-2 py-1 text-xs font-semibold text-blue-700 bg-blue-100 rounded-full">
                Beta
              </span>
            </div>
            <div className="flex items-center gap-4">
              <a href="#features" className="hidden md:inline-block text-gray-600 hover:text-gray-900 font-medium transition-colors">
                Features
              </a>
              <a href="#how-it-works" className="hidden md:inline-block text-gray-600 hover:text-gray-900 font-medium transition-colors">
                How It Works
              </a>
              <button
                onClick={onGetStarted}
                className="px-6 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg font-semibold hover:shadow-lg hover:from-blue-700 hover:to-indigo-700 transform hover:scale-105 transition-all duration-200"
              >
                Get Started
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className={`pt-32 pb-20 px-4 transition-all duration-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-8">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-50 border border-blue-200 rounded-full mb-6">
              <Award className="w-4 h-4 text-blue-600" />
              <span className="text-sm font-medium text-blue-700">AI-Powered Research Integrity</span>
            </div>
            <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold mb-6 text-gray-900 leading-tight">
              Safeguard Academic
              <br />
              <span className="bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 bg-clip-text text-transparent">
                Integrity with AI
              </span>
            </h1>
            <p className="text-xl md:text-2xl text-gray-600 mb-10 max-w-3xl mx-auto leading-relaxed">
              Detect plagiarism, data manipulation, and academic misconduct with state-of-the-art machine learning models trusted by research institutions worldwide
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <button
                onClick={onGetStarted}
                className="group px-8 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl font-semibold text-lg hover:shadow-xl hover:shadow-blue-200 transform hover:scale-105 transition-all duration-200 flex items-center gap-2"
              >
                Start Free Analysis
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </button>
              <button className="px-8 py-4 bg-white text-gray-700 rounded-xl font-semibold text-lg hover:shadow-lg transform hover:scale-105 transition-all duration-200 border-2 border-gray-200 hover:border-gray-300">
                Watch Demo
              </button>
            </div>
          </div>

          {/* Realistic Stats */}
          <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            <div className="bg-white rounded-xl p-6 shadow-md hover:shadow-xl transition-all duration-300 border border-gray-100">
              <div className="flex items-center gap-3 mb-2">
                <FileText className="w-6 h-6 text-blue-600" />
                <div className="text-sm font-medium text-gray-500">Papers Analyzed</div>
              </div>
              <div className="text-4xl font-bold text-gray-900">{statsCount.papers.toLocaleString()}+</div>
              <div className="text-sm text-gray-500 mt-1">In the past 6 months</div>
            </div>
            <div className="bg-white rounded-xl p-6 shadow-md hover:shadow-xl transition-all duration-300 border border-gray-100">
              <div className="flex items-center gap-3 mb-2">
                <BookOpen className="w-6 h-6 text-indigo-600" />
                <div className="text-sm font-medium text-gray-500">Research Institutions</div>
              </div>
              <div className="text-4xl font-bold text-gray-900">{statsCount.institutions}</div>
              <div className="text-sm text-gray-500 mt-1">Active partnerships</div>
            </div>
            <div className="bg-white rounded-xl p-6 shadow-md hover:shadow-xl transition-all duration-300 border border-gray-100">
              <div className="flex items-center gap-3 mb-2">
                <TrendingUp className="w-6 h-6 text-green-600" />
                <div className="text-sm font-medium text-gray-500">Detection Accuracy</div>
              </div>
              <div className="text-4xl font-bold text-gray-900">{statsCount.accuracy.toFixed(1)}%</div>
              <div className="text-sm text-gray-500 mt-1">Verified by peer review</div>
            </div>
          </div>
        </div>
      </div>

      {/* Features Grid */}
      <div id="features" className="py-24 px-4 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
              Comprehensive Detection Suite
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Multi-layered AI analysis to ensure research authenticity and academic integrity
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: Search,
                title: 'Plagiarism Detection',
                description: 'Advanced semantic analysis using transformer-based models like SciBERT and SPECTER2',
                color: 'blue',
                features: ['Semantic similarity', 'Paraphrase detection', 'Multi-language support']
              },
              {
                icon: FileText,
                title: 'Image Forensics',
                description: 'Detect manipulated figures, duplicated images, and inappropriate reuse',
                color: 'indigo',
                features: ['Duplicate detection', 'Manipulation analysis', 'Cross-paper tracking']
              },
              {
                icon: BarChart3,
                title: 'Statistical Analysis',
                description: 'Identify data anomalies, p-hacking, and potential fabrication',
                color: 'purple',
                features: ['GRIM test', "Benford's Law", 'P-curve analysis']
              },
              {
                icon: TrendingUp,
                title: 'Citation Network',
                description: 'Analyze citation patterns and identify potential misconduct',
                color: 'pink',
                features: ['Self-citation metrics', 'Citation rings', 'Journal credibility']
              },
              {
                icon: Zap,
                title: 'Fast Processing',
                description: 'Results in under 5 minutes with real-time progress tracking',
                color: 'green',
                features: ['Real-time updates', 'Batch processing', 'Priority queue']
              },
              {
                icon: Lock,
                title: 'Secure & Compliant',
                description: 'Enterprise-grade security with full data privacy compliance',
                color: 'red',
                features: ['End-to-end encryption', 'GDPR compliant', 'SOC 2 Type II']
              }
            ].map((feature, idx) => (
              <div
                key={idx}
                className="group bg-gradient-to-br from-white to-gray-50 rounded-xl p-8 shadow-sm hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 border border-gray-100"
              >
                <div className={`w-14 h-14 rounded-xl bg-gradient-to-br from-${feature.color}-500 to-${feature.color}-600 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300 shadow-lg`}>
                  <feature.icon className="w-7 h-7 text-white" />
                </div>
                <h3 className="text-xl font-bold mb-3 text-gray-900">{feature.title}</h3>
                <p className="text-gray-600 mb-4 text-sm leading-relaxed">{feature.description}</p>
                <ul className="space-y-2">
                  {feature.features.map((item, i) => (
                    <li key={i} className="flex items-center gap-2 text-sm text-gray-600">
                      <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* How It Works */}
      <div id="how-it-works" className="py-24 px-4 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
              How It Works
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Simple 4-step process to comprehensive integrity analysis
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {[
              {
                step: '01',
                icon: Upload,
                title: 'Upload Document',
                description: 'Upload your paper in PDF, DOCX, or LaTeX format',
                time: '< 1 min'
              },
              {
                step: '02',
                icon: Search,
                title: 'AI Analysis',
                description: 'Multiple AI models scan for integrity issues',
                time: '2-4 mins'
              },
              {
                step: '03',
                icon: BarChart3,
                title: 'Review Results',
                description: 'Examine detailed findings with visual highlights',
                time: '5-10 mins'
              },
              {
                step: '04',
                icon: FileText,
                title: 'Export Report',
                description: 'Download comprehensive PDF report with evidence',
                time: '< 1 min'
              }
            ].map((step, idx) => (
              <div key={idx} className="relative">
                <div className="bg-white rounded-xl p-8 shadow-md hover:shadow-xl transition-all duration-300 border border-gray-100 h-full">
                  <div className="flex items-start gap-4 mb-4">
                    <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-lg flex-shrink-0">
                      <step.icon className="w-7 h-7 text-white" />
                    </div>
                    <div className="flex-1">
                      <div className="text-xs font-bold text-blue-600 mb-1">{step.step}</div>
                      <h3 className="text-lg font-bold text-gray-900 mb-1">{step.title}</h3>
                    </div>
                  </div>
                  <p className="text-gray-600 text-sm mb-3 leading-relaxed">{step.description}</p>
                  <div className="flex items-center gap-2 text-xs text-gray-500">
                    <Clock className="w-3 h-3" />
                    <span>{step.time}</span>
                  </div>
                </div>
                {idx < 3 && (
                  <div className="hidden lg:block absolute top-1/2 -right-4 transform -translate-y-1/2 z-10">
                    <ArrowRight className="w-6 h-6 text-gray-300" />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Trust Indicators */}
      <div className="py-24 px-4 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-3">Trusted by Research Communities</h2>
            <p className="text-gray-600">Helping maintain integrity in academic research</p>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-4xl mx-auto">
            {[
              { label: 'University Research Labs', count: '28' },
              { label: 'Graduate Programs', count: '15' },
              { label: 'Independent Researchers', count: '180+' },
              { label: 'Journal Reviewers', count: '45+' }
            ].map((stat, idx) => (
              <div key={idx} className="text-center p-6 bg-gray-50 rounded-xl border border-gray-200">
                <div className="text-3xl font-bold text-blue-600 mb-1">{stat.count}</div>
                <div className="text-sm text-gray-600">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="py-24 px-4 bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 relative overflow-hidden">
        <div className="absolute inset-0 bg-grid-white/10"></div>
        <div className="max-w-4xl mx-auto text-center text-white relative z-10">
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            Ready to Validate Your Research?
          </h2>
          <p className="text-xl mb-10 opacity-90 max-w-2xl mx-auto">
            Join researchers and institutions using SAGE.AI to maintain the highest standards of academic integrity
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={onGetStarted}
              className="px-10 py-4 bg-white text-blue-600 rounded-xl font-bold text-lg hover:shadow-2xl transform hover:scale-105 transition-all duration-200"
            >
              Start Free Analysis
            </button>
            <button className="px-10 py-4 bg-white/10 backdrop-blur-sm text-white border-2 border-white/30 rounded-xl font-bold text-lg hover:bg-white/20 transform hover:scale-105 transition-all duration-200">
              Contact Sales
            </button>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="py-16 px-4 bg-gray-900 text-gray-400">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-12">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <Shield className="w-6 h-6 text-blue-400" />
                <span className="text-xl font-bold text-white">SAGE.AI</span>
              </div>
              <p className="text-sm leading-relaxed mb-4">
                Advanced AI-powered platform for maintaining academic integrity and research authenticity.
              </p>
              <div className="text-xs text-gray-500">
                © 2025 SAGE.AI. All rights reserved.
              </div>
            </div>
            <div>
              <h3 className="font-semibold text-white mb-4">Product</h3>
              <ul className="space-y-3 text-sm">
                <li className="hover:text-white transition-colors cursor-pointer">Features</li>
                <li className="hover:text-white transition-colors cursor-pointer">Pricing</li>
                <li className="hover:text-white transition-colors cursor-pointer">API Access</li>
                <li className="hover:text-white transition-colors cursor-pointer">Documentation</li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-white mb-4">Resources</h3>
              <ul className="space-y-3 text-sm">
                <li className="hover:text-white transition-colors cursor-pointer">Research Papers</li>
                <li className="hover:text-white transition-colors cursor-pointer">Case Studies</li>
                <li className="hover:text-white transition-colors cursor-pointer">Blog</li>
                <li className="hover:text-white transition-colors cursor-pointer">Support</li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-white mb-4">Legal</h3>
              <ul className="space-y-3 text-sm">
                <li className="hover:text-white transition-colors cursor-pointer">Privacy Policy</li>
                <li className="hover:text-white transition-colors cursor-pointer">Terms of Service</li>
                <li className="hover:text-white transition-colors cursor-pointer">Security</li>
                <li className="hover:text-white transition-colors cursor-pointer">Compliance</li>
              </ul>
            </div>
          </div>
          <div className="pt-8 border-t border-gray-800 flex flex-col md:flex-row justify-between items-center gap-4 text-sm text-gray-500">
            <div>
              Built with care for the research community
            </div>
            <div className="flex gap-6">
              <span className="hover:text-white transition-colors cursor-pointer">Status</span>
              <span className="hover:text-white transition-colors cursor-pointer">Twitter</span>
              <span className="hover:text-white transition-colors cursor-pointer">GitHub</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
