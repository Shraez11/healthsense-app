import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="HealthSense — Dashboard", layout="wide")
dashboard_html = r"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>HealthSense — Dashboard</title>

  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">

  <style>
  :root{
    --bg-1: #05060a;
    --bg-2: #071124;
    --glass-bg: rgba(255,255,255,0.04);
    --glass-border: rgba(255,255,255,0.06);
    --accent-1: #7afcff;
    --accent-2: #6b46ff;
    --muted: rgba(255,255,255,0.6);
    --glass-blur: 8px;
    --radius: 14px;
    --container: 1200px;
    --shadow-neon: 0 8px 30px rgba(107,70,255,0.12), 0 2px 8px rgba(122,252,255,0.03);
    font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial;
    color-scheme: dark;
  }
  *{box-sizing:border-box}
  html,body{height:100%}
  body{
    margin:0;
    background: linear-gradient(180deg,var(--bg-1),var(--bg-2));
    color:#e8eef8;
    -webkit-font-smoothing:antialiased;
    -moz-osx-font-smoothing:grayscale;
  }
  .container{max-width:var(--container);margin:0 auto;padding:2rem;}
  .particles-bg{position:fixed;inset:0;z-index:0;pointer-events:none;opacity:0.6}
  .site-header{position:sticky;top:0;z-index:50;backdrop-filter: blur(6px) saturate(120%);background: linear-gradient(180deg, rgba(3,6,12,0.45), rgba(3,6,12,0.15));border-bottom: 1px solid rgba(255,255,255,0.03);}
  .header-inner{display:flex;align-items:center;justify-content:space-between;gap:1rem}
  .logo{font-weight:800;letter-spacing:0.6px;font-size:1.1rem;color:var(--accent-1);text-decoration:none;text-shadow: 0 2px 10px rgba(106,58,255,0.12)}
  .nav{display:flex;align-items:center;gap:1rem}
  .nav-link{color:var(--muted);text-decoration:none;padding:0.6rem;border-radius:8px}
  .glass-card{background:var(--glass-bg);border:1px solid var(--glass-border);border-radius:var(--radius);padding:1.2rem;backdrop-filter: blur(var(--glass-blur));box-shadow: var(--shadow-neon);}
  .kpi{padding:0.6rem;border-radius:10px;background:linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));border:1px solid rgba(255,255,255,0.02)}
  .kpi-value{font-weight:800;color:var(--accent-2)}
  .kpi-label{font-size:0.75rem;color:var(--muted)}
  .sparkline path{stroke-dasharray: 400;stroke-dashoffset: 400;animation: dash 2.6s cubic-bezier(.2,.9,.2,1) forwards;}
  @keyframes dash{to{stroke-dashoffset:0}}
  .grid-3{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem}
  @media (max-width:980px){
    .grid-3{grid-template-columns:1fr}
  }
  </style>

  <!-- tsParticles -->
  <script src="https://cdn.jsdelivr.net/npm/tsparticles@2.11.1/tsparticles.bundle.min.js"></script>
  <!-- GSAP -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/ScrollTrigger.min.js"></script>
  <!-- Chart.js -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.3.0/chart.umd.min.js"></script>
</head>
<body>
  <div id="tsparticles" class="particles-bg" aria-hidden="true"></div>

  <header class="site-header">
    <div class="container header-inner">
      <a class="logo" href="javascript:void(0)">HealthSense</a>
      <nav class="nav">
        <a class="nav-link" href="#">Home</a>
        <a class="nav-link" href="#">Profile</a>
        <a class="nav-link" href="#">Integrations</a>
      </nav>
    </div>
  </header>

  <main class="container" style="position:relative;z-index:6;">
    <div class="glass-card" style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;">
      <div>
        <h2 style="margin:0">Realtime Telemetry</h2>
        <div style="color:var(--muted)">Last 5 minutes</div>
      </div>
      <div style="display:flex;gap:0.6rem">
        <button class="cta" id="analyze">Analyze</button>
      </div>
    </div>

    <div class="grid-3" style="margin-bottom:1rem;">
      <div class="glass-card">
        <h4 style="margin:0">Active Devices</h4>
        <div style="font-size:1.6rem;font-weight:700;color:var(--accent-2);">1,254</div>
      </div>
      <div class="glass-card">
        <h4 style="margin:0">Alerts (24h)</h4>
        <div style="font-size:1.6rem;font-weight:700;color:#ff7b6b;">42</div>
      </div>
      <div class="glass-card">
        <h4 style="margin:0">Average HR</h4>
        <div style="font-size:1.6rem;font-weight:700;color:var(--accent-1);">74 bpm</div>
      </div>
    </div>

    <div class="glass-card" style="padding:1rem;margin-bottom:1rem;">
      <canvas id="chart-telemetry" height="140"></canvas>
    </div>

    <div style="display:grid;grid-template-columns:2fr 1fr;gap:1rem;">
      <div class="glass-card">
        <h4>Device Activity</h4>
        <svg viewBox="0 0 200 60" style="width:100%;height:60px">
          <path d="M0,40 C30,22 60,10 90,20 C120,32 150,10 200,6" stroke="url(#g2)" stroke-width="2" fill="none"/>
          <defs><linearGradient id="g2"><stop offset="0%" stop-color="#7afcff"/><stop offset="100%" stop-color="#6b46ff"/></linearGradient></defs>
        </svg>
        <div style="margin-top:0.8rem;color:var(--muted)">List of active devices and quick actions (demo)</div>
      </div>

      <aside class="glass-card" style="padding:1rem;">
        <h5 style="margin:0 0 0.6rem 0">Alerts</h5>
        <div style="color:var(--muted);font-size:0.95rem">L. Gomez — HR 102 bpm · SpO₂ 92% (High)</div>
        <div style="margin-top:0.8rem"><button class="cta" id="ack">Acknowledge</button></div>
      </aside>
    </div>
  </main>

  <footer style="padding:1.2rem 2rem;color:var(--muted)">&copy; <span id="year"></span> HealthSense</footer>

  <script>
  // Setup year
  document.getElementById('year').textContent = new Date().getFullYear();

  // tsparticles
  if (window.tsParticles) {
    tsParticles.load("tsparticles", {
      fpsLimit: 60,
      particles: {
        number: { value: 60, density: { enable: true, area: 800 } },
        color: { value: ["#7afcff", "#6b46ff", "#7b61ff"] },
        shape: { type: "circle" },
        opacity: { value: 0.12 },
        size: { value: { min: 1, max: 4 } },
        move: { enable: true, speed: 0.8, direction: "none", outMode: "out" },
        links: { enable: true, distance: 150, color: "#6b46ff", opacity: 0.04, width: 1 }
      },
      interactivity: {
        events: { onHover: { enable: true, mode: "grab" }, onClick: { enable: true, mode: "push" } },
        modes: { grab: { distance: 140, links: { opacity: 0.12 } }, push: { quantity: 3 } }
      },
      detectRetina: true
    });
  }

  // GSAP animations
  if (window.gsap) {
    gsap.registerPlugin(ScrollTrigger);
    const tl = gsap.timeline({ defaults: { duration: 0.9, ease: "power3.out" }});
    tl.from(".logo", { y: -10, opacity: 0, delay: 0.1 })
      .from(".glass-card", { y: 10, opacity: 0, stagger: 0.06 }, "-=0.6")
      .from("#chart-telemetry", { scale: 0.98, opacity: 0 }, "-=0.5");
  }

  // Chart.js demo
  if (window.Chart) {
    const ctx = document.getElementById('chart-telemetry').getContext('2d');
    const labels = Array.from({length:24}, (_,i)=> i + 'm');
    const data = labels.map(()=> 60 + Math.random()*30);
    new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          label: 'Heart Rate',
          data,
          borderColor: 'rgba(122,252,255,0.95)',
          backgroundColor: 'rgba(107,70,255,0.06)',
          tension: 0.35,
          pointRadius: 0
        }]
      },
      options: { plugins:{legend:{display:false}}, scales:{x:{display:false}, y:{grid:{color:'rgba(255,255,255,0.03)'}}} }
    });
  }

  // Small interactions
  document.getElementById('analyze').addEventListener('click', ()=> {
    const b = document.getElementById('analyze');
    b.textContent = 'Analyzing…';
    b.disabled = true;
    setTimeout(()=>{ b.textContent = 'Analyze'; b.disabled = false; }, 1500);
  });
  document.getElementById('ack').addEventListener('click', ()=> {
    const b = document.getElementById('ack');
    b.textContent = 'Acknowledged ✓';
    b.disabled = true;
    setTimeout(()=>{ b.textContent = 'Acknowledge'; b.disabled = false; }, 1800);
  });
  </script>
</body>
</html>
"""

components.html(dashboard_html, height=920, scrolling=True)
