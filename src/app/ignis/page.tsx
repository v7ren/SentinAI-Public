"use client";
import React, { useEffect, useRef, useState } from "react";
import { Shield, Zap, Lock, Check, ArrowRight, Terminal, Cpu, Network, Globe, Github, Rocket, Sparkles, ChevronDown, ChevronRight, Minus, Palette, X, } from "lucide-react";
const THEMES = {
    zinc: {
        name: "Zinc (Default)", type: "LIGHT",
        colors: { bg: "#fafafa", surface: "#ffffff", border: "#e4e4e7", textMain: "#18181b", textMuted: "#71717a", accent: "#18181b", accentText: "#ffffff" },
    },
    obsidian: {
        name: "Obsidian", type: "DARK",
        colors: { bg: "#0a0a0a", surface: "#111111", border: "#27272a", textMain: "#fafafa", textMuted: "#71717a", accent: "#ffffff", accentText: "#000000" },
    },
    aurora: {
        name: "Aurora", type: "DARK",
        colors: { bg: "#050d1a", surface: "#0d1f35", border: "#1a3a5c", textMain: "#e0f0ff", textMuted: "#6b9ec4", accent: "#38bdf8", accentText: "#000000" },
    },
    forest: {
        name: "Forest", type: "DARK",
        colors: { bg: "#080f0a", surface: "#0f1f12", border: "#1a3320", textMain: "#e0ffe8", textMuted: "#5a9a6a", accent: "#4ade80", accentText: "#000000" },
    },
    crimson: {
        name: "Crimson", type: "DARK",
        colors: { bg: "#0f0505", surface: "#1a0a0a", border: "#3a1010", textMain: "#ffe0e0", textMuted: "#a05050", accent: "#f87171", accentText: "#000000" },
    },
} as const;
type ThemeKey = keyof typeof THEMES;
export default function SentinAI() {
    const observerRef = useRef<IntersectionObserver | null>(null);
    const [isLoaded, setIsLoaded] = useState(false);
    const [scrolled, setScrolled] = useState(false);
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const [isAnnual, setIsAnnual] = useState(true);
    const [openFaq, setOpenFaq] = useState<number | null>(null);
    const [activeTheme, setActiveTheme] = useState<ThemeKey>("obsidian");
    const [showThemeSwitcher, setShowThemeSwitcher] = useState(false);
    const [imageLoaded, setImageLoaded] = useState(false);
    const theme = THEMES[activeTheme];
    const isDark = theme.type === "DARK";
    const t = theme.colors;
    useEffect(() => {
        setIsLoaded(true);
        const handleScroll = () => setScrolled(window.scrollY > 20);
        window.addEventListener("scroll", handleScroll);
        return () => window.removeEventListener("scroll", handleScroll);
    }, []);
    useEffect(() => {
        observerRef.current = new IntersectionObserver((entries) => entries.forEach((e) => { if (e.isIntersecting)
            e.target.classList.add("visible"); }), { threshold: 0.1, rootMargin: "0px 0px -50px 0px" });
        document.querySelectorAll(".aos-item, .philosophy-block").forEach((el) => observerRef.current?.observe(el));
        return () => observerRef.current?.disconnect();
    }, []);
    useEffect(() => {
        document.body.style.overflow = isMenuOpen ? "hidden" : "unset";
    }, [isMenuOpen]);
    const features = [
        { icon: Terminal, title: "Deep Code Analysis", description: "AI-powered scanning across your entire codebase using DeepWiki for comprehensive context understanding." },
        { icon: Cpu, title: "Multi-Tier AI", description: "Tiered OpenRouter stack: CHEAP_MODEL for breadth, SMART_MODEL / TIER2_MODEL for deep semantic analysis." },
        { icon: Zap, title: "Automated PoC", description: "Automatically generate proof-of-concept exploits for confirmed vulnerabilities to streamline remediation." },
        { icon: Network, title: "Architecture Mapping", description: "Visualize project structure and dependencies to identify security boundaries and attack surfaces." },
        { icon: Lock, title: "Compliance Reporting", description: "Generate detailed security reports aligned with OWASP, NIST, and SOC2 compliance frameworks." },
        { icon: Shield, title: "Intelligent Alerts", description: "Priority-based notifications with false-positive filtering to focus on real threats." },
    ];
    const plans = [
        {
            name: "Scout", description: "For hobbyists and open source.", price: 0, highlight: false, cta: "Start for Free",
            features: ["Unlimited Public Repositories", "5,000 Lines of Code / mo", "Basic Vulnerability Scanning", "Community Support", "7-day History Retention"],
        },
        {
            name: "Sentinel", description: "For professional developers and small teams.", price: isAnnual ? 24 : 29, highlight: true, cta: "Go Pro",
            features: ["Unlimited Private Repositories", "100,000 Lines of Code / mo", "Real-time CI/CD Integration", "Advanced Dependency Graph", "Priority Email Support", "90-day History Retention", "GitHub PR Comments"],
        },
        {
            name: "Guardian", description: "For scaling organizations requiring compliance.", price: isAnnual ? 99 : 119, highlight: false, cta: "Contact Sales",
            features: ["Unlimited Lines of Code", "SSO (SAML & OIDC)", "Custom Rule Engine", "Audit Logs & Compliance Reports", "Dedicated Success Manager", "Unlimited History", "Self-hosted Option Available"],
        },
    ];
    const faqs = [
        { q: "How do you count lines of code?", a: "We only count lines of code in files that are actively scanned. Comments, whitespace, and ignored files (.gitignore) are not counted against your quota." },
        { q: "Can I switch plans later?", a: "Absolutely. You can upgrade or downgrade your plan at any time from your dashboard. Prorated charges will apply automatically." },
        { q: "Is there a free trial for Sentinel?", a: "Yes! We offer a 14-day free trial for the Sentinel plan so you can test the CI/CD integrations with your private repositories." },
        { q: "Do you support on-premise hosting?", a: "Yes, our Guardian plan includes options for self-hosting Sentinel on your own infrastructure for maximum security compliance." },
    ];
    const partners = ["Acme Corp", "Warp Systems", "SecurityFirst", "Nebula Ops", "CyberDyne", "Massive Dynamic", "Hooli", "Initech"];
    return (<div className={`relative font-sans overflow-x-hidden min-h-screen transition-all duration-700 ${isLoaded ? "opacity-100" : "opacity-0"}`} style={{ backgroundColor: t.bg, color: t.textMain }}>
      <style>{`
        .grain-overlay::before {
          content:""; position:fixed; top:0; left:0; width:100%; height:100%;
          pointer-events:none; z-index:9999;
          background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.05'/%3E%3C/svg%3E");
          opacity:0.35;
        }
        .aos-item { opacity:0; transform:translateY(24px); transition:opacity 0.8s cubic-bezier(.16,1,.3,1), transform 0.8s cubic-bezier(.16,1,.3,1); }
        .aos-item.visible { opacity:1; transform:translateY(0); }
        .aos-delay-1{transition-delay:.1s} .aos-delay-2{transition-delay:.2s}
        .aos-delay-3{transition-delay:.3s} .aos-delay-4{transition-delay:.4s}
        .aos-delay-5{transition-delay:.5s}
        @keyframes marquee { 0%{transform:translateX(0)} 100%{transform:translateX(-50%)} }
        .marquee-track { display:flex; width:max-content; animation:marquee 30s linear infinite; }
        .marquee-track:hover { animation-play-state:paused; }
        .philosophy-block { opacity:0; transform:scale(0.98); transition:opacity 0.8s ease, transform 0.8s ease; }
        .philosophy-block.visible { opacity:1; transform:scale(1); }
        .philosophy-block .p-label { opacity:0; transform:translateY(10px); transition:opacity .5s ease .2s, transform .5s ease .2s; }
        .philosophy-block.visible .p-label { opacity:1; transform:translateY(0); }
        .philosophy-block .p-quote { opacity:0; transform:translateY(10px); transition:opacity .5s ease .4s, transform .5s ease .4s; }
        .philosophy-block.visible .p-quote { opacity:1; transform:translateY(0); }
        .p-hr { height:1px; width:0; margin:0 auto; transition:width 1s cubic-bezier(.16,1,.3,1) .8s; }
        .philosophy-block.visible .p-hr { width:100%; }
        .p-vline { height:0; width:1px; margin:0 auto; transition:height .8s cubic-bezier(.16,1,.3,1) 1.5s; }
        .philosophy-block.visible .p-vline { height:5rem; }
        .p-rect { position:absolute; top:0; left:0; right:0; bottom:0; clip-path:inset(0 0 100% 0); transition:clip-path 1.2s cubic-bezier(.16,1,.3,1) 2.4s; pointer-events:none; }
        .philosophy-block.visible .p-rect { clip-path:inset(0 0 0 0); }
        .philosophy-block.visible .p-vline { transition:height .8s cubic-bezier(.16,1,.3,1) 1.5s, opacity .5s ease 2.8s; opacity:0.3; }
        .p-est { opacity:0; transition:opacity .5s ease 3.2s; }
        .philosophy-block.visible .p-est { opacity:1; }
        @keyframes spin { from{transform:rotate(0deg)} to{transform:rotate(360deg)} }
        .spin-slow { animation:spin 10s linear infinite; }
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.5} }
        .pulse { animation:pulse 2s ease-in-out infinite; }
      `}</style>

      <div className="grain-overlay"/>

      
      <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end gap-3">
        {showThemeSwitcher && (<div className="p-4 rounded-2xl shadow-2xl w-56 border" style={{ backgroundColor: t.surface, borderColor: t.border }}>
            <div className="flex justify-between items-center mb-3 pb-2 border-b" style={{ borderColor: t.border }}>
              <span className="text-xs font-bold uppercase tracking-wider" style={{ color: t.textMuted }}>Theme</span>
              <button onClick={() => setShowThemeSwitcher(false)}><X className="w-4 h-4" style={{ color: t.textMuted }}/></button>
            </div>
            <div className="space-y-1">
              {(Object.keys(THEMES) as ThemeKey[]).map((key) => (<button key={key} onClick={() => setActiveTheme(key)} className="flex items-center gap-3 p-2 rounded-lg w-full text-left transition-colors" style={{ backgroundColor: activeTheme === key ? `${t.accent}15` : "transparent" }}>
                  <div className="w-5 h-5 rounded border shadow-sm shrink-0" style={{ backgroundColor: THEMES[key].colors.bg, borderColor: THEMES[key].colors.border }}/>
                  <span className="text-sm font-medium" style={{ color: t.textMain }}>{THEMES[key].name}</span>
                  {activeTheme === key && <Check className="w-3 h-3 ml-auto" style={{ color: t.accent }}/>}
                </button>))}
            </div>
          </div>)}
        <button onClick={() => setShowThemeSwitcher(!showThemeSwitcher)} className="h-12 w-12 rounded-full border shadow-xl flex items-center justify-center transition-transform hover:scale-110" style={{ backgroundColor: t.surface, borderColor: t.border, color: t.textMain }}>
          <Palette className="w-5 h-5"/>
        </button>
      </div>

      
      <nav className="fixed top-0 left-0 right-0 z-50 px-6 md:px-16 py-5 flex justify-between items-center transition-all duration-300 border-b" style={{
            backgroundColor: scrolled ? `${t.bg}CC` : "transparent",
            borderColor: scrolled ? t.border : "transparent",
            backdropFilter: scrolled ? "blur(16px)" : "none",
        }}>
        <a href="/" className="flex items-center gap-3 text-xl tracking-[0.2em] uppercase font-bold relative z-50" style={{ color: isMenuOpen ? "#ffffff" : t.textMain }}>
          <img src="/logo.svg" alt="" className="w-8 h-8 rounded-sm object-contain shrink-0" aria-hidden/>
          SENTINAI
        </a>

        <div className="hidden md:flex items-center gap-10">
          {["Features", "Pricing", "About", "Docs"].map((item) => (<a key={item} href={`#${item.toLowerCase()}`} className="text-xs tracking-[0.2em] uppercase transition-colors font-medium opacity-60 hover:opacity-100" style={{ color: t.textMain }}>{item}</a>))}
          <a href="#pricing" className="px-5 py-2 text-xs tracking-[0.2em] uppercase font-bold rounded-full transition-colors" style={{ backgroundColor: t.accent, color: t.accentText }}>
            Get Started
          </a>
        </div>

        
        <button className="md:hidden relative z-50 p-2 -mr-2" onClick={() => setIsMenuOpen(!isMenuOpen)} aria-label="Toggle Menu">
          <div className="w-6 h-5 flex flex-col justify-between">
            <span className={`w-full h-0.5 transition-all duration-300 ${isMenuOpen ? "rotate-45 translate-y-2 bg-white" : ""}`} style={{ backgroundColor: isMenuOpen ? undefined : t.textMain }}/>
            <span className={`w-full h-0.5 transition-all duration-300 ${isMenuOpen ? "opacity-0 bg-white" : ""}`} style={{ backgroundColor: isMenuOpen ? undefined : t.textMain }}/>
            <span className={`w-full h-0.5 transition-all duration-300 ${isMenuOpen ? "-rotate-45 -translate-y-2.5 bg-white" : ""}`} style={{ backgroundColor: isMenuOpen ? undefined : t.textMain }}/>
          </div>
        </button>

        
        <div className={`fixed inset-0 bg-zinc-900 z-40 flex flex-col justify-center px-8 transition-all duration-500 ${isMenuOpen ? "opacity-100 visible" : "opacity-0 invisible pointer-events-none"}`}>
          <div className="flex flex-col gap-8">
            {["Features", "Pricing", "About", "Sign In"].map((item, i) => (<a key={item} href={`#${item.toLowerCase()}`} onClick={() => setIsMenuOpen(false)} className={`text-4xl text-white font-light tracking-widest uppercase transition-all duration-500 ${isMenuOpen ? "translate-y-0 opacity-100" : "translate-y-10 opacity-0"}`} style={{ transitionDelay: `${i * 80}ms` }}>{item}</a>))}
          </div>
        </div>
      </nav>

      
      <section className="relative min-h-screen flex items-center overflow-hidden pt-32 pb-24 md:py-0">
        <div className="absolute inset-0 z-0">
          <img src="https://images.unsplash.com/photo-1588882452498-c52ff32bfdb0?q=80&w=2050&auto=format&fit=crop" alt="" onLoad={() => setImageLoaded(true)} className={`w-full h-full object-cover select-none transition-all duration-2500 ease-out ${imageLoaded ? "scale-100" : "scale-110 opacity-0"}`} style={{ opacity: isDark ? 0.35 : 0.07, filter: isDark ? "none" : "invert(1) grayscale(1)" }}/>
          <div className="absolute inset-0" style={{ background: `linear-gradient(to bottom, ${t.bg}, transparent 40%, ${t.bg})` }}/>
          <div className="absolute inset-0" style={{ background: `radial-gradient(circle at 60% 50%, ${t.accent}12, transparent 70%)` }}/>
        </div>
        <div className="absolute inset-0 pointer-events-none" style={{ opacity: isDark ? 0.04 : 0.03, backgroundImage: `linear-gradient(${t.textMain} 1px, transparent 1px), linear-gradient(90deg, ${t.textMain} 1px, transparent 1px)`, backgroundSize: "120px 120px" }}/>

        <div className="relative z-10 w-full px-6 sm:px-10 md:px-16 lg:px-24">
          <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-8 items-center">
            
            <div className="lg:col-span-6 flex flex-col">
              <div className="flex items-center gap-4 mb-6 aos-item aos-delay-1">
                <span className="h-px w-10" style={{ backgroundColor: t.accent }}/>
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border text-xs font-medium" style={{ borderColor: t.border, backgroundColor: `${t.surface}80`, color: t.textMuted }}>
                  <span className="flex h-2 w-2 rounded-full pulse" style={{ backgroundColor: t.accent }}/>
                  Next-Gen Security
                  <ChevronRight className="w-3 h-3"/>
                </div>
              </div>

              <h1 className="text-5xl sm:text-6xl md:text-7xl font-light leading-[0.95] tracking-tight mb-8 aos-item aos-delay-2">
                Security powered <br />
                by <span style={{ color: t.textMuted }}>Intelligence</span>
              </h1>

              <p className="text-sm md:text-lg max-w-md mb-12 leading-relaxed border-l pl-6 aos-item aos-delay-3" style={{ color: t.textMuted, borderColor: t.border }}>
                SentinAI combines DeepWiki-powered code analysis with multi-tier LLM technology to identify vulnerabilities other scanners miss.
              </p>

              <div className="flex flex-wrap gap-5 mb-12 aos-item aos-delay-4">
                <a href="#pricing" className="px-8 py-4 overflow-hidden w-full sm:w-auto text-center text-sm tracking-[0.2em] uppercase font-bold rounded-full transition-all hover:shadow-lg" style={{ backgroundColor: t.accent, color: t.accentText }}>
                  Start Free Trial
                </a>
                <a href="#features" className="px-8 py-4 border overflow-hidden w-full sm:w-auto text-center text-sm tracking-[0.2em] uppercase transition-colors rounded-full" style={{ borderColor: t.border, color: t.textMain }}>
                  View Features
                </a>
              </div>

              
              <div className="flex items-center gap-6 aos-item aos-delay-5">
                <div className="flex -space-x-3">
                  {[1, 2, 3, 4].map((i) => (<div key={i} className="w-9 h-9 rounded-full border-2 overflow-hidden" style={{ borderColor: t.bg, backgroundColor: t.surface }}>
                      <div className="w-full h-full rounded-full opacity-30" style={{ background: `linear-gradient(135deg, ${t.accent}, transparent)` }}/>
                    </div>))}
                </div>
                <div>
                  <div className="flex items-center gap-0.5 mb-1">
                    {[1, 2, 3, 4, 5].map((i) => <Sparkles key={i} className="w-3 h-3 fill-current" style={{ color: t.accent }}/>)}
                  </div>
                  <span className="text-xs font-medium" style={{ color: t.textMuted }}>Trusted by 10,000+ developers</span>
                </div>
              </div>
            </div>

            
            <div className="lg:col-span-6 relative mt-12 lg:mt-0 aos-item aos-delay-5">
              <div className="relative w-full aspect-square max-w-md mx-auto lg:mr-0">
                <div className="absolute inset-0 border overflow-hidden rounded-2xl" style={{ backgroundColor: t.surface, borderColor: t.border }}>
                  <div className="absolute inset-0 opacity-10" style={{ backgroundImage: `radial-gradient(${t.textMain} 1px, transparent 1px)`, backgroundSize: "20px 20px" }}/>
                  <div className="absolute top-1/4 left-1/4 w-1/2 h-1/2 border rounded-full spin-slow" style={{ borderColor: t.border }}/>
                  <div className="absolute top-1/3 left-1/3 w-1/3 h-1/3 border rounded-full" style={{ borderColor: `${t.accent}40` }}/>
                  <div className="absolute inset-0 opacity-5" style={{ background: `radial-gradient(circle at 60% 40%, ${t.accent}, transparent 60%)` }}/>
                </div>
                <div className="absolute -top-6 -left-4 md:-top-8 md:-left-12 p-5 shadow-2xl border w-48 md:w-56 rounded-xl" style={{ backgroundColor: t.surface, borderColor: t.border }}>
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-2 h-2 bg-emerald-500 rounded-full pulse"/>
                    <p className="text-[10px] uppercase tracking-widest" style={{ color: t.textMuted }}>System Status</p>
                  </div>
                  <p className="text-2xl font-light" style={{ color: t.textMain }}>Secure</p>
                  <div className="mt-3 h-1 w-full rounded-full overflow-hidden" style={{ backgroundColor: t.border }}>
                    <div className="h-full w-full bg-emerald-500 rounded-full"/>
                  </div>
                </div>
                <div className="absolute -bottom-8 -right-2 md:-bottom-10 md:-right-12 p-6 shadow-2xl w-60 rounded-xl border" style={{ backgroundColor: t.bg, borderColor: t.border }}>
                  <div className="flex justify-between items-start mb-4">
                    <Shield className="w-5 h-5" style={{ color: t.accent }} strokeWidth={1.5}/>
                    <span className="text-xs" style={{ color: t.textMuted }}>V.2.0</span>
                  </div>
                  <p className="text-[10px] uppercase tracking-widest mb-1" style={{ color: t.textMuted }}>Vulnerabilities</p>
                  <p className="text-3xl font-light" style={{ color: t.textMain }}>0 Critical</p>
                  <p className="text-xs mt-2" style={{ color: t.textMuted }}>Last scan: 2 mins ago</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      
      <section className="py-6 border-y overflow-hidden" style={{ backgroundColor: t.surface, borderColor: t.border }}>
        <div className="marquee-track" style={{ opacity: 0.4 }}>
          {[...partners, ...partners].map((p, i) => (<div key={i} className="flex items-center mx-8">
              <span className="text-lg tracking-[0.2em] uppercase font-light whitespace-nowrap" style={{ color: t.textMain }}>{p} •</span>
            </div>))}
        </div>
      </section>

      
      <section id="features" className="py-24 md:py-32 px-6 sm:px-10 md:px-16">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row justify-between items-end mb-12 pb-8 border-b" style={{ borderColor: t.border }}>
            <div>
              <span className="text-xs tracking-[0.35em] uppercase aos-item" style={{ color: t.textMuted }}>Capabilities</span>
              <h2 className="text-3xl md:text-5xl font-light mt-3 aos-item aos-delay-1">
                Technical <span style={{ color: t.textMuted }}>Mastery</span>
              </h2>
            </div>
            <button className="hidden md:flex items-center gap-2 text-sm font-medium transition-colors hover:opacity-80 aos-item" style={{ color: t.accent }}>
              View all features <ArrowRight className="w-4 h-4"/>
            </button>
          </div>

          
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4" style={{ gridAutoRows: "280px" }}>
            
            <div className="col-span-1 md:col-span-2 relative group overflow-hidden rounded-3xl border aos-item" style={{ backgroundColor: t.surface, borderColor: t.border }}>
              <div className="absolute inset-0 opacity-5" style={{ background: `linear-gradient(to bottom right, ${t.accent}, transparent)` }}/>
              <div className="relative z-10 p-8 h-full flex flex-col justify-between">
                <div className="w-12 h-12 rounded-2xl border flex items-center justify-center" style={{ backgroundColor: t.bg, borderColor: t.border }}>
                  <Globe className="w-6 h-6" style={{ color: t.accent }}/>
                </div>
                <div>
                  <h3 className="text-xl font-medium mb-2">Project Agnostic</h3>
                  <p className="text-sm max-w-sm" style={{ color: t.textMuted }}>Works with React, Vue, Node, Python, and Go. Our engine auto-detects your stack.</p>
                </div>
              </div>
            </div>

            
            <div className="col-span-1 relative group overflow-hidden rounded-3xl border aos-item aos-delay-1" style={{ backgroundColor: t.surface, borderColor: t.border, gridRow: "span 2" }}>
              <div className="relative z-10 p-8 h-full flex flex-col">
                <div className="w-12 h-12 rounded-2xl border flex items-center justify-center mb-auto" style={{ backgroundColor: t.bg, borderColor: t.border }}>
                  <Zap className="w-6 h-6" style={{ color: t.accent }}/>
                </div>
                <div className="my-8 space-y-2 opacity-50 group-hover:opacity-100 transition-opacity duration-500">
                  <div className="h-2 w-full rounded-full overflow-hidden" style={{ backgroundColor: t.bg }}>
                    <div className="h-full w-2/3 rounded-full" style={{ backgroundColor: t.accent }}/>
                  </div>
                  <div className="flex justify-between text-[10px] font-mono" style={{ color: t.textMuted }}>
                    <span>SCANNING</span><span>64ms</span>
                  </div>
                  <div className="p-3 rounded-lg border font-mono text-[10px]" style={{ backgroundColor: t.bg, borderColor: t.border, color: t.textMuted }}>
                    <span className="text-green-500">&gt;</span> No leaks detected
                  </div>
                </div>
                <div>
                  <h3 className="text-xl font-medium mb-2">Realtime Analysis</h3>
                  <p className="text-sm" style={{ color: t.textMuted }}>Powered by a custom Rust engine, scans complete in milliseconds.</p>
                </div>
              </div>
            </div>

            
            {[
            { icon: Lock, title: "Enterprise Ready", desc: "SSO, Audit Logs, and dedicated support channels included." },
            { icon: Terminal, title: "CLI First", desc: "Prefer the terminal? npx sentinel scan" },
            { icon: Github, title: "GitHub Bot", desc: "Automatically comments on PRs with security suggestions." },
        ].map(({ icon: Icon, title, desc }, i) => (<div key={title} className={`col-span-1 relative group overflow-hidden rounded-3xl border aos-item aos-delay-${i + 2}`} style={{ backgroundColor: t.surface, borderColor: t.border }}>
                <div className="relative z-10 p-8 h-full flex flex-col justify-between">
                  <div className="w-12 h-12 rounded-2xl border flex items-center justify-center" style={{ backgroundColor: t.bg, borderColor: t.border }}>
                    <Icon className="w-6 h-6" style={{ color: t.accent }}/>
                  </div>
                  <div>
                    <h3 className="text-xl font-medium mb-2">{title}</h3>
                    <p className="text-sm" style={{ color: t.textMuted }}>{desc}</p>
                  </div>
                </div>
              </div>))}
          </div>

          
          <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-px border" style={{ backgroundColor: t.border, borderColor: t.border }}>
            {features.map((feature, index) => (<div key={feature.title} className="group relative p-8 md:p-10 h-[260px] flex flex-col justify-between aos-item" style={{ backgroundColor: t.surface, transitionDelay: `${index * 60}ms` }}>
                <div>
                  <div className="flex justify-between items-start mb-5">
                    <span className="font-mono text-xs" style={{ color: t.border }}>0{index + 1}</span>
                    <feature.icon className="w-5 h-5" style={{ color: t.textMuted }}/>
                  </div>
                  <h3 className="text-lg font-medium mb-2">{feature.title}</h3>
                  <p className="text-sm leading-relaxed" style={{ color: t.textMuted }}>{feature.description}</p>
                </div>
                <div className="w-8 h-8 rounded-full border flex items-center justify-center transition-all duration-300 group-hover:scale-110" style={{ borderColor: t.border, color: t.textMuted }}>
                  <ArrowRight className="w-3 h-3"/>
                </div>
              </div>))}
          </div>
        </div>
      </section>

      
      <section id="about" className="py-24 md:py-32 px-6 sm:px-10 md:px-16 border-t" style={{ borderColor: t.border }}>
        <div className="max-w-4xl mx-auto text-center aos-item">
          <span className="text-xs tracking-[0.35em] uppercase block mb-8" style={{ color: t.textMuted }}>Core Philosophy</span>
          <blockquote>
            <p className="text-2xl sm:text-3xl md:text-5xl font-light leading-[1.3]">
              &ldquo;We believe that true security is invisible. It is not a barrier, but a{" "}
              <span style={{ color: t.textMuted }}>foundation</span> upon which great things are built.&rdquo;
            </p>
            <div className="mt-8 flex justify-center">
              <div className="h-px w-12" style={{ backgroundColor: t.border }}/>
            </div>
          </blockquote>
        </div>
      </section>

      
      <section id="pricing" className="py-24 md:py-32 px-6 sm:px-10 md:px-16 border-t" style={{ borderColor: t.border }}>
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col items-center text-center mb-16">
            <span className="text-xs tracking-[0.35em] uppercase mb-4 aos-item" style={{ color: t.textMuted }}>Investment</span>
            <h2 className="text-3xl md:text-5xl font-light tracking-tight mb-6 aos-item aos-delay-1">
              Transparent <span style={{ color: t.textMuted }}>Pricing</span>
            </h2>
            <div className="flex items-center gap-4 mt-4 aos-item aos-delay-2">
              <span className={`text-sm font-medium transition-opacity ${!isAnnual ? "opacity-100" : "opacity-40"}`}>Monthly</span>
              <button onClick={() => setIsAnnual(!isAnnual)} className="w-14 h-7 rounded-full p-1 transition-colors duration-300" style={{ backgroundColor: isAnnual ? t.accent : t.border }}>
                <div className={`w-5 h-5 rounded-full shadow-lg transform transition-transform duration-300 ${isAnnual ? "translate-x-7" : "translate-x-0"}`} style={{ backgroundColor: t.bg }}/>
              </button>
              <span className={`text-sm font-medium transition-opacity ${isAnnual ? "opacity-100" : "opacity-40"}`}>
                Yearly{" "}
                <span className="ml-1 text-[10px] px-2 py-0.5 rounded-full border" style={{ color: t.accent, borderColor: `${t.accent}40`, backgroundColor: `${t.accent}10` }}>
                  SAVE 20%
                </span>
              </span>
            </div>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {plans.map((plan, i) => (<div key={plan.name} className="relative flex flex-col p-8 rounded-3xl border transition-all duration-500 aos-item" style={{
                backgroundColor: t.surface,
                borderColor: plan.highlight ? t.accent : t.border,
                boxShadow: plan.highlight ? `0 0 50px -10px ${t.accent}30` : "none",
                marginTop: plan.highlight ? "-1.5rem" : "0",
                marginBottom: plan.highlight ? "1.5rem" : "0",
                transitionDelay: `${i * 100}ms`,
            }}>
                {plan.highlight && (<div className="absolute -top-4 left-1/2 -translate-x-1/2 text-xs font-bold px-3 py-1 rounded-full shadow-lg flex items-center gap-1" style={{ backgroundColor: t.accent, color: t.accentText }}>
                    <Sparkles className="w-3 h-3"/> MOST POPULAR
                  </div>)}
                <div className="mb-6">
                  <h3 className="text-xl font-medium mb-1">{plan.name}</h3>
                  <p className="text-sm" style={{ color: t.textMuted }}>{plan.description}</p>
                </div>
                <div className="mb-6 pb-6 border-b" style={{ borderColor: t.border }}>
                  <span className="text-4xl font-light">${plan.price}</span>
                  <span className="text-sm ml-2" style={{ color: t.textMuted }}>/mo</span>
                  {isAnnual && plan.price > 0 && (<p className="text-xs mt-1" style={{ color: t.textMuted }}>Billed ${plan.price * 12} yearly</p>)}
                </div>
                <ul className="space-y-3 mb-8 grow">
                  {plan.features.map((f) => (<li key={f} className="flex items-start gap-3 text-sm" style={{ color: t.textMuted }}>
                      <Check className="w-4 h-4 mt-0.5 shrink-0" style={{ color: plan.highlight ? t.accent : t.textMuted }}/>
                      {f}
                    </li>))}
                </ul>
                <button className="w-full py-3 rounded-xl font-medium text-sm transition-all duration-300 border" style={{
                backgroundColor: plan.highlight ? t.accent : "transparent",
                color: plan.highlight ? t.accentText : t.textMain,
                borderColor: plan.highlight ? "transparent" : t.border,
            }}>
                  {plan.cta}
                </button>
              </div>))}
          </div>
        </div>
      </section>

      
      <section className="py-24 border-t px-6 sm:px-10 md:px-16" style={{ borderColor: t.border }}>
        <div className="max-w-3xl mx-auto">
          <h2 className="text-3xl font-light text-center mb-12 aos-item">Frequently Asked Questions</h2>
          <div className="space-y-3">
            {faqs.map((faq, index) => (<div key={index} className="border rounded-2xl overflow-hidden aos-item" style={{ backgroundColor: t.surface, borderColor: t.border, transitionDelay: `${index * 50}ms` }}>
                <button onClick={() => setOpenFaq(openFaq === index ? null : index)} className="w-full p-6 flex items-center justify-between text-left">
                  <span className="font-medium">{faq.q}</span>
                  {openFaq === index
                ? <Minus className="w-4 h-4 shrink-0" style={{ color: t.textMuted }}/>
                : <ChevronDown className="w-4 h-4 shrink-0" style={{ color: t.textMuted }}/>}
                </button>
                <div className={`px-6 text-sm leading-relaxed overflow-hidden transition-all duration-300 ${openFaq === index ? "max-h-40 pb-6 opacity-100" : "max-h-0 opacity-0"}`} style={{ color: t.textMuted }}>
                  {faq.a}
                </div>
              </div>))}
          </div>
          <div className="mt-10 text-center">
            <p className="text-sm" style={{ color: t.textMuted }}>
              Still have questions?{" "}
              <a href="#" className="underline underline-offset-4 hover:opacity-80" style={{ color: t.accent }}>
                Chat with our security engineers
              </a>
            </p>
          </div>
        </div>
      </section>

      
      <section className="relative py-12 md:py-16 overflow-hidden border-t" style={{ borderColor: t.border, backgroundColor: isDark ? t.surface : "#18181b" }}>
        <div className="absolute inset-0 opacity-10" style={{ backgroundImage: `linear-gradient(${isDark ? t.border : "#333"} 1px, transparent 1px), linear-gradient(90deg, ${isDark ? t.border : "#333"} 1px, transparent 1px)`, backgroundSize: "40px 40px" }}/>
        <div className="relative z-10 max-w-4xl mx-auto px-6 md:px-8 text-center philosophy-block">
          <div className="p-rect" style={{ border: `1px solid ${isDark ? t.border : "#52525b"}` }}/>
          <div className="relative z-20 py-16 md:py-20 px-4 md:px-8">
            <span className="text-xs tracking-[0.35em] uppercase block p-label" style={{ color: isDark ? t.textMuted : "#71717a" }}>
              Initiate Protocol
            </span>
            <h2 className="mt-6 mb-8 text-3xl sm:text-4xl md:text-5xl font-light leading-[1.2] p-quote" style={{ color: isDark ? t.textMain : "#f4f4f5" }}>
              Ready to <span style={{ color: isDark ? t.textMuted : "#71717a" }}>Secure</span> Your Future?
            </h2>
            <div className="flex flex-col items-center w-full p-quote">
              <div className="flex flex-col sm:flex-row justify-center gap-5">
                <a href="#pricing" className="px-10 py-4 text-sm tracking-[0.2em] uppercase font-bold rounded-full transition-colors" style={{ backgroundColor: t.accent, color: t.accentText }}>
                  Get Started
                </a>
                <a href="#" className="px-8 py-4 border text-sm tracking-[0.2em] uppercase rounded-full transition-colors" style={{ borderColor: isDark ? t.border : "#52525b", color: isDark ? t.textMuted : "#a1a1aa" }}>
                  Contact Sales
                </a>
              </div>
              <div className="w-full flex flex-col items-center mt-16 md:mt-12">
                <div className="p-hr w-full" style={{ backgroundColor: isDark ? t.border : "#52525b" }}/>
                <div>
                  <div className="p-vline" style={{ backgroundColor: isDark ? t.border : "#52525b" }}/>
                  <p className="text-xs tracking-[0.25em] p-est mt-4" style={{ color: isDark ? t.textMuted : "#71717a" }}>
                    SECURE // 2024
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      
      <footer className="py-12 px-6 md:px-16 border-t" style={{ backgroundColor: "#000000", borderColor: "#27272a" }}>
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row justify-between items-start gap-12 mb-12">
            <div className="max-w-xs">
              <div className="flex items-center gap-2 font-bold text-xl tracking-tight mb-4 text-white">
                <img src="/logo.svg" alt="" className="w-5 h-5 rounded object-contain shrink-0" aria-hidden/>
                SENTINAI<span className="text-zinc-500">.AI</span>
              </div>
              <p className="text-sm leading-relaxed text-zinc-500">The next generation of static code analysis. Built for speed, accuracy, and developer happiness.</p>
            </div>
            <div className="flex gap-16 flex-wrap">
              {[
            { label: "Product", links: ["Features", "Integrations", "Pricing", "Changelog"] },
            { label: "Company", links: ["About", "Blog", "Careers"] },
            { label: "Legal", links: ["Privacy", "Terms"] },
        ].map(({ label, links }) => (<div key={label} className="flex flex-col gap-3">
                  <span className="font-medium text-white text-sm">{label}</span>
                  {links.map((l) => <a key={l} href="#" className="text-sm text-zinc-500 hover:text-white transition-colors">{l}</a>)}
                </div>))}
            </div>
          </div>
          <div className="flex flex-col md:flex-row justify-between items-center pt-8 border-t border-zinc-800 gap-4">
            <span className="text-xs text-zinc-500">© 2024 SentinAI. All rights reserved.</span>
            <div className="flex gap-6">
              <Github className="w-5 h-5 text-zinc-500 hover:text-white cursor-pointer transition-colors"/>
              <div className="w-5 h-5 text-zinc-500 hover:text-white cursor-pointer transition-colors">
                <svg viewBox="0 0 24 24" fill="currentColor" className="w-full h-full">
                  <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
                </svg>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>);
}
