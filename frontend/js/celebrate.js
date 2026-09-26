/* Confeti ligero en un <canvas>. No hace nada si el sistema pide reducir el movimiento. */

const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
const COLORS = ["#22c55e", "#4ade80", "#3b82f6", "#93c5fd", "#facc15", "#f472b6"];
const DURATION_MS = 1800;

export function celebrate() {
  if (reducedMotion.matches || document.querySelector(".confetti")) return;
  const canvas = Object.assign(document.createElement("canvas"), { className: "confetti" });
  canvas.setAttribute("aria-hidden", "true");
  canvas.width = innerWidth;
  canvas.height = innerHeight;
  document.body.append(canvas);
  const ctx = canvas.getContext("2d");

  const pieces = Array.from({ length: 140 }, () => ({
    x: innerWidth / 2 + (Math.random() - 0.5) * innerWidth * 0.3,
    y: innerHeight * 0.35,
    vx: (Math.random() - 0.5) * 14,
    vy: -Math.random() * 13 - 4,
    size: 5 + Math.random() * 6,
    color: COLORS[Math.floor(Math.random() * COLORS.length)],
    spin: Math.random() * Math.PI,
  }));

  const start = performance.now();
  function frame(now) {
    const elapsed = now - start;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.globalAlpha = Math.max(0, 1 - elapsed / DURATION_MS);
    for (const p of pieces) {
      p.vy += 0.35; // gravedad
      p.x += p.vx;
      p.y += p.vy;
      p.spin += 0.2;
      ctx.fillStyle = p.color;
      ctx.fillRect(p.x, p.y, p.size, p.size * Math.abs(Math.cos(p.spin)));
    }
    if (elapsed < DURATION_MS) requestAnimationFrame(frame);
    else canvas.remove();
  }
  requestAnimationFrame(frame);
}
