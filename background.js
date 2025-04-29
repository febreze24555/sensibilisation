// Animation réseau de points reliés par des lignes (constellation)
const POINTS = 200;
const DIST = 100;
const MOUSE_REPEL_DIST = 90;
const points = [];
let mouse = {x: window.innerWidth/2, y: window.innerHeight/2};

for (let i = 0; i < POINTS; i++) {
    points.push({
        x: Math.random() * window.innerWidth,
        y: Math.random() * window.innerHeight,
        vx: (Math.random() - 0.5) * 0.3,
        vy: (Math.random() - 0.5) * 0.3
    });
}

const canvas = document.createElement('canvas');
canvas.id = 'bg-anim';
canvas.style.position = 'fixed';
canvas.style.top = '0';
canvas.style.left = '0';
canvas.style.width = '100vw';
canvas.style.height = '100vh';
canvas.style.zIndex = '0';
canvas.style.pointerEvents = 'none';
document.body.prepend(canvas);

function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}
window.addEventListener('resize', resizeCanvas);
resizeCanvas();

window.addEventListener('mousemove', (e) => {
    mouse.x = e.clientX;
    mouse.y = e.clientY;
});

function animate() {
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    // Points
    for (let i = 0; i < POINTS; i++) {
        let p = points[i];
        // Mouvement léger
        p.x += p.vx;
        p.y += p.vy;
        if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
        if (p.y < 0 || p.y > canvas.height) p.vy *= -1;
        // Effet répulsif de la souris
        let dxm = p.x - mouse.x, dym = p.y - mouse.y;
        let dm = Math.sqrt(dxm*dxm + dym*dym);
        if (dm < MOUSE_REPEL_DIST) {
            // Repousser plus fort si très proche
            let force = (MOUSE_REPEL_DIST - dm) / MOUSE_REPEL_DIST * 1.2;
            p.x += dxm / dm * force * 2.2;
            p.y += dym / dm * force * 2.2;
        }
    }
    // Lignes
    for (let i = 0; i < POINTS; i++) {
        for (let j = i+1; j < POINTS; j++) {
            let p1 = points[i], p2 = points[j];
            let dx = p1.x - p2.x, dy = p1.y - p2.y;
            let d = Math.sqrt(dx*dx + dy*dy);
            // On ne trace pas de ligne si la souris est trop proche d'un des deux points
            let mouseDist1 = Math.sqrt((p1.x-mouse.x)*(p1.x-mouse.x)+(p1.y-mouse.y)*(p1.y-mouse.y));
            let mouseDist2 = Math.sqrt((p2.x-mouse.x)*(p2.x-mouse.x)+(p2.y-mouse.y)*(p2.y-mouse.y));
            if (d < DIST && mouseDist1 > MOUSE_REPEL_DIST && mouseDist2 > MOUSE_REPEL_DIST) {
                ctx.strokeStyle = 'rgba(67,160,71,' + (1 - d/DIST) * 0.17 + ')';
                ctx.lineWidth = 1.05;
                ctx.beginPath();
                ctx.moveTo(p1.x, p1.y);
                ctx.lineTo(p2.x, p2.y);
                ctx.stroke();
            }
        }
    }
    // Points
    for (let i = 0; i < POINTS; i++) {
        let p = points[i];
        ctx.beginPath();
        ctx.arc(p.x, p.y, 2.6, 0, 2 * Math.PI);
        ctx.fillStyle = 'rgba(67,160,71,0.45)';
        ctx.shadowColor = 'rgba(67,160,71,0.15)';
        ctx.shadowBlur = 6;
        ctx.fill();
        ctx.shadowBlur = 0;
    }
    requestAnimationFrame(animate);
}
animate();
