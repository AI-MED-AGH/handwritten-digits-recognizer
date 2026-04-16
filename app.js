const API_URL = "http://localhost:8000/predict";

const canvas = document.getElementById('inputCanvas');
const ctx = canvas.getContext('2d');
const svg = document.getElementById('treeSvg');
let isDrawing = false;
let weights = Array(10).fill(0);
let activeBeads = [];
let nodes = [];

function initCanvas() {
    ctx.clearRect(0, 0, 28, 28);
    canvas.onmousedown = () => isDrawing = true;
    window.onmouseup = () => {
        if (isDrawing) {
            isDrawing = false;
            predict();
        }
    };
    canvas.onmousemove = (e) => {
        if (!isDrawing) return;
        const rect = canvas.getBoundingClientRect();
        const x = (e.clientX - rect.left) / (rect.width / 28);
        const y = (e.clientY - rect.top) / (rect.height / 28);

        ctx.fillStyle = "white";
        ctx.beginPath();
        ctx.arc(x, y, 1.2, 0, Math.PI * 2);
        ctx.fill();
    };
}

function clearCanvas() {
    ctx.clearRect(0, 0, 28, 28);
    weights.fill(0);
}

async function predict() {
    const imgData = ctx.getImageData(0, 0, 28, 28).data;
    const flatPixels = [];
    for (let i = 0; i < imgData.length; i += 4) {
        flatPixels.push(imgData[i]);
    }

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({data: [flatPixels]}),
        });
        if (!response.ok) throw new Error(`HTTP Error: ${response.status}`);
        const result = await response.json();
        weights = result[0].proba.slice(0, 10);
    } catch (e) {
        console.error("API Error:", e);
    }
}

function spawnBeads() {
    weights.forEach((w, i) => {
        // Spawn beads only for weights above 20%
        if (w > 0.2 && Math.random() < w * 0.4) {
            const bead = document.createElementNS("http://www.w3.org/2000/svg", "circle");
            const radius = 2 + (w * 2);
            bead.setAttribute("r", radius);
            bead.setAttribute("class", "bead");
            
            if (w > 0.8) bead.style.filter = "drop-shadow(0 0 6px #15B762)";
            svg.appendChild(bead);
            
            // Pass the weight to read it upon impact
            activeBeads.push({
                el: bead, 
                path: nodes[i].path, 
                targetIndex: i, 
                weight: w, 
                pos: 0, 
                speed: 0.015
            });
        }
    });
}

function updateBeads() {
    spawnBeads();
    for (let i = activeBeads.length - 1; i >= 0; i--) {
        const b = activeBeads[i];
        b.pos += b.speed;
        
        if (b.pos >= 1) {
            b.el.remove();
            
            const targetNode = nodes[b.targetIndex];
            if (targetNode && targetNode.rect) {
                // Set green color and opacity based on weight
                targetNode.rect.style.fill = "#15B762";
                targetNode.rect.style.fillOpacity = b.weight; 
                targetNode.rect.classList.add('active');

                if (targetNode.timeoutId) clearTimeout(targetNode.timeoutId);
                
                // Highlight duration: 500ms
                targetNode.timeoutId = setTimeout(() => {
                    targetNode.rect.style.fill = ""; // Revert to CSS (#2a2a2a)
                    targetNode.rect.style.fillOpacity = "";
                    targetNode.rect.classList.remove('active');
                }, 500);
            }
            activeBeads.splice(i, 1);
        } else {
            const point = b.path.getPointAtLength(b.pos * b.path.getTotalLength());
            b.el.setAttribute("cx", point.x);
            b.el.setAttribute("cy", point.y);
        }
    }
    requestAnimationFrame(updateBeads);
}

function initGraph() {
    const w = window.innerWidth;
    const h = window.innerHeight;
    const centerX = w / 2;
    const centerY = h / 2;

    const offsetX = 400; 
    const canvasRadiusX = 160; 
    const spacingY = 120; 
    const startYPos = centerY - (spacingY * 2);

    for (let i = 0; i < 10; i++) {
        let startX, startY, targetX, targetY;
        let nodeIndex = i % 5;

        targetY = startYPos + (nodeIndex * spacingY);
        const startYOffset = centerY - 100 + (nodeIndex * 50);

        if (i < 5) {
            startX = centerX - canvasRadiusX;
            startY = startYOffset;
            targetX = centerX - offsetX;
        } else {
            startX = centerX + canvasRadiusX;
            startY = startYOffset;
            targetX = centerX + offsetX;
        }

        const angle = Math.atan2(targetY - startY, targetX - startX);
        const endX = targetX - Math.cos(angle) * 52;
        const endY = targetY - Math.sin(angle) * 52;

        const cx1 = startX + (targetX - startX) * 0.4;
        const cy1 = startY;
        const cx2 = startX + (targetX - startX) * 0.6;
        const cy2 = targetY;

        const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
        path.setAttribute("d", `M ${startX} ${startY} C ${cx1} ${cy1}, ${cx2} ${cy2}, ${endX} ${endY}`);
        path.setAttribute("class", "path-bg");
        svg.appendChild(path);

        const size = 104; 
        const square = document.createElementNS("http://www.w3.org/2000/svg", "rect");
        square.setAttribute("x", targetX - size / 2);
        square.setAttribute("y", targetY - size / 2);
        square.setAttribute("width", size);
        square.setAttribute("height", size);
        square.setAttribute("class", "node");
        svg.appendChild(square);

        const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
        text.setAttribute("x", targetX);
        text.setAttribute("y", targetY);
        text.setAttribute("dy", "0.35em");
        text.setAttribute("class", "node-text");
        text.textContent = i;
        svg.appendChild(text);

        nodes.push({ path: path, rect: square });
    }
}

initGraph();
initCanvas();
updateBeads();