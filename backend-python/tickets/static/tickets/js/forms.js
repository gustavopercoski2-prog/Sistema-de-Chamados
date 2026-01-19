function updateFileName(input) {
    const label = document.getElementById('file-name-display');
    const icon = input.nextElementSibling.querySelector('i');

    if (input.files && input.files[0]) {
        label.innerHTML = `<strong>${input.files[0].name}</strong>`;
        label.classList.add('text-primary');
        icon.className = "bi bi-check-circle-fill fs-3 mb-2 text-primary";
        input.nextElementSibling.style.borderColor = "var(--brand-primary)";
        input.nextElementSibling.style.backgroundColor = "rgba(37, 99, 235, 0.05)";
    } else {
        label.innerText = "Arraste ou clique para anexar";
        label.classList.remove('text-primary');
        icon.className = "bi bi-cloud-arrow-up fs-3 mb-2 opacity-50";
        input.nextElementSibling.style.borderColor = "var(--border-subtle)";
        input.nextElementSibling.style.backgroundColor = "var(--input-bg)";
    }
}

document.addEventListener("DOMContentLoaded", function () {
    
    // forçar estilo nos INPUTS
    const inputs = document.querySelectorAll('.form-body input:not([type="checkbox"]):not([type="file"]), .form-body textarea, .form-body select');
    inputs.forEach(function (input) {
        if (input.tagName === 'SELECT') {
            input.classList.add('form-select');
        } else {
            input.classList.add('form-control');
        }
    });

    // logica de SLA
    const prioritySelect = document.getElementById('id_prioridade_select') || document.getElementById('id_prioridade');
    const slaDesc = document.getElementById('sla-desc');
    
    // mapeamento dos itens da lista visual
    const lis = {
        'ALTA': document.getElementById('li-alta'),
        'MEDIA': document.getElementById('li-media'), 
        'MÉDIA': document.getElementById('li-media'), 
        'BAIXA': document.getElementById('li-baixa')
    };

    if(prioritySelect && slaDesc) {
        const slaMap = { 
            'BAIXA': '30 horas', 
            'MEDIA': '16 horas', 
            'MÉDIA': '16 horas',
            'ALTA': '6 horas' 
        };
        
        const updatePriorityInfo = () => {
            let val = prioritySelect.value ? prioritySelect.value.toUpperCase() : 'BAIXA';
            

            // atualizar as horas
            if (slaMap[val]) {
                slaDesc.innerHTML = slaMap[val];
            }

            Object.values(lis).forEach(li => { 
                if(li) { 
                    li.style.opacity = '0.5'; 
                    li.style.fontWeight = 'normal'; 
                }
            });
            
            if(lis[val]) { 
                lis[val].style.opacity = '1'; 
                lis[val].style.fontWeight = 'bold'; 
            }
        };

        prioritySelect.addEventListener('change', updatePriorityInfo);
        
        // executa uma vez ao carregar para ajustar o estado inicial
        setTimeout(updatePriorityInfo, 100); 
    } else {
        console.warn("Aviso: Elementos da lógica de SLA (Select ou Descrição) não foram encontrados no HTML.");
    }
});