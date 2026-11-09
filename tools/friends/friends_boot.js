/* ---------- avvio: pulsante nella Centrale TVA > Operazioni (nessuna modifica al resto della Centrale) ---------- */
function mountLauncher() {
  if (document.getElementById('tfLauncher')) return true;
  var acc = document.getElementById('faAccount'), grp = acc && acc.closest('.cen-grp'); if (!grp) return false;
  var b = h('button', { type: 'button', class: 'reset-btn tf-open', id: 'tfOpen', onclick: function () { openUI(); } }, ['👥 Apri TVA Friends ', h('span', { class: 'tf-badge', id: 'tfBadge', hidden: true, 'aria-label': 'Non letti' })]);
  var sec = h('section', { class: 'cen-card cen-grp', id: 'tfLauncher' }, [h('h3', {}, ['TVA Friends']), h('p', { class: 'cen-help' }, ['Varianti, Legame Nexus, Squadre, Serate Marvel, Quiz e Duelli, Archivio condiviso e Comunicazioni. Funziona con codici e file, anche offline. Diario TVA, voti e progressi restano privati.']), b]);
  grp.parentNode.insertBefore(sec, grp.nextSibling);
  try { var raw = localStorage.getItem(KEY); if (raw) { load(); updateBadges(); } } catch (e) {}
  return true;
}
(function boot() { var n = 0; (function t() { if (mountLauncher() || ++n > 60) return; setTimeout(t, 300); })(); })();
try { Object.defineProperty(window, 'tvaFriends', { value: Object.freeze({ open: openUI, close: closeUI, version: 1, cloudEnabled: function () { return CLOUD_ENABLED === true; }, unread: function () { load(); return unreadCount(); } }), configurable: false }); } catch (e) {}
