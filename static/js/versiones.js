// Crear una instancia de Notyf
const notyf = new Notyf({
  duration: 3000,
  position: { x: 'right', y: 'top' },
});

// Función para manejar la verificación de actualizaciones
document.getElementById('checkUpdateBtn').addEventListener('click', function() {
  // Mostrar el modal de carga
  document.getElementById('loadingModal').style.display = 'flex';
  document.getElementById('checkUpdateBtn').disabled = true;
  document.getElementById('checkUpdateBtn').disabled = false;
  
  // Simulamos un retraso de 3 segundos para la petición
  setTimeout(function() {
    fetch('/check_for_update', {
      method: 'POST',
    })
    .then(response => response.json())
    .then(data => {
      // Ocultar el modal de carga
      document.getElementById('loadingModal').style.display = 'none';

      // Mostrar el modal con el resultado de la actualización
      document.getElementById('updateModal').style.display = 'flex';

      // Verificar si hay una nueva versión
      if (data.new_version_available) {
        document.getElementById('updateMessage').innerText = "¡Hay una nueva versión disponible! Haz clic en 'Actualizar' para actualizar.";
        document.getElementById('updateBtn').style.display = 'inline-block';  // Mostrar el botón de actualizar
        notyf.success('¡Nueva versión disponible! Puedes actualizar.');
      } else {
        document.getElementById('updateMessage').innerText = "Estás usando la última versión.";
        document.getElementById('updateBtn').style.display = 'none';  // Ocultar el botón de actualizar
        notyf.success('Estás usando la última versión.');
      }
    })
    .catch(error => {
      console.error('Error al comprobar la actualización:', error);
      document.getElementById('loadingModal').style.display = 'none';
      notyf.error('Hubo un error al comprobar la actualización.');
      alert('Hubo un error al comprobar la actualización.');
    });
  }, 3000); // Simulamos un retraso de 3 segundos
});

// Descargar e insertar archivos al hacer clic en el botón de actualizar
document.getElementById('updateBtn').addEventListener('click', function () {
  const updateMessage = document.getElementById('updateMessage');
  const downloadingBar = document.getElementById('downloadingBar');
  const updateModal = document.getElementById('updateModal');

  // Abre el modal
  updateModal.classList.remove('hidden');
  
  // Inicia la descarga
  fetch('/download_latest_version')
      .then(response => {
          if (!response.ok) {
              throw new Error(`Error en la descarga: ${response.status}`);
          }
          
          // Obtener el lector del cuerpo de la respuesta para leer en fragmentos
          const reader = response.body.getReader();
          const contentLength = response.headers.get('Content-Length');
          
          let receivedLength = 0; // Tamaño recibido hasta el momento
          let totalLength = parseInt(contentLength, 10); // Longitud total del archivo
          
          // Mientras no se haya descargado completamente el archivo
          const progressInterval = setInterval(() => {
              if (receivedLength < totalLength) {
                  updateMessage.textContent = `Descargando... (${Math.round((receivedLength / totalLength) * 100)}%)`;
                  downloadingBar.value = (receivedLength / totalLength) * 100;
              }
          }, 500);

          // Leer el contenido de la respuesta en fragmentos
          return new Response(new ReadableStream({
              start(controller) {
                  function push() {
                      reader.read().then(({ done, value }) => {
                          if (done) {
                              controller.close();
                              clearInterval(progressInterval); // Detener la barra de progreso
                              updateMessage.textContent = 'Descarga completada!';
                              setTimeout(() => {
                                  closeModal(); // Cerrar el modal después de un pequeño retraso
                              }, 1000);
                              return;
                          }
                          
                          receivedLength += value.length; // Incrementar la cantidad descargada
                          controller.enqueue(value); // Encolar el fragmento descargado
                          push(); // Seguir leyendo
                      }).catch(err => {
                          console.error('Error al leer la respuesta:', err);
                          new Notyf().error('Error al descargar la última versión.');
                          controller.error(err);
                      });
                  }
                  push();
              }
          })).blob();
      })
      .then(blob => {
          // Procesar el archivo descargado si es necesario
          const files = [blob]; // Aquí puedes manejar el archivo como desees
          new Notyf().success(`Archivos descargados: ${files.length} archivo(s)`);
      })
      .catch(error => {
          console.error('Error al obtener la última versión:', error);
          new Notyf().error('Error al descargar la última versión.');
          clearInterval(progressInterval); // Detener la barra de progreso si hay error
          closeModal(); // Cerrar el modal
      });
});




// Función para cerrar el modal cuando se haga clic fuera de él
function closeModal(event) {
  if (event.target === event.currentTarget) {
      event.currentTarget.style.display = 'none';  // Cierra el modal
  }
}

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

