const MIXPANEL_TOKEN = 'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6';
const GA_MEASUREMENT_ID = 'G-XKQP92MFVT';

export function trackEvent(name, props = {}) {
  if (typeof window === 'undefined') return;
  try {
    if (window.mixpanel) window.mixpanel.track(name, props);
    if (window.gtag) window.gtag('event', name, props);
  } catch (e) {
    console.warn('Analytics track failed', e);
  }
}

export function identify(userId, traits = {}) {
  if (typeof window === 'undefined') return;
  try {
    if (window.mixpanel) window.mixpanel.identify(userId);
    if (window.gtag) window.gtag('set', { user_id: userId });
  } catch (e) {
    console.warn('Analytics identify failed', e);
  }
}

export { MIXPANEL_TOKEN, GA_MEASUREMENT_ID };
