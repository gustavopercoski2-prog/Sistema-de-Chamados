document.addEventListener('DOMContentLoaded', function() {
    initTheme();
    initActionMenu(); 
    initSpaBehavior(); 
    
    // iniciar os cronômetros
    initTimers(); 
});

let globalTimerInterval = null;

function initTimers() {
    if (globalTimerInterval) {
        clearInterval(globalTimerInterval);
    }

    const updateTimers = () => {
        const timers = document.querySelectorAll('.sla-timer');
        const now = new Date();

        timers.forEach(timer => {
            const createdStr = timer.getAttribute('data-created');
            
            if (!createdStr) return;

            const createdDate = new Date(createdStr);
            
            let diff = now - createdDate; 

            if (diff < 0) diff = 0;

            const days = Math.floor(diff / (1000 * 60 * 60 * 24));
            const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

            let result = "";
            
            if (days > 0) {
                result += `${days}d `;
            }
            
            if (hours > 0 || days > 0) {
                result += `${hours}h `;
            }
            
            result += `${minutes}m`;

            if (days === 0 && hours === 0 && minutes === 0) {
                result = "Agora mesmo";
            }

            timer.textContent = result;

            // o chamado fica vermelho se passar de 2 dias
            if (days >= 2) {
                timer.classList.add('text-danger');
            }
        });
    };

    updateTimers();

    globalTimerInterval = setInterval(updateTimers, 60000); 
}

// logica SPA
function initSpaBehavior() {
    document.body.addEventListener('click', function(e) {
        const link = e.target.closest('.card-link, .page-link');

        if (link && !link.closest('.disabled') && !link.hasAttribute('data-bs-toggle')) {
            if (link.hostname === window.location.hostname) {
                if (link.getAttribute('href').includes('export')) return;

                e.preventDefault();
                const url = link.getAttribute('href');
                loadContent(url);
            }
        }
    });

    window.addEventListener('popstate', function() {
        loadContent(window.location.href, false);
    });
}

async function loadContent(url, pushState = true) {
    const container = document.getElementById('ticketForm');
    
    if (container) container.style.opacity = '0.5';

    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error('Erro na rede');

        const text = await response.text();
        const parser = new DOMParser();
        const doc = parser.parseFromString(text, 'text/html');

        // pega o novo conteúdo
        const newContainer = doc.getElementById('ticketForm');
        
        // troca o conteúdo
        if (container && newContainer) {
            container.innerHTML = newContainer.innerHTML;
        }

        // atualiza a url
        if (pushState) {
            window.history.pushState({}, '', url);
        }

        initActionMenu(); 
        initTimers();     
        
        updateActiveCards(doc); 

    } catch (error) {
        console.error('Erro:', error);
        window.location.href = url; 
    } finally {
        if (container) container.style.opacity = '1';
    }
}

function updateActiveCards(newDoc) {
    // atualizar a linha de cards 
    const currentMetricRow = document.querySelector('.row.g-3.mb-5');
    const newMetricRow = newDoc.querySelector('.row.g-3.mb-5');
    if (currentMetricRow && newMetricRow) {
        currentMetricRow.innerHTML = newMetricRow.innerHTML;
    }
}

// checkbox
function initActionMenu() {
    // selecionar todos
    window.toggleAllCheckboxes = function(state) {
        const checkboxes = document.querySelectorAll('input[name="selected_tickets"]');
        checkboxes.forEach(cb => cb.checked = state);
    };

    // ajax
    const dropdownElementList = [].slice.call(document.querySelectorAll('.dropdown-toggle'));
    dropdownElementList.map(function (dropdownToggleEl) {
        return new bootstrap.Dropdown(dropdownToggleEl);
    });
}

// trocar o tema pra escuro / claro
function initTheme() {
    const themeToggleMenu = document.getElementById('theme-toggle-menu');
    const html = document.documentElement;
    const savedTheme = localStorage.getItem('theme') || 'light';
    
    // salvar o tema
    html.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);

    if (themeToggleMenu) {
        const newToggle = themeToggleMenu.cloneNode(true);
        themeToggleMenu.parentNode.replaceChild(newToggle, themeToggleMenu);
        
        newToggle.addEventListener('click', (e) => {
            e.preventDefault();
            const current = html.getAttribute('data-theme');
            const next = current === 'dark' ? 'light' : 'dark';
            
            html.setAttribute('data-theme', next);
            localStorage.setItem('theme', next);
            updateThemeIcon(next);
        });
    }
}

function updateThemeIcon(theme) {
    const themeIconMenu = document.getElementById('theme-icon-menu');
    if (themeIconMenu) {
        themeIconMenu.className = theme === 'light' ? 'bi bi-sun-fill text-warning' : 'bi bi-moon-stars text-primary';
    }
}