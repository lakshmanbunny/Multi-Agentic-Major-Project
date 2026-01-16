/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    darkMode: 'class',
    theme: {
        extend: {
            colors: {
                'primary': '#752dbe',
                'accent-cyan': '#00d4ff',
                'accent-green': '#00ff88',
                'surface-dark': '#1a1a2e',
                'background-dark': '#0a0a0f',
                'glass-border': 'rgba(255, 255, 255, 0.08)',
            },
            fontFamily: {
                'display': ['Space Grotesk', 'sans-serif'],
                'body': ['Inter', 'sans-serif'],
                'mono': ['JetBrains Mono', 'monospace'],
            },
            boxShadow: {
                'neon-purple': '0 0 15px rgba(117, 45, 190, 0.5)',
                'neon-cyan': '0 0 10px rgba(0, 212, 255, 0.4)',
            },
        },
    },
    plugins: [],
}
