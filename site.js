(() => {
  const root = document.documentElement;
  const systemDark = window.matchMedia('(prefers-color-scheme: dark)');
  const currentTheme = () => root.dataset.theme || (systemDark.matches ? 'dark' : 'light');
  const button = document.querySelector('.theme-toggle');
  const syncTheme = () => {
    const theme = currentTheme();
    button?.setAttribute('aria-label', `Switch to ${theme === 'dark' ? 'light' : 'dark'} theme`);
    const frame = document.querySelector('iframe.giscus-frame');
    frame?.contentWindow?.postMessage({ giscus: { setConfig: { theme: theme === 'dark' ? 'dark' : 'light' } } }, 'https://giscus.app');
  };
  if (button) {
    button.hidden = false;
    syncTheme();
    button.addEventListener('click', () => {
      root.dataset.theme = currentTheme() === 'dark' ? 'light' : 'dark';
      try { localStorage.setItem('publication-theme', root.dataset.theme); } catch {}
      syncTheme();
    });
    systemDark.addEventListener('change', syncTheme);
    const followCommentTheme = frame => {
      frame.addEventListener('load', syncTheme);
      syncTheme();
    };
    const commentFrame = document.querySelector('iframe.giscus-frame');
    if (commentFrame) followCommentTheme(commentFrame);
    else if (document.querySelector('.giscus')) {
      const observer = new MutationObserver(() => {
        const frame = document.querySelector('iframe.giscus-frame');
        if (frame) { followCommentTheme(frame); observer.disconnect(); }
      });
      observer.observe(document.querySelector('.giscus'), { childList: true, subtree: true });
    }
  }
  const contents = document.querySelector('.contents-panel details');
  if (contents && window.matchMedia('(max-width: 760px)').matches) contents.open = false;
  const headings = [...document.querySelectorAll('.prose h2[id]')];
  const tocLinks = [...document.querySelectorAll('.contents-panel a')];
  if (headings.length && 'IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      const current = entries.filter(entry => entry.isIntersecting).sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)[0];
      if (!current) return;
      for (const link of tocLinks) {
        if (link.hash === `#${current.target.id}`) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      }
    }, { rootMargin: '0px 0px -60% 0px' });
    headings.forEach(heading => observer.observe(heading));
  }
  const copy = document.querySelector('.copy-link');
  if (copy && navigator.clipboard && window.isSecureContext) {
    copy.hidden = false;
    copy.addEventListener('click', async () => {
      const status = document.querySelector('.copy-status');
      try {
        await navigator.clipboard.writeText(document.querySelector('link[rel=canonical]').href);
        status.textContent = 'Link copied';
      } catch { status.textContent = 'Copy the address from your browser.'; }
    });
  }
})();
