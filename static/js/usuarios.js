const btnAgregar = document.querySelector('.btn-agregar');
const modal = document.getElementById('modal-agregar');
const closeModal = document.getElementById('close-modal');

btnAgregar.addEventListener('click', () => {
    modal.classList.add('show'); // Añadir la clase 'show' al modal
});

closeModal.addEventListener('click', () => {
    modal.classList.remove('show'); // Quitar la clase 'show' para cerrarlo
});

window.addEventListener('click', (event) => {
    if (event.target === modal) {
        modal.classList.remove('show'); // Cerrar modal si se hace clic fuera de él
    }
});
