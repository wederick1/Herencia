document.addEventListener('DOMContentLoaded', function() {
    // Inicialización de Notyf para notificaciones
    const notyf = new Notyf({
        position: {
            x: 'right',  // Puedes usar 'right' o 'left' para la posición horizontal
            y: 'top',    // Puedes usar 'top' o 'bottom' para la posición vertical
        },
        duration: 4000, // Duración de la notificación (en milisegundos)
    });

    // Obtener el formulario y el botón
    const form = document.getElementById('addTenantForm');
    const addTenantButton = document.querySelector('.btn-agregar');
    const modal = document.getElementById('modal');
    const closeModalButton = document.querySelector('.close-btn');

    // Mostrar el modal al hacer clic en el botón "Agregar Inquilino"
    addTenantButton.addEventListener('click', function() {
        modal.style.display = 'block'; // Asegurarse de que el modal se muestre
        setTimeout(function() {
            modal.classList.add('show'); // Añadir clase para animación suave
        }, 10); // Retrasar para aplicar la animación
    });

    // Cerrar el modal al hacer clic en el botón de cierre
    closeModalButton.addEventListener('click', function() {
        modal.classList.remove('show'); // Eliminar clase para animación
        setTimeout(function() {
            modal.style.display = 'none'; // Ocultar el modal después de la animación
        }, 600); // Esperar a que termine la animación
    });

    // Cerrar el modal si se hace clic fuera de él
    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            modal.classList.remove('show');
            setTimeout(function() {
                modal.style.display = 'none';
            }, 600);
        }
    });

    // Función para enviar los datos del formulario
    form.addEventListener('submit', function(event) {
        event.preventDefault(); // Evitar que el formulario se envíe de manera tradicional

        // Obtener los valores de los campos
        const name = document.getElementById('name').value;
        const idValue = document.getElementById('idValue').value;
        const tower = document.getElementById('tower').value;
        let startDate = document.getElementById('startDate').value; // Fecha en formato yyyy-mm-dd

        // Verificar si se ha proporcionado una fecha
        if (startDate) {
            // Dividir la fecha en partes (año, mes, día)
            const [year, month, day] = startDate.split('-');
            // Formatear la fecha a mes/día/año
            startDate = `${month}/${day}/${year}`;
        } else {
            console.error('La fecha no está definida.');
            return; // Detener si no hay fecha
        }

        // Crear el objeto con los datos
        const tenantData = {
            name: name,
            idValue: idValue,
            tower: tower,
            startDate: startDate
        };

        // Enviar los datos al servidor usando fetch
        fetch('/addTenant', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(tenantData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Mostrar notificación de éxito
                notyf.success('Inquilino agregado con éxito!');
                // Cerrar el modal después de enviar
                modal.classList.remove('show');
                setTimeout(function() {
                    modal.style.display = 'none';
                }, 600);
                // Limpiar el formulario
                form.reset();
                // Recargar la página después de 2 segundos para que el usuario vea la notificación
                setTimeout(() => {
                    window.location.reload();  // Recarga la página
                }, 4000); // Espera 2 segundos antes de recargar la página
            } else {
                alert('Hubo un error al agregar el inquilino: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error al enviar los datos:', error);
        });
    });
});


$(document).ready(function() {
    // Evento al hacer clic en el botón de actualizar la fecha de salida
    $(document).on('click', '.update-end-date-btn', function() {
        var $button = $(this);  // Obtener el botón clickeado
        var $row = $button.closest('tr');  // Obtener la fila del inquilino
        var tenantId = $row.data('id');  // Obtener el ID del inquilino

        if (!tenantId) {
            console.error("No se encontró el ID del inquilino.");
            return;
        }

        // Obtener la fecha actual en formato mes/día/año
        var currentDate = new Date();
        var endDate = currentDate.toLocaleDateString('en-US'); // Formato: mes/día/año

        // Actualizar la UI con la nueva fecha
        $button.text(endDate);  // Cambiar el texto del botón por la fecha
        $button.prop('disabled', true);  // Desactivar el botón para evitar clics posteriores

        // Actualizar la columna "Fecha de Salida" en la tabla
        $row.find('td:nth-child(6)').text(endDate);  // Actualizar la celda de la fecha de salida

        // Crear el objeto con los datos a enviar
        var requestData = {
            tenant_id: tenantId,
            end_date: endDate
        };

        // Enviar la solicitud POST con los datos
        $.ajax({
            url: '/updateEndDate',  // Ruta a tu backend
            type: 'POST',
            contentType: 'application/json',  // Tipo de contenido
            data: JSON.stringify(requestData),  // Convertir el objeto a JSON
            success: function(response) {
                if (response.success) {
                    console.log('Fecha de salida actualizada');
                } else {
                    console.error('Error al actualizar la fecha de salida:', response.error);
                }
            },
            error: function(xhr, status, error) {
                console.error('Error al hacer la solicitud:', error);
                console.log(xhr.responseText);  // Ver los detalles de la respuesta de error
            }
        });
    });
});

// modal Buscar
document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('modalHistorial');
    const openBtn = document.querySelector('.btn-leer');
    const closeBtn = modal.querySelector('.close-btn');
    const inputTower = document.getElementById('towerInput');
    const resultadosTable = document.querySelector('#historialTable tbody');

    // Función para abrir el modal
    const openModal = () => {
        modal.style.display = 'block';
        setTimeout(() => modal.classList.add('show'), 10);
    };

    // Función para cerrar el modal
    const closeModal = () => {
        modal.classList.remove('show');
        setTimeout(() => (modal.style.display = 'none'), 600);
    };

    // Abrir el modal al hacer clic en el botón
    openBtn.addEventListener('click', openModal);

    // Abrir o cerrar el modal al presionar la tecla "H"
    document.addEventListener('keydown', (event) => {
        const isHistorialInquilinos = window.location.pathname.includes('historial_inquilinos');
        const activeElement = document.activeElement; // Elemento que tiene el foco
    
        // Verificar si el foco está en un input o textarea
        const isTyping = activeElement.tagName === 'INPUT' || activeElement.tagName === 'TEXTAREA';
    
        if (isHistorialInquilinos && event.key.toLowerCase() === 'h' && !isTyping) {
            if (modal.style.display === 'block') {
                closeModal();  // Si el modal está abierto, lo cerramos
            } else {
                openModal();   // Si el modal está cerrado, lo abrimos
            }
        }
    });
    

    // Cerrar el modal al hacer clic en el botón de cierre
    closeBtn.addEventListener('click', closeModal);

    // Cerrar modal al hacer clic fuera del contenido
    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeModal();
        }
    });

    // Buscar historial dinámicamente mientras se escribe
    inputTower.addEventListener('input', async () => {
        const tower = inputTower.value.trim();

        if (!tower) {
            resultadosTable.innerHTML = ''; // Limpiar resultados si el campo está vacío
            return;
        }

        try {
            const response = await fetch('/getHistorial', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tower })
            });

            const data = await response.json();

            if (data.success) {
                // Limpiar la tabla
                resultadosTable.innerHTML = '';

                // Llenar la tabla con los resultados
                data.historial.forEach((row) => { 
                    const tr = document.createElement('tr');
                    const estado = row.fechaSalida ? row.fechaSalida : 'Activo';
                    const claseEstado = row.fechaSalida ? '' : 'estado-activo';
                    tr.innerHTML = `
                        <td>${row.id}</td>
                        <td>${row.nombre}</td>
                        <td>${row.torre}</td>
                        <td>${row.fechaEntrada}</td>
                        <td class="${claseEstado}">${estado}</td>
                    `;
                    resultadosTable.appendChild(tr);
                });
                
            } else {
                resultadosTable.innerHTML = '<tr><td colspan="5">Sin resultados</td></tr>';
            }
        } catch (error) {
            console.error('Error al obtener el historial:', error);
            alert('Ocurrió un error al obtener los datos.');
        }
    });
});

// modal editar
document.addEventListener('DOMContentLoaded', () => {
    const modalEdit = document.getElementById('modalEdit');
    const openBtns = document.querySelectorAll('.btn-edit');
    const closeModalBtn = modalEdit.querySelector('.close-btn');
    const editForm = document.getElementById('editForm');

    // Crear instancia de Notyf
    const notyf = new Notyf({
        position: {
            x: 'right',  // Puedes usar 'right' o 'left' para la posición horizontal
            y: 'top',    // Puedes usar 'top' o 'bottom' para la posición vertical
        },
        duration: 4000, // Duración de la notificación (en milisegundos)
    });

    // Función para convertir una fecha en formato yyyy-mm-dd a dd-mm-yyyy
    function formatDateToDMY(dateString) {
        const date = new Date(dateString);
        const day = String(date.getDate()).padStart(2, '0'); // Asegurarse de que el día tenga dos dígitos
        const month = String(date.getMonth() + 1).padStart(2, '0'); // El mes en JavaScript es 0-indexado
        const year = date.getFullYear();
        return `${day}-${month}-${year}`;
    }

    // Función para convertir una fecha en formato dd-mm-yyyy a yyyy-mm-dd
    function formatDateToYMD(dateString) {
        const [day, month, year] = dateString.split('-');
        return `${year}-${month}-${day}`;
    }

    // Abrir el modal al hacer clic en el botón de editar
    openBtns.forEach((btn) => {
        btn.addEventListener('click', (event) => {
            const tr = event.target.closest('tr'); // Obtener el <tr> al que pertenece el botón
            const tenantId = tr.getAttribute('data-id');
            const name = tr.getAttribute('data-name');
            const idValue = tr.getAttribute('data-idvalue');
            const tower = tr.getAttribute('data-tower');
            const startDate = tr.getAttribute('data-startdate');
            
            // Rellenar el formulario con los datos del inquilino
            document.getElementById('editName').value = name;
            document.getElementById('editIdValue').value = idValue;
            document.getElementById('editTower').value = tower;

            // Convertir la fecha de yyyy-mm-dd a dd-mm-yyyy y precargarla
            document.getElementById('editStartDate').value = formatDateToDMY(startDate);

            // Mostrar el modal
            modalEdit.style.display = 'block';
            setTimeout(() => modalEdit.classList.add('show'), 10);

            // Guardar el tenantId en el formulario para enviarlo con la solicitud
            document.getElementById('editForm').setAttribute('data-tenant-id', tenantId);
        });
    });

    // Cerrar el modal al hacer clic en la "x"
    closeModalBtn.addEventListener('click', () => {
        modalEdit.classList.remove('show');
        setTimeout(() => (modalEdit.style.display = 'none'), 600);
    });

    // Cerrar modal al hacer clic fuera del contenido
    window.addEventListener('click', (e) => {
        if (e.target === modalEdit) {
            modalEdit.classList.remove('show');
            setTimeout(() => (modalEdit.style.display = 'none'), 600);
        }
    });

    // Enviar los cambios de edición al servidor
    editForm.addEventListener('submit', async (event) => {
        event.preventDefault(); // Evitar que el formulario se envíe de forma tradicional
        
        // Obtener los nuevos valores
        const name = document.getElementById('editName').value;
        const idValue = document.getElementById('editIdValue').value;
        const tower = document.getElementById('editTower').value;
        const startDate = document.getElementById('editStartDate').value;
        const tenantId = editForm.getAttribute('data-tenant-id'); // Obtener el tenantId desde el formulario

        // Convertir la fecha de dd-mm-yyyy a yyyy-mm-dd
        const formattedStartDate = formatDateToYMD(startDate);
        
        try {
            const response = await fetch('/updateTenant', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    tenantId,
                    updatedData: {
                        name,
                        idValue,
                        tower,
                        startDate: formattedStartDate // Enviar la fecha en formato yyyy-mm-dd
                    }
                })
            });

            const data = await response.json();
            if (data.success) {
                // Mostrar notificación exitosa
                notyf.success('Inquilino actualizado con éxito');
                
                // Cerrar el modal
                modalEdit.classList.remove('show');
                setTimeout(() => (modalEdit.style.display = 'none'), 600);
                
                setTimeout(() => {
                    window.location.reload();  // Recarga la página
                }, 4000); 
            } else {
                // Mostrar notificación de error
                notyf.error('Error al actualizar el inquilino');
            }
        } catch (error) {
            console.error('Error al enviar los cambios:', error);
            notyf.error('Hubo un error al intentar actualizar.');
        }
    });
});







