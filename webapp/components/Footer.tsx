export default function Footer() {
  return (
    <footer className="bg-white border-t border-zinc-200 mt-20">
      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="grid md:grid-cols-4 gap-8 mb-8">
          <div>
            <h4 className="font-bold text-zinc-900 mb-4">SafeEats</h4>
            <p className="text-sm text-zinc-600">Smart allergen detection for every meal.</p>
          </div>
          <div>
            <h4 className="font-semibold text-zinc-900 mb-4">Product</h4>
            <ul className="space-y-2 text-sm text-zinc-600">
              <li><a href="#" className="hover:text-blue-600">Features</a></li>
              <li><a href="#" className="hover:text-blue-600">Pricing</a></li>
              <li><a href="#" className="hover:text-blue-600">API</a></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold text-zinc-900 mb-4">Company</h4>
            <ul className="space-y-2 text-sm text-zinc-600">
              <li><a href="/privacy" className="hover:text-blue-600">Privacy</a></li>
              <li><a href="#" className="hover:text-blue-600">Terms</a></li>
              <li><a href="#" className="hover:text-blue-600">Contact</a></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold text-zinc-900 mb-4">Resources</h4>
            <ul className="space-y-2 text-sm text-zinc-600">
              <li><a href="#" className="hover:text-blue-600">Blog</a></li>
              <li><a href="#" className="hover:text-blue-600">Help</a></li>
              <li><a href="#" className="hover:text-blue-600">Support</a></li>
            </ul>
          </div>
        </div>
        <div className="border-t border-zinc-200 pt-8">
          <p className="text-center text-sm text-zinc-600">
            © 2025 SafeEats. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  )
}
