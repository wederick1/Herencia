const rowsPerPage = 10;
let currentPage = 1;
let data = []; // Aquí se cargarán los datos desde Flask

const tableBody = document.querySelector("#historial-table tbody");
const pagination = document.querySelector("#pagination");

// Función para obtener los datos desde Flask
async function fetchData() {
    try {
        const response = await fetch('/api/historial');
        if (!response.ok) throw new Error("Error al obtener los datos");
        data = await response.json();
        renderTable();  // Renderiza la tabla con los primeros 10 registros
        renderPagination(); // Renderiza la paginación
    } catch (error) {
        console.error(error);
        alert("No se pudieron cargar los datos.");
    }
}

// Función para renderizar la tabla con los datos de la página actual
function renderTable(page = 1) {
    tableBody.innerHTML = "";
    const start = (page - 1) * rowsPerPage;
    const end = start + rowsPerPage;
    const pageData = data.slice(start, end);

    pageData.forEach(row => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${row.id}</td>
            <td>${row.fecha}</td>
            <td>${row.nombre}</td>
            <td>${row.identificacion}</td>
            <td>${row.rol}</td>
            <td>${row.torre}</td>
            <td>${row.propietario}</td>
            <td>${row.hora_entrada}</td>
            <td>${row.hora_salida || ""}</td>
        `;
        tableBody.appendChild(tr);
    });
}

// Función para renderizar la paginación
function renderPagination() {
    pagination.innerHTML = "";
    const totalPages = Math.ceil(data.length / rowsPerPage);

    for (let i = 1; i <= totalPages; i++) {
        const button = document.createElement("button");
        button.textContent = i;
        button.className = i === currentPage ? "disabled" : "";
        button.addEventListener("click", () => {
            if (i !== currentPage) {
                currentPage = i;
                renderTable(i);
                renderPagination();
            }
        });
        pagination.appendChild(button);
    }
}

// Función para filtrar los datos con base en nombre, torre y propietario
function filterTable() {
    const input = document.getElementById("search-input");
    const filter = input.value.toLowerCase();

    // Filtra los datos en memoria (sin importar la paginación)
    const filteredData = data.filter(row => {
        const nombre = row.nombre.toLowerCase();
        const torre = row.torre.toLowerCase();
        const propietario = row.propietario.toLowerCase();
        
        return nombre.includes(filter) || torre.includes(filter) || propietario.includes(filter);
    });

    // Actualiza la tabla con los resultados filtrados
    currentPage = 1;  // Resetear a la primera página para mostrar los resultados desde el principio
    renderFilteredTable(filteredData);  // Actualizar la tabla con los datos filtrados
    renderFilteredPagination(filteredData);  // Actualizar la paginación con los datos filtrados
}

// Función para renderizar la tabla con los resultados filtrados
function renderFilteredTable(filteredData) {
    tableBody.innerHTML = "";
    const start = (currentPage - 1) * rowsPerPage;
    const end = start + rowsPerPage;
    const pageData = filteredData.slice(start, end);

    pageData.forEach(row => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${row.id}</td>
            <td>${row.fecha}</td>
            <td>${row.nombre}</td>
            <td>${row.identificacion}</td>
            <td>${row.rol}</td>
            <td>${row.torre}</td>
            <td>${row.propietario}</td>
            <td>${row.hora_entrada}</td>
            <td>${row.hora_salida || ""}</td>
        `;
        tableBody.appendChild(tr);
    });
}

// Función para renderizar la paginación con los resultados filtrados
function renderFilteredPagination(filteredData) {
    pagination.innerHTML = "";
    const totalPages = Math.ceil(filteredData.length / rowsPerPage);

    for (let i = 1; i <= totalPages; i++) {
        const button = document.createElement("button");
        button.textContent = i;
        button.className = i === currentPage ? "disabled" : "";
        button.addEventListener("click", () => {
            if (i !== currentPage) {
                currentPage = i;
                renderFilteredTable(filteredData);  // Actualizar la tabla con los resultados de la página actual
                renderFilteredPagination(filteredData);  // Actualizar la paginación con los resultados filtrados
            }
        });
        pagination.appendChild(button);
    }
}

// Evento para realizar la búsqueda mientras se escribe
document.getElementById("search-input").addEventListener("keyup", filterTable);

// Inicializa los datos
fetchData();

document.getElementById("export-button").addEventListener("click", exportToExcel);

document.getElementById("export-button").addEventListener("click", exportToExcel);

function exportToExcel() {
    // Verifica que los datos estén disponibles
    if (!data || data.length === 0) {
        alert("No hay datos para exportar.");
        return;
    }

    // Convierte los datos en una hoja de cálculo
    const worksheet = XLSX.utils.json_to_sheet(data); // `data` es tu arreglo
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "Historial");

    // Genera el archivo Excel y lo descarga
    XLSX.writeFile(workbook, "historial.xlsx");
}
