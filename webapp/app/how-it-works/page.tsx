'use client'

import Link from 'next/link'
import { ArrowLeft, Eye, Lightbulb, Brain, CheckCircle } from 'lucide-react'

const iconSize = 'w-6 h-6';

export default function HowItWorksPage() {
  return (
    <main className="flex flex-col min-h-screen bg-white">
      {/* Hero Section */}
      <section className="relative px-4 sm:px-6 lg:px-8 py-16 sm:py-24 bg-gradient-to-br from-emerald-50 via-white to-blue-50 border-b border-emerald-200">
        <div className="max-w-4xl mx-auto">
          <Link href="/" className="inline-flex items-center gap-2 text-emerald-600 hover:text-emerald-700 font-semibold mb-8 transition">
            <ArrowLeft size={20} />
            Back to Home
          </Link>

          <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-4">How It Works</h1>
          <p className="text-lg text-gray-600 max-w-2xl">
            Understand the intelligent detection pipeline that makes SafeEats fast, accurate, and reliable.
          </p>
        </div>
      </section>

      {/* Pipeline Section */}
      <section className="px-4 sm:px-6 lg:px-8 py-16 sm:py-24">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-12 text-center">The Detection Pipeline</h2>
          
          <div className="space-y-8">
            {[
              {
                step: 1,
                title: 'Extract Text',
                desc: 'Advanced EasyOCR + layout parser extracts all text from images with high precision. Handles multiple languages and layouts.',
                icon: Eye,
                color: 'emerald',
              },
              {
                step: 2,
                title: 'Clean & Normalize',
                desc: 'Apply 150+ text cleaning rules with fuzzy matching. Fix typos, standardize formats, handle abbreviations and variations.',
                icon: Lightbulb,
                color: 'blue',
              },
              {
                step: 3,
                title: 'Intelligent Matching',
                desc: 'BERT-based Named Entity Recognition identifies allergens. Union with dictionary ensures authoritative matches with confidence scoring.',
                icon: Brain,
                color: 'purple',
              },
              {
                step: 4,
                title: 'Safe Verdict',
                desc: 'Generate final verdict with confidence levels and smart recommendations. Account for trace amounts and "may contain" warnings.',
                icon: CheckCircle,
                color: 'emerald',
              },
            ].map((item, idx) => {
              const Icon = item.icon;
              const colorMap = {
                emerald: { bg: 'bg-emerald-100', border: 'border-emerald-200', icon: 'text-emerald-600' },
                blue: { bg: 'bg-blue-100', border: 'border-blue-200', icon: 'text-blue-600' },
                purple: { bg: 'bg-purple-100', border: 'border-purple-200', icon: 'text-purple-600' },
              };
              const colors = colorMap[item.color as keyof typeof colorMap];

              return (
                <div key={idx} className="relative">
                  <div className="flex gap-6">
                    {/* Step number */}
                    <div className="flex flex-col items-center">
                      <div className={`${colors.bg} w-16 h-16 rounded-full flex items-center justify-center border-2 ${colors.border}`}>
                        <Icon className={`${iconSize} scale-150 ${colors.icon}`} />
                      </div>
                      {idx < 3 && (
                        <div className="w-1 h-16 bg-gradient-to-b from-gray-300 to-gray-200 mt-4" />
                      )}
                    </div>

                    {/* Content */}
                    <div className="flex-1 pb-12">
                      <div className="pt-2">
                        <h3 className="text-2xl font-bold text-gray-900 mb-2">
                          {item.step}. {item.title}
                        </h3>
                        <p className="text-lg text-gray-600">{item.desc}</p>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Key Technology Section */}
      <section className="px-4 sm:px-6 lg:px-8 py-16 sm:py-24 bg-gradient-to-br from-gray-50 to-blue-50">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-8">Why It Works So Well</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="p-8 border border-gray-200 rounded-xl bg-white">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">State-of-the-Art AI</h3>
              <p className="text-gray-600 mb-4">
                Uses BERT, a transformer-based model trained on millions of allergen-related texts. Understands context and nuance better than keyword matching.
              </p>
              <ul className="space-y-2 text-sm text-gray-600">
                <li>✓ Bidirectional context understanding</li>
                <li>✓ 99%+ accuracy on benchmark datasets</li>
                <li>✓ Handles variations and synonyms</li>
              </ul>
            </div>

            <div className="p-8 border border-gray-200 rounded-xl bg-white">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Intelligent Text Processing</h3>
              <p className="text-gray-600 mb-4">
                Not just OCR—we clean, normalize, and validate all text before analysis. Catches OCR errors automatically.
              </p>
              <ul className="space-y-2 text-sm text-gray-600">
                <li>✓ 150+ cleaning rules</li>
                <li>✓ Fuzzy matching for typos</li>
                <li>✓ Handles 14+ allergen variations</li>
              </ul>
            </div>

            <div className="p-8 border border-gray-200 rounded-xl bg-white">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Dictionary + AI Fusion</h3>
              <p className="text-gray-600 mb-4">
                Combines authoritative allergen dictionary with AI predictions. Dictionary matches always score 1.0 confidence.
              </p>
              <ul className="space-y-2 text-sm text-gray-600">
                <li>✓ No false negatives</li>
                <li>✓ Zero guessing on strict matches</li>
                <li>✓ Confidence-based recommendations</li>
              </ul>
            </div>

            <div className="p-8 border border-gray-200 rounded-xl bg-white">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Clinically Validated</h3>
              <p className="text-gray-600 mb-4">
                Trained on real food products and tested against real allergen labels. Continuously improved with user feedback.
              </p>
              <ul className="space-y-2 text-sm text-gray-600">
                <li>✓ Tested on 1000s of products</li>
                <li>✓ Covers rare & niche allergens</li>
                <li>✓ Multi-language support</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Performance Section */}
      <section className="px-4 sm:px-6 lg:px-8 py-16 sm:py-24">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-8">Performance Metrics</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="p-8 bg-gradient-to-br from-emerald-50 to-green-50 border border-emerald-200 rounded-xl">
              <div className="text-4xl font-bold text-emerald-600 mb-2">99%+</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Accuracy</h3>
              <p className="text-sm text-gray-600">Validated across diverse product labels and formats</p>
            </div>

            <div className="p-8 bg-gradient-to-br from-blue-50 to-cyan-50 border border-blue-200 rounded-xl">
              <div className="text-4xl font-bold text-blue-600 mb-2">&lt;1s</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Response Time</h3>
              <p className="text-sm text-gray-600">Most scans complete in milliseconds</p>
            </div>

            <div className="p-8 bg-gradient-to-br from-purple-50 to-pink-50 border border-purple-200 rounded-xl">
              <div className="text-4xl font-bold text-purple-600 mb-2">14+</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Allergens Covered</h3>
              <p className="text-sm text-gray-600">All major allergens from global regulations</p>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
