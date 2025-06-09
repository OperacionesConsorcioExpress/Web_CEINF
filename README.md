# Web_CEINF

Sitio web estático para el Centro de Información CEINF, diseñado para alojarse en GitHub Pages.

## ✅ Características

- Página de inicio (`index.html`) con navegación.
- Página de encuesta (`pages/forms_redirect.html`) que cambia dinámicamente según el reporte.
- Página de contacto (`pages/contacto.html`).
- Estilos personalizados en `css/estilos.css`.
- Estructura moderna y funcional.

## 📁 Project Structure

```
/
Web_CEINF/
├── index.html               ← Página de inicio con menú y contenido
├── css/
│   └── estilos.css          ← Estilos globales (ya lo tienes)
├── pages/
│   ├── contacto.html        ← Formulario de información del proceso
│   └── forms_redirect.html  ← Formulario de Encuesta
└── images/
    └── logo.png

```

## ▶️ Cómo ejecutar localmente

1. Abre la carpeta en Visual Studio Code.
2. Haz clic derecho sobre `index.html` y elige **"Abrir con Live Server"** (si tienes instalada la extensión).
3. También puedes abrir el archivo directamente en tu navegador.

## 🚀 Cómo desplegar en GitHub Pages

1. Ve a **Settings > Pages** del repositorio.
2. En **Source**, elige `gh-pages` (o `main`) y carpeta `/ (root)`.
3. Tu sitio estará disponible en:

```
https://<usuario>.github.io/Web_CEINF/
```

## 📁 Estructura

- `index.html`: Página principal
- `css/estilos.css`: Estilos globales
- `pages/forms_redirect.html`: Formulario embebido por parámetro `reporte`
- `pages/contacto.html`: Página de contacto
- `images/`, `docs/`: Carpetas opcionales para contenido adicional
