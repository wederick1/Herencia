document.addEventListener('DOMContentLoaded', () => {
    const versions = [
      { version: "v1.0", details: "Primera versión lanzada con funcionalidades básicas." },
      { version: "v1.1", details: "Se mejoraron algunas optimizaciones de rendimiento." },
      { version: "v1.2", details: "Añadido soporte para nuevas plataformas." },
      { version: "v2.0", details: "Gran actualización con nueva interfaz de usuario y nuevas características." },
      { version: "v2.1", details: "Corrección de bugs menores y mejoras de seguridad." },
    ];
  
    const branchesContainer = document.querySelector('.branches');
    const versionDetails = document.getElementById('version-details');
  
    // Crear ramas del árbol con las versiones
    versions.forEach((versionObj, index) => {
      const branch = document.createElement('div');
      branch.classList.add('branch');
      branch.innerText = versionObj.version;
      branch.dataset.index = index;
      
      // Cuando se hace clic en una versión, mostrar detalles
      branch.addEventListener('click', () => {
        const currentVersion = versions[branch.dataset.index];
        versionDetails.innerText = currentVersion.details;
        versionDetails.style.display = 'block';
        
        // Marcar la versión activa
        document.querySelectorAll('.branch').forEach(branch => branch.classList.remove('active'));
        branch.classList.add('active');
      });
  
      branchesContainer.appendChild(branch);
    });
  });
  