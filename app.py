import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Metro Dash",
    page_icon="🏃",
    layout="centered"
)

st.title("🏃 Metro Dash")
st.write("Run, jump, slide and collect coins!")

game = r"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body {
    margin: 0;
    background: #172638;
    color: white;
    font-family: Arial;
    text-align: center;
}
canvas {
    width: 100%;
    max-width: 420px;
    background: #344b60;
    border-radius: 12px;
    touch-action: none;
}
button {
    padding: 13px 9px;
    margin: 3px;
    border: 0;
    border-radius: 9px;
    background: #ffcf40;
    font-weight: bold;
    font-size: 15px;
}
</style>
</head>
<body>

<canvas id="game" width="420" height="600"></canvas>
<br>
<button onclick="move(-1)">⬅ LEFT</button>
<button onclick="jump()">⬆ JUMP</button>
<button onclick="slide()">⬇ SLIDE</button>
<button onclick="move(1)">RIGHT ➡</button>
<br>
<button onclick="restart()">🔄 RESTART</button>
<p id="info">Score: 0 | Coins: 0</p>

<script>
const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");

let lane, jumpY, jumpTime, slideTime;
let obstacles, coins, score, coinCount;
let ended, lastTime, spawn, roadMove;

function restart() {
    lane = 1;
    jumpY = 0;
    jumpTime = 0;
    slideTime = 0;
    obstacles = [];
    coins = [];
    score = 0;
    coinCount = 0;
    ended = false;
    lastTime = 0;
    spawn = 0.7;
    roadMove = 0;
    requestAnimationFrame(loop);
}

function move(n) {
    if (!ended) lane = Math.max(0, Math.min(2, lane + n));
}

function jump() {
    if (!ended && jumpTime <= 0 && slideTime <= 0) {
        jumpTime = 0.7;
    }
}

function slide() {
    if (!ended && slideTime <= 0 && jumpTime <= 0) {
        slideTime = 0.6;
    }
}

document.addEventListener("keydown", e => {
    if (e.key === "ArrowLeft") move(-1);
    if (e.key === "ArrowRight") move(1);
    if (e.key === "ArrowUp" || e.key === " ") jump();
    if (e.key === "ArrowDown") slide();
});

let sx = 0, sy = 0;

canvas.addEventListener("pointerdown", e => {
    sx = e.clientX;
    sy = e.clientY;
});

canvas.addEventListener("pointerup", e => {
    let dx = e.clientX - sx;
    let dy = e.clientY - sy;

    if (Math.abs(dx) > Math.abs(dy) && Math.abs(dx) > 25) {
        move(dx > 0 ? 1 : -1);
    } else if (Math.abs(dy) > 25) {
        dy < 0 ? jump() : slide();
    }
});

function drawPlayer() {
    let x = [105, 210, 315][lane];
    let y = 490 - jumpY;

    ctx.fillStyle = "#ffcf40";

    if (slideTime > 0) {
        ctx.fillRect(x - 24, y - 15, 48, 24);
        slideTime = Math.max(0, slideTime - frameDT);
    } else {
        ctx.fillRect(x - 15, y - 35, 30, 40);

        ctx.fillStyle = "#f0b99b";
        ctx.beginPath();
        ctx.arc(x, y - 45, 13, 0, Math.PI * 2);
        ctx.fill();
    }
}

function drawBackground() {
    ctx.fillStyle = "#1d3448";
    ctx.fillRect(0, 0, 420, 600);

    for (let i = 0; i < 7; i++) {
        let x = i * 65;
        ctx.fillStyle = "#304a60";
        ctx.fillRect(x, 70, 48, 110);
    }

    ctx.fillStyle = "#485565";
    ctx.beginPath();
    ctx.moveTo(70, 100);
    ctx.lineTo(350, 100);
    ctx.lineTo(420, 600);
    ctx.lineTo(0, 600);
    ctx.closePath();
    ctx.fill();

    ctx.strokeStyle = "#e6edf2";
    ctx.lineWidth = 3;
    ctx.setLineDash([25, 22]);
    ctx.lineDashOffset = -roadMove;

    ctx.beginPath();
    ctx.moveTo(165, 100);
    ctx.lineTo(140, 600);
    ctx.moveTo(255, 100);
    ctx.lineTo(280, 600);
    ctx.stroke();
    ctx.setLineDash([]);
}

let frameDT = 0;

function loop(time) {
    if (ended) {
        drawBackground();
        drawPlayer();
        drawObjects();

        ctx.fillStyle = "white";
        ctx.textAlign = "center";
        ctx.font = "bold 32px Arial";
        ctx.fillText("GAME OVER", 210, 280);
        ctx.font = "18px Arial";
        ctx.fillText("Press RESTART", 210, 315);
        ctx.textAlign = "left";
        return;
    }

    frameDT = lastTime
        ? Math.min((time - lastTime) / 1000, 0.04)
        : 0;

    lastTime = time;
    score += frameDT * 10;
    roadMove = (roadMove + 260 * frameDT) % 47;

    jumpTime = Math.max(0, jumpTime - frameDT);
    slideTime = Math.max(0, slideTime - frameDT);

    jumpY = jumpTime > 0
        ? Math.sin((jumpTime / 0.7) * Math.PI) * 100
        : 0;

    spawn -= frameDT;

    if (spawn <= 0) {
        let l = Math.floor(Math.random() * 3);

        obstacles.push({
            lane: l,
            y: -35,
            type: Math.random() < 0.5 ? "barrier" : "gate",
            checked: false
        });

        if (Math.random() < 0.8) {
            coins.push({
                lane: Math.floor(Math.random() * 3),
                y: -90,
                collected: false
            });
        }

        spawn = 0.9;
    }

    obstacles.forEach(o => {
        o.y += 260 * frameDT;

        if (
            o.lane === lane &&
            !o.checked &&
            o.y > 450 &&
            o.y < 515
        ) {
            o.checked = true;

            let safe = o.type === "barrier"
                ? jumpTime > 0.15
                : slideTime > 0.15;

            if (!safe) ended = true;
        }
    });

    coins.forEach(c => {
        c.y += 260 * frameDT;

        if (
            !c.collected &&
            c.lane === lane &&
            c.y > 450 &&
            c.y < 510
        ) {
            c.collected = true;
            coinCount++;
            score += 5;
        }
    });

    obstacles = obstacles.filter(o => o.y < 640);
    coins = coins.filter(c => c.y < 620 && !c.collected);

    drawBackground();
    drawObjects();
    drawPlayer();

    ctx.fillStyle = "white";
    ctx.font = "bold 20px Arial";
    ctx.fillText("Score: " + Math.floor(score), 12, 28);
    ctx.fillText("Coins: " + coinCount, 12, 55);

    document.getElementById("info").innerText =
        "Score: " + Math.floor(score) + " | Coins: " + coinCount;

    requestAnimationFrame(loop);
}

function drawObjects() {
    obstacles.forEach(o => {
        let x = [105, 210, 315][o.lane];

        if (o.type === "barrier") {
            ctx.fillStyle = "#e74c4c";
            ctx.fillRect(x - 25, o.y - 15, 50, 35);
        } else {
            ctx.fillStyle = "#35c5ed";
            ctx.fillRect(x - 32, o.y - 30, 64, 12);
            ctx.fillRect(x - 27, o.y - 18, 8, 25);
            ctx.fillRect(x + 19, o.y - 18, 8, 25);
        }
    });

    coins.forEach(c => {
        if (c.collected) return;

        let x = [105, 210, 315][c.lane];

        ctx.fillStyle = "#ffdc38";
        ctx.beginPath();
        ctx.arc(x, c.y, 11, 0, Math.PI * 2);
        ctx.fill();
    });
}

restart();
</script>
</body>
</html>
"""

components.html(game, height=760, scrolling=False)
