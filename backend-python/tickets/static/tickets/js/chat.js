document.addEventListener("DOMContentLoaded", function() {
    
    // scroll automatico pro fim do chat
    var chatHistory = document.getElementById('chatHistory');
    if(chatHistory) {
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    // 2. logica de colar imagem
    const chatInput = document.getElementById('chatInputText');
    const fileInputChat = document.getElementById('id_chat_file');
    
    if(chatInput && fileInputChat) {
        chatInput.addEventListener('paste', function(e) {
            const items = (e.clipboardData || e.originalEvent.clipboardData).items;
            for (let item of items) {
                if (item.kind === 'file') {
                    const blob = item.getAsFile();
                    const file = new File([blob], "print_colado.png", { type: "image/png" });
                    
                    // simula input de arquivo
                    const dataTransfer = new DataTransfer();
                    dataTransfer.items.add(file);
                    fileInputChat.files = dataTransfer.files;
                    
                    showChatPreview(fileInputChat);
                }
            }
        });
    }

    // tema (dark/light)
    const themeToggle = document.getElementById('theme-toggle-btn');
    const themeIcon = document.getElementById('theme-icon');
    const html = document.documentElement;
    const savedTheme = localStorage.getItem('theme') || 'light';
    
    // mantem tema salvo
    html.setAttribute('data-theme', savedTheme);
    if(themeIcon) themeIcon.className = savedTheme === 'light' ? 'bi bi-sun-fill text-warning' : 'bi bi-moon-stars text-primary';

    if(themeToggle) {
        themeToggle.addEventListener('click', (e) => {
            e.preventDefault();
            const next = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
            
            html.setAttribute('data-theme', next);
            localStorage.setItem('theme', next);
            
            // troca o icone
            if(themeIcon) themeIcon.className = next === 'light' ? 'bi bi-sun-fill text-warning' : 'bi bi-moon-stars text-primary';
        });
    }
});

// funçoes

function openImageModal(url) {
    const modalImg = document.getElementById('previewImageFull');
    if(modalImg) {
        modalImg.src = url;
        const myModal = new bootstrap.Modal(document.getElementById('imagePreviewModal'));
        myModal.show();
    }
}

function showChatPreview(input) {
    const preview = document.getElementById('uploadPreview');
    const txt = document.getElementById('previewText');
    if (input.files && input.files[0]) {
        if(preview) preview.style.display = 'block';
        if(txt) txt.innerText = `Anexado: ${input.files[0].name}`;
    }
}

function validateSingleFile(input) {
    const label = document.getElementById('file-name-display');
    if (input.files && input.files[0]) {
        if (input.files[0].size > 10 * 1024 * 1024) {
            alert("Erro: Arquivo excede 10MB."); 
            input.value = ""; 
            return;
        }
        if(label) label.innerHTML = `<strong>${input.files[0].name}</strong>`;
    }
}