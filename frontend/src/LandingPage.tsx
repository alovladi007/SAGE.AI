import React, { useState, useEffect } from 'react';
import { Shield, Search, BarChart3, Users, CheckCircle, ArrowRight, Upload, FileText, TrendingUp, Lock, Zap, Globe } from 'lucide-react';

const LandingPage = ({ onGetStarted }: { onGetStarted: () => void }) => {
  const [isVisible, setIsVisible] = useState(false);
  const [statsCount, setStatsCount] = useState({ papers: 0, users: 0, accuracy: 0 });

  useEffect(() => {
    setIsVisible(true);
    // Animate statistics
    const timer = setInterval(() => {
      setStatsCount(prev => ({
        papers: prev.papers < 1000000 ? prev.papers + 10000 : 1000000,
        users: prev.users < 50000 ? prev.users + 500 : 50000,
        accuracy: prev.accuracy < 99.9 ? prev.accuracy + 0.1 : 99.9
      }));
    }, 50);
    setTimeout(() => clearInterval(timer), 2000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Navigation */}
      <nav className="fixed top-0 w-full bg-white/80 backdrop-blur-md shadow-sm z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <Shield className="w-8 h-8 text-blue-600" />
              <span className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                SAGE.AI
              </span>
            </div>
            <button
              onClick={onGetStarted}
              className="px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-full font-semibold hover:shadow-lg transform hover:scale-105 transition-all duration-200"
            >
              Get Started
            </button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className={`pt-32 pb-20 px-4 transition-all duration-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-6xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent animate-pulse">
            Academic Integrity
            <br />
            Powered by AI
          </h1>
          <p className="text-xl md:text-2xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Detect plagiarism, data fabrication, and academic misconduct with cutting-edge machine learning technology
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <button
              onClick={onGetStarted}
              className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-full font-bold text-lg hover:shadow-2xl transform hover:scale-105 transition-all duration-200 flex items-center gap-2"
            >
              Start Analyzing <ArrowRight className="w-5 h-5" />
            </button>
            <button className="px-8 py-4 bg-white text-gray-700 rounded-full font-bold text-lg hover:shadow-lg transform hover:scale-105 transition-all duration-200 border-2 border-gray-200">
              View Demo
            </button>
          </div>

          {/* Animated Stats */}
          <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            <div className="bg-white rounded-2xl p-6 shadow-lg hover:shadow-2xl transition-shadow duration-300">
              <div className="text-4xl font-bold text-blue-600">{statsCount.papers.toLocaleString()}+</div>
              <div className="text-gray-600 mt-2">Papers Analyzed</div>
            </div>
            <div className="bg-white rounded-2xl p-6 shadow-lg hover:shadow-2xl transition-shadow duration-300">
              <div className="text-4xl font-bold text-purple-600">{statsCount.users.toLocaleString()}+</div>
              <div className="text-gray-600 mt-2">Active Users</div>
            </div>
            <div className="bg-white rounded-2xl p-6 shadow-lg hover:shadow-2xl transition-shadow duration-300">
              <div className="text-4xl font-bold text-pink-600">{statsCount.accuracy.toFixed(1)}%</div>
              <div className="text-gray-600 mt-2">Accuracy Rate</div>
            </div>
          </div>
        </div>
      </div>

      {/* Features Grid */}
      <div className="py-20 px-4 bg-white">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-4xl md:text-5xl font-bold text-center mb-4">
            Comprehensive Detection Suite
          </h2>
          <p className="text-xl text-gray-600 text-center mb-12">
            Advanced AI-powered tools for maintaining academic integrity
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: Search,
                title: 'Plagiarism Detection',
                description: 'Advanced semantic similarity analysis using transformer models',
                color: 'blue',
                features: ['Text similarity', 'Paraphrase detection', 'Cross-language support']
              },
              {
                icon: FileText,
                title: 'Image Analysis',
                description: 'Detect manipulated figures and duplicate images',
                color: 'purple',
                features: ['Duplicate detection', 'Manipulation analysis', 'Figure reuse tracking']
              },
              {
                icon: BarChart3,
                title: 'Statistical Anomalies',
                description: 'Identify p-hacking and data fabrication',
                color: 'pink',
                features: ['GRIM test', "Benford's Law", 'P-value validation']
              },
              {
                icon: TrendingUp,
                title: 'Citation Analysis',
                description: 'Track citation patterns and self-citation',
                color: 'indigo',
                features: ['Network analysis', 'Self-citation detection', 'Predatory journals']
              },
              {
                icon: Zap,
                title: 'Real-time Processing',
                description: 'Get results in minutes, not hours',
                color: 'green',
                features: ['Instant analysis', 'Live updates', 'Batch processing']
              },
              {
                icon: Lock,
                title: 'Enterprise Security',
                description: 'Bank-level encryption and compliance',
                color: 'red',
                features: ['GDPR compliant', 'SOC 2 certified', 'Data encryption']
              }
            ].map((feature, idx) => (
              <div
                key={idx}
                className="group bg-gradient-to-br from-white to-gray-50 rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-2 border border-gray-100"
              >
                <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br from-${feature.color}-500 to-${feature.color}-600 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300`}>
                  <feature.icon className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-2xl font-bold mb-3 text-gray-800">{feature.title}</h3>
                <p className="text-gray-600 mb-4">{feature.description}</p>
                <ul className="space-y-2">
                  {feature.features.map((item, i) => (
                    <li key={i} className="flex items-center gap-2 text-sm text-gray-600">
                      <CheckCircle className="w-4 h-4 text-green-500" />
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* How It Works */}
      <div className="py-20 px-4 bg-gradient-to-br from-blue-50 to-purple-50">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-4xl md:text-5xl font-bold text-center mb-16">
            How It Works
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            {[
              { step: '1', icon: Upload, title: 'Upload', description: 'Upload your academic paper or thesis' },
              { step: '2', icon: Search, title: 'Analyze', description: 'AI scans for plagiarism and anomalies' },
              { step: '3', icon: BarChart3, title: 'Review', description: 'Get comprehensive analysis results' },
              { step: '4', icon: FileText, title: 'Report', description: 'Download detailed integrity report' }
            ].map((step, idx) => (
              <div key={idx} className="text-center">
                <div className="relative">
                  <div className="w-20 h-20 mx-auto rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center mb-4 shadow-lg">
                    <step.icon className="w-10 h-10 text-white" />
                  </div>
                  <div className="absolute -top-2 -right-2 w-8 h-8 bg-white rounded-full flex items-center justify-center font-bold text-blue-600 shadow-md">
                    {step.step}
                  </div>
                </div>
                <h3 className="text-xl font-bold mb-2">{step.title}</h3>
                <p className="text-gray-600">{step.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Social Proof */}
      <div className="py-20 px-4 bg-white">
        <div className="max-w-7xl mx-auto text-center">
          <h2 className="text-4xl font-bold mb-12">Trusted by Leading Institutions</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 items-center opacity-50">
            {['Harvard', 'MIT', 'Stanford', 'Oxford', 'Cambridge', 'Yale', 'Princeton', 'Berkeley'].map((uni, idx) => (
              <div key={idx} className="text-2xl font-bold text-gray-400 hover:text-gray-600 transition-colors">
                {uni}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="py-20 px-4 bg-gradient-to-r from-blue-600 to-purple-600">
        <div className="max-w-4xl mx-auto text-center text-white">
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            Ready to Ensure Academic Integrity?
          </h2>
          <p className="text-xl mb-8 opacity-90">
            Join thousands of institutions using SAGE.AI to maintain the highest standards
          </p>
          <button
            onClick={onGetStarted}
            className="px-12 py-4 bg-white text-blue-600 rounded-full font-bold text-lg hover:shadow-2xl transform hover:scale-105 transition-all duration-200"
          >
            Get Started Now
          </button>
        </div>
      </div>

      {/* Footer */}
      <footer className="py-12 px-4 bg-gray-900 text-gray-400">
        <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Shield className="w-6 h-6 text-blue-400" />
              <span className="text-xl font-bold text-white">SAGE.AI</span>
            </div>
            <p className="text-sm">
              Advanced AI-powered academic integrity platform
            </p>
          </div>
          <div>
            <h3 className="font-bold text-white mb-4">Product</h3>
            <ul className="space-y-2 text-sm">
              <li>Features</li>
              <li>Pricing</li>
              <li>API</li>
              <li>Documentation</li>
            </ul>
          </div>
          <div>
            <h3 className="font-bold text-white mb-4">Company</h3>
            <ul className="space-y-2 text-sm">
              <li>About</li>
              <li>Blog</li>
              <li>Careers</li>
              <li>Contact</li>
            </ul>
          </div>
          <div>
            <h3 className="font-bold text-white mb-4">Legal</h3>
            <ul className="space-y-2 text-sm">
              <li>Privacy</li>
              <li>Terms</li>
              <li>Security</li>
              <li>Compliance</li>
            </ul>
          </div>
        </div>
        <div className="max-w-7xl mx-auto mt-8 pt-8 border-t border-gray-800 text-center text-sm">
          © 2025 SAGE.AI. All rights reserved.
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
