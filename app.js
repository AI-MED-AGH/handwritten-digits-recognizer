const API_URL = "http://localhost:8000/predict";

const canvas = document.getElementById('inputCanvas');
const ctx = canvas.getContext('2d');
const svg = document.getElementById('treeSvg');
let isDrawing = false;
let weights = Array(10).fill(0);
let activeBeads = [];
let nodes = [];

function initGraph() {
    // startY jest teraz niżej, by pasowało do środka wysokości 600px
    const startX = 20, startY = 300;

    for (let i = 0; i < 10; i++) {
        // targetY ma większe odstępy (i * 57)
        const targetX = 400, targetY = 40 + i * 57;

        const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
        path.setAttribute("d", `M ${startX} ${startY} C ${startX + 180} ${startY}, ${targetX - 180} ${targetY}, ${targetX} ${targetY}`);
        path.setAttribute("class", "path-bg");
        svg.appendChild(path);

        const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        // Promień zwiększony z 16 do 26
        circle.setAttribute("cx", targetX);
        circle.setAttribute("cy", targetY);
        circle.setAttribute("r", "26");
        circle.setAttribute("class", "node");
        svg.appendChild(circle);

        const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
        text.setAttribute("x", targetX);
        text.setAttribute("y", targetY);
        // dy="0.35em" idealnie centruje tekst w pionie względem współrzędnej Y
        text.setAttribute("dy", "0.35em");
        text.setAttribute("class", "node-text");
        text.textContent = i;
        svg.appendChild(text);

        nodes.push({path: path});
    }
}

function initCanvas() {
    ctx.fillStyle = "black";
    ctx.fillRect(0, 0, 28, 28);

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
    ctx.fillStyle = "black";
    ctx.fillRect(0, 0, 28, 28);
    weights.fill(0);
}

async function predict() {
    const imgData = ctx.getImageData(0, 0, 28, 28).data;
    const flatPixels = [];

    // Pobieramy tylko kanał czerwony (wartości od 0 do 255 typu int)
    // Nie dzielimy przez 255.0, robi to teraz backend
    for (let i = 0; i < imgData.length; i += 4) {
        flatPixels.push(imgData[i]);
    }

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            // Zmieniono klucz na 'data' i dodano nawiasy kwadratowe, tworząc listę list
            body: JSON.stringify({data: [flatPixels]}),
        });

        if (!response.ok) {
            throw new Error(`Błąd HTTP: ${response.status}`);
        }

        const result = await response.json();

        // Backend zwraca tablicę odpowiedzi dla całego batcha. Bierzemy indeks 0.
        // Używamy slice(0, 10), aby pobrać prawdopodobieństwa tylko dla cyfr 0-9
        // i zignorować klasę 'shadow' (indeks 10), która wywalała by błędy w rysowaniu grafu.
        weights = result[0].proba.slice(0, 10);

    } catch (e) {
        console.error("Błąd API:", e);
    }
}

function spawnBeads() {
    weights.forEach((w, i) => {
        // Próg obniżony do 0.05 (5%) - pokazujemy alternatywne, mniej pewne wybory
        // Gęstość silnie zależy od wagi (w * 0.4), pewność rzędu 90% wygeneruje ciągły strumień
        if (w > 0.05 && Math.random() < w * 0.4) {
            const bead = document.createElementNS("http://www.w3.org/2000/svg", "circle");

            // Opcjonalnie: możemy też nieznacznie skalować wielkość koralika z wagą
            const radius = 2 + (w * 2);
            bead.setAttribute("r", radius);
            bead.setAttribute("class", "bead");

            // Efekt pulsu/rozbłysku dla głównych wyników
            if (w > 0.8) bead.style.filter = "drop-shadow(0 0 6px #00ff88)";

            svg.appendChild(bead);
            activeBeads.push({el: bead, path: nodes[i].path, pos: 0, speed: 0.015});
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
            activeBeads.splice(i, 1);
        } else {
            const point = b.path.getPointAtLength(b.pos * b.path.getTotalLength());
            b.el.setAttribute("cx", point.x);
            b.el.setAttribute("cy", point.y);
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
        nodeList[label].style.stroke = "#00ff88";
        setTimeout(() => nodeList[label].style.stroke = originalStroke, 500);

    } catch (e) {
        console.error("Collector Error:", e);
    }
}

function initGraph() {
    const startX = 20, startY = 300;

    for (let i = 0; i < 10; i++) {
        const targetX = 400, targetY = 40 + i * 57;

        const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
        path.setAttribute("d", `M ${startX} ${startY} C ${startX + 180} ${startY}, ${targetX - 180} ${targetY}, ${targetX} ${targetY}`);
        path.setAttribute("class", "path-bg");
        svg.appendChild(path);

        const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        circle.setAttribute("cx", targetX);
        circle.setAttribute("cy", targetY);
        circle.setAttribute("r", "26");
        circle.setAttribute("class", "node");

        // Collect data on double-click on a circle
        circle.ondblclick = () => collectCurrentData(i);

        svg.appendChild(circle);

        const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
        text.setAttribute("x", targetX);
        text.setAttribute("y", targetY);
        text.setAttribute("dy", "0.35em");
        text.setAttribute("class", "node-text");
        text.textContent = i;

        // Collect data on double-click on a text
        text.ondblclick = () => collectCurrentData(i);

        svg.appendChild(text);
        nodes.push({path: path});
    }
}

initGraph();
initCanvas();
updateBeads();