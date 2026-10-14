(() => {
  'use strict';
  const id = 'G-P2LV2GRM83';
  const preferenceKey = 'dn-analytics-consent-v1';
  const production = ['dheerajnamburu.com', 'www.dheerajnamburu.com', 'dheeraj5612.github.io'].includes(location.hostname);
  const notice = document.getElementById('analytics-notice');
  const settings = document.getElementById('privacy-dialog');
  let enabled = false;
  let started = false;
  const emittedDepths = new Set();
  function preference() {
    try { return localStorage.getItem(preferenceKey); } catch { return null; }
  }
  function event(name, parameters = {}) {
    if (enabled && production && typeof window.gtag === 'function') {
      window.gtag('event', name, { ...parameters, transport_type: 'beacon' });
    }
  }
  function start() {
    if (started || !production) return;
    started = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag('consent', 'default', {
      analytics_storage: 'granted', ad_storage: 'denied',
      ad_user_data: 'denied', ad_personalization: 'denied'
    });
    window.gtag('js', new Date());
    let referrer = '';
    try { referrer = new URL(document.referrer).origin; } catch {}
    window.gtag('config', id, {
      allow_google_signals: false,
      allow_ad_personalization_signals: false,
      page_location: location.origin + location.pathname,
      page_referrer: referrer
    });
    const tag = document.createElement('script');
    tag.async = true;
    tag.src = 'https://www.googletagmanager.com/gtag/js?id=' + id;
    document.head.appendChild(tag);
    [15, 30, 60].forEach(seconds => {
      setTimeout(() => event('engaged_reading', { seconds }), seconds * 1000);
    });
  }
  function choose(allowed) {
    enabled = allowed;
    try { localStorage.setItem(preferenceKey, allowed ? 'granted' : 'denied'); } catch {}
    if (notice) notice.hidden = true;
    if (settings?.open) settings.close();
    if (allowed) {
      window['ga-disable-' + id] = false;
      if (started) window.gtag('consent', 'update', { analytics_storage: 'granted' });
      start();
    } else {
      window['ga-disable-' + id] = true;
      if (started) window.gtag('consent', 'update', { analytics_storage: 'denied' });
      document.cookie.split(';').forEach(cookie => {
        const name = cookie.split('=')[0].trim();
        if (name === '_ga' || name.startsWith('_ga_')) {
          ['', '; domain=.' + location.hostname, '; domain=dheerajnamburu.com', '; domain=.dheerajnamburu.com'].forEach(domain => {
            document.cookie = name + '=; max-age=0; path=/' + domain;
          });
        }
      });
    }
  }
  document.querySelectorAll('[data-analytics-choice]').forEach(button => {
    button.addEventListener('click', () => choose(button.dataset.analyticsChoice === 'allow'));
  });
  document.getElementById('privacy-settings')?.addEventListener('click', () => settings?.showModal());
  document.getElementById('privacy-close')?.addEventListener('click', () => settings?.close());
  document.addEventListener('click', e => {
    const link = e.target.closest('a[href]');
    if (!link) return;
    const url = new URL(link.href, location.href);
    if (url.protocol === 'mailto:') event('contact_email_click');
    else if (url.pathname.endsWith('.pdf')) event('resume_download');
    else if (link.dataset.trackGroup === 'utility') event('utility_visit', { site: url.hostname, kind: link.dataset.kind || 'live' });
    else if (link.dataset.trackGroup === 'game') event('game_visit', { site: url.hostname });
    else if (link.dataset.trackGroup === 'utility-directory') event('utilities_directory_click', { placement: link.dataset.placement || 'page' });
    else if (['commandgate.ai', 'fouro.ai', 'apps.apple.com'].includes(url.hostname)) {
      const project = url.hostname === 'commandgate.ai' ? 'CommandGate' : url.hostname === 'fouro.ai' ? 'Fouro Chat' : 'FilmyCam';
      event('project_visit', { project, placement: link.closest('.project-preview') ? 'image' : 'title' });
    } else if (['www.linkedin.com', 'github.com'].includes(url.hostname)) {
      event('social_profile_click', { platform: url.hostname.includes('linkedin') ? 'LinkedIn' : 'GitHub' });
    }
  });
  window.addEventListener('scroll', () => {
    if (!enabled) return;
    const total = document.documentElement.scrollHeight - innerHeight;
    if (total <= 0) return;
    const depth = Math.min(100, Math.round(scrollY / total * 100));
    [25, 50, 75, 100].forEach(percent => {
      if (depth >= percent && !emittedDepths.has(percent)) {
        emittedDepths.add(percent);
        event('reading_depth', { percent });
      }
    });
  }, { passive: true });
  const saved = preference();
  if (saved === 'granted') { enabled = true; start(); }
  if (notice) notice.hidden = saved !== null;
})();
