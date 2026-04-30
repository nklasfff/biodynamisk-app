/* ============================================
   Bibliotek-store — gemte tekster i localStorage
   ============================================
   Skema (localStorage["biodynamisk-bibliotek"]):
   [
     {
       type: "invitation",
       id: "...",
       gemtDato: "2026-04-30",
       snapshot: { navn, evokation, invitation, kategori, kategori_label }
     }
   ]

   `type` er typed fra start så lag 2 (favoritter på tværs af appen)
   kan udvides uden migration. I lag 1 bruges kun type="invitation".
*/

(function () {
  'use strict';

  const KEY = 'biodynamisk-bibliotek';

  function hent() {
    try {
      const raw = localStorage.getItem(KEY);
      if (!raw) return [];
      const parsed = JSON.parse(raw);
      return Array.isArray(parsed) ? parsed : [];
    } catch (e) {
      return [];
    }
  }

  function gem(item) {
    if (!item || !item.id || !item.type) return;
    const liste = hent();
    if (liste.find(x => x.id === item.id && x.type === item.type)) return;
    liste.push({
      type: item.type,
      id: item.id,
      gemtDato: new Date().toISOString().slice(0, 10),
      snapshot: item.snapshot || {}
    });
    try { localStorage.setItem(KEY, JSON.stringify(liste)); } catch (e) {}
  }

  function fjern(type, id) {
    const liste = hent().filter(x => !(x.id === id && x.type === type));
    try { localStorage.setItem(KEY, JSON.stringify(liste)); } catch (e) {}
  }

  function harGemt(type, id) {
    return hent().some(x => x.id === id && x.type === type);
  }

  window.BibliotekStore = { hent, gem, fjern, harGemt };
})();
