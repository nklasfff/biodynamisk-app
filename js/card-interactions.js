// Foldable cards — toggle, click-to-close, back-to-top
// Bruges af kapitel.html, stadie.html, zone.html, begreb.html

function toggleCard(headerOrCard) {
  const card = headerOrCard.classList.contains('card')
    ? headerOrCard
    : headerOrCard.closest('.card');
  const content = card.querySelector('.card-content');
  const chevron = card.querySelector('.chevron');

  card.classList.toggle('open');

  if (card.classList.contains('open')) {
    if (chevron) chevron.style.transform = 'rotate(180deg)';
    content.style.maxHeight = content.scrollHeight + 'px';
  } else {
    if (chevron) chevron.style.transform = 'rotate(0deg)';
    content.style.maxHeight = '0';
  }
}

// Klik på selve content-area lukker kortet
// (men ikke klik på links, knapper eller nested <details>/<summary> i ordlisten)
function closeCardFromContent(event, content) {
  if (event.target.closest('a, button, summary, details')) return;
  const card = content.closest('.card');
  if (card && card.classList.contains('open')) {
    toggleCard(card);
  }
}

// Smooth scroll til toppen af siden
function scrollToTop(event) {
  if (event) event.stopPropagation();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Sikrer at nye sider altid starter øverst
window.addEventListener('pageshow', () => {
  window.scrollTo(0, 0);
});

// Når en <details> toggler inde i et åbent kort, re-justér kortets max-height
// så indholdet ikke bliver clippet. 'toggle' event bobler ikke, så vi bruger capture.
document.addEventListener('toggle', (e) => {
  if (e.target.tagName !== 'DETAILS') return;
  const card = e.target.closest('.card');
  if (!card || !card.classList.contains('open')) return;
  const content = card.querySelector('.card-content');
  if (content) {
    content.style.maxHeight = content.scrollHeight + 'px';
  }
}, true);
