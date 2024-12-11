document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault();  // Evita que el formulario se envíe de forma predeterminada

    // Obtener los datos del formulario
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    // Realizar la solicitud POST al servidor
    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `username=${username}&password=${password}`
    })
    .then(response => response.json())  // Convertir la respuesta a JSON
    .then(data => {
        const errorBox = document.getElementById('error-box');
        const errorMessage = document.getElementById('error-message');

        if (data.error) {
            // Si hay un error en la respuesta, mostramos el mensaje de error
            errorMessage.textContent = data.error;
            errorBox.classList.add('show');  // Mostrar el cuadro de error
        } else if (data.message) {
            // Si la respuesta es exitosa, redirigir
            window.location.href = '/home';  // Redirige a la página principal
        }

        // Desaparecer el mensaje de error después de 3 segundos
        setTimeout(() => {
            errorBox.classList.remove('show');  // Elimina la clase 'show' para ocultarlo
        }, 3000);  // 3000 milisegundos = 3 segundos
    })
    .catch(error => {
        console.error('Error:', error);
        const errorMessage = document.getElementById('error-message');
        errorMessage.textContent = 'Usuario y/o contraseña incorrectos';
        const errorBox = document.getElementById('error-box');
        errorBox.classList.add('show');  // Mostrar el cuadro de error

        // Desaparecer el mensaje de error después de 3 segundos
        setTimeout(() => {
            errorBox.classList.remove('show');  // Elimina la clase 'show' para ocultarlo
        }, 3000);  // 3000 milisegundos = 3 segundos
    });
});
