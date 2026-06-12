// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
//  PokéShop — Efectos interactivos
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

// ── 1. Fondo del hero que cambia cada cierto tiempo ──
const imagenesHero = [
  'https://images.pokemontcg.io/sv1/6_hires.png',     // Charizard
  'https://images.pokemontcg.io/sv3pt5/28_hires.png', // Pikachu
  'https://images.pokemontcg.io/sv2/52_hires.png',    // Mewtwo
  'https://images.pokemontcg.io/sv6/110_hires.png',   // Rayquaza
];

function rotarFondoHero() {
  const hero = document.querySelector('.hero-bg');
  if (!hero) return;  // si no estamos en la página de inicio, no hacer nada

  let index = 0;

  setInterval(() => {
    index = (index + 1) % imagenesHero.length;

    // Fade out
    hero.style.opacity = '0';

    setTimeout(() => {
      hero.style.backgroundImage = `
        linear-gradient(135deg, rgba(10,10,15,.85) 0%, rgba(10,10,15,.6) 50%, rgba(10,10,15,.9) 100%),
        url('${imagenesHero[index]}')
      `;
      // Fade in
      hero.style.opacity = '1';
    }, 400); // espera a que termine el fade out

  }, 5000); // cambia cada 5 segundos
}

// ── 2. Animación al agregar al carrito (efecto "pop") ──
function animarBotonesCarrito() {
  document.querySelectorAll('.btn-agregar').forEach(btn => {
    btn.addEventListener('click', () => {
      btn.classList.add('pop');
      setTimeout(() => btn.classList.remove('pop'), 300);
    });
  });
}

// ── Inicializar todo cuando carga la página ──
document.addEventListener('DOMContentLoaded', () => {
  rotarFondoHero();
  animarBotonesCarrito();
});
