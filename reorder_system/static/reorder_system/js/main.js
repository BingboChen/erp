// MaxFactory - Script principale

document.addEventListener('DOMContentLoaded', function() {
    // Evidenzia la voce di menu attiva in base all'URL corrente
    highlightActiveMenuItem();
    
    // Inizializza eventuali componenti interattivi
    initComponents();
});

/**
 * Evidenzia la voce di menu corrispondente alla pagina corrente
 */
function highlightActiveMenuItem() {
    const currentPath = window.location.pathname;
    // Seleziona tutti i link nella navbar
    const menuItems = document.querySelectorAll('.nav-list a');
    
    menuItems.forEach(item => {
        const href = item.getAttribute('href');
        
        // Non rimuoviamo la classe active se è già stata impostata nel template
        // Questo permette ai template di avere priorità nell'impostare la classe active
        
        // Caso 1: Link esatto alla pagina corrente
        if (href === currentPath) {
            item.classList.add('active');
        }
        // Caso 2: Pagina di dettaglio fornitore - attiva il link alla lista fornitori
        else if (currentPath.match(/\/fornitori\/\d+\/$/) && href.includes('/fornitori/') && !href.match(/\/fornitori\/\d+\//)) {
            item.classList.add('active');
        }
        // Caso 3: Sottopagina di una sezione (ma non per la home '/')
        else if (href !== '/' && href !== '' && currentPath.startsWith(href)) {
            item.classList.add('active');
        }
    });
}

/**
 * Inizializza componenti interattivi della pagina
 */
function initComponents() {
    // Esempio: gestione dropdown menu
    const dropdowns = document.querySelectorAll('.dropdown');
    
    dropdowns.forEach(dropdown => {
        const trigger = dropdown.querySelector('.dropdown-trigger');
        const content = dropdown.querySelector('.dropdown-content');
        
        if (trigger && content) {
            trigger.addEventListener('click', function(e) {
                e.preventDefault();
                content.classList.toggle('show');
            });
            
            // Chiudi dropdown quando si clicca fuori
            document.addEventListener('click', function(e) {
                if (!dropdown.contains(e.target)) {
                    content.classList.remove('show');
                }
            });
        }
    });
}