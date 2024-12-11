document.addEventListener("DOMContentLoaded", function () {
    const towerInput = document.getElementById("tower");
    const nameInputVisitor = document.getElementById("Name");
    const nameInput = document.getElementById("newName");
    const towerSuggestions = document.getElementById("towerSuggestions");
    const nameSuggestions = document.getElementById("nameSuggestions");
    const form = document.getElementById("visitorForm");
    const showFormButton = document.getElementById("showFormButton");
    const cancelFormButton = document.getElementById("cancelFormButton");
    const table = document.getElementById("visitorTableBody");
    const cedulaInput = document.getElementById("idValue");
    const roleInput = document.getElementById("role");
    const ownerInput = document.getElementById("ownerType");
    const notyf = new Notyf({
        position: {
            x: 'right',  // Puedes usar 'right' o 'left' para la posición horizontal
            y: 'top',    // Puedes usar 'top' o 'bottom' para la posición vertical
        },
        duration: 4000, // Duración de la notificación (en milisegundos)
        ripple: true,   // Efecto de onda al mostrar la notificación
    });

    let data = {};  // Para almacenar la relación entre torre y propietario
    let visitors = []; // Lista de visitantes obtenida del backend

    let counter = 1; // Contador para IDs de visitantes

    // Función para mostrar las sugerencias
    function showSuggestions(input, list, suggestions) {
        list.innerHTML = "";
        if (suggestions.length === 0) {
            list.classList.add("hidden");
        } else {
            list.classList.remove("hidden");
        }
        
        suggestions.forEach((suggestion) => {
            const div = document.createElement("div");
            div.textContent = suggestion;
            div.addEventListener("click", function () {
                input.value = suggestion;
                list.classList.add("hidden");

                // Llenar los campos relacionados con la torre o el nombre
                if (input === towerInput && data[suggestion]) {
                    nameInput.value = data[suggestion] || "";
                } else if (input === nameInputVisitor) {
                    towerInput.value = Object.keys(data).find(
                        (key) => data[key] === suggestion
                    ) || "";

                    // Actualizar los campos de visitante basado en el nombre seleccionado
                    const selectedVisitor = visitors.find(visitor => visitor.nombre === suggestion);
                    if (selectedVisitor) {
                        cedulaInput.value = selectedVisitor.cedula;
                        roleInput.value = selectedVisitor.rol;
                        ownerInput.value = selectedVisitor.propietario_id;
                    }
                }
            });
            list.appendChild(div);
        });
    }

    // Función de debounce para mejorar rendimiento
    function debounce(func, delay) {
        let timeout;
        return function (...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), delay);
        };
    }

    // Manejar entradas del usuario con debounce para la torre
    towerInput.addEventListener(
        "input",
        debounce(function () {
            const query = towerInput.value.trim().toLowerCase();
            const filteredTowers = Object.keys(data).filter((tower) =>
                tower.toLowerCase().includes(query)
            );
            showSuggestions(towerInput, towerSuggestions, filteredTowers);
        }, 300)
    );

    // Manejar entradas del usuario con debounce para los nombres de los visitantes
    nameInputVisitor.addEventListener(
        "input",
        debounce(function () {
            const query = nameInputVisitor.value.trim().toLowerCase();
            const filteredNames = visitors.filter(visitor =>
                visitor.nombre.toLowerCase().includes(query)
            ).map(visitor => visitor.nombre);
            showSuggestions(nameInputVisitor, nameSuggestions, filteredNames);
        }, 300)
    );

    // Cargar datos desde el backend (torres y propietarios)
    fetch("/get_towers_and_owners")
        .then((response) => response.json())
        .then((result) => {
            data = result; // Guardar los datos de torres y propietarios para autocompletar
        })
        .catch((error) => {
            console.error("Error al obtener los datos del backend:", error);
        });

    // Cargar los datos de los visitantes
    fetch("/get_visitor_data")
        .then((response) => response.json())
        .then((result) => {
            visitors = result; // Guardar los datos de los visitantes para autocompletar
        })
        .catch((error) => {
            console.error("Error al obtener los visitantes:", error);
        });

    // Ocultar sugerencias al hacer clic fuera
    document.addEventListener("click", function (e) {
        if (!towerInput.contains(e.target) && !towerSuggestions.contains(e.target)) {
            towerSuggestions.classList.add("hidden");
        }
        if (!nameInputVisitor.contains(e.target) && !nameSuggestions.contains(e.target)) {
            nameSuggestions.classList.add("hidden");
        }
    });

    // Mostrar el formulario al hacer clic en el botón
    showFormButton.addEventListener("click", function () {
        form.classList.remove("hidden");
        showFormButton.classList.add("hidden");
    });

    // Ocultar el formulario al hacer clic en "Cancelar"
    cancelFormButton.addEventListener("click", function () {
        form.classList.add("hidden");
        showFormButton.classList.remove("hidden");
    });

    // Manejar el envío del formulario
    form.addEventListener("submit", function (event) {
        event.preventDefault(); // Evitar el envío del formulario

        const name = nameInputVisitor.value.trim();
        const idValue = cedulaInput.value.trim();
        const role = roleInput.value.trim();
        const tower = towerInput.value.trim();
        const ownerType = nameInput.value.trim();

        if (name && idValue && role && tower && ownerType) {
            // Obtener el próximo ID desde el backend
            fetch("/get_next_id")
                .then(response => response.json())
                .then(data => {
                    if (!data.next_id) {
                        throw new Error("No se pudo obtener el siguiente ID.");
                    }

                    const uniqueId = data.next_id; // ID único obtenido del backend
                    const date = new Date();
                    const formattedDate = `${date.getDate()}/${date.getMonth() + 1}/${date.getFullYear()}`;
                    const formattedTime = format12HourTime(date); // Hora de entrada

                    // Crear la fila de la tabla
                    const newRow = document.createElement("tr");
                    newRow.setAttribute("id", uniqueId); // Asignar el ID único al elemento <tr>
                    newRow.innerHTML = `
                        <td>${uniqueId}</td>
                        <td>${formattedDate}</td>
                        <td>${name}</td>
                        <td>${idValue}</td>
                        <td>${role}</td>
                        <td>${tower}</td>
                        <td>${ownerType}</td>
                        <td>${formattedTime}</td>
                        <td class="exitCell">
                            <button class="markExit">Marcar Salida</button>
                        </td>
                    `;

                    // Agregar evento para "Marcar Salida"
                    newRow.querySelector(".markExit").addEventListener("click", function () {
                        const exitDate = new Date();
                        const exitTime = format12HourTime(exitDate);

                        const exitCell = this.parentElement;
                        exitCell.textContent = exitTime;

                        // Utilizar el ID único de la fila
                        const rowId = newRow.getAttribute("id");

                        fetch("/mark_exit", {
                            method: "POST",
                            headers: {
                                "Content-Type": "application/x-www-form-urlencoded", // Tipo de contenido
                            },
                            body: new URLSearchParams({
                                visitor_id: rowId,
                                exit_time: exitTime,
                            }),
                        })
                            .then((response) => response.json())
                            .then((data) => {
                                if (data.message) {
                                    notyf.success(data.message);
                                } else {
                                    notyf.error(data.message);
                                }
                            })
                            .catch((error) => {
                                console.error("Error al marcar salida:", error);
                            });
                    });

                    table.appendChild(newRow);

                    // Enviar los datos al backend (a /add_visitor)
                    fetch("/add_visitor", {
                        method: "POST",
                        body: new URLSearchParams({
                            name: name,
                            idValue: idValue,
                            role: role,
                            tower: tower,
                            ownerType: ownerType,
                            date: formattedDate,
                            entryTime: formattedTime,
                        }),
                    })
                        .then((response) => response.json())
                        .then((data) => {
                            if (data.message) {
                                notyf.success(data.message);
                            } else {
                                notyf.error(data.message || "Error desconocido al agregar visitante.");
                            }
                        })
                        .catch((error) => {
                            console.error("Error al agregar visitante:", error);
                            notyf.error("Error al agregar visitante. Intenta nuevamente.");
                        });

                    // Enviar los mismos datos a la ruta /add_visit
                    fetch("/add_visit", {
                        method: "POST",
                        body: new URLSearchParams({
                            name: name,
                            idValue: idValue,
                            role: role,
                            tower: tower,
                            ownerType: ownerType,
                            date: formattedDate,
                            entryTime: formattedTime,
                        }),
                    })
                        .then((response) => response.json())
                        .then((data) => {
                            if (data.message) {
                                notyf.success(data.message);
                            } else {
                                notyf.error(data.message || "Error desconocido al agregar visita.");
                            }
                        })
                        .catch((error) => {
                            console.error("Error al agregar visita:", error);
                            notyf.error("Error al agregar visita. Intenta nuevamente.");
                        });

                    // Reseteo del formulario y cambios en la interfaz
                    form.reset();
                    form.classList.add("hidden");
                    showFormButton.classList.remove("hidden");

                })
                .catch(error => {
                    console.error("Error al obtener el siguiente ID:", error);
                    alert("Error al generar un nuevo visitante. Intente nuevamente.");
                });
        } else {
            alert("Por favor, complete todos los campos.");
        }
    });


    // Función para formatear la hora en formato de 12 horas
    function format12HourTime(date) {
        let hours = date.getHours();
        const minutes = date.getMinutes();
        const ampm = hours >= 12 ? "PM" : "AM";
        hours = hours % 12 || 12; // Convertir a formato de 12 horas
        return `${hours}:${minutes.toString().padStart(2, "0")} ${ampm}`;
    }
});




document.addEventListener("DOMContentLoaded", () => {
    // Menú desplegable de usuario
    const userIcon = document.querySelector(".user-icon");
    const dropdownMenu = document.querySelector(".user-dropdown .dropdown-menu");

    userIcon.addEventListener("click", () => {
        dropdownMenu.classList.toggle("active");
    });

    document.addEventListener("click", (event) => {
        if (!userIcon.contains(event.target) && !dropdownMenu.contains(event.target)) {
            dropdownMenu.classList.remove("active");
        }
    });

    // Sidebar Toggle
    const sidebar = document.querySelector(".sidebar");
    const content = document.querySelector(".content");
    const toggleButton = document.getElementById("toggleSidebar");
    const arrowIcon = toggleButton.querySelector("i");

    toggleButton.addEventListener("click", () => {
        sidebar.classList.toggle("hidden");
        content.classList.toggle("expanded");

        if (sidebar.classList.contains("hidden")) {
            arrowIcon.style.transform = "rotate(0deg)";
        } else {
            arrowIcon.style.transform = "rotate(180deg)";
        }
    });

    let lastScrollTop = 0;
    const topBar = document.querySelector('.top-bar');

    window.addEventListener('scroll', function() {
        let currentScroll = window.pageYOffset || document.documentElement.scrollTop;

        // Si el scroll es hacia abajo y se ha desplazado más de 10px, oculta el top-bar
        if (currentScroll > lastScrollTop && currentScroll > 10) {
            topBar.classList.add('hidden'); // Añadir la clase 'hidden' para ocultar
        } else if (currentScroll < lastScrollTop) {
            topBar.classList.remove('hidden'); // Elimina la clase 'hidden' para mostrar
        }
        
        // Actualiza la posición del último scroll
        lastScrollTop = currentScroll <= 0 ? 0 : currentScroll; // Evita valores negativos
    });
});

    // // Función para verificar la sesión cada 5 segundos
    // // setInterval(function() {
    // //     fetch('/check_session')
    // //         .then(response => {
    // //             if (response.status === 401) {
    // //                 Si el usuario no está logueado, redirige al login
    // //                 window.location.href = "/login";
    // //             } else {
    // //                 Si está logueado, obtiene la respuesta y puede hacer algo con ella
    // //                 response.json().then(data => {
    // //                     console.log("Usuario logueado:", data.username);
    // //                 });
    // //             }
    // //         })
    // //         .catch(error => {
    // //             console.log("Error al verificar la sesión:", error);
    // //         });
    // // }, 1000);  // 5000 ms = 5 segundos