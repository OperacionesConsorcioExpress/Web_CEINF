// src/data/menu.ts

export const headerMenu = [
    { name: 'Info', link: '/Web_CEINF/theme-info' },
    { name: 'Equipo', link: '/Web_CEINF/team' },
    { name: 'Blog', link: '/Web_CEINF/blog' },
    { name: 'Menú', link: '/Web_CEINF/style-guide', showArrow: false,
        children: [
            { name: 'Tipografia', link: '/Web_CEINF/style-guide#typography' },
            { name: 'Colores', link: '/Web_CEINF/style-guide#colors' },
            { name: 'Links', link: '/Web_CEINF/style-guide#links' },
            { name: 'Botones', link: '/Web_CEINF/style-guide#buttons' },
            { name: 'Formas', link: '/Web_CEINF/style-guide#forms' },
            { name: 'Listas', link: '/Web_CEINF/style-guide#lists' },
        ]
    }
];

export const footerMenu = [
    { name: 'Guías', link: '/Web_CEINF/style-guide' },
];

export const legalMenu = [
    { name: 'PolÍtica de Privacidad', link: '/Web_CEINF/legal/privacy-policy' },
    { name: 'Terminos del Servicio', link: '/Web_CEINF/legal/terms-of-service' }
];

