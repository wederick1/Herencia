function toggleDetails(element) {
  const details = element.querySelector('.version-details');
  const allDetails = document.querySelectorAll('.version-details');
  
  // Cerrar otros detalles abiertos
  allDetails.forEach(function(detail) {
      if (detail !== details) {
          detail.style.display = 'none';
      }
  });

  // Alternar la visibilidad del detalle de la versión seleccionada
  details.style.display = (details.style.display === 'block') ? 'none' : 'block';
}