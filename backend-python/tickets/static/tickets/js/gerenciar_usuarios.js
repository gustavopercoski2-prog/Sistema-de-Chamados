document.addEventListener('DOMContentLoaded', function() {
    
    // trocar o tema pra escuro / claro
    const themeBtn = document.getElementById('themeToggle');
    if (themeBtn) {
        const themeIcon = themeBtn.querySelector('i');
        
        // salvar o tema
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
        updateIcon(savedTheme, themeIcon);

        themeBtn.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateIcon(newTheme, themeIcon);
        });
    }

    function updateIcon(theme, iconElement) {
        if (!iconElement) return;
        if(theme === 'dark') {
            iconElement.classList.remove('bi-moon-stars');
            iconElement.classList.add('bi-sun');
        } else {
            iconElement.classList.remove('bi-sun');
            iconElement.classList.add('bi-moon-stars');
        }
    }

    // aplicar classes
    document.querySelectorAll('input, select').forEach(el => {
        if (el.type !== 'checkbox' && el.type !== 'hidden' && !el.classList.contains('dual-list-select')) {
            el.classList.add(el.tagName === 'SELECT' ? 'form-select' : 'form-control');
            el.classList.add('form-control-pro');
        }
    });

    // filtro de lista principal
    const searchInput = document.getElementById('userSearch');
    const sectorFilter = document.getElementById('setorFilter');
    const items = document.querySelectorAll('.user-item');
    const countBadge = document.getElementById('countBadge');

    function filterList() {
        if(!searchInput || !items) return;

        const term = searchInput.value.toLowerCase();
        const sector = sectorFilter ? sectorFilter.value.toLowerCase() : "";
        let visibleCount = 0;

        items.forEach(item => {
            const nameEl = item.querySelector('.user-name');
            const sectorEl = item.querySelector('.user-sector');
            
            const name = nameEl ? nameEl.innerText.toLowerCase() : "";
            const itemSector = sectorEl ? sectorEl.innerText.toLowerCase() : "";
            
            const matchesSearch = name.includes(term);
            const matchesSector = sector === "" || itemSector.includes(sector);

            if (matchesSearch && matchesSector) {
                item.style.display = 'flex';
                visibleCount++;
            } else {
                item.style.display = 'none';
            }
        });
        if(countBadge) countBadge.innerText = visibleCount;
    }

    if(searchInput) searchInput.addEventListener('keyup', filterList);
    if(sectorFilter) sectorFilter.addEventListener('change', filterList);

    // selecionar todos
    const selectAllBtn = document.getElementById('selectAll');
    if(selectAllBtn) {
        selectAllBtn.addEventListener('change', function() {
            const isChecked = this.checked;
            document.querySelectorAll('.user-checkbox').forEach(cb => {
                if(cb.closest('.user-item').style.display !== 'none') {
                    cb.checked = isChecked;
                }
            });
        });
    }

    // filtros do MODAL
    setupFilter('filterAvailable', 'listAvailable');
    setupFilter('filterChosen', 'listChosen');
});

// acoes em massa
function submitBulkAction(action) {
    const selected = document.querySelectorAll('.user-checkbox:checked');
    if (selected.length === 0) { alert("Selecione pelo menos um usuário."); return; }
    if (action === 'delete' && !confirm(`Tem certeza que deseja excluir ${selected.length} usuários?`)) return;
    
    const input = document.getElementById('bulkActionInput');
    const form = document.getElementById('bulkForm');
    
    if(input && form) {
        input.value = action;
        form.submit();
    }
}

// exportar dados
function exportData(type) {
    const url = `/gestao/usuarios/exportar/?format=${type}`;
    window.location.href = url;
}

// listbox ---
function moveItems(sourceId, destId) {
    const source = document.getElementById(sourceId);
    const dest = document.getElementById(destId);
    if(!source || !dest) return;
    
    const selectedOptions = Array.from(source.selectedOptions);
    
    selectedOptions.forEach(option => {
        option.selected = false;
        dest.appendChild(option);
    });
    sortList(dest);
}

function chooseAll(e) {
    e.preventDefault();
    const source = document.getElementById('listAvailable');
    const dest = document.getElementById('listChosen');
    if(!source || !dest) return;

    Array.from(source.options).forEach(option => dest.appendChild(option));
    sortList(dest);
}

function removeAll(e) {
    e.preventDefault();
    const source = document.getElementById('listAvailable');
    const dest = document.getElementById('listChosen');
    if(!source || !dest) return;

    Array.from(dest.options).forEach(option => source.appendChild(option));
    sortList(source);
}

function setupFilter(inputId, listId) {
    const input = document.getElementById(inputId);
    if(!input) return;

    input.addEventListener('keyup', function() {
        const filter = this.value.toLowerCase();
        const list = document.getElementById(listId);
        const options = list.getElementsByTagName('option');
        for (let i = 0; i < options.length; i++) {
            const text = options[i].text.toLowerCase();
            options[i].style.display = text.includes(filter) ? "" : "none";
        }
    });
}

function sortList(select) {
    const options = Array.from(select.options);
    options.sort((a, b) => a.text.localeCompare(b.text));
    options.forEach(o => select.add(o));
}

// selecionar itens antes de enviar
const formGrupo = document.getElementById('formGrupo');
if(formGrupo) {
    formGrupo.addEventListener('submit', function() {
        const chosenList = document.getElementById('listChosen');
        for (let i = 0; i < chosenList.options.length; i++) {
            chosenList.options[i].selected = true;
        }
    });
}