"use client";
import React, { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '@/app/hooks/useAuth';
import { Mail, Lock, ArrowRight, Github, Loader2, User, Moon, Sun, Shield, Zap, CheckCircle } from 'lucide-react';
export default function LoginPage() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const { isAuthenticated, loading, error: authError, login, register, googleLogin } = useAuth();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [name, setName] = useState('');
    const [isRegistering, setIsRegistering] = useState(false);
    const [localError, setLocalError] = useState('');
    const [submitting, setSubmitting] = useState(false);
    const [theme, setTheme] = useState<'dark' | 'light'>('dark');
    const [agreed, setAgreed] = useState(false);
    const [showPassword, setShowPassword] = useState(false);
    const displayError = localError || authError || '';
    useEffect(() => {
        if (!loading && isAuthenticated) {
            const redirect = searchParams.get('redirect') || '/dashboard';
            router.replace(redirect);
        }
    }, [loading, isAuthenticated, router, searchParams]);
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLocalError('');
        setSubmitting(true);
        try {
            const success = isRegistering
                ? await register(email, password, name)
                : await login(email, password);
            if (success) {
                const redirect = searchParams.get('redirect') || '/dashboard';
                router.push(redirect);
            }
        }
        catch {
            setLocalError('Network error. Please try again.');
        }
        finally {
            setSubmitting(false);
        }
    };
    if (loading) {
        return (<div className={`min-h-screen flex items-center justify-center ${theme === 'dark' ? 'bg-zinc-950' : 'bg-zinc-50'}`}>
        <div className="flex flex-col items-center gap-3">
          <Loader2 className={`w-5 h-5 animate-spin ${theme === 'dark' ? 'text-zinc-500' : 'text-zinc-400'}`}/>
          <p className={`text-[10px] uppercase tracking-widest ${theme === 'dark' ? 'text-zinc-600' : 'text-zinc-400'}`}>Authenticating</p>
        </div>
      </div>);
    }
    if (isAuthenticated)
        return null;
    return (<div className={`min-h-screen w-full flex items-center justify-center p-4 relative overflow-hidden transition-colors duration-500 ${theme === 'dark' ? 'bg-zinc-950' : 'bg-zinc-50'}`}>

      
      <button onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')} className={`absolute top-6 right-6 p-2 rounded-full transition-all z-10 ${theme === 'dark'
            ? 'bg-zinc-900 text-zinc-400 hover:text-white border border-zinc-800'
            : 'bg-white text-zinc-600 hover:text-zinc-900 border border-zinc-200 shadow-sm'}`}>
        {theme === 'dark' ? <Sun className="w-4 h-4"/> : <Moon className="w-4 h-4"/>}
      </button>

      
      <div className="absolute inset-0 opacity-20 pointer-events-none" style={{
            backgroundImage: `linear-gradient(${theme === 'dark' ? '#333' : '#cbd5e1'} 1px, transparent 1px), linear-gradient(90deg, ${theme === 'dark' ? '#333' : '#cbd5e1'} 1px, transparent 1px)`,
            backgroundSize: '40px 40px',
        }}/>

      
      <div className={`absolute top-1/4 left-1/4 w-64 h-64 rounded-full blur-3xl opacity-10 pointer-events-none transition-colors duration-500 ${theme === 'dark' ? 'bg-violet-500' : 'bg-blue-300'}`}/>
      <div className={`absolute bottom-1/4 right-1/4 w-64 h-64 rounded-full blur-3xl opacity-10 pointer-events-none transition-colors duration-500 ${theme === 'dark' ? 'bg-blue-500' : 'bg-violet-300'}`}/>

      
      <div className="relative z-10 w-full max-w-4xl mx-auto flex flex-col lg:flex-row items-center gap-8 lg:gap-16">
        <BrandingPanel theme={theme}/>
        <AuthForm theme={theme} email={email} setEmail={setEmail} password={password} setPassword={setPassword} name={name} setName={setName} isRegistering={isRegistering} setIsRegistering={(v) => { setIsRegistering(v); setLocalError(''); }} submitting={submitting} displayError={displayError} agreed={agreed} setAgreed={setAgreed} showPassword={showPassword} setShowPassword={setShowPassword} handleSubmit={handleSubmit} googleLogin={googleLogin}/>
      </div>
    </div>);
}
function BrandingPanel({ theme }: {
    theme: 'dark' | 'light';
}) {
    const isDark = theme === 'dark';
    const features = [
        { icon: Shield, label: 'Deep Code Analysis', desc: 'AI-powered scanning with DeepWiki for full codebase context' },
        { icon: Zap, label: 'Multi-Tier AI', desc: 'Tiered OpenRouter models: fast triage (CHEAP_MODEL) then deep analysis (SMART_MODEL)' },
        { icon: Lock, label: 'Fewer False Positives', desc: 'Confidence scoring and LLM filtering so you focus on real issues' },
    ];
    return (<div className="flex-1 flex flex-col gap-6 px-4 lg:px-0 max-w-sm mx-auto lg:mx-0">
      
      <a href="/" className="flex items-center gap-2 w-fit group">
        <img src="/logo.svg" alt="" className="w-8 h-8 rounded-sm object-contain shrink-0" aria-hidden/>
        <span className={`text-sm font-bold tracking-[0.2em] uppercase ${isDark ? 'text-zinc-100' : 'text-zinc-900'}`}>SentinAI</span>
      </a>
      
      <div>
        <h1 className={`text-3xl font-bold leading-tight tracking-tight ${isDark ? 'text-zinc-100' : 'text-zinc-900'}`}>
          Security powered<br />
          <span className={isDark ? 'text-zinc-500' : 'text-zinc-400'}>by Intelligence.</span>
        </h1>
        <p className={`mt-3 text-xs leading-relaxed ${isDark ? 'text-zinc-500' : 'text-zinc-500'}`}>
          Sign in to run AI-powered SAST scans, get actionable vulnerability reports, and optional PoC generation. Built for developers who ship secure code.
        </p>
      </div>
      
      <div className="flex flex-col gap-4">
        {features.map(({ icon: Icon, label, desc }) => (<div key={label} className="flex items-start gap-3">
            <div className={`mt-0.5 p-1.5 border rounded-sm shrink-0 ${isDark ? 'border-zinc-800 bg-zinc-900/60' : 'border-zinc-200 bg-white shadow-sm'}`}>
              <Icon className={`w-3.5 h-3.5 ${isDark ? 'text-zinc-400' : 'text-zinc-600'}`} strokeWidth={1.5}/>
            </div>
            <div>
              <p className={`text-[11px] font-semibold uppercase tracking-wider ${isDark ? 'text-zinc-300' : 'text-zinc-700'}`}>{label}</p>
              <p className={`text-[10px] mt-0.5 ${isDark ? 'text-zinc-600' : 'text-zinc-400'}`}>{desc}</p>
            </div>
          </div>))}
      </div>
      
      <div className={`border-t pt-4 ${isDark ? 'border-zinc-800' : 'border-zinc-200'}`}>
        <div className="flex items-center gap-2 mb-2">
          <div className="flex -space-x-2">
            {['#6366f1', '#8b5cf6', '#22d3ee', '#34d399'].map((color, i) => (<div key={i} className={`w-6 h-6 rounded-full border-2 flex items-center justify-center text-[8px] font-bold text-white ${isDark ? 'border-zinc-950' : 'border-zinc-50'}`} style={{ backgroundColor: color }}>
                {['A', 'B', 'C', 'D'][i]}
              </div>))}
          </div>
          <div className="flex items-center gap-1">
            {[...Array(5)].map((_, i) => (<svg key={i} className="w-2.5 h-2.5 fill-amber-400" viewBox="0 0 20 20">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
              </svg>))}
          </div>
        </div>
        <p className={`text-[10px] italic ${isDark ? 'text-zinc-600' : 'text-zinc-400'}`}>
          "SentinAI caught a SQLi our old scanner missed. The PoC script made remediation a no-brainer."
        </p>
        <p className={`text-[9px] mt-1 uppercase tracking-wider ${isDark ? 'text-zinc-700' : 'text-zinc-400'}`}>— Dev team, security-first startup</p>
      </div>
    </div>);
}
type AuthFormProps = {
    theme: 'dark' | 'light';
    email: string;
    setEmail: (v: string) => void;
    password: string;
    setPassword: (v: string) => void;
    name: string;
    setName: (v: string) => void;
    isRegistering: boolean;
    setIsRegistering: (v: boolean) => void;
    submitting: boolean;
    displayError: string;
    agreed: boolean;
    setAgreed: (v: boolean) => void;
    showPassword: boolean;
    setShowPassword: (v: boolean) => void;
    handleSubmit: (e: React.FormEvent) => void;
    googleLogin: () => void;
};
function AuthForm({ theme, email, setEmail, password, setPassword, name, setName, isRegistering, setIsRegistering, submitting, displayError, agreed, setAgreed, showPassword, setShowPassword, handleSubmit, googleLogin, }: AuthFormProps) {
    const [isVisible, setIsVisible] = useState(false);
    useEffect(() => {
        setIsVisible(false);
        const t = setTimeout(() => setIsVisible(true), 100);
        return () => clearTimeout(t);
    }, [theme]);
    const strength = [
        password.length >= 8,
        /[A-Z]/.test(password),
        /[0-9]/.test(password),
        /[^A-Za-z0-9]/.test(password),
    ].filter(Boolean).length;
    const strengthColors = ['bg-red-500', 'bg-orange-400', 'bg-yellow-400', 'bg-green-500'];
    const strengthLabels = ['Weak', 'Fair', 'Good', 'Strong'];
    const strengthTextColors = ['text-red-500', 'text-orange-400', 'text-yellow-400', 'text-green-500'];
    const isDark = theme === 'dark';
    const s = {
        lineColor: isDark ? '#52525b' : '#d4d4d8',
        glassBg: isDark ? 'rgba(9, 9, 11, 0.9)' : 'rgba(255, 255, 255, 0.85)',
        glassBorder: isDark ? '#3f3f46' : '#e4e4e7',
        text: isDark ? 'text-zinc-200' : 'text-zinc-900',
        subText: isDark ? 'text-zinc-500' : 'text-zinc-400',
        inputBg: isDark ? 'bg-zinc-900/50' : 'bg-zinc-50',
        inputBorder: isDark ? 'border-zinc-800' : 'border-zinc-200',
        inputFocus: isDark ? 'focus:border-zinc-500 focus:bg-zinc-900' : 'focus:border-zinc-400 focus:bg-white',
        inputPh: isDark ? 'placeholder:text-zinc-700' : 'placeholder:text-zinc-400',
        icon: isDark ? 'text-zinc-600 group-focus-within:text-zinc-300' : 'text-zinc-400 group-focus-within:text-zinc-800',
        divider: isDark ? 'border-zinc-800' : 'border-zinc-200',
        socialBtn: isDark
            ? 'bg-zinc-900 border-zinc-800 hover:bg-zinc-800 hover:border-zinc-600 text-zinc-300'
            : 'bg-white border-zinc-200 hover:bg-zinc-50 hover:border-zinc-300 text-zinc-600 shadow-sm',
        primaryBtn: isDark
            ? 'bg-zinc-100 text-zinc-950 hover:bg-white hover:shadow-[0_0_20px_rgba(255,255,255,0.1)]'
            : 'bg-zinc-900 text-white hover:bg-black hover:shadow-lg',
        linkText: isDark ? 'text-zinc-300 hover:text-white' : 'text-zinc-900 hover:text-black',
    };
    return (<div className={`relative w-full max-w-[360px] mx-auto philosophy-block ${isVisible ? 'visible' : ''}`}>
      <style>{`
        .philosophy-block { opacity:0; transform:scale(0.98); transition:opacity .5s ease,transform .5s ease; }
        .philosophy-block.visible { opacity:1; transform:scale(1); }
        .anim-hr { height:1px; width:0; margin:0 auto; background:${s.lineColor}; transition:width .8s cubic-bezier(.16,1,.3,1) .2s; }
        .philosophy-block.visible .anim-hr { width:100%; }
        .anim-line { height:0; width:1px; margin:0 auto; background:${s.lineColor}; transition:height .6s cubic-bezier(.16,1,.3,1) .8s; }
        .philosophy-block.visible .anim-line { height:20px; }
        .anim-rect {
          position:absolute; inset:0;
          border:1px solid ${s.glassBorder};
          background:${s.glassBg};
          backdrop-filter:blur(12px);
          clip-path:inset(0 0 100% 0);
          transition:clip-path 1s cubic-bezier(.16,1,.3,1) 1.2s;
          z-index:-1;
          box-shadow:${isDark ? '0 0 40px rgba(0,0,0,0.6)' : '0 10px 40px -10px rgba(0,0,0,0.08)'};
        }
        .philosophy-block.visible .anim-rect { clip-path:inset(0 0 0 0); }
        .anim-content { opacity:0; transform:translateY(10px); transition:opacity .6s ease 2s,transform .6s ease 2s; }
        .philosophy-block.visible .anim-content { opacity:1; transform:translateY(0); }
      `}</style>

      <div className="anim-rect"/>

      
      {['-top-px -left-px border-t border-l', '-top-px -right-px border-t border-r', '-bottom-px -left-px border-b border-l', '-bottom-px -right-px border-b border-r'].map((p, i) => (<div key={i} className={`absolute ${p} w-2 h-2 transition-opacity duration-500 delay-[2200ms] ${isDark ? 'border-zinc-400' : 'border-zinc-900'}`} style={{ opacity: isVisible ? 1 : 0 }}/>))}

      <div className="px-6 py-8">
        
        <div className="flex flex-col items-center mb-6">
          <div className="w-full">
            <div className="anim-hr"/>
            <div className="anim-line"/>
          </div>
        </div>

        <div className="anim-content">
          
          <div className="mb-5">
            <h2 className={`text-base font-bold tracking-tight ${isDark ? 'text-zinc-100' : 'text-zinc-900'}`}>
              {isRegistering ? 'Create your account' : 'Welcome back'}
            </h2>
            <p className={`text-[10px] mt-0.5 ${isDark ? 'text-zinc-600' : 'text-zinc-400'}`}>
              {isRegistering ? 'Create your SentinAI account. Start with a free scan—no credit card required.' : 'Sign in to access your dashboard and run security scans.'}
            </p>
          </div>

          
          {displayError && (<div className={`mb-4 px-3 py-2 border text-[10px] leading-relaxed ${isDark
                ? 'bg-red-950/40 border-red-800/60 text-red-400'
                : 'bg-red-50 border-red-200 text-red-600'}`}>
              {displayError}
            </div>)}

          <form onSubmit={handleSubmit} className="space-y-3">
            
            <div className={`grid transition-[grid-template-rows] duration-500 ease-[cubic-bezier(.16,1,.3,1)] ${isRegistering ? 'grid-rows-[1fr]' : 'grid-rows-[0fr]'}`}>
              <div className="overflow-hidden">
                <div className="pb-3">
                  <div className="relative group">
                    <User className={`absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 transition-colors ${s.icon}`}/>
                    <input type="text" value={name} onChange={e => setName(e.target.value)} autoComplete="name" tabIndex={isRegistering ? 0 : -1} placeholder="Full Name" className={`w-full ${s.inputBg} border ${s.inputBorder} ${s.text} text-xs py-2.5 pl-9 pr-4 focus:outline-none ${s.inputFocus} transition-all ${s.inputPh}`}/>
                  </div>
                </div>
              </div>
            </div>

            
            <div className="relative group">
              <Mail className={`absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 transition-colors ${s.icon}`}/>
              <input type="email" value={email} onChange={e => setEmail(e.target.value)} required autoComplete="email" placeholder="Email Address" className={`w-full ${s.inputBg} border ${s.inputBorder} ${s.text} text-xs py-2.5 pl-9 pr-4 focus:outline-none ${s.inputFocus} transition-all ${s.inputPh}`}/>
            </div>

            
            <div className="space-y-1.5">
              <div className="relative group">
                <Lock className={`absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 transition-colors ${s.icon}`}/>
                <input type={showPassword ? 'text' : 'password'} value={password} onChange={e => setPassword(e.target.value)} required minLength={6} autoComplete={isRegistering ? 'new-password' : 'current-password'} placeholder="Password" className={`w-full ${s.inputBg} border ${s.inputBorder} ${s.text} text-xs py-2.5 pl-9 pr-10 focus:outline-none ${s.inputFocus} transition-all ${s.inputPh}`}/>
                <button type="button" onClick={() => setShowPassword(!showPassword)} className={`absolute right-3 top-1/2 -translate-y-1/2 text-[9px] uppercase tracking-wider transition-colors ${isDark ? 'text-zinc-600 hover:text-zinc-400' : 'text-zinc-400 hover:text-zinc-700'}`}>
                  {showPassword ? 'Hide' : 'Show'}
                </button>
              </div>

              
              <div className={`grid transition-[grid-template-rows] duration-300 ${isRegistering && password.length > 0 ? 'grid-rows-[1fr]' : 'grid-rows-[0fr]'}`}>
                <div className="overflow-hidden">
                  <div className="pt-1 pb-0.5">
                    <div className="flex gap-1 mb-1">
                      {[...Array(4)].map((_, i) => (<div key={i} className={`h-0.5 flex-1 rounded-full transition-all duration-300 ${i < strength ? strengthColors[strength - 1] : isDark ? 'bg-zinc-800' : 'bg-zinc-200'}`}/>))}
                    </div>
                    <p className={`text-[9px] ${isDark ? 'text-zinc-600' : 'text-zinc-400'}`}>
                      Strength:{' '}
                      <span className={`font-semibold ${strength > 0 ? strengthTextColors[strength - 1] : ''}`}>
                        {strength > 0 ? strengthLabels[strength - 1] : '—'}
                      </span>
                    </p>
                  </div>
                </div>
              </div>

              
              <div className={`grid transition-[grid-template-rows] duration-300 ${!isRegistering ? 'grid-rows-[1fr]' : 'grid-rows-[0fr]'}`}>
                <div className="overflow-hidden flex justify-end pt-0.5">
                  <a href="#" className={`text-[9px] uppercase tracking-wider transition-colors ${isDark ? 'text-zinc-600 hover:text-zinc-400' : 'text-zinc-500 hover:text-zinc-800'}`}>
                    Forgot password?
                  </a>
                </div>
              </div>
            </div>

            
            <div className={`grid transition-[grid-template-rows] duration-500 ${isRegistering ? 'grid-rows-[1fr]' : 'grid-rows-[0fr]'}`}>
              <div className="overflow-hidden">
                <div className="pt-1 pb-1">
                  <label className="flex items-start gap-2 cursor-pointer">
                    <div onClick={() => setAgreed(!agreed)} className={`mt-0.5 w-3.5 h-3.5 flex-shrink-0 border flex items-center justify-center transition-all ${agreed
            ? isDark ? 'bg-zinc-200 border-zinc-200' : 'bg-zinc-900 border-zinc-900'
            : isDark ? 'border-zinc-700 bg-zinc-900/50' : 'border-zinc-300 bg-zinc-50'}`}>
                      {agreed && <CheckCircle className={`w-2.5 h-2.5 ${isDark ? 'text-zinc-900' : 'text-white'}`}/>}
                    </div>
                    <span className={`text-[9px] leading-relaxed ${isDark ? 'text-zinc-600' : 'text-zinc-400'}`}>
                      I agree to the{' '}
                      <a href="#" className={`underline underline-offset-2 ${isDark ? 'text-zinc-400 hover:text-zinc-200' : 'text-zinc-600 hover:text-zinc-900'}`}>Terms of Service</a>
                      {' '}and{' '}
                      <a href="#" className={`underline underline-offset-2 ${isDark ? 'text-zinc-400 hover:text-zinc-200' : 'text-zinc-600 hover:text-zinc-900'}`}>Privacy Policy</a>
                    </span>
                  </label>
                </div>
              </div>
            </div>

            
            <div className="relative flex items-center py-1">
              <div className={`flex-grow border-t ${s.divider}`}/>
              <span className={`flex-shrink-0 mx-2 text-[9px] uppercase tracking-widest ${isDark ? 'text-zinc-600' : 'text-zinc-400'}`}>Or continue with</span>
              <div className={`flex-grow border-t ${s.divider}`}/>
            </div>

            
            <div className="grid grid-cols-2 gap-3">
              <button type="button" onClick={googleLogin} className={`flex items-center justify-center gap-2 py-2 px-4 border transition-all text-[10px] uppercase tracking-wider ${s.socialBtn}`}>
                <svg className="w-3.5 h-3.5" viewBox="0 0 24 24">
                  <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                  <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                  <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                  <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
                </svg>
                <span>Google</span>
              </button>
              <button type="button" className={`flex items-center justify-center gap-2 py-2 px-4 border transition-all text-[10px] uppercase tracking-wider group ${s.socialBtn}`}>
                <Github className={`w-3.5 h-3.5 transition-colors ${isDark ? 'text-zinc-500 group-hover:text-white' : 'text-zinc-400 group-hover:text-zinc-600'}`}/>
                <span>Github</span>
              </button>
            </div>

            
            <button type="submit" disabled={submitting || (isRegistering && !agreed)} className={`w-full py-3 text-[10px] uppercase tracking-[0.2em] font-bold active:scale-[0.99] transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed mt-1 ${s.primaryBtn}`}>
              {submitting
            ? <Loader2 className="w-3.5 h-3.5 animate-spin"/>
            : <>{isRegistering ? 'Create Account' : 'Sign In'} <ArrowRight className="w-3 h-3"/></>}
            </button>
          </form>

          
          <div className="text-center pt-3">
            <p className={`text-[9px] uppercase tracking-wide ${s.subText}`}>
              {isRegistering ? 'Have an account? ' : 'No account? '}
              <button type="button" onClick={() => setIsRegistering(!isRegistering)} className={`font-semibold underline underline-offset-4 transition-colors uppercase ${s.linkText} decoration-zinc-500`}>
                {isRegistering ? 'Sign In' : 'Create one'}
              </button>
            </p>
          </div>

          
          <div className={`mt-5 pt-4 border-t flex items-center justify-center gap-4 ${isDark ? 'border-zinc-800' : 'border-zinc-200'}`}>
            {['OWASP', 'SOC 2', 'NIST'].map(badge => (<div key={badge} className="flex items-center gap-1">
                <Shield className={`w-2.5 h-2.5 ${isDark ? 'text-zinc-700' : 'text-zinc-400'}`}/>
                <span className={`text-[8px] uppercase tracking-widest ${isDark ? 'text-zinc-700' : 'text-zinc-400'}`}>{badge}</span>
              </div>))}
          </div>
        </div>
      </div>
    </div>);
}
