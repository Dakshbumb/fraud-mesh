/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'visa-blue': '#1a1f71',
        'visa-gold': '#f7b600',
        'mastercard-red': '#eb001b',
        'mastercard-orange': '#f79e1b',
      },
      backgroundImage: {
        'visa-gradient': 'linear-gradient(135deg, #1a1f71 0%, #0f52ba 100%)',
        'mastercard-gradient': 'linear-gradient(135deg, #eb001b 0%, #f79e1b 100%)',
        'premium-gradient': 'linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%)',
      },
      animation: {
        'pulse-glow': 'pulse-glow 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-in': 'fadeIn 0.3s ease-out',
        'badge-pulse': 'badge-pulse 2s ease-in-out infinite',
      },
      keyframes: {
        'pulse-glow': {
          '0%, 100%': {
            opacity: '1',
            boxShadow: '0 0 10px rgba(34, 197, 94, 0.5)',
          },
          '50%': {
            opacity: '0.7',
            boxShadow: '0 0 20px rgba(34, 197, 94, 0.8)',
          },
        },
        fadeIn: {
          from: {
            opacity: '0',
            transform: 'translateY(10px)',
          },
          to: {
            opacity: '1',
            transform: 'translateY(0)',
          },
        },
        'badge-pulse': {
          '0%, 100%': {
            transform: 'scale(1)',
          },
          '50%': {
            transform: 'scale(1.05)',
          },
        },
      },
    },
  },
  plugins: [],
}
