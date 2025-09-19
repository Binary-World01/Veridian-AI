document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('lightbox-modal');
    const modalImg = document.getElementById('lightbox-image');
    const closeBtn = document.querySelector('.close-btn');

    document.querySelectorAll('.gallery-grid img').forEach(image => {
        image.style.cursor = 'pointer';
        image.addEventListener('click', function() {
            modal.style.display = 'block';
            modalImg.src = this.src;
        });
    });

    function closeModal() {
        modal.style.display = 'none';
    }

    if (closeBtn) {
        closeBtn.addEventListener('click', closeModal);
    }

    if (modal) {
        modal.addEventListener('click', function(event) {
            if (event.target === modal) {
                closeModal();
            }
        });
    }

    try {
        const socket = io();
        const gallery = document.getElementById('real-time-gallery');

        if (socket && gallery) {
            socket.on('new_image', function(data) {
                const newItem = document.createElement('div');
                newItem.classList.add('gallery-item');
                newItem.innerHTML = `<img src="/static/${data.path}" alt="${data.prompt}"><p>"${data.prompt}" by ${data.author}</p>`;
                
                newItem.querySelector('img').style.cursor = 'pointer';
                newItem.querySelector('img').addEventListener('click', function() {
                    modal.style.display = 'block';
                    modalImg.src = this.src;
                });

                gallery.prepend(newItem);
            });
        }
    } catch (e) {
        console.log("Socket.IO not loaded or used on this page.");
    }
});