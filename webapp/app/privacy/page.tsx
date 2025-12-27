export default function PrivacyPage() {
  return (
    <main className="max-w-4xl mx-auto px-4 py-12">
      <article className="bg-white rounded-2xl shadow-lg p-8 prose prose-zinc max-w-none">
        <h1 className="text-4xl font-bold text-zinc-900 mb-8">Privacy Policy</h1>

        <div className="space-y-8 text-zinc-700">
          <section>
            <h2 className="text-2xl font-bold text-zinc-900 mb-4">1. Introduction</h2>
            <p>
              SafeEats ("we," "us," "our," or "Company") is committed to protecting your privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our website and application.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-zinc-900 mb-4">2. Information We Collect</h2>
            <p>We may collect information about you in a variety of ways. The information we may collect on the Site includes:</p>
            <ul className="list-disc list-inside space-y-2 ml-4">
              <li><strong>Personal Data:</strong> Email address, name, password</li>
              <li><strong>Allergen Information:</strong> Your allergen profile and severity levels</li>
              <li><strong>Scan History:</strong> Products scanned, allergen detection results, images uploaded</li>
              <li><strong>Device Information:</strong> IP address, browser type, device type</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-zinc-900 mb-4">3. Use of Your Information</h2>
            <p>Having accurate information about you permits us to provide you with a smooth, efficient, and customized experience. Specifically, we may use information collected about you via the Site to:</p>
            <ul className="list-disc list-inside space-y-2 ml-4">
              <li>Provide allergen detection services</li>
              <li>Generate personalized scan results</li>
              <li>Improve our services and user experience</li>
              <li>Send you service-related announcements</li>
              <li>Respond to your inquiries and support requests</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-zinc-900 mb-4">4. Disclosure of Your Information</h2>
            <p>We do not sell, trade, or rent your personal identification information to others. We do not disclose any personal information except:</p>
            <ul className="list-disc list-inside space-y-2 ml-4">
              <li>To comply with applicable laws and regulations</li>
              <li>When required by legal process or court order</li>
              <li>To protect the rights and safety of our users</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-zinc-900 mb-4">5. Security of Your Information</h2>
            <p>
              We use administrative, technical, and physical security measures to protect your personal information. However, no method of transmission over the Internet is 100% secure. While we strive to use commercially acceptable means to protect your personal information, we cannot guarantee its absolute security.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-zinc-900 mb-4">6. Data Retention</h2>
            <p>
              We retain your personal information for as long as your account is active or as needed to provide you services. You may request deletion of your account and associated data at any time by contacting us.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-zinc-900 mb-4">7. Your Rights</h2>
            <p>You have the right to:</p>
            <ul className="list-disc list-inside space-y-2 ml-4">
              <li>Access your personal information</li>
              <li>Correct inaccurate data</li>
              <li>Request deletion of your data</li>
              <li>Withdraw consent at any time</li>
              <li>Port your data to another service</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-zinc-900 mb-4">8. Changes to This Privacy Policy</h2>
            <p>
              SafeEats reserves the right to modify this privacy policy at any time. Changes and clarifications will take effect immediately upon their posting to the Website. If we make material changes to this policy, we will notify you through our Services or by other means.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-zinc-900 mb-4">9. Contact Us</h2>
            <p>
              If you have questions or comments about this Privacy Policy, please contact us at:
            </p>
            <div className="bg-blue-50 p-4 rounded-lg border border-blue-200 mt-4">
              <p><strong>Email:</strong> privacy@safeeats.app</p>
              <p><strong>Address:</strong> SafeEats Support Team</p>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-zinc-900 mb-4">10. Disclaimer</h2>
            <p className="bg-red-50 p-4 rounded-lg border border-red-200 text-red-700">
              <strong>Important:</strong> SafeEats is an advisory tool only and should not be used as a substitute for professional medical advice. Always consult with a healthcare professional or allergist for diagnosis and treatment of food allergies. Results from our allergen detection system are provided "as-is" without warranty.
            </p>
          </section>
        </div>

        <div className="mt-12 pt-8 border-t border-zinc-200">
          <a href="/" className="text-blue-600 font-semibold hover:text-blue-700">
            ← Back to Home
          </a>
        </div>
      </article>
    </main>
  )
}
