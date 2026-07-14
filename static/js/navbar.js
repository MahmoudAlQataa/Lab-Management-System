// ============================================================
// navbar.js — التحكم بالقائمة الجانبية (Hamburger Drawer)
// يُحمّل بكل صفحة فيها header (نفس نمط theme.css / base.css)
// ============================================================

document.addEventListener('DOMContentLoaded', function () {
    const hamburgerBtn = document.getElementById('hamburgerBtn');
    const drawerCloseBtn = document.getElementById('drawerCloseBtn');
    const sideDrawer = document.getElementById('sideDrawer');
    const drawerOverlay = document.getElementById('drawerOverlay');
    const settingsToggle = document.querySelector('.drawer-settings-toggle');
    const settingsSubmenu = document.querySelector('.drawer-submenu');

    function openDrawer() {
        sideDrawer.classList.add('open');
        drawerOverlay.classList.add('open');
    }

    function closeDrawer() {
        sideDrawer.classList.remove('open');
        drawerOverlay.classList.remove('open');
    }

    if (hamburgerBtn) {
        hamburgerBtn.addEventListener('click', openDrawer);
    }

    if (drawerCloseBtn) {
        drawerCloseBtn.addEventListener('click', closeDrawer);
    }

    if (drawerOverlay) {
        drawerOverlay.addEventListener('click', closeDrawer);
    }

    // Settings — قائمة فرعية (accordion)
    if (settingsToggle && settingsSubmenu) {
        settingsToggle.addEventListener('click', function () {
            settingsToggle.classList.toggle('open');
            settingsSubmenu.classList.toggle('open');
        });
    }
});