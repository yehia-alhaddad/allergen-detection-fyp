export const metadata = {
  title: 'FAQ — SafeEats',
  description: 'Common questions and clear answers about SafeEats.',
}

import Link from 'next/link'
import { ArrowLeft, ChevronDown } from 'lucide-react'

const faqs: { q: string; a: string }[] = [
  {
    q: 'What can I scan?',
    a: 'You can upload product label photos, take live camera captures, or paste ingredient lists. Works with any image format (JPG, PNG, PDF) and any text format.',
  },
  {
    q: 'Which allergens do you detect?',
    a: 'We cover 14+ major allergens: peanuts, tree nuts, milk, eggs, fish, shellfish, wheat, gluten, soy, sesame, celery, mustard, sulfites, and mollusks. Plus international variations and synonyms.',
  },
  {
    q: 'How accurate is SafeEats?',
    a: 'We achieve 99%+ accuracy through BERT NER + dictionary matching on real products. But food allergies are serious—always verify against the original label when in doubt.',
  },
  {
    q: 'Do you store my scans?',
    a: 'Only if you create an account. Without an account, scans are processed and discarded immediately. With an account, you control your history and can delete scans anytime.',
  },
  {
    q: 'Can you detect "may contain" warnings?',
    a: 'Yes. We specifically flag precautionary statements like "may contain," "processed in," and "manufactured with" allergens—and alert you appropriately.',
  },
  {
    q: 'What image quality do I need?',
    a: 'Best results: well-lit photos, sharp focus, ingredient list fully visible, no glare or shadows. But we\'re designed to handle real-world conditions—even photos from grocery stores work.',
  },
  {
    q: 'How fast are results?',
    a: 'Most scans complete in under 1 second. The system is optimized for instant shopping decisions—no waiting around.',
  },
  {
    q: 'Do I need to create an account?',
    a: 'No. You can scan immediately as a guest. But accounts unlock personalized allergen profiles, scan history, and personalized recommendations.',
  },
  {
    q: 'Is my data private?',
    a: 'Absolutely. Your scans are encrypted, never sold, and not used for tracking. We\'re GDPR compliant and take privacy as seriously as food safety.',
  },
  {
    q: 'What languages does it support?',
    a: 'English is fully supported. Our OCR works with multiple languages on labels; allergen detection is optimized for English ingredient lists.',
  },
]

export default function FAQPage() {
  return (
    <main className="flex flex-col min-h-screen bg-white">
      {/* Hero Section */}
      <section className="relative px-4 sm:px-6 lg:px-8 py-16 sm:py-24 bg-gradient-to-br from-emerald-50 via-white to-blue-50 border-b border-emerald-200">
        <div className="max-w-4xl mx-auto">
          <Link href="/" className="inline-flex items-center gap-2 text-emerald-600 hover:text-emerald-700 font-semibold mb-8 transition">
            <ArrowLeft size={20} />
            Back to Home
          </Link>

          <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-4">Frequently Asked Questions</h1>
          <p className="text-lg text-gray-600">
            Common questions answered. Can't find what you need? Reach out to our support team.
          </p>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="px-4 sm:px-6 lg:px-8 py-16 sm:py-24">
        <div className="max-w-4xl mx-auto">
          <div className="space-y-4">
            {faqs.map((faq, idx) => (
              <details key={idx} className="group border border-gray-200 rounded-lg hover:border-emerald-300 transition-all">
                <summary className="flex cursor-pointer items-center justify-between p-6 font-semibold text-gray-900 hover:bg-emerald-50 transition">
                  <span>{faq.q}</span>
                  <ChevronDown className="h-5 w-5 transition-transform group-open:rotate-180" />
                </summary>
                <div className="border-t border-gray-200 px-6 py-4 text-gray-600">
                  {faq.a}
                </div>
              </details>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="px-4 sm:px-6 lg:px-8 py-16 sm:py-24 bg-gradient-to-r from-emerald-600 to-green-600">
        <div className="max-w-2xl mx-auto text-center">
          <h2 className="text-3xl font-bold text-white mb-4">Still Have Questions?</h2>
          <p className="text-lg text-emerald-100 mb-8">
            We're here to help. Contact us anytime—we respond within 24 hours.
          </p>
          <Link href="/signup">
            <button className="px-8 py-4 bg-white text-emerald-600 rounded-lg font-semibold hover:bg-gray-100 transition-all">
              Get Started →
            </button>
          </Link>
        </div>
      </section>
    </main>
  );
}
