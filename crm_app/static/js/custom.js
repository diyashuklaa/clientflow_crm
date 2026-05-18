// ClientFlow CRM — Custom JS

document.addEventListener('DOMContentLoaded', function () {

    // Sidebar toggle for mobile
    const toggleBtn = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');

    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', function () {
            sidebar.classList.toggle('open');
        });

        // Close on outside click
        document.addEventListener('click', function (e) {
            if (!sidebar.contains(e.target) && !toggleBtn.contains(e.target)) {
                sidebar.classList.remove('open');
            }
        });
    }

    // Auto-dismiss flash messages after 5s
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }, 5000);
    });

    // Highlight active nav with current URL
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-item').forEach(function (link) {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // Confirm on all delete forms
    document.querySelectorAll('form[data-confirm]').forEach(function (form) {
        form.addEventListener('submit', function (e) {
            if (!confirm(form.dataset.confirm || 'Are you sure?')) {
                e.preventDefault();
            }
        });
    });

    // Inject current time context for dashboard greeting
    const now = new Date();
    const greetingEl = document.querySelector('.dashboard-welcome .greeting-time');
    if (greetingEl) {
        const hour = now.getHours();
        let greeting = 'Good Morning';
        if (hour >= 12 && hour < 17) greeting = 'Good Afternoon';
        else if (hour >= 17) greeting = 'Good Evening';
        greetingEl.textContent = greeting;
    }

    // Chart.js global defaults
    if (typeof Chart !== 'undefined') {
        Chart.defaults.font.family = 'DM Sans';
        Chart.defaults.color = '#6B7280';
        Chart.defaults.plugins.tooltip.backgroundColor = '#1A1D2E';
        Chart.defaults.plugins.tooltip.padding = 10;
        Chart.defaults.plugins.tooltip.cornerRadius = 8;
        Chart.defaults.plugins.tooltip.titleFont = { family: 'Syne', weight: '700' };
    }

    // Quick status color indicator on table rows
    document.querySelectorAll('.status-badge').forEach(function (badge) {
        const tr = badge.closest('tr');
        if (tr) {
            if (badge.classList.contains('status-won')) {
                tr.style.borderLeft = '3px solid #2EC4B6';
            } else if (badge.classList.contains('status-lost')) {
                tr.style.borderLeft = '3px solid #FF6B6B';
            }
        }
    });

});
