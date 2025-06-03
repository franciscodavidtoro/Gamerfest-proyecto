function crearCuenta() {
  const username = document.querySelector('input[placeholder="Nombre de usuario"]').value.trim();
  const apellido = document.querySelector('input[placeholder="Apellido"]').value.trim();
  const correo = document.querySelector('input[placeholder="correo"]').value.trim();
  const password = document.getElementById('password').value.trim();
  const rolSeleccionado = document.querySelector('input[name="rol"]:checked');

  if (!username || !apellido || !correo || !password || !rolSeleccionado) {
    Swal.fire({
      icon: 'error',
      title: 'Faltan campos por llenar',
      text: 'Por favor, completa todos los campos antes de continuar.'
    });
    return;
  }

  // Crear correo completo
  const emailCompleto = correo + "@example.com";

  // Obtener usuarios existentes
  let usuarios = JSON.parse(localStorage.getItem('usuarios')) || [];

  // Verificar si ya existe ese nombre de usuario
  const existe = usuarios.some(u => u.username === username);
  if (existe) {
    Swal.fire({
      icon: 'error',
      title: 'Usuario existente',
      text: 'El nombre de usuario ya está registrado.'
    });
    return;
  }

  // Agregar nuevo usuario
  usuarios.push({
    username,
    apellido,
    email: emailCompleto,
    password,
    rol: rolSeleccionado.value
  });

  // Guardar en localStorage
  localStorage.setItem('usuarios', JSON.stringify(usuarios));

  Swal.fire({
    icon: 'success',
    title: 'Cuenta creada',
    text: 'Tu cuenta ha sido registrada exitosamente.',
    confirmButtonText: 'Iniciar sesión'
  }).then(() => {
    window.location.href = 'inicio_sesion.html'; // cambia si tu página de login tiene otro nombre
  });
}





function redirigirPorRol() {
  const username = document.querySelector('input[aria-label="Username"]').value.trim();
  // Si usas contraseña, recógela igual:
  // const password = document.getElementById('password').value.trim();

  if (!username) {
    alert("Por favor, ingresa el usuario");
    return;
  }

  let usuarios = JSON.parse(localStorage.getItem('usuarios')) || [];

  // Buscar usuario en la lista
  const usuarioEncontrado = usuarios.find(u => u.username === username);

  if (!usuarioEncontrado) {
    alert("Usuario no registrado");
    return;
  }

  // Aquí podrías validar contraseña si la tienes

  // Guardar rol en localStorage para usar en otras páginas
  localStorage.setItem('rolUsuario', usuarioEncontrado.rol);
  localStorage.setItem('username', usuarioEncontrado.username);

  // Redirigir según el rol
  switch (usuarioEncontrado.rol) {
    case 'profesor':
      window.location.href = 'tutor_page.html';
      break;
    case 'alumno':
      window.location.href = 'alumno_page.html';
      break;
    case 'coordinador':
      window.location.href = 'coordinador_page.html';
      break;
    default:
      alert('Rol no reconocido');
  }
}
