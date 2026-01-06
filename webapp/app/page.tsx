'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { CheckCircle, AlertCircle, Clock, Shield, Zap, BarChart3 } from 'lucide-react';

const iconClass = 'w-6 h-6';

export default function Home() {
  const [user, setUser] = useState<any>(null);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const res = await fetch('/api/auth/session', { cache: 'no-store', credentials: 'include' });
        if (res.ok) {
          const session = await res.json();
          setUser(session.user);
        } else {
          setUser(null);
        }
      } catch (err) {
        setUser(null);
      } finally {
        setChecking(false);
      }
    };

    checkAuth();
  }, []);

  const isLoggedIn = !checking && !!user;

  return (
    <main className="flex flex-col min-h-screen bg-white">
      {/* Hero Section */}
      <section className="relative px-4 sm:px-6 lg:px-8 py-20 sm:py-32 bg-gradient-to-br from-emerald-50 via-white to-blue-50 overflow-hidden border-b border-emerald-200">
        <div className="absolute inset-0 opacity-5" style={{backgroundImage: 'url("data:image/svg+xml,%3Csvg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg"%3E%3Cg fill="none" fill-rule="evenodd"%3E%3Cg fill="%23000000" fill-opacity="0.1"%3E%3Cpath d="M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z"/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")'}} />
        <div className="max-w-4xl mx-auto relative z-10">
          <div className="flex items-center justify-center gap-2 mb-6">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-100 rounded-full shadow-sm">
              <CheckCircle className="w-4 h-4 text-emerald-600" />
              <span className="text-sm font-semibold text-emerald-900">Food-Safety Tuned & Secure by Design</span>
            </div>
          </div>
          
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight text-gray-900 mb-6 text-center leading-tight">
            Smart Allergen Detection<br />for <span className="bg-gradient-to-r from-emerald-600 to-green-600 bg-clip-text text-transparent">Safe Eating</span>
          </h1>
          
          <p className="text-lg sm:text-xl text-gray-600 text-center mb-8 max-w-2xl mx-auto leading-relaxed">
            Instantly scan food packages, take photos, or paste ingredients. Our AI-powered system detects 14+ allergens with 99%+ accuracy using advanced NER and OCR technology.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
            <Link href="/dashboard">
              <button className="px-8 py-4 bg-gradient-to-r from-emerald-600 to-green-600 text-white rounded-lg font-semibold hover:shadow-lg transition-all">
                Start Scanning →
              </button>
            </Link>
            {!isLoggedIn && (
              <Link href="/signup">
                <button className="px-8 py-4 border-2 border-emerald-600 text-emerald-600 rounded-lg font-semibold hover:bg-emerald-50 transition-all">
                  Create Account
                </button>
              </Link>
            )}
          </div>

          <div className="grid grid-cols-3 gap-4 max-w-2xl mx-auto">
            <div className="text-center p-4 bg-white rounded-lg shadow-sm border border-emerald-100">
              <div className="text-3xl font-bold text-emerald-600 mb-1">99%+</div>
              <div className="text-sm text-gray-600 font-medium">Accuracy</div>
            </div>
            <div className="text-center p-4 bg-white rounded-lg shadow-sm border border-blue-100">
              <div className="text-3xl font-bold text-blue-600 mb-1">&lt;1s</div>
              <div className="text-sm text-gray-600 font-medium">Response Time</div>
            </div>
            <div className="text-center p-4 bg-white rounded-lg shadow-sm border border-purple-100">
              <div className="text-3xl font-bold text-purple-600 mb-1">3</div>
              <div className="text-sm text-gray-600 font-medium">Input Methods</div>
            </div>
          </div>
        </div>
      </section>

      {/* Three Input Methods */}
      <section className="px-4 sm:px-6 lg:px-8 py-16 sm:py-24">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">Multiple Ways to Scan</h2>
            <p className="text-lg text-gray-600">Choose the method that works best for you</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Upload */}
            <div className="p-8 border-2 border-gray-200 rounded-xl hover:border-emerald-500 hover:shadow-lg transition-all">
              <div className="w-12 h-12 bg-emerald-100 rounded-lg flex items-center justify-center mb-4">
                <AlertCircle className={`${iconClass} text-emerald-600`} />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Upload Image</h3>
              <ul className="space-y-2 text-gray-600">
                <li className="flex gap-2">
                  <span className="text-emerald-600 font-bold">✓</span> Scan package labels
                </li>
                <li className="flex gap-2">
                  <span className="text-emerald-600 font-bold">✓</span> Clear ingredient lists
                </li>
                <li className="flex gap-2">
                  <span className="text-emerald-600 font-bold">✓</span> PDF documents
                </li>
              </ul>
            </div>

            {/* Camera */}
            <div className="p-8 border-2 border-gray-200 rounded-xl hover:border-blue-500 hover:shadow-lg transition-all">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <Zap className={`${iconClass} text-blue-600`} />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Take Photo</h3>
              <ul className="space-y-2 text-gray-600">
                <li className="flex gap-2">
                  <span className="text-blue-600 font-bold">✓</span> Real-time scanning
                </li>
                <li className="flex gap-2">
                  <span className="text-blue-600 font-bold">✓</span> At grocery stores
                </li>
                <li className="flex gap-2">
                  <span className="text-blue-600 font-bold">✓</span> Restaurant menus
                </li>
              </ul>
            </div>

            {/* Paste Text */}
            <div className="p-8 border-2 border-gray-200 rounded-xl hover:border-purple-500 hover:shadow-lg transition-all">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                <BarChart3 className={`${iconClass} text-purple-600`} />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Paste Text</h3>
              <ul className="space-y-2 text-gray-600">
                <li className="flex gap-2">
                  <span className="text-purple-600 font-bold">✓</span> Manual ingredient lists
                </li>
                <li className="flex gap-2">
                  <span className="text-purple-600 font-bold">✓</span> From websites/apps
                </li>
                <li className="flex gap-2">
                  <span className="text-purple-600 font-bold">✓</span> Quick reference
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="px-4 sm:px-6 lg:px-8 py-16 sm:py-24 bg-gradient-to-br from-gray-50 to-blue-50">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">Intelligent Detection Pipeline</h2>
            <p className="text-lg text-gray-600">From image to verified allergen list in seconds</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {[
              { step: 1, title: 'Extract Text', desc: 'Advanced OCR + layout analysis' },
              { step: 2, title: 'Clean & Normalize', desc: 'Fix typos, standardize format (150+ rules)' },
              { step: 3, title: 'Intelligent Matching', desc: 'BERT NER + dictionary union' },
              { step: 4, title: 'Safe Verdict', desc: 'Confidence scoring & recommendations' },
            ].map((item, idx) => (
              <div key={idx} className="relative">
                <div className="bg-white p-6 rounded-lg border-2 border-emerald-200 h-full">
                  <div className="text-3xl font-bold text-emerald-600 mb-2">{item.step}</div>
                  <h4 className="font-semibold text-gray-900 mb-2">{item.title}</h4>
                  <p className="text-sm text-gray-600">{item.desc}</p>
                </div>
                {idx < 3 && (
                  <div className="hidden md:block absolute top-1/2 -right-2 transform -translate-y-1/2 text-emerald-400 text-2xl">→</div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Key Features */}
      <section className="px-4 sm:px-6 lg:px-8 py-16 sm:py-24">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">Why SafeEats?</h2>
            <p className="text-lg text-gray-600">Built with food safety professionals and users with allergies</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {[
              {
                icon: CheckCircle,
                title: 'Comprehensive Coverage',
                desc: 'Detects 14+ common allergens (nuts, dairy, shellfish, gluten, sesame, soy, fish, eggs, celery, mustard, lupin, sulfites, mollusks, peanuts) with smart recommendations for trace amounts.',
                color: 'emerald',
              },
              {
                icon: Shield,
                title: 'Privacy & Security',
                desc: 'Your scans are encrypted and stored securely. No food preferences sold to third parties. Fully compliant with data protection regulations.',
                color: 'blue',
              },
              {
                icon: Clock,
                title: 'Instant Scanning',
                desc: 'Get results in under 1 second. Perfect for quick decisions at grocery stores, restaurants, or while cooking at home.',
                color: 'purple',
              },
              {
                icon: Zap,
                title: 'Smart Recommendations',
                desc: 'Beyond detection—get actionable suggestions, alternatives, and confidence levels for every allergen. Learn as you scan.',
                color: 'orange',
              },
            ].map((feature, idx) => {
              const Icon = feature.icon;
              const colorMap = {
                emerald: { bg: 'bg-emerald-100', icon: 'text-emerald-600' },
                blue: { bg: 'bg-blue-100', icon: 'text-blue-600' },
                purple: { bg: 'bg-purple-100', icon: 'text-purple-600' },
                orange: { bg: 'bg-orange-100', icon: 'text-orange-600' },
              };
              const colors = colorMap[feature.color as keyof typeof colorMap];

              return (
                <div key={idx} className="p-8 border border-gray-200 rounded-xl hover:shadow-lg transition-all">
                  <div className={`${colors.bg} w-12 h-12 rounded-lg flex items-center justify-center mb-4`}>
                    <Icon className={`${iconClass} ${colors.icon}`} />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-3">{feature.title}</h3>
                  <p className="text-gray-600">{feature.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="px-4 sm:px-6 lg:px-8 py-16 sm:py-24 bg-gradient-to-r from-emerald-600 to-green-600">
        <div className="max-w-2xl mx-auto text-center">
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-6">Ready to Eat Safely?</h2>
          <p className="text-lg text-emerald-100 mb-8">Join thousands who trust SafeEats for allergen detection. No credit card required.</p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/dashboard">
              <button className="px-8 py-4 bg-white text-emerald-600 rounded-lg font-semibold hover:bg-gray-100 transition-all">
                Start Scanning Now
              </button>
            </Link>
            {!isLoggedIn && (
              <Link href="/signup">
                <button className="px-8 py-4 border-2 border-white text-white rounded-lg font-semibold hover:bg-emerald-700 transition-all">
                  Create Free Account
                </button>
              </Link>
            )}
          </div>
        </div>
      </section>
    </main>
  );
}
