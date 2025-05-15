# Titan Core - Tema Astro
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

**Titan Core** Es un tema de alto rendimiento y lleno de funcionalidades para Astro JS, diseñado para sitios web modernos, blogs y portafolios. Con componentes de interfaz bellos, múltiples opciones de tema y un enfoque en el rendimiento, Titan Core te ayuda a construir sitios atractivos rápidamente..

[Live Demo](https://titan-core.netlify.app)

## ✨ Features

- 🎨 **Múltiples opciones de tema** - Elige entre varios temas de colo
- 📱 **Totalmente responsivo** - Se ve bien en todos los dispositivos
- 🚀 **Enfocado en rendimiento** - Optimizado para velocidad y SEO
- 📝 **Listo para blog** - Funcionalidad completa de blog con categorías y paginación
- 🔍 **SEO optimizado** - Etiquetas meta, Open Graph, Twitter Cards y sitemap
- 🧩 **Basado en componentes** - Arquitectura modular fácil de personalizar
- 🎭 **Animaciones listas** - Integración con AOS (Animate On Scroll) para animaciones suaves
- 📊 **Sección de estadísticas** - Muestra tus métricas con componentes visuales
- 🤝 **Grid de equipo** - Muestra a los miembros de tu equipo
- 🔄 **Diseños flexibles** - Secciones tipo hero, grids de funciones, paneles divididos y más
- 📋 **Componente de preguntas frecuentes** - Acordeón fácil de usar para FAQs
- 📞 **Componentes de contacto** -  - Muestra información de contacto directamente
- 🏢 **Showcase de logos** - Muestra logos de socios o clientes
- 🔘 **Componentes UI modernos** - Botones, formularios, tarjetas y más

## 🚀 Inicio rápido

```bash
# Crea un nuevo proyecto con este tema
npm create astro@latest -- --template rspisarski/titan-core

# o clona el repositorio directamente
git clone https://github.com/rspisarski/titan-core.git my-website
cd my-website
npm install
npm run dev
```

## 📁 Project Structure

```
/
├── public/             # Archivos estáticos
│   └── favicon.ico
├── src/
│   ├── assets/         # Imágenes y otros recursos
│   ├── components/     # Componentes de interfaz
│   │   ├── blog/       # Componentes específicos del blog
│   │   ├── forms/      # Formularios
│   │   ├── icons/      # Íconos
│   │   ├── sections/   # Secciones de página
│   │   ├── team/       # Componentes del equipo
│   │   └── ui/         # Componentes UI básicos
│   ├── content/        # Colecciones de contenido
│   ├── data/           # Archivos de configuración y datos
│   ├── layouts/        # Diseños de página
│   ├── pages/          # Rutas de página
│   ├── styles/         # Estilos globales
│   └── utils/          # Funciones utilitarias
└── package.json
```

## ⚙️ Configuration

Personaliza tu sitio editando los archivos en el directorio `src/data/`:

- `config.ts` - Configuración general del sitio incluyendo info de la empresa y SEO
- `menu.ts` - Estructura del menú de navegación
- `features.ts` - Contenido de la sección de características
- `faqs.ts` - Preguntas frecuentes
- `logos.ts` - Logos de socios/clientes
- `stats.ts` - Datos de estadísticas
- `categories.ts` - Categorías del blog

## 🎨 Temas

Titan Core incluye 10 temas preconfigurados inspirados en la mitología griega. Puedes elegir un tema para todo el sitio desde el archivo `themeSetting` objetos en `src/data/config.ts`:

```typescript
export const themeSetting = {
  theme: 'zeus' // Elige uno de los 10 temas disponibles
}
```

### Temas disponibles:

1. `zeus` - Tema de cielo y trueno
2. `poseidon` - Tema de los mares
3. `hades` - Tema del inframundo
4. `apollo` - Tema del sol y la luz
5. `artemis` - Tema de la luna y la caza
6. `ares` - Tema de guerra y fuego
7. `athena` - Tema de sabiduría
8. `hermes` - Tema de velocidad
9. `dionysus` - Tema de festividad
10. `demeter` - Tema de la naturaleza

### Eliminar el selector de temas

Por defecto, Titan Core incluye un componente para cambiar de tema. Si deseas mantener un solo tema en todo el sitio:

1. Abre  `src/layouts/Layout.astro`
2. Elimina o comenta la importación del selector:
   ```astro
   // Remove this line
   import ThemeSwitcher from "../components/ThemeSwitcher.astro";
   ```
3. Quita el componente del body:
   ```astro
   <body data-theme={theme}>
     <Header />
     <slot />
     <Footer footerCta={footerCta} />
     <!-- Remove this line -->W
     <ThemeSwitcher />
     
     <script>
       import AOS from 'aos';
       AOS.init({
         duration: 800,
         once: true,
       });
     </script>
   </body>
   ```

Esto garantizará que se use solo el tema definido en tu configuración.

## 📝 Gestión de contenido

Titan Core usa las colecciones de contenido de Astro para los posts del blog y otros contenidos. Agrega tu contenido en `src/content/`.

## 🧩 Componentes

Titan Core incluye una amplia variedad de componentes:

- **Componentes de diseño**: : Hero, características, panel dividido, llamada a la acción, etc.
- **Componentes UI**: Botones, formularios, tarjetas, etc.
- **Componentes para blog**: Tarjetas de post, categorías, etc.
- **Componentes de equipo**: Grillas de miembros, tarjetas, etc.

## 🛠️ Comandos

| Comandos                | Acción                                           |
| :--------------------- | :----------------------------------------------- |
| `npm install`          | Instala las dependencias                           |
| `npm run dev`          | Inicia el servidor local en `localhost:4321`      |
| `npm run build`        | Compila el sitio para producción en `./dist/`          |
| `npm run preview`      | Previsualiza el sitio construido localmente    |
| `npm run astro ...`    | Ejecuta comandos CLI como `astro add`, `astro check` |

## 📄 License

Este proyecto está bajo la licencia MIT - ver el archivo LICENSE para más detalles.

## 🙏 Credits

- Construido con [Astro](https://astro.build)
- Animaciones por [AOS](https://michalsnik.github.io/aos/)
- Íconos por [Lucide](https://lucide.dev)
