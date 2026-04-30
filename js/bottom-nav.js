// Bottom navigation — 5 tabs delt af alle sider
// Hver side har <nav class="bottom-nav" data-active="modellen|behandleren|rejsen|inspiration|info"></nav>
// Dette script fylder den med markup og markerer den aktive tab.

(function() {
  const TABS = [
    {
      key: 'modellen',
      href: 'modellen.html',
      label: 'Modellen',
      icon: '<circle cx="12" cy="12" r="3"/><circle cx="6" cy="6" r="1.5"/><circle cx="18" cy="6" r="1.5"/><circle cx="6" cy="18" r="1.5"/><circle cx="18" cy="18" r="1.5"/>'
    },
    {
      key: 'behandleren',
      href: 'behandleren.html',
      label: 'Behandleren',
      icon: '<circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>'
    },
    {
      key: 'rejsen',
      href: 'rejsen.html',
      label: 'Rejsen',
      icon: '<path d="M3 18 Q 6 15, 9 12 T 15 9 T 21 6"/>'
    },
    {
      key: 'inspiration',
      href: 'inspiration.html',
      label: 'Inspiration',
      icon: '<circle cx="10" cy="12" r="4"/><circle cx="14" cy="12" r="4"/><circle cx="12" cy="9" r="4"/>'
    },
    {
      key: 'info',
      href: 'info.html',
      label: 'Info',
      icon: '<circle cx="12" cy="12" r="9"/><path d="M12 8v0M12 11v5"/>'
    }
  ];

  function render() {
    const nav = document.querySelector('nav.bottom-nav');
    if (!nav) return;
    const active = nav.getAttribute('data-active') || '';
    nav.innerHTML = TABS.map(tab => `
      <button class="nav-tab${tab.key === active ? ' nav-tab-active' : ''}" onclick="window.location.href='${tab.href}'">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          ${tab.icon}
        </svg>
        <span class="nav-label">${tab.label}</span>
      </button>
    `).join('');
  }

  // Eksponer render globalt så dynamiske sider kan kalde efter container.innerHTML
  window.BottomNav = { render };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', render);
  } else {
    render();
  }
})();
