// Component Loader - Fallback for when SSI is not available
class ComponentLoader {
    static components = {};
    
    static async loadComponent(name, targetElement) {
        try {
            if (!ComponentLoader.components[name]) {
                const response = await fetch(`/components/${name}.html`);
                if (response.ok) {
                    ComponentLoader.components[name] = await response.text();
                } else {
                    return false;
                }
            }
            
            if (targetElement) {
                targetElement.innerHTML = ComponentLoader.components[name];
                return true;
            }
        } catch (error) {
            return false;
        }
    }
    
    static async loadComponents() {
        // Only load if we detect SSI includes haven't been processed
        const hasSSIIncludes = document.body.innerHTML.includes('<!--#include');
        
        if (hasSSIIncludes) {
            
            // Load navigation
            const navPlaceholder = document.querySelector('[data-component="navigation"]');
            if (navPlaceholder) {
                await ComponentLoader.loadComponent('navigation', navPlaceholder);
            }
            
            // Load footer  
            const footerPlaceholder = document.querySelector('[data-component="footer"]');
            if (footerPlaceholder) {
                await ComponentLoader.loadComponent('footer', footerPlaceholder);
            }
            
            // Load scripts
            const scriptsPlaceholder = document.querySelector('[data-component="scripts"]');
            if (scriptsPlaceholder) {
                const loaded = await ComponentLoader.loadComponent('scripts', scriptsPlaceholder);
                if (loaded) {
                    // Execute the loaded scripts
                    const scripts = scriptsPlaceholder.querySelectorAll('script');
                    scripts.forEach(script => {
                        const newScript = document.createElement('script');
                        newScript.textContent = script.textContent;
                        document.head.appendChild(newScript);
                    });
                }
            }
        }
    }
    
    static initializePage() {
        // Load components and initialize theme manager
        ComponentLoader.loadComponents().then(() => {
            if (typeof ThemeManager !== 'undefined') {
                ThemeManager.initialize();
            }
        });
    }
}

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', ComponentLoader.initializePage);
} else {
    ComponentLoader.initializePage();
}