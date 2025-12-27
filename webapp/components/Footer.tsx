import Link from 'next/link'
import { Github, Linkedin, Mail, Heart } from 'lucide-react'

export default function Footer() {
  const currentYear = new Date().getFullYear()
  const socialLinks = [
    { icon: Github, href: 'https://github.com/yehia-alhaddad/allergen-detection-fyp', label: 'GitHub' },
    { icon: Linkedin, href: 'https://linkedin.com', label: 'LinkedIn' },
    { icon: Mail, href: 'mailto:support@safeeats.app', label: 'Email' },
  ]

  return (
    <footer className="bg-gradient-to-b from-zinc-50 to-zinc-100 border-t border-zinc-200 mt-20">
      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="grid md:grid-cols-5 gap-8 mb-12">
          {/* Brand */}
          <div className="col-span-1">
            <h4 className="font-bold text-lg text-zinc-900 mb-4 flex items-center gap-2">
              🥗 SafeEats
            </h4>
            <p className="text-sm text-zinc-600 leading-relaxed mb-4">
              Smart allergen detection powered by AI/ML. Scan, detect, stay safe.
            </p>
            <div className="flex gap-3">
              {socialLinks.map(({ icon: Icon, href, label }) => (
                <a
                  key={label}
                  href={href}
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label={label}
                  className="text-zinc-600 hover:text-blue-600 transition"
                >
                  <Icon size={18} />
                </a>
              ))}
            </div>
          </div>

          {/* Product */}
          <div>
            <h4 className="font-semibold text-zinc-900 mb-4">Product</h4>
            <ul className="space-y-2 text-sm text-zinc-600">
              <li><Link href="/dashboard" className="hover:text-blue-600 transition">Dashboard</Link></li>
              <li><Link href="/" className="hover:text-blue-600 transition">Features</Link></li>
              <li><a href="https://github.com/yehia-alhaddad/allergen-detection-fyp/blob/main/docs/API_README.md" target="_blank" rel="noopener noreferrer" className="hover:text-blue-600 transition">API Docs</a></li>
              <li><Link href="/privacy" className="hover:text-blue-600 transition">Privacy Policy</Link></li>
            </ul>
          </div>

          {/* Company */}
          <div>
            <h4 className="font-semibold text-zinc-900 mb-4">Company</h4>
            <ul className="space-y-2 text-sm text-zinc-600">
              <li><a href="#" className="hover:text-blue-600 transition">About Us</a></li>
              <li><a href="#" className="hover:text-blue-600 transition">Blog</a></li>
              <li><a href="#" className="hover:text-blue-600 transition">Careers</a></li>
              <li><a href="mailto:support@safeeats.app" className="hover:text-blue-600 transition">Contact</a></li>
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h4 className="font-semibold text-zinc-900 mb-4">Resources</h4>
            <ul className="space-y-2 text-sm text-zinc-600">
              <li><a href="https://github.com/yehia-alhaddad/allergen-detection-fyp" target="_blank" rel="noopener noreferrer" className="hover:text-blue-600 transition">GitHub Repo</a></li>
              <li><a href="https://github.com/yehia-alhaddad/allergen-detection-fyp#readme" target="_blank" rel="noopener noreferrer" className="hover:text-blue-600 transition">Documentation</a></li>
              <li><a href="/" className="hover:text-blue-600 transition">FAQ</a></li>
              <li><a href="#" className="hover:text-blue-600 transition">Support</a></li>
            </ul>
          </div>

          {/* Tech Stack */}
          <div>
            <h4 className="font-semibold text-zinc-900 mb-4">Built With</h4>
            <ul className="space-y-1 text-xs text-zinc-600">
              <li>• Next.js 14</li>
              <li>• FastAPI</li>
              <li>• PyTorch + NER</li>
              <li>• EasyOCR</li>
              <li>• Prisma ORM</li>
            </ul>
          </div>
        </div>

        {/* Divider */}
        <div className="border-t border-zinc-300 pt-8">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-sm text-zinc-600 flex items-center gap-1">
              © {currentYear} SafeEats. Made with <Heart size={14} className="text-red-500" /> for food safety.
            </p>
            <p className="text-xs text-zinc-500">
              Version 1.0.0 | <a href="#" className="hover:text-zinc-700 transition">Terms of Service</a>
            </p>
          </div>
        </div>
      </div>
    </footer>
  )
}
