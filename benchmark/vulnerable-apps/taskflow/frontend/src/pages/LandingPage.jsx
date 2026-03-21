import { Link } from 'react-router-dom';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
        <span className="text-xl font-bold text-indigo-600">TaskFlow</span>
        <div className="flex gap-4">
          <Link to="/login" className="text-gray-600 hover:text-gray-900">Log in</Link>
          <Link to="/register" className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">Sign up</Link>
        </div>
      </nav>

      <section className="max-w-4xl mx-auto px-6 py-20 text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Project management for engineering teams
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          Tasks, projects, and team collaboration in one place. No fluff — just what you need to ship.
        </p>
        <Link to="/register" className="inline-block px-8 py-3 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700">
          Get started free
        </Link>
      </section>

      <section className="max-w-6xl mx-auto px-6 py-16">
        <h2 className="text-2xl font-semibold text-gray-900 text-center mb-12">Features</h2>
        <div className="grid md:grid-cols-3 gap-8">
          <div className="bg-white p-6 rounded-xl border border-gray-200">
            <h3 className="font-semibold text-gray-900 mb-2">Projects & tasks</h3>
            <p className="text-gray-600">Organize work by project. Create tasks, set priority and due dates, assign owners.</p>
          </div>
          <div className="bg-white p-6 rounded-xl border border-gray-200">
            <h3 className="font-semibold text-gray-900 mb-2">Team collaboration</h3>
            <p className="text-gray-600">Invite your team, comment on tasks, and keep an activity feed per project.</p>
          </div>
          <div className="bg-white p-6 rounded-xl border border-gray-200">
            <h3 className="font-semibold text-gray-900 mb-2">Reports & export</h3>
            <p className="text-gray-600">Generate PDF reports and bulk import from CSV or XML.</p>
          </div>
        </div>
      </section>

      <section className="max-w-4xl mx-auto px-6 py-16">
        <h2 className="text-2xl font-semibold text-gray-900 text-center mb-12">Pricing</h2>
        <div className="grid md:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-xl border border-gray-200 text-center">
            <h3 className="font-semibold text-gray-900">Free</h3>
            <p className="text-3xl font-bold text-indigo-600 mt-2">$0</p>
            <p className="text-gray-600 text-sm mt-1">Up to 3 projects, 5 members</p>
            <Link to="/register" className="mt-4 inline-block w-full py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50">Start free</Link>
          </div>
          <div className="bg-white p-6 rounded-xl border-2 border-indigo-500 rounded-xl text-center relative">
            <span className="absolute -top-3 left-1/2 -translate-x-1/2 px-2 py-0.5 bg-indigo-500 text-white text-xs rounded">Popular</span>
            <h3 className="font-semibold text-gray-900">Pro</h3>
            <p className="text-3xl font-bold text-indigo-600 mt-2">$12</p>
            <p className="text-gray-600 text-sm mt-1">Unlimited projects & members</p>
            <Link to="/register" className="mt-4 inline-block w-full py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">Start trial</Link>
          </div>
          <div className="bg-white p-6 rounded-xl border border-gray-200 text-center">
            <h3 className="font-semibold text-gray-900">Enterprise</h3>
            <p className="text-3xl font-bold text-indigo-600 mt-2">Custom</p>
            <p className="text-gray-600 text-sm mt-1">SSO, SLA, dedicated support</p>
            <a href="mailto:sales@taskflow.io" className="mt-4 inline-block w-full py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50">Contact sales</a>
          </div>
        </div>
      </section>

      <section className="max-w-4xl mx-auto px-6 py-16">
        <h2 className="text-2xl font-semibold text-gray-900 text-center mb-12">What teams say</h2>
        <div className="grid md:grid-cols-2 gap-8">
          <blockquote className="bg-white p-6 rounded-xl border border-gray-200">
            <p className="text-gray-700">"We switched from spreadsheets to TaskFlow and never looked back. Simple and fast."</p>
            <footer className="mt-4 text-sm text-gray-500">— Sarah, CTO at StartupXYZ</footer>
          </blockquote>
          <blockquote className="bg-white p-6 rounded-xl border border-gray-200">
            <p className="text-gray-700">"Finally a tool that doesn't get in the way. Our team ships faster now."</p>
            <footer className="mt-4 text-sm text-gray-500">— Mike, Eng lead at Acme</footer>
          </blockquote>
        </div>
      </section>

      <footer className="border-t border-gray-200 mt-20 py-8 px-6 text-center text-sm text-gray-500">
        © {new Date().getFullYear()} TaskFlow Inc. All rights reserved.
      </footer>
    </div>
  );
}
