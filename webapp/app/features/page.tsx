'use client'

import Link from 'next/link'
import { ArrowLeft, Upload, Camera, Type, Shield, Brain, Zap, CheckCircle } from 'lucide-react'

const iconSize = 'w-6 h-6';

export default function FeaturesPage() {
  return (
    <main className="flex flex-col min-h-screen bg-white">
      {/* Hero Section */}
      <section className="relative px-4 sm:px-6 lg:px-8 py-16 sm:py-24 bg-gradient-to-br from-emerald-50 via-white to-blue-50 border-b border-emerald-200">
        <div className="max-w-4xl mx-auto">
          <Link href="/" className="inline-flex items-center gap-2 text-emerald-600 hover:text-emerald-700 font-semibold mb-8 transition">
            <ArrowLeft size={20} />
            Back to Home
          </Link>

          <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-4">All Features</h1>
          <p className="text-lg text-gray-600 max-w-2xl">
            Discover the complete toolkit for safe allergen detection. Learn what each feature offers and how to get the most value.
          </p>
        </div>
      </section>

      {/* Scanning Methods Section */}
      <section className="px-4 sm:px-6 lg:px-8 py-16 sm:py-24">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-12">Scanning Methods</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Image Upload */}
            <div className="p-8 border-2 border-gray-200 rounded-xl hover:border-emerald-500 hover:shadow-lg transition-all">
              <div className="w-12 h-12 bg-emerald-100 rounded-lg flex items-center justify-center mb-4">
                <Upload className="text-emerald-600" size={24} />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Upload Image</h3>
              <p className="text-gray-600 mb-4">
                Upload product label photos or ingredient list images with high clarity.
              </p>
              <div className="space-y-2">
                <div>
                  <h4 className="font-semibold text-gray-900 mb-2">Benefits:</h4>
                  <ul className="text-sm text-gray-600 space-y-1">
                    <li>✓ Precise text extraction</li>
                    <li>✓ Works with any format (JPG, PNG, PDF)</li>
                    <li>✓ Auto-saved to history</li>
                  </ul>
                </div>
              </div>
            </div>

            {/* Camera */}
            <div className="p-8 border-2 border-gray-200 rounded-xl hover:border-blue-500 hover:shadow-lg transition-all">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <Camera className="text-blue-600" size={24} />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Take Photo</h3>
              <p className="text-gray-600 mb-4">
                Real-time scanning using your device's camera at stores or restaurants.
              </p>
              <div className="space-y-2">
                <div>
                  <h4 className="font-semibold text-gray-900 mb-2">Benefits:</h4>
                  <ul className="text-sm text-gray-600 space-y-1">
                    <li>✓ Instant results (&lt;1s)</li>
                    <li>✓ Perfect for quick checks</li>
                    <li>✓ No need to wait</li>
                  </ul>
                </div>
              </div>
            </div>

            {/* Text */}
            <div className="p-8 border-2 border-gray-200 rounded-xl hover:border-purple-500 hover:shadow-lg transition-all">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                <Type className="text-purple-600" size={24} />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Paste Text</h3>
              <p className="text-gray-600 mb-4">
                Copy and paste ingredients from websites, apps, or online sources.
              </p>
              <div className="space-y-2">
                <div>
                  <h4 className="font-semibold text-gray-900 mb-2">Benefits:</h4>
                  <ul className="text-sm text-gray-600 space-y-1">
                    <li>✓ Quick manual entry</li>
                    <li>✓ Works with any text</li>
                    <li>✓ No photo needed</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Tech Features Section */}
      <section className="px-4 sm:px-6 lg:px-8 py-16 sm:py-24 bg-gradient-to-br from-gray-50 to-blue-50">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-12">Technology & Capabilities</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {[
              {
                icon: Brain,
                title: 'BERT NER Engine',
                desc: 'Advanced Named Entity Recognition using bidirectional transformers for precise allergen identification.',
                color: 'emerald',
              },
              {
                icon: Zap,
                title: '150+ Text Cleaning Rules',
                desc: 'Intelligent OCR text normalization with typo correction and fuzzy matching.',
                color: 'blue',
              },
              {
                icon: Shield,
                title: '14+ Allergen Coverage',
                desc: 'Detects all major allergens: nuts, dairy, shellfish, gluten, sesame, soy, fish, eggs, and more.',
                color: 'purple',
              },
              {
                icon: CheckCircle,
                title: 'Confidence Scoring',
                desc: 'Every detection comes with confidence levels to help you make informed decisions.',
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
                    <Icon className={`${iconSize} ${colors.icon}`} />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">{feature.title}</h3>
                  <p className="text-gray-600">{feature.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Privacy Section */}
      <section className="px-4 sm:px-6 lg:px-8 py-16 sm:py-24">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-8">Privacy & Security</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="p-8 border border-gray-200 rounded-xl">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Your Data is Yours</h3>
              <ul className="space-y-2 text-gray-600">
                <li className="flex gap-2">
                  <span className="text-emerald-600 font-bold">✓</span> End-to-end encrypted scans
                </li>
                <li className="flex gap-2">
                  <span className="text-emerald-600 font-bold">✓</span> No selling to third parties
                </li>
                <li className="flex gap-2">
                  <span className="text-emerald-600 font-bold">✓</span> GDPR compliant
                </li>
              </ul>
            </div>

            <div className="p-8 border border-gray-200 rounded-xl">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Secure Processing</h3>
              <ul className="space-y-2 text-gray-600">
                <li className="flex gap-2">
                  <span className="text-emerald-600 font-bold">✓</span> Processed on secure servers
                </li>
                <li className="flex gap-2">
                  <span className="text-emerald-600 font-bold">✓</span> Delete scans anytime
                </li>
                <li className="flex gap-2">
                  <span className="text-emerald-600 font-bold">✓</span> No tracking or analytics
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
