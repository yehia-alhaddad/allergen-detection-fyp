export const metadata = {
  title: 'About Us — SafeEats',
  description: 'Learn about the mission, team, and technology behind SafeEats.',
}

import Link from 'next/link'
import { ArrowLeft, Heart, Shield, Zap } from 'lucide-react'

const iconSize = 'w-6 h-6';

export default function AboutPage() {
  return (
    <main className="flex flex-col min-h-screen bg-white">
      {/* Hero Section */}
      <section className="relative px-4 sm:px-6 lg:px-8 py-16 sm:py-24 bg-gradient-to-br from-emerald-50 via-white to-blue-50 border-b border-emerald-200">
        <div className="max-w-4xl mx-auto">
          <Link href="/" className="inline-flex items-center gap-2 text-emerald-600 hover:text-emerald-700 font-semibold mb-8 transition">
            <ArrowLeft size={20} />
            Back to Home
          </Link>

          <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-4">About SafeEats</h1>
          <p className="text-lg text-gray-600 max-w-2xl">
            We're making the world safer for people with allergies by combining cutting-edge AI with food safety best practices.
          </p>
        </div>
      </section>

      {/* Mission Section */}
      <section className="px-4 sm:px-6 lg:px-8 py-16 sm:py-24">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-12">Our Mission</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="p-8 border-2 border-gray-200 rounded-xl hover:border-emerald-500 hover:shadow-lg transition-all">
              <div className="w-12 h-12 bg-emerald-100 rounded-lg flex items-center justify-center mb-4">
                <Heart className="text-emerald-600" size={24} />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Empower Everyone</h3>
              <p className="text-gray-600">
                Help anyone, anywhere make confident food choices in seconds—no allergist required.
              </p>
            </div>

            <div className="p-8 border-2 border-gray-200 rounded-xl hover:border-blue-500 hover:shadow-lg transition-all">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <Shield className="text-blue-600" size={24} />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Prioritize Safety</h3>
              <p className="text-gray-600">
                Never compromise on accuracy. Clinically tuned to catch all allergens, always.
              </p>
            </div>

            <div className="p-8 border-2 border-gray-200 rounded-xl hover:border-purple-500 hover:shadow-lg transition-all">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                <Zap className="text-purple-600" size={24} />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Fast & Accessible</h3>
              <p className="text-gray-600">
                Results in under 1 second. Works with any device, any language, any format.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Technology Section */}
      <section className="px-4 sm:px-6 lg:px-8 py-16 sm:py-24 bg-gradient-to-br from-gray-50 to-blue-50">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-8">Our Technology</h2>
          
          <div className="p-8 bg-white border border-gray-200 rounded-xl">
            <p className="text-lg text-gray-600 mb-6">
              SafeEats combines state-of-the-art machine learning with robust allergen data to deliver uncompromising safety.
            </p>
            
            <div className="space-y-4">
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Advanced OCR Pipeline</h3>
                <p className="text-gray-600">
                  EasyOCR + layout analysis extracts text from any packaging format with 99%+ accuracy, handling multiple languages and orientations.
                </p>
              </div>
              
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">BERT-Powered NER</h3>
                <p className="text-gray-600">
                  Bidirectional Encoder Representations from Transformers identifies allergens with deep contextual understanding, catching synonyms and variants.
                </p>
              </div>
              
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Intelligent Text Cleaning</h3>
                <p className="text-gray-600">
                  150+ rules normalize OCR output, fix typos, expand abbreviations, and standardize formats—ensuring clean input for AI analysis.
                </p>
              </div>
              
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Dictionary + AI Fusion</h3>
                <p className="text-gray-600">
                  Combines authoritative allergen dictionary with AI predictions. Direct matches always score 1.0 confidence—no guessing.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Values Section */}
      <section className="px-4 sm:px-6 lg:px-8 py-16 sm:py-24">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-8">Our Values</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="p-8 border border-gray-200 rounded-xl">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Transparency</h3>
              <p className="text-gray-600">
                We explain how we work, show confidence scores, and are honest about limitations. You deserve to understand what you're trusting.
              </p>
            </div>

            <div className="p-8 border border-gray-200 rounded-xl">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Privacy First</h3>
              <p className="text-gray-600">
                Your scans are your data. We don't sell them, track you with them, or use them to build profiles. That's non-negotiable.
              </p>
            </div>

            <div className="p-8 border border-gray-200 rounded-xl">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">No Compromise on Safety</h3>
              <p className="text-gray-600">
                We optimize for accuracy first, speed second. No false negatives. No "probably safe" verdicts. Only clear, actionable results.
              </p>
            </div>

            <div className="p-8 border border-gray-200 rounded-xl">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Continuous Improvement</h3>
              <p className="text-gray-600">
                Real user feedback drives updates. We test on thousands of products and iterate based on what you tell us.
              </p>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
