import Link from 'next/link'
import { TrendingUp, BarChart3, Bell, Globe, Zap, Shield } from 'lucide-react'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Navbar */}
      <nav className="bg-white shadow-sm border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-8 h-8 text-blue-600" />
              <span className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                ASO RankGuard
              </span>
            </div>
            <div className="hidden md:flex items-center gap-8">
              <Link href="#features" className="text-slate-600 hover:text-slate-900 transition">
                Features
              </Link>
              <Link href="/pricing" className="text-slate-600 hover:text-slate-900 transition">
                Pricing
              </Link>
              <Link href="/login" className="text-slate-600 hover:text-slate-900 transition">
                Login
              </Link>
              <Link 
                href="/login?signup=true"
                className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-2 rounded-lg hover:shadow-lg transition"
              >
                Start Free Trial
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          <h1 className="text-5xl md:text-6xl font-extrabold text-slate-900 mb-6">
            Dominate App Store Rankings with
            <span className="block bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">Real-Time ASO Intelligence</span>
          </h1>
          <p className="text-xl text-slate-600 mb-8 max-w-3xl mx-auto">
            Track keyword rankings, analyze competitors, and get instant alerts when your apps move. 
            Make data-driven decisions to skyrocket your visibility.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/login?signup=true"
              className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:shadow-xl transition transform hover:-translate-y-1"
            >
              Start Free - No Credit Card
            </Link>
            <Link
              href="#features"
              className="bg-white border-2 border-slate-300 text-slate-900 px-8 py-4 rounded-lg text-lg font-semibold hover:border-blue-600 transition"
            >
              See How It Works
            </Link>
          </div>
          
          {/* Stats */}
          <div className="grid grid-cols-3 gap-8 mt-16 max-w-2xl mx-auto">
            <div>
              <div className="text-4xl font-bold text-blue-600">200+</div>
              <div className="text-slate-600">Apps Tracked</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-blue-600">50K+</div>
              <div className="text-slate-600">Keywords</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-blue-600">99.9%</div>
              <div className="text-slate-600">Uptime</div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-slate-900 mb-4">
              Everything you need to dominate ASO
            </h2>
            <p className="text-xl text-slate-600">
              Powerful features to track, analyze, and optimize your app store presence
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="bg-gradient-to-br from-blue-50 to-purple-50 p-8 rounded-2xl hover:shadow-lg transition">
              <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center mb-4">
                <TrendingUp className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 mb-2">
                Real-Time Rank Tracking
              </h3>
              <p className="text-slate-600">
                Monitor your keyword rankings every hour. Never miss a position change with automatic updates.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="bg-gradient-to-br from-green-50 to-emerald-50 p-8 rounded-2xl hover:shadow-lg transition">
              <div className="w-12 h-12 bg-green-600 rounded-lg flex items-center justify-center mb-4">
                <BarChart3 className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 mb-2">
                Competitor Analysis
              </h3>
              <p className="text-slate-600">
                Discover what keywords your competitors rank for. Steal their best strategies.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="bg-gradient-to-br from-orange-50 to-red-50 p-8 rounded-2xl hover:shadow-lg transition">
              <div className="w-12 h-12 bg-orange-600 rounded-lg flex items-center justify-center mb-4">
                <Bell className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 mb-2">
                Smart Alerts
              </h3>
              <p className="text-slate-600">
                Get instant Telegram notifications when rankings drop or competitors make moves.
              </p>
            </div>

            {/* Feature 4 */}
            <div className="bg-gradient-to-br from-purple-50 to-pink-50 p-8 rounded-2xl hover:shadow-lg transition">
              <div className="w-12 h-12 bg-purple-600 rounded-lg flex items-center justify-center mb-4">
                <Globe className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 mb-2">
                Multi-Market Support
              </h3>
              <p className="text-slate-600">
                Track rankings across all App Store countries. Perfect for global apps.
              </p>
            </div>

            {/* Feature 5 */}
            <div className="bg-gradient-to-br from-cyan-50 to-blue-50 p-8 rounded-2xl hover:shadow-lg transition">
              <div className="w-12 h-12 bg-cyan-600 rounded-lg flex items-center justify-center mb-4">
                <Zap className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 mb-2">
                Historical Data
              </h3>
              <p className="text-slate-600">
                Access 90+ days of ranking history. Identify trends and seasonal patterns.
              </p>
            </div>

            {/* Feature 6 */}
            <div className="bg-gradient-to-br from-slate-50 to-gray-100 p-8 rounded-2xl hover:shadow-lg transition">
              <div className="w-12 h-12 bg-slate-600 rounded-lg flex items-center justify-center mb-4">
                <Shield className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 mb-2">
                Secure & Private
              </h3>
              <p className="text-slate-600">
                Enterprise-grade security. Your data is encrypted and never shared.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-purple-600">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl font-bold text-white mb-4">
            Ready to boost your app rankings?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Join hundreds of developers optimizing their ASO strategy
          </p>
          <Link
            href="/login?signup=true"
            className="bg-white text-blue-600 px-8 py-4 rounded-lg text-lg font-semibold hover:shadow-xl transition inline-block"
          >
            Start Free Trial - No Credit Card Required
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-900 text-slate-400 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <TrendingUp className="w-6 h-6 text-blue-500" />
                <span className="text-white font-bold">ASO RankGuard</span>
              </div>
              <p className="text-sm">
                Real-time ASO intelligence for modern app developers.
              </p>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-sm">
                <li><Link href="#features" className="hover:text-white transition">Features</Link></li>
                <li><Link href="/pricing" className="hover:text-white transition">Pricing</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-sm">
                <li><Link href="/about" className="hover:text-white transition">About</Link></li>
                <li><Link href="/contact" className="hover:text-white transition">Contact</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Legal</h4>
              <ul className="space-y-2 text-sm">
                <li><Link href="/privacy" className="hover:text-white transition">Privacy</Link></li>
                <li><Link href="/terms" className="hover:text-white transition">Terms</Link></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-slate-800 mt-12 pt-8 text-center text-sm">
            <p>&copy; 2026 ASO RankGuard. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
