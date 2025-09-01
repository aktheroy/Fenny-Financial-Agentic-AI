// Configuration Constants
const CONFIG = {
  ROW_COUNT: 10,
  REPEAT_COUNT: 20,
  COLORS: [
    "#00ffcc", "#ff6ec4", "#ffff66", "#66ff66",
    "#ff0000", "#ff4500", "#ff1493", "#ffa500"
  ]
};

// Currency icons (Font Awesome classes)
const ICONS = [
  '<i class="fas fa-dollar-sign"></i>',
  '<i class="fas fa-euro-sign"></i>',
  '<i class="fas fa-pound-sign"></i>',
  '<i class="fas fa-yen-sign"></i>',
  '<i class="fa-solid fa-bitcoin-sign"></i>',
  '<i class="fas fa-ruble-sign"></i>',
  '<i class="fas fa-won-sign"></i>',
  '<i class="fa-solid fa-indian-rupee-sign"></i>',
  '<i class="fas fa-lira-sign"></i>',
  '<i class="fas fa-shekel-sign"></i>'
];

/**
 * Shuffle array using Fisher-Yates algorithm
 * @param {Array} array - Array to shuffle
 * @returns {Array} New shuffled array
 */
function shuffleArray(array) {
  const copy = [...array];
  for (let i = copy.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
}

/**
 * Creates a single currency row element
 * @param {boolean} reverse - If true, reverses animation direction
 * @returns {HTMLElement} Row element
 */
function createCurrencyRow(reverse) {
  const row = document.createElement("div");
  row.className = "currency";

  const slide = document.createElement("div");
  slide.className = `currency-slide${reverse ? " reverse" : ""}`;

  // Build icons efficiently
  const shuffledIcons = shuffleArray(ICONS).join("");
  slide.innerHTML = shuffledIcons.repeat(CONFIG.REPEAT_COUNT);

  row.appendChild(slide);
  return row;
}

/**
 * Generate and insert currency rows into the container
 */
function generateCurrencyRows(container) {
  const fragment = document.createDocumentFragment();
  for (let i = 0; i < CONFIG.ROW_COUNT; i++) {
    fragment.appendChild(createCurrencyRow(i % 2 !== 0));
  }
  container.appendChild(fragment);
}

/**
 * Initialize hover effects with random color change
 */
function initializeHoverEffects(container) {
  const colors = CONFIG.COLORS;
  const colorsLen = colors.length;

  container.addEventListener("mouseover", (e) => {
    if (e.target.matches(".currency-slide i")) {
      const randomColor = colors[(Math.random() * colorsLen) | 0];
      e.target.style.setProperty("--hover-color", randomColor);
    }
  });

  container.addEventListener("mouseout", (e) => {
    if (e.target.matches(".currency-slide i")) {
      e.target.style.removeProperty("--hover-color");
    }
  });
}

// Initialize once DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("currencies-container");
  if (!container) return;

  generateCurrencyRows(container);
  initializeHoverEffects(container);
});
