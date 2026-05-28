## Proceso de desarrollo por commits

El proyecto fue construido de forma progresiva, separando estructura, estilos, interacciones y documentación para que el historial de Git muestre una evolución clara del frontend.

### Commit 1 — Primera versión visual de la landing

**Commit:** `feat: add initial landing page shell`

Se creó la base inicial del sitio con la estructura principal de `index.html`, el archivo base de estilos `css/styles.css`, el favicon y la imagen principal del producto.

Este primer avance incluyó:

* Header básico
* Hero principal visible
* Título del producto
* Texto descriptivo
* Botones de llamada a la acción
* Imagen principal
* Tokens iniciales de CSS
* Responsive mínimo
* Diagramas iniciales de arquitectura y secuencia como documentación de proyección futura

En este punto también se agregaron los diagramas técnicos para documentar cómo podría evolucionar el proyecto hacia una arquitectura con backend, base de datos y pagos. Estos diagramas no son una dependencia funcional de la landing actual, sino una proyección técnica.

---

### Commit 2 — Assets y base visual del producto

**Commit:** `chore: add product visual assets`

Se organizaron los recursos visuales necesarios para que la landing pudiera cargar correctamente las imágenes y assets locales.

Este avance incluyó:

* Carpeta de imágenes del producto
* Recursos visuales de galería
* Organización de assets
* Preparación de rutas para el hero y secciones visuales

Este paso permitió que las siguientes secciones pudieran desarrollarse sin depender de imágenes externas.

---

### Commit 3 — Secciones principales de contenido

**Commit:** `feat: add product content sections`

Se agregaron las secciones principales de contenido de la landing.

Este avance incluyó:

* Sección de características
* Galería base
* Especificaciones técnicas
* Tabla comparativa
* Testimonios
* FAQ en HTML
* Footer informativo

El objetivo de este commit fue completar la estructura semántica del contenido antes de trabajar el pulido visual y las interacciones.

---

### Commit 4 — Estilos completos de la landing

**Commit:** `feat: complete landing page visual styling`

Se completó el diseño visual de la landing sobre la estructura creada previamente.

Este avance incluyó:

* Cards con estilo premium
* Grid de galería
* Estilos para tablas
* Estilos para FAQ
* Footer responsive
* Sombras
* Estados hover
* Espaciados finales
* Responsive más completo

Este commit separó la estructura del contenido del diseño final, manteniendo un historial más claro y profesional.

---

### Commit 5 — Interacciones generales

**Commit:** `feat: add landing page interactions`

Se agregaron las interacciones principales de la landing en JavaScript vanilla.

Este avance incluyó:

* Conexión de `js/main.js`
* Cambio de tema claro / oscuro
* Persistencia de tema con `localStorage`
* FAQ accordion
* Galería expandible
* Lightbox con controles
* Cierre con tecla `Escape`
* Scroll suave
* Año dinámico del footer
* Formulario de leads con feedback local

Este commit mantuvo las interacciones generales separadas de la lógica del carrito y del asistente.

---

### Commit 6 — Carrito local

**Commit:** `feat: add local cart experience`

Se agregó una experiencia de carrito local sin backend.

Este avance incluyó:

* Archivo `js/cart.js`
* Botón de agregar al carrito
* Contador en el header
* Sección de carrito
* Control de cantidad
* Cálculo de subtotal
* Persistencia con `localStorage`
* Mensajes de feedback
* Botón de checkout con fallback hacia cotización
* Estilos del carrito

El carrito funciona completamente en frontend y no depende de base de datos, Stripe ni API externa.

---

### Commit 7 — Pulido estático del frontend

**Commit:** `refactor: polish static landing frontend`

Se revisó y pulió el frontend completo para dejarlo funcional como sitio estático.

Este avance incluyó:

* Limpieza de estructura HTML
* Corrección de estilos inconsistentes
* Mejoras responsive
* Revisión de interacciones locales
* Eliminación de dependencias innecesarias de backend
* Ajustes para que la landing funcione correctamente sin servicios externos

El objetivo fue dejar la entrega principal lista como frontend estático, estable y usable.

---

### Commit 8 — Asistente de producto

**Commit:** `feat: add product assistant widget`

Se agregó un asistente flotante de producto con respuestas locales.

Este avance incluyó:

* Archivo `js/assistant.js`
* Botón flotante del asistente
* Panel de chat
* Formulario de mensaje
* Respuestas locales sobre el producto
* Fallback para preguntas no reconocidas
* Cierre accesible
* Soporte para tecla `Escape`
* Estilos del widget

El asistente no requiere backend ni API externa para funcionar en esta entrega.

---

### Commit 9 — Accesibilidad y responsive final

**Commit:** `refactor: improve accessibility and responsive polish`

Se aplicaron mejoras finales de accesibilidad y comportamiento responsive.

Este avance incluyó:

* Mejoras en `aria-label`
* Uso correcto de `aria-expanded`
* Uso correcto de `aria-controls`
* Mensajes con `aria-live`
* Estados con `role="status"`
* Revisión de textos alternativos en imágenes
* Estados `focus-visible`
* Soporte para `prefers-reduced-motion`
* Mejoras responsive para mobile
* Estados disabled y loading
* Cierre accesible de modales y paneles

Este commit buscó mejorar la experiencia de usuario, navegación con teclado y adaptación a pantallas pequeñas.

---

### Commit 10 — Documentación final

**Commit:** `docs: update project readme`

Se actualizó el README para explicar el proyecto, su alcance real, las funcionalidades implementadas y la proyección arquitectónica futura.

Este avance incluyó:

* Descripción general del proyecto
* Tecnologías usadas
* Estructura del repositorio
* Instrucciones de ejecución
* Funcionalidades frontend
* Explicación del carrito local
* Explicación del asistente local
* Accesibilidad
* Responsive design
* Diagramas de arquitectura y secuencia como proyección futura
* Proceso de desarrollo por commits
* Checklist manual de pruebas

Esta documentación deja claro que la entrega actual es un frontend estático funcional, mientras que backend, base de datos, pagos e IA externa quedan como evolución futura.
