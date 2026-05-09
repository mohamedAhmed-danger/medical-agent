/* ============================================
   IBYCO MANAGEMENT SYSTEM — MAIN JS
   Place at: static/js/main.js
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {

  /* ── 1. SIDEBAR — MOBILE TOGGLE ── */
  const sidebarToggle  = document.getElementById('sidebarToggle');
  const sidebar        = document.getElementById('sidebar');
  const sidebarOverlay = document.getElementById('sidebarOverlay');

  function openSidebar() {
    sidebar.classList.add('open');
    sidebarOverlay.classList.add('open');
    sidebarToggle.setAttribute('aria-expanded', 'true');
    // Animate hamburger → X
    const bars = sidebarToggle.querySelectorAll('span');
    bars[0].style.transform = 'translateY(6px) rotate(45deg)';
    bars[1].style.opacity   = '0';
    bars[2].style.transform = 'translateY(-6px) rotate(-45deg)';
  }

  function closeSidebar() {
    sidebar.classList.remove('open');
    sidebarOverlay.classList.remove('open');
    sidebarToggle.setAttribute('aria-expanded', 'false');
    const bars = sidebarToggle.querySelectorAll('span');
    bars[0].style.transform = '';
    bars[1].style.opacity   = '';
    bars[2].style.transform = '';
  }

  if (sidebarToggle) {
    sidebarToggle.addEventListener('click', () => {
      sidebar.classList.contains('open') ? closeSidebar() : openSidebar();
    });
  }

  if (sidebarOverlay) {
    sidebarOverlay.addEventListener('click', closeSidebar);
  }

  /* ── 2. ACTIVE NAV LINK ── */
  const currentPath = window.location.pathname;
  document.querySelectorAll('.nav-item').forEach(a => {
    const href = a.getAttribute('href');
    if (href && currentPath.startsWith(href) && href !== '/') {
      a.classList.add('active');
    } else if (href === '/' && currentPath === '/') {
      a.classList.add('active');
    }
  });

  /* ── 3. FLASH MESSAGES AUTO-DISMISS ── */
  function dismissFlash(el) {
    el.classList.add('hide');
    setTimeout(() => el.remove(), 320);
  }

  document.querySelectorAll('.flash-msg').forEach(msg => {
    const closeBtn = msg.querySelector('.flash-close');
    if (closeBtn) closeBtn.addEventListener('click', () => dismissFlash(msg));
    setTimeout(() => {
      if (msg.isConnected) dismissFlash(msg);
    }, 5000);
  });

  /* ── 4. SCROLL ANIMATION (Intersection Observer) ── */
  const animEls = document.querySelectorAll('[data-animate]');
  if (animEls.length) {
    const observer = new IntersectionObserver(entries => {
      entries.forEach((entry, i) => {
        if (entry.isIntersecting) {
          const delay = entry.target.dataset.delay || i * 60;
          setTimeout(() => entry.target.classList.add('visible'), Number(delay));
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.08 });
    animEls.forEach(el => observer.observe(el));
  }

  /* ── 5. TABLE SEARCH / FILTER ── */
  const searchInput = document.getElementById('tableSearch');
  if (searchInput) {
    searchInput.addEventListener('input', () => {
      const q = searchInput.value.trim().toLowerCase();
      document.querySelectorAll('tbody tr').forEach(row => {
        row.style.display = row.textContent.toLowerCase().includes(q) ? '' : 'none';
      });
    });
  }

  /* ── 6. CONFIRM DELETE MODAL ── */
  document.querySelectorAll('[data-confirm]').forEach(el => {
    el.addEventListener('click', e => {
      const msg = el.dataset.confirm || 'هل أنت متأكد؟';
      const existing = document.getElementById('confirmModal');
      if (!existing) {
        if (!window.confirm(msg)) e.preventDefault();
        return;
      }
      e.preventDefault();
      showConfirmModal(msg).then(confirmed => {
        if (confirmed) {
          // If it's a link, navigate; if it's a form button, submit
          if (el.tagName === 'A') window.location.href = el.href;
          else if (el.closest('form')) el.closest('form').submit();
        }
      });
    });
  });

  /* ── 7. GENERIC MODAL SYSTEM ── */
  document.querySelectorAll('[data-modal-open]').forEach(btn => {
    btn.addEventListener('click', () => {
      const id = btn.dataset.modalOpen;
      const overlay = document.getElementById(id);
      if (overlay) overlay.classList.add('open');
    });
  });

  document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', e => {
      if (e.target === overlay) overlay.classList.remove('open');
    });
    overlay.querySelectorAll('[data-modal-close], .modal-close').forEach(btn => {
      btn.addEventListener('click', () => overlay.classList.remove('open'));
    });
  });

  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
      document.querySelectorAll('.modal-overlay.open').forEach(o => o.classList.remove('open'));
      closeSidebar();
    }
  });

  /* ── 8. FORM SUBMIT — LOADING STATE ── */
  document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', () => {
      const submitBtn = form.querySelector('.btn-submit');
      if (submitBtn) {
        submitBtn.disabled = true;
        const originalHTML = submitBtn.innerHTML;
        submitBtn.innerHTML = `<span class="spinner"></span> جارٍ الحفظ...`;
        setTimeout(() => {
          submitBtn.disabled = false;
          submitBtn.innerHTML = originalHTML;
        }, 8000);
      }
    });
  });

  /* ── 9. TOOLTIP (lightweight) ── */
  const tooltip = document.createElement('div');
  tooltip.id = 'tooltip';
  Object.assign(tooltip.style, {
    position: 'fixed', zIndex: '9999',
    background: '#1e2030', color: '#f1f5f9',
    padding: '5px 10px', borderRadius: '6px',
    fontSize: '0.78rem', pointerEvents: 'none',
    opacity: '0', transition: 'opacity 0.15s',
    border: '1px solid rgba(255,255,255,0.08)',
    whiteSpace: 'nowrap', boxShadow: '0 4px 12px rgba(0,0,0,0.4)',
  });
  document.body.appendChild(tooltip);

  document.querySelectorAll('[data-tooltip]').forEach(el => {
    el.addEventListener('mouseenter', () => {
      tooltip.textContent = el.dataset.tooltip;
      tooltip.style.opacity = '1';
    });
    el.addEventListener('mousemove', e => {
      tooltip.style.top  = (e.clientY - 36) + 'px';
      tooltip.style.left = (e.clientX - tooltip.offsetWidth / 2) + 'px';
    });
    el.addEventListener('mouseleave', () => {
      tooltip.style.opacity = '0';
    });
  });

  /* ── HELPER: Confirm modal ── */
  function showConfirmModal(message) {
    const existing = document.getElementById('confirmModal');
    if (!existing) return Promise.resolve(window.confirm(message));

    const msgEl = existing.querySelector('#confirmMessage');
    if (msgEl) msgEl.textContent = message;
    existing.classList.add('open');

    return new Promise(resolve => {
      const confirmBtn = existing.querySelector('#confirmOk');
      const cancelBtn  = existing.querySelector('#confirmCancel');

      function cleanup(val) {
        existing.classList.remove('open');
        confirmBtn && confirmBtn.removeEventListener('click', onOk);
        cancelBtn  && cancelBtn.removeEventListener('click', onCancel);
        resolve(val);
      }

      function onOk()     { cleanup(true);  }
      function onCancel() { cleanup(false); }

      confirmBtn && confirmBtn.addEventListener('click', onOk);
      cancelBtn  && cancelBtn.addEventListener('click',  onCancel);
    });
  }

});

/* ── GLOBAL: copy text to clipboard ── */
function copyToClipboard(text) {
  navigator.clipboard.writeText(text).then(() => showToast('تم النسخ!', 'success'));
}

/* ── GLOBAL: lightweight toast ── */
function showToast(message, type = 'info') {
  const container = document.querySelector('.flash-container') || (() => {
    const c = document.createElement('div');
    c.className = 'flash-container';
    document.body.appendChild(c);
    return c;
  })();

  const el = document.createElement('div');
  el.className = `flash-msg flash-${type}`;
  const icons = { success: '✓', danger: '✕', warning: '⚠', info: 'ℹ' };
  el.innerHTML = `<span>${icons[type] || 'ℹ'}</span> ${message}
    <button class="flash-close" aria-label="إغلاق">✕</button>`;

  container.appendChild(el);
  el.querySelector('.flash-close').addEventListener('click', () => {
    el.classList.add('hide');
    setTimeout(() => el.remove(), 320);
  });
  setTimeout(() => {
    if (el.isConnected) {
      el.classList.add('hide');
      setTimeout(() => el.remove(), 320);
    }
  }, 4500);
}