import Link from 'next/link'
import { Zap, Camera, BarChart3, Shield, Eye, Database } from 'lucide-react'

export default function HomePage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 py-20 text-center">
        <div className="mb-8 inline-block">
          <div className="bg-blue-100 text-blue-700 px-4 py-2 rounded-full text-sm font-semibold">
            🛡️ Smart Allergen Detection
          </div>
        </div>
        
        <h1 className="text-5xl md:text-6xl font-bold text-zinc-900 mb-6 leading-tight">
          Eat with <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">Confidence</span>
        </h1>
        
        <p className="text-xl text-zinc-600 mb-10 max-w-2xl mx-auto leading-relaxed">
          Instantly detect allergens in any product. Upload photos, scan barcodes, paste ingredients—
          <strong> your personalized safety companion</strong> works in seconds.
        </p>
        
        <div className="flex flex-col sm:flex-row justify-center gap-4 mb-16">
          <Link 
            href="/dashboard" 
            className="px-8 py-4 rounded-lg bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold hover:shadow-lg hover:scale-105 transition-all duration-200 flex items-center justify-center gap-2"
          >
            <Zap size={20} />
            Start Scanning Now
          </Link>
          <Link 
            href="/privacy" 
            className="px-8 py-4 rounded-lg border-2 border-zinc-300 text-zinc-700 font-semibold hover:bg-zinc-100 transition-all duration-200"
          >
            Learn More
          </Link>
        </div>

        {/* Trust Badges */}
        <div className="flex flex-wrap justify-center gap-8 text-sm text-zinc-600 mb-12">
          <div className="flex items-center gap-2">
            <Shield size={18} className="text-green-600" />
            <span>100% Secure</span>
          </div>
          <div className="flex items-center gap-2">
            <Eye size={18} className="text-blue-600" />
            <span>No Data Sold</span>
          </div>
          <div className="flex items-center gap-2">
            <Zap size={18} className="text-yellow-600" />
            <span>Instant Results</span>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="max-w-7xl mx-auto px-4 py-16">
        <h2 className="text-3xl font-bold text-center mb-12 text-zinc-900">
          How It Works
        </h2>
        
        <div className="grid md:grid-cols-3 gap-8 mb-20">
          {/* Feature 1 */}
          <div className="group bg-white rounded-2xl p-8 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-300">
            <div className="bg-gradient-to-br from-blue-100 to-blue-200 w-14 h-14 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
              <Camera className="text-blue-600" size={28} />
            </div>
            <h3 className="text-xl font-bold text-zinc-900 mb-3">Scan Instantly</h3>
            <p className="text-zinc-600 leading-relaxed mb-4">
              Upload a photo, scan a barcode, or type ingredients. Our AI instantly analyzes for allergens.
            </p>
            <div className="text-sm text-blue-600 font-semibold">Works with 4 methods →</div>
          </div>

          {/* Feature 2 */}
          <div className="group bg-white rounded-2xl p-8 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-300">
            <div className="bg-gradient-to-br from-purple-100 to-purple-200 w-14 h-14 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
              <BarChart3 className="text-purple-600" size={28} />
            </div>
            <h3 className="text-xl font-bold text-zinc-900 mb-3">Smart Matching</h3>
            <p className="text-zinc-600 leading-relaxed mb-4">
              We match against your personal allergen list with 99%+ accuracy. Handles synonyms & variations.
            </p>
            <div className="text-sm text-purple-600 font-semibold">Personalized for you →</div>
          </div>

          {/* Feature 3 */}
          <div className="group bg-white rounded-2xl p-8 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-300">
            <div className="bg-gradient-to-br from-pink-100 to-pink-200 w-14 h-14 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
              <Database className="text-pink-600" size={28} />
            </div>
            <h3 className="text-xl font-bold text-zinc-900 mb-3">Your History</h3>
            <p className="text-zinc-600 leading-relaxed mb-4">
              Track all scans, compare products, and see your allergen exposure trends over time.
            </p>
            <div className="text-sm text-pink-600 font-semibold">Full control & privacy →</div>
          </div>
        </div>

        {/* Methods Showcase */}
        <div className="bg-white rounded-2xl p-12 shadow-md border border-zinc-100">
          <h3 className="text-2xl font-bold text-zinc-900 mb-8 text-center">
            Choose Your Scanning Method
          </h3>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { icon: '📸', label: 'Image Upload', desc: 'Upload label photo' },
              { icon: '📹', label: 'Camera Capture', desc: 'Take live photo' },
              { icon: '📦', label: 'Barcode Scan', desc: 'Scan UPC/EAN' },
              { icon: '✍️', label: 'Text Input', desc: 'Paste ingredients' }
            ].map((method, i) => (
              <div key={i} className="flex flex-col items-center text-center p-6 rounded-xl bg-gradient-to-br from-zinc-50 to-zinc-100 hover:from-blue-50 hover:to-purple-50 transition-colors">
                <span className="text-4xl mb-3">{method.icon}</span>
                <h4 className="font-semibold text-zinc-900 mb-1">{method.label}</h4>
                <p className="text-sm text-zinc-600">{method.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Social Proof / Stats */}
      <section className="max-w-7xl mx-auto px-4 py-16">
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-12 text-white text-center">
          <h2 className="text-3xl font-bold mb-8">Trusted by Allergy Sufferers</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div>
              <div className="text-4xl font-bold mb-2">99%+</div>
              <p className="text-blue-100">Allergen Detection Accuracy</p>
            </div>
            <div>
              <div className="text-4xl font-bold mb-2">&lt;1s</div>
              <p className="text-blue-100">Average Scan Time</p>
            </div>
            <div>
              <div className="text-4xl font-bold mb-2">4 Ways</div>
              <p className="text-blue-100">To Scan Products</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="max-w-7xl mx-auto px-4 py-20 text-center">
        <h2 className="text-4xl font-bold text-zinc-900 mb-6">
          Ready to Eat Safely?
        </h2>
        <p className="text-xl text-zinc-600 mb-8">
          Create your personalized allergen profile and start scanning in seconds.
        </p>
        <Link 
          href="/dashboard" 
          className="inline-block px-10 py-4 rounded-lg bg-gradient-to-r from-blue-600 to-purple-600 text-white font-bold text-lg hover:shadow-lg hover:scale-105 transition-all duration-200"
        >
          Get Started Free
        </Link>
      </section>
    </main>
  )
}
