const API_URL = "http://localhost:8000/predict";

const canvas = document.getElementById('inputCanvas');
const ctx = canvas.getContext('2d');
const svg = document.getElementById('treeSvg');
let isDrawing = false;
let weights = Array(10).fill(0);
let activeBeads = [];
let nodes = [];
let greenColor = "#00D170"

let displayedWeights = Array(10).fill(0);

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
        const x = (e.clientX - rect.left) / 10;
        const y = (e.clientY - rect.top) / 10;

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

        if (!response.ok) {
            throw new Error(`Błąd HTTP: ${response.status}`);
        }

        const result = await response.json();

        weights = result[0].proba.slice(0, 10);

    } catch (e) {
        console.error("Błąd API:", e);
    }
}

function spawnBeads() {
    weights.forEach((w, i) => {
        if (w > 0.05 && Math.random() < w * 0.4) {
            const bead = document.createElementNS("http://www.w3.org/2000/svg", "circle");

            const radius = 2 + (w * 2);
            bead.setAttribute("r", radius);
            bead.setAttribute("class", "bead");

            if (w > 0.8) bead.style.filter = `drop-shadow(0 0 5px ${greenColor})`;

            svg.appendChild(bead);
            activeBeads.push({el: bead, path: nodes[i].path, pos: 0, speed: 0.015, targetIndex: i, payload: 0.15});
        }
    });
}

function updateBeads() {
    spawnBeads();

    for (let i = activeBeads.length - 1; i >= 0; i--) {
        const b = activeBeads[i];
        b.pos += b.speed;

        if (b.pos >= 1) {
            displayedWeights[b.targetIndex] = Math.min(1.0, displayedWeights[b.targetIndex] + b.payload)
            b.el.remove();
            activeBeads.splice(i, 1);
        } else {
            const point = b.path.getPointAtLength(b.pos * b.path.getTotalLength());
            b.el.setAttribute("cx", point.x);
            b.el.setAttribute("cy", point.y);
        }
    }

    // Lighten up nodes (clear logic is handled by clearCanvas() which sets up weights.fill(0))

    for (let i = 0; i < 10; i++) {
        let dw = displayedWeights[i];

        // Calculate new node color
        // Base: (r: 42, g: 42, b: 42)
        // Goal: (r: 0, g: 209, b: 112)
        const r = Math.round(42 + (0 - 42) * dw);
        const g = Math.round(42 + (209 - 42) * dw);
        const b = Math.round(42 + (112 - 42) * dw);

        // Set a new color to the node
        nodes[i].shape.style.fill = `rgb(${r}, ${g}, ${b})`;

        let stroke = Math.max(85, 255 * dw)
        nodes[i].shape.style.stroke = `rgb(${stroke}, ${stroke}, ${stroke})`;

        // Dynamically light up a node when the certainty level exceeds 5%
        if (dw > 0.05) {
            nodes[i].shape.style.filter = `drop-shadow(0 0 ${dw * 3}px rgba(0, 255, 136, ${dw}))`;
        } else {
            nodes[i].shape.style.filter = 'none';
        }

        // Smoothly fade out a node glow
        let decay = 0.01
        if (displayedWeights[i] > 0) {
            displayedWeights[i] = Math.max(0, displayedWeights[i] - decay);
        }
    }

    requestAnimationFrame(updateBeads);
}

// Send data to CSV file for fine-tuning
async function collectCurrentData(label) {
    const imgData = ctx.getImageData(0, 0, 28, 28).data;
    const flatPixels = [];
    for (let i = 0; i < imgData.length; i += 4) {
        flatPixels.push(imgData[i]);
    }

    try {
        const response = await fetch("http://localhost:8000/collect", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                label: label,
                pixels: flatPixels
            }),
        });
        const res = await response.json();
        console.log("Collector:", res.message);

        // Add visual feedback on double-click
        const nodeList = document.querySelectorAll('.node');
        const originalStroke = nodeList[label].style.stroke;
        nodeList[label].style.stroke = greenColor;
        setTimeout(() => nodeList[label].style.stroke = originalStroke, 500);

    } catch (e) {
        console.error("Collector Error:", e);
    }
}

function initGraph() {
    const startX = 20, startY = 400;


    // nodes placement
    const nodePositions = Array.from({ length: 10 }, (_, i) => ({
            x: 400,
            y: 60 + (i * 76)
        }));

    for (let i = 0; i < 10; i++) {
        const targetX = nodePositions[i].x;
        const targetY = nodePositions[i].y;

        const angle = Math.atan2(targetY - startY, targetX - startX);

        const size = 64;

        const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
        //path.setAttribute("d", `M ${startX} ${startY} C ${startX + 180} ${startY}, ${targetX} ${targetY + 180}, ${endX} ${endY}`);

        //curve adjustment
        const cx1 = startX + (targetX - startX) * 0.4;
        const cy1 = startY + (targetY - startY) * 0.0;

        const cx2 = startX + (targetX - startX) * 0.6;
        const cy2 = targetY + (targetY - startY) * 0.0;

        path.setAttribute("d",
            `M ${startX} ${startY}
            C ${cx1} ${cy1},
            ${cx2} ${cy2},
            ${targetX} ${targetY}`
        );

        path.setAttribute("class", "path-bg");
        svg.appendChild(path);

        const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");

        rect.setAttribute("x", targetX - size / 2);
        rect.setAttribute("y", targetY - size / 2);
        rect.setAttribute("width", size);
        rect.setAttribute("height", size);

        // Round node corners
        rect.setAttribute("rx", "0");
        rect.setAttribute("class", "node");

        // Collect data on double-click on a node
        rect.ondblclick = () => collectCurrentData(i);

        svg.appendChild(rect);

        const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
        text.setAttribute("x", targetX);
        text.setAttribute("y", targetY);
        text.setAttribute("dy", "0.35em");
        text.setAttribute("class", "node-text");
        text.textContent = i;

        // Collect data on double-click on a text
        text.ondblclick = () => collectCurrentData(i);

        svg.appendChild(text);
        nodes.push({path: path, shape: rect});
    }
}

initGraph();
initCanvas();
updateBeads();