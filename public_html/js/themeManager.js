// Theme management for IVYSTUDY
const ThemeManager = {
    STORAGE_KEY: 'darkMode',
    LEGACY_STORAGE_KEY: 'darkModeEnabled',
    DARK_MODE_CLASS: 'dark-mode',

    initialize() {
        // Check for saved preference or system preference
        const savedTheme = localStorage.getItem(this.STORAGE_KEY);
        const legacyEnabled = localStorage.getItem(this.LEGACY_STORAGE_KEY);
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

        const explicitDark = savedTheme === 'true' || savedTheme === 'enabled' || legacyEnabled === 'true';
        if (explicitDark || (savedTheme === null && legacyEnabled === null && prefersDark)) {
            document.body.classList.add(this.DARK_MODE_CLASS);
        }

        // Normalize storage to a single boolean string used site-wide.
        localStorage.setItem(this.STORAGE_KEY, document.body.classList.contains(this.DARK_MODE_CLASS) ? 'true' : 'false');
        localStorage.removeItem(this.LEGACY_STORAGE_KEY);
        
        this.updateIcons();
        this.setupListeners();
    },

    toggle() {
        const isDarkMode = document.body.classList.toggle(this.DARK_MODE_CLASS);
        localStorage.setItem(this.STORAGE_KEY, isDarkMode ? 'true' : 'false');
        localStorage.removeItem(this.LEGACY_STORAGE_KEY);
        this.updateIcons();
        document.dispatchEvent(new Event('themeChanged'));
    },

    updateIcons() {
        const isDarkMode = document.body.classList.contains(this.DARK_MODE_CLASS);
        const icon = isDarkMode ? 'dark_mode' : 'light_mode';
        
        // Update all theme toggle buttons
        document.querySelectorAll('.theme-toggle-icon').forEach(el => {
            el.textContent = icon;
        });
    },

    setupListeners() {
        // Listen for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
            if (localStorage.getItem(this.STORAGE_KEY) === null) {
                document.body.classList.toggle(this.DARK_MODE_CLASS, e.matches);
                this.updateIcons();
            }
        });

        // Listen for storage changes (sync across tabs)
        window.addEventListener('storage', e => {
            if (e.key === this.STORAGE_KEY) {
                document.body.classList.toggle(this.DARK_MODE_CLASS, e.newValue === 'true');
                this.updateIcons();
            }
        });
    }
};
