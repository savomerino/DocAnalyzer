document.addEventListener('DOMContentLoaded', function() {

    // Función para mostrar el modal de loading
    function showLoading() {
        document.getElementById('loading-modal').style.display = 'flex';
    }

    // Función para ocultar el modal de loading
    function hideLoading() {
        document.getElementById('loading-modal').style.display = 'none';
    }

    // Función para manejar la subida y análisis de PDFs e imágenes
    document.getElementById('upload-form').addEventListener('submit', function(event) {
        event.preventDefault();
        var formData = new FormData();
        var fileInput = document.getElementById('file-input');
        if (fileInput.files.length === 0) {
            alert('Por favor, selecciona un archivo.');
            return;
        }
        formData.append('file', fileInput.files[0]);

        // Muestra el modal de loading
        showLoading();

        fetch('/extract-pdf', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error en la respuesta del servidor.');
            }
            return response.json();
        })
        .then(data => {
            hideLoading();
            if (data.error) {
                alert('Error: ' + data.error);
            } else {
                document.getElementById('extracted-text').textContent = data.extracted_text;
                let signaturesContainer = document.getElementById('signatures-container');
                signaturesContainer.innerHTML = '';
                if (data.images && data.images.length > 0) {
                    data.images.forEach(function(imgPath) {
                        let img = document.createElement('img');
                        img.src = imgPath;
                        img.alt = "Firma o sello detectado";
                        img.style.maxWidth = "150px";
                        img.style.margin = "10px";
                        signaturesContainer.appendChild(img);
                    });
                } else {
                    signaturesContainer.innerHTML = '<p>No se detectaron firmas ni sellos.</p>';
                }
            }
        })
        .catch(error => {
            hideLoading();
            console.error('Error:', error);
            alert('Ocurrió un error al procesar el archivo.');
        });
    });

    // Función para manejar la generación de resúmenes
    document.getElementById('summarize-form').addEventListener('submit', function(event) {
        event.preventDefault();
        var text = document.getElementById('document-text').value;
        if (!text.trim()) {
            alert('Por favor, ingresa el texto del documento.');
            return;
        }
        var payload = { text: text };

        showLoading();
        fetch('/summarize-document', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error en la respuesta del servidor.');
            }
            return response.json();
        })
        .then(data => {
            hideLoading();
            if (data.error) {
                alert('Error: ' + data.error);
            } else {
                document.getElementById('summary-result').textContent = data.summary;
            }
        })
        .catch(error => {
            hideLoading();
            console.error('Error:', error);
            alert('Ocurrió un error al generar el resumen.');
        });
    });
});
