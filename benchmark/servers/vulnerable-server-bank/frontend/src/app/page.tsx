'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';

export default function LandingPage() {
  const [promoCode, setPromoCode] = useState('');
  const [displayedPromo, setDisplayedPromo] = useState('');

  // VULNERABILITY: DOM-based XSS via location.hash
  useEffect(() => {
    const hash = window.location.hash.slice(1);
    if (hash) {
      // VULNERABILITY: InnerHTML with unsanitized user input
      const promoDiv = document.getElementById('promo-display');
      if (promoDiv) {
        promoDiv.innerHTML = decodeURIComponent(hash);
      }
    }
  }, []);

  // VULNERABILITY: Prototype Pollution via query parameter
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const config = params.get('config');

    if (config) {
      try {
        // VULNERABILITY: Deep merge without prototype pollution protection
        const userConfig = JSON.parse(config);
        const defaultConfig = { theme: 'light', lang: 'en' };

        // Pollutes Object.prototype if config has __proto__ or constructor
        const merged = { ...defaultConfig, ...userConfig };

        // Apply config
        Object.assign(defaultConfig, merged);
      } catch (e) {
        console.error('Config parse error:', e);
      }
    }
  }, []);

  // VULNERABILITY: PostMessage without origin validation
  useEffect(() => {
    const handler = (event: MessageEvent) => {
      // VULNERABILITY: No origin check, accepts messages from any domain
      if (event.data.type === 'setPromo') {
        setPromoCode(event.data.code);
        setDisplayedPromo(event.data.code);
      }

      // VULNERABILITY: Can execute arbitrary code via postMessage
      if (event.data.type === 'exec') {
        try {
          // DANGEROUS: eval on data from any origin
          const result = eval(event.data.script);
          event.source?.postMessage({ result }, '*');
        } catch (e) {
          console.error('Exec error:', e);
        }
      }
    };

    window.addEventListener('message', handler);
    return () => window.removeEventListener('message', handler);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-blue-800 to-indigo-900">
      {/* Header */}
      <nav className="bg-blue-900 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center">
                <span className="text-blue-900 font-bold text-xl">SB</span>
              </div>
              <span className="ml-3 text-xl font-bold">SecureBank</span>
            </div>
            <div className="flex space-x-4">
              <Link href="/login" className="px-4 py-2 text-white hover:text-blue-200">
                Sign In
              </Link>
              <Link href="/register" className="px-4 py-2 bg-white text-blue-900 rounded-lg hover:bg-gray-100">
                Open Account
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <div className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto">
          <div className="relative z-10 pb-8 bg-transparent sm:pb-16 md:pb-20 lg:pb-28 xl:pb-32">
            <main className="mt-10 mx-auto max-w-7xl px-4 sm:mt-12 sm:px-6 md:mt-16 lg:mt-20 xl:mt-28">
              <div className="text-center">
                <h1 className="text-4xl tracking-tight font-extrabold text-white sm:text-5xl md:text-6xl">
                  <span className="block">Banking Made</span>
                  <span className="block text-blue-200">Simple & Secure</span>
                </h1>
                <p className="mt-3 max-w-md mx-auto text-base text-blue-100 sm:text-lg md:mt-5 md:text-xl md:max-w-3xl">
                  Experience the future of banking with SecureBank. Zero fees, high interest rates,
                  and military-grade security for your peace of mind.
                </p>
                <div className="mt-5 max-w-md mx-auto sm:flex sm:justify-center md:mt-8">
                  <div className="rounded-md shadow">
                    <Link href="/register" className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-blue-900 bg-white hover:bg-gray-50 md:py-4 md:text-lg md:px-10">
                      Get Started
                    </Link>
                  </div>
                </div>

                {/* VULNERABILITY: XSS target via innerHTML */}
                <div id="promo-display" className="mt-4 text-yellow-300" />

                {/* VULNERABILITY: Reflected XSS via promo code */}
                {displayedPromo && (
                  <div
                    className="mt-4 text-green-300"
                    // VULNERABILITY: dangerouslySetInnerHTML with user-controlled data
                    dangerouslySetInnerHTML={{ __html: `Promo code applied: ${displayedPromo}` }}
                  />
                )}
              </div>
            </main>
          </div>
        </div>
      </div>

      {/* Features */}
      <div className="bg-white py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-base text-blue-600 font-semibold tracking-wide uppercase">Features</h2>
            <p className="mt-2 text-3xl leading-8 font-extrabold tracking-tight text-gray-900 sm:text-4xl">
              Why Choose SecureBank?
            </p>
          </div>
          <div className="mt-20 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
            {[
              { title: 'High Interest', desc: 'Earn up to 4.5% APY on savings' },
              { title: 'No Fees', desc: 'Zero monthly fees, zero hidden charges' },
              { title: '24/7 Support', desc: 'Round-the-clock customer service' },
              { title: 'Mobile Banking', desc: 'Bank from anywhere, anytime' },
              { title: 'Secure Cards', desc: 'Virtual cards for online purchases' },
              { title: 'Instant Transfer', desc: 'Send money in seconds' },
            ].map((feature, i) => (
              <div key={i} className="pt-6">
                <div className="flow-root bg-gray-50 rounded-lg px-6 pb-8">
                  <div className="-mt-6">
                    <h3 className="mt-8 text-lg font-medium text-gray-900 tracking-tight">{feature.title}</h3>
                    <p className="mt-5 text-base text-gray-500">{feature.desc}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Security Promise */}
      <div className="bg-blue-800 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-extrabold text-white">Your Security is Our Priority</h2>
          <p className="mt-4 text-xl text-blue-100">
            FDIC insured up to $250,000. 256-bit encryption. Biometric authentication.
          </p>
        </div>
      </div>
    </div>
  );
}
