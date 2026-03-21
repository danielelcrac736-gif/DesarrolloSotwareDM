# 👥 Gestión de Usuarios - Prototipo

Sistema completo para la gestión de usuarios con autenticación, CRUD y base de datos SQLite.

## 🚀 Características

- ✅ **Autenticación**: Login seguro con JWT
- ✅ **CRUD Completo**: Crear, Leer, Actualizar, Eliminar usuarios
- ✅ **Base de Datos**: SQLite local
- ✅ **Interfaz Moderna**: UI responsive y amigable
- ✅ **Estados de Usuario**: Activar/Desactivar usuarios
- ✅ **Búsqueda**: Filtrar usuarios por nombre o email
- ✅ **Contraseñas Encriptadas**: Usando bcrypt

## 📋 Requisitos

- Node.js (versión 14 o superior)
- npm (incluido con Node.js)

## 🔧 Instalación y Ejecución

### 1. Instalar dependencias del Backend

```bash
cd backend
npm install
```

### 2. Iniciar el Servidor

```bash
npm start
```

El servidor se iniciará en `http://localhost:3000`

Verás un mensaje como:
```
✅ Servidor ejecutándose en http://localhost:3000
📝 Gestión de Usuarios iniciado

🔐 Credenciales de prueba:
   Email: admin@example.com
   Contraseña: 123456
```

### 3. Abrir la Interfaz

En otra terminal o navegador, abre:
```
file:///ruta/a/frontend/index.html
```

O simplemente arrastra el archivo `index.html` al navegador.

## 🔐 Credenciales de Prueba

```
Email: admin@example.com
Contraseña: 123456
```

## 📂 Estructura del Proyecto

```
usuarios-app/
├── backend/
│   ├── package.json          # Dependencias
│   ├── server.js             # Servidor Express
│   ├── db.js                 # Configuración SQLite
│   └── usuarios.db           # Base de datos (se crea automáticamente)
│
└── frontend/
    ├── index.html            # Página principal
    └── assets/
        ├── css/
        │   └── styles.css    # Estilos
        └── js/
            └── app.js        # Lógica de la aplicación
```

## 🛠️ API REST Endpoints

### Autenticación

```
POST /api/login
Body: { email, contraseña }
Response: { token, usuario }
```

### Usuarios (requieren token)

```
GET /api/usuarios                    # Obtener todos los usuarios
GET /api/usuarios/:id                # Obtener usuario por ID
POST /api/usuarios                   # Crear nuevo usuario
PUT /api/usuarios/:id                # Actualizar usuario
DELETE /api/usuarios/:id             # Eliminar usuario
PATCH /api/usuarios/:id/estado       # Cambiar estado (activo/inactivo)
```

**Headers requeridos para todas las rutas protegidas:**
```
Authorization: Bearer <token>
```

## 🎯 Funcionalidades del Sistema

### Login
- Ingresa con tus credenciales
- Genera token JWT válido por 24 horas
- Sesión persistente en localStorage

### Gestión de Usuarios
1. **Crear Usuario**
   - Formulario para ingresar nombre, email y contraseña
   - Validación de email único
   - Contraseña encriptada con bcrypt

2. **Ver Usuarios**
   - Lista de todos los usuarios registrados
   - Muestra nombre, email y estado
   - Fecha de creación

3. **Editar Usuario**
   - Click en "Editar" para modificar datos
   - Opcional cambiar contraseña
   - Modificar estado (activo/inactivo)

4. **Eliminar Usuario**
   - Confirmación antes de eliminar
   - No se puede eliminar usuario admin

5. **Buscar Usuarios**
   - Búsqueda en tiempo real
   - Por nombre o email

## 🔒 Seguridad

- Contraseñas encriptadas con bcrypt (10 rondas)
- Tokens JWT para autenticación
- Validación de entrada en el backend
- CORS habilitado para desarrollo
- Email único en la base de datos

## 📱 Diseño Responsive

- Funciona en desktop, tablet y móvil
- Interfaz adaptativa
- Navegación intuitiva

## 🐛 Solución de Problemas

### Puerto 3000 en uso
Si el puerto 3000 está en uso, modifica el puerto en `server.js`:
```javascript
const PORT = 3001; // Cambiar a otro puerto
```

### Error de conexión
Asegúrate de que:
1. El servidor backend está corriendo
2. La URL en `app.js` (API_URL) es correcta
3. CORS está habilitado

### Base de datos corrupta
Elimina el archivo `usuarios.db` para crear una nueva:
```bash
rm backend/usuarios.db
npm start
```

## 📝 Notas de Desarrollo

- La base de datos SQLite se crea automáticamente al iniciar
- Usuario admin se inserta automáticamente la primera vez
- Los tokens expiran en 24 horas
- Implementar autenticación más robusta para producción

## 🚀 Próximas Mejoras

- [ ] Autenticación con redes sociales
- [ ] Recuperación de contraseña
- [ ] Roles y permisos
- [ ] Historial de auditoría
- [ ] Validación más completa
- [ ] Temas dark/light
- [ ] Exportar datos a CSV/Excel
- [ ] Backup automático de BD

## 📄 Licencia

Este es un prototipo de demostración.

---

**¡Listo para usar! Disfruta gestionando usuarios.** 👥✨
