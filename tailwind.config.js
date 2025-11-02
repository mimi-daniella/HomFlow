/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./src/**/*.{js,jsx,ts,tsx}", // if you're using React or similar
    "./components/**/*.{html,js}", // if you have components elsewhere
  ],

  theme: {
    extend: {
      fontFamily: {
        poppins: ["Poppins", "sans-serif"],
      },

      colors: {
        primary: "#6F00FF",
        secondary: "#14b8a6",
        secondaryHover: "#1ABC",
        accent: "",
        specialBlue: "#1ABC",
      },

      keyframes: {
        "gradient-move": {
          "0%, 100%": { backgroundPosition: "0% 50%" },
          "50%": { backgroundPosition: "100% 50%" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-10px)" },
        },

        fadeIn: {
          "0%": { opacity: "0", transform: scale(0.95) },
          "100%": { opacity: "1", transform: scale(1) },
        },
      },

      animation: {
        "gradient-motion": "gradient-move 10s ease infinite",
        float: "float 2s ease-in-out infinite",
        fadeIn: "fadeIn 0.3s ease-out forwards",
      },

      backgroundSize: {
        200: "200% 200%",
      },

    },
  },
  plugins: [],
};
