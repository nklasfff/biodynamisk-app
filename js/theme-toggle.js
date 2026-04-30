/**
 * Dark Mode Toggle
 * Håndterer tre tilstande: light, dark, system (følger prefers-color-scheme)
 */

(function() {
  const THEME_KEY = 'biodynamisk-theme';
  const THEMES = ['system', 'light', 'dark'];

  // Hent gemt præference eller brug "system" som default
  function getSavedTheme() {
    const saved = localStorage.getItem(THEME_KEY);
    return THEMES.includes(saved) ? saved : 'system';
  }

  // Gem præference
  function saveTheme(theme) {
    localStorage.setItem(THEME_KEY, theme);
  }

  // Anvend theme på document
  function applyTheme(theme) {
    const root = document.documentElement;

    if (theme === 'system') {
      root.removeAttribute('data-theme');
    } else {
      root.setAttribute('data-theme', theme);
    }

    updateToggleIcon(theme);
  }

  // Opdater toggle-knappens ikon baseret på aktuel theme
  function updateToggleIcon(theme) {
    const toggle = document.querySelector('.theme-toggle');
    if (!toggle) return;

    // Bestem hvilket ikon der skal vises
    let iconHTML;

    if (theme === 'dark') {
      // Vis sol-ikon når dark mode er aktiv (klik for at skifte til light)
      iconHTML = `
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="12" cy="12" r="4"/>
          <path d="M12 2v2m0 16v2M4.93 4.93l1.41 1.41m11.32 11.32l1.41 1.41M2 12h2m16 0h2M4.93 19.07l1.41-1.41m11.32-11.32l1.41-1.41"/>
        </svg>
      `;
    } else if (theme === 'light') {
      // Vis "system"-ikon når light mode er aktiv (klik for at skifte til system)
      iconHTML = `
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <rect x="2" y="3" width="20" height="14" rx="2"/>
          <path d="M8 21h8m-4-4v4"/>
        </svg>
      `;
    } else {
      // Vis måne-ikon når system mode er aktiv (klik for at skifte til dark)
      iconHTML = `
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
        </svg>
      `;
    }

    toggle.innerHTML = iconHTML;
    toggle.setAttribute('aria-label', `Skift til ${getNextTheme(theme)}-tilstand`);
    toggle.setAttribute('title', `Tema: ${theme === 'system' ? 'System' : theme === 'dark' ? 'Mørk' : 'Lys'}`);
  }

  // Bestem næste theme i cyklus: system → dark → light → system
  function getNextTheme(currentTheme) {
    const index = THEMES.indexOf(currentTheme);
    return THEMES[(index + 1) % THEMES.length];
  }

  // Toggle mellem themes
  function toggleTheme() {
    const currentTheme = getSavedTheme();
    const nextTheme = getNextTheme(currentTheme);

    saveTheme(nextTheme);
    applyTheme(nextTheme);
  }

  // Initialisér ved page load
  function init() {
    const savedTheme = getSavedTheme();
    applyTheme(savedTheme);

    // Tilføj event listener til toggle-knap
    const toggle = document.querySelector('.theme-toggle');
    if (toggle) {
      toggle.addEventListener('click', toggleTheme);
    }

    // Lyt til system theme ændringer når i system-mode
    if (window.matchMedia) {
      const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');
      darkModeQuery.addEventListener('change', (e) => {
        const currentTheme = getSavedTheme();
        if (currentTheme === 'system') {
          // Trigger en re-render af ikonet når system theme ændres
          updateToggleIcon('system');
        }
      });
    }
  }

  // Kør init når DOM er klar
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
