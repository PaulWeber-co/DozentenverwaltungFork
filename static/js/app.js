/* ═══════════════════════════════════════
   Dozentenverwaltung – Frontend JS
   ═══════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', function () {

    // ─── Sidebar Toggle (Mobile) ───
    const toggleBtn = document.querySelector('.btn-sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.querySelector('.sidebar-overlay');

    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            sidebar.classList.toggle('show');
            overlay.classList.toggle('show');
        });
    }

    if (overlay) {
        overlay.addEventListener('click', () => {
            sidebar.classList.remove('show');
            overlay.classList.remove('show');
        });
    }

    // ─── Auto-dismiss alerts ───
    document.querySelectorAll('.alert-dismissible').forEach(alert => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 5000);
    });

    // ─── Confirm Delete ───
    document.querySelectorAll('[data-confirm]').forEach(el => {
        el.addEventListener('click', function (e) {
            const msg = this.getAttribute('data-confirm') || 'Sind Sie sicher?';
            if (!confirm(msg)) {
                e.preventDefault();
                e.stopImmediatePropagation();
            }
        });
    });

    // ─── Filter form auto-submit ───
    document.querySelectorAll('.auto-submit').forEach(el => {
        el.addEventListener('change', function () {
            this.closest('form').submit();
        });
    });

    // ─── Preference fields toggle ───
    const praeferenzSelect = document.getElementById('praeferenz');
    const prioFields = document.getElementById('prio-fields');
    if (praeferenzSelect && prioFields) {
        function togglePrioFields() {
            if (praeferenzSelect.value === 'A') {
                prioFields.style.display = '';
            } else if (praeferenzSelect.value === 'M') {
                prioFields.style.display = '';
                document.getElementById('bachelor_prioritaet').value = '';
            } else if (praeferenzSelect.value === 'B') {
                prioFields.style.display = '';
                document.getElementById('master_prioritaet').value = '';
            }
        }
        praeferenzSelect.addEventListener('change', togglePrioFields);
        togglePrioFields();
    }

    // ─── Niveau-Präferenz toggle in Zuweisung Form ───
    const dozentSelect = document.getElementById('dozent_id');
    const niveauPraefField = document.getElementById('niveau-praeferenz-group');
    // We always show it since we don't load dozent data via AJAX here

    // ─── DataTable-like sorting for tables ───
    document.querySelectorAll('.sortable-table th[data-sort]').forEach(th => {
        th.style.cursor = 'pointer';
        th.addEventListener('click', function () {
            const table = this.closest('table');
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            const colIdx = Array.from(this.parentElement.children).indexOf(this);
            const isAsc = this.classList.contains('sort-asc');

            // Reset other headers
            table.querySelectorAll('th').forEach(h => {
                h.classList.remove('sort-asc', 'sort-desc');
            });

            rows.sort((a, b) => {
                const aText = a.children[colIdx]?.textContent.trim().toLowerCase() || '';
                const bText = b.children[colIdx]?.textContent.trim().toLowerCase() || '';
                if (!isNaN(aText) && !isNaN(bText)) {
                    return isAsc ? bText - aText : aText - bText;
                }
                return isAsc ? bText.localeCompare(aText, 'de') : aText.localeCompare(bText, 'de');
            });

            this.classList.add(isAsc ? 'sort-desc' : 'sort-asc');
            rows.forEach(row => tbody.appendChild(row));
        });
    });

    // ─── Search filter for tables ───
    document.querySelectorAll('[data-table-search]').forEach(input => {
        const tableId = input.getAttribute('data-table-search');
        const table = document.getElementById(tableId);
        if (!table) return;
        input.addEventListener('input', function () {
            const term = this.value.toLowerCase();
            table.querySelectorAll('tbody tr').forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(term) ? '' : 'none';
            });
        });
    });

    // ─── Print button ───
    document.querySelectorAll('.btn-print').forEach(btn => {
        btn.addEventListener('click', () => window.print());
    });
});

