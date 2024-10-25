/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{html,ts}",
  ],
  theme: {
    extend: {
      backgroundImage: {
        'custom-gradient-blue': 'linear-gradient(180deg, rgba(217, 217, 217, 0) 0%, rgba(0, 163, 255, 0.6) 77.5%, rgba(0, 163, 255, 0.9) 100%)',
        'custom-gradient-red': 'linear-gradient(180deg, rgba(217, 217, 217, 0) 0%, #E67E7E 100%)',
        'custom-gradient-yellow': 'linear-gradient(180deg, rgba(217, 217, 217, 0) 0%, #E0B23C 100%)',
        'custom-gradient-green': 'linear-gradient(180deg, rgba(217, 217, 217, 0) 0%, #61C977 100%)',
        'custom-gradient-pink': 'linear-gradient(180deg, rgba(217, 217, 217, 0) 0%, #D16CC1 100%)',
        'custom-gradient-purple': 'linear-gradient(180deg, rgba(217, 217, 217, 0) 0%, #4957D7 100%)',
      },
      colors: {
        primary: {
          black: 'rgba(0, 0, 0, 1)',
          grey: 'rgba(146, 146, 146, 1)',
          lightGrey: 'rgba(220, 220, 220, 1)',
          lightGrey2: 'rgba(240, 240, 240, 1)',
          skyBlue: 'rgba(0, 163, 255, 1)',
          skyBlue2: 'rgba(0, 163, 255, 0.7)',
          skyBlue3: 'rgba(0, 163, 255, 0.4)',
          darkBlue: 'rgba(1, 31, 109, 1)',
          green: 'rgba(0, 184, 29, 1)',
          red: 'rgba(226, 3, 3, 1)'
        },
        secondary: {
          red: { 
            dark: 'rgba(220, 70, 70, 1)',
            mid: 'rgba(220, 70, 70, 0.7)',
            light: 'rgba(220, 70, 70, 0.4)',
          },
          green: { 
            dark: 'rgba(53, 202, 85, 1)',
            mid: 'rgba(53, 202, 85, 0.7)',
            light: 'rgba(53, 202, 85, 0.4)',
          },
          yellow: { 
            dark: 'rgba(235, 169, 0, 1)',
            mid: 'rgba(235, 169, 0, 0.7)',
            light: 'rgba(235, 169, 0, 0.4)',
          },
          pink: { 
            dark: 'rgba(213, 69, 190, 1)',
            mid: 'rgba(213, 69, 190, 0.7)',
            light: 'rgba(213, 69, 190, 0.4)',
          },
          blue: { 
            dark: 'rgba(19, 39, 221, 1)',
            mid: 'rgba(19, 39, 221, 0.7)',
            light: 'rgba(19, 39, 221, 0.4)',
          },
        },
        accent: {
          light: '#fbbf24',
          DEFAULT: '#f59e0b',
          dark: '#b45309',
        },
        neutral: {
          light: '#f3f4f6',
          DEFAULT: '#d1d5db',
          dark: '#4b5563',
        },
      },
    }
  },
  plugins: [
    function({ addUtilities }) {
      const newUtilities = {
        '.header1': {
          fontSize: '2.75rem',
          lineHeight: '3rem',  // even more relaxed
        },
        '.header2': {
          fontSize: '1.75rem',
          lineHeight: '2rem',  // even more relaxed
        },

        '.body': {
          fontSize: '1.25rem',
          lineHeight: '1.5rem',  // even more relaxed
        },

        // Medium screens (md)
        '@media (max-width: 768px)': {
          '.header1': {
            fontSize: '2.25rem !important',
            lineHeight: '2.5rem !important',
          },
          '.header2': {
            fontSize: '1.5rem !important',
            lineHeight: '1.75rem !important',
          },
          '.body': {
            fontSize: '1rem !important',
            lineHeight: '1.25rem !important',  // relaxed for medium screens
          },
        },

        // Small screens (sm)
        '@media (max-width: 576px)': {
          '.header1': {
            fontSize: '1.75rem !important',
            lineHeight: '1.75rem !important',
          },
          '.header2': {
            fontSize: '1.25rem !important',
            lineHeight: '1.5rem !important',
          },
          '.body': {
            fontSize: '0.75rem !important',
            lineHeight: '1rem !important',  // relaxed for medium screens
          },
        },
      }
      addUtilities(newUtilities, ['responsive'])
    }
  ],
}

