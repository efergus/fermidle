/** @type {import('tailwindcss').Config} */
export default {
	content: ['./src/**/*.{html,js,ts,svelte}'],
	theme: {
		extend: {
			strokeWidth: {
				3: '3px'
			}
		},

		colors: {
			primary: 'rgb(var(--color-primary) / <alpha-value>)',
			secondary: 'rgb(var(--color-secondary) / <alpha-value>)',
			contrast: 'rgb(var(--color-contrast) / <alpha-value>)',
			'contrast-secondary': 'rgb(var(--color-contrast-secondary) / <alpha-value>)',
			theme: 'rgb(var(--color-theme) / <alpha-value>)'
		}
	},
	plugins: []
};
