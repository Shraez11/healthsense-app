import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="HealthSense — Profile", layout="centered")

profile_html = r"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>HealthSense — Profile</title>

  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">
  <style>
  :root{
    --bg-1: #05060a; --bg-2: #071124; --glass-bg: rgba(255,255,255,0.04); --glass-border: rgba(255,255,255,0.06);
    --accent-1: #7afcff; --accent-2: #6b46ff; --muted: rgba(255,255,255,0.6); --glass-blur: 8px; --radius: 14px;
    font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial;
    color-scheme: dark;
  }
  *{box-sizing:border-box}
  html,body{height:100%}
  body{margin:0;background: linear-gradient(180deg,var(--bg-1),var(--bg-2));color:#e8eef8}
  .container{max-width:1000px;margin:0 auto;padding:2rem}
  .glass-card{background:var(--glass-bg);border:1px solid var(--glass-border);border-radius:var(--radius);padding:1.2rem;backdrop-filter: blur(var(--glass-blur));box-shadow: 0 8px 30px rgba(107,70,255,0.08);}
  .profile-head{display:flex;gap:1rem;align-items:center}
  .avatar{width:96px;height:96px;border-radius:14px;background:linear-gradient(180deg,#111827,#0b1222);display:flex;align-items:center;justify-content:center;font-weight:800;color:var(--accent-1);font-size:28px}
  .meta{color:var(--muted)}
  .stats{display:flex;gap:1rem;margin-top:1rem}
  .stat{padding:0.6rem;border-radius:10px;background:linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01))}
  .particles-bg{position:fixed;inset:0;z-index:0;pointer-events:none;opacity:0.45}
  </style>

  <script src="https://cdn.jsdelivr.net/npm/tsparticles@2.11.1/tsparticles.bundle.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/ScrollTrigger.min.js"></script>
</head>
<body>
  <div id="tsparticles" class="particles-bg" aria-hidden="true"></div>

  <div class="container" style="position:relative;z-index:5">
    <div class="glass-card profile-head">
      <div class="avatar">JS</div>
      <div style="flex:1">
        <h2 style="margin:0">Dr. Jane Smith</h2>
        <div class="meta">Cardiologist · Health Network</div>
        <div style="margin-top:0.6rem"><button class="cta" id="message">Message</button></div>
      </div>
      <div style="text-align:right">
        <div style="color:var(--muted)">On-call</div>
        <div style="font-weight:700">Today · 08:00–18:00</div>
      </div>
    </div>

    <div class="stats" style="margin-top:1rem">
      <div class="stat glass-card"><div style="font-weight:700;color:var(--accent-2)">1,254</div><div style="color:var(--muted)">Devices</div></div>
      <div class="stat glass-card"><div style="font-weight:700;color:#ff7b6b">42</div><div style="color:var(--muted)">Alerts (24h)</div></div>
      <div class="stat glass-card"><div style="font-weight:700;color:var(--accent-1)">74 bpm</div><div style="color:var(--muted)">Avg HR</div></div>
    </div>

    <div style="display:grid;grid-template-columns:2fr 1fr;gap:1rem;margin-top:1rem">
      <div class="glass-card">
        <h4 style="margin-top:0">Recent Vitals</h4>
        <ul style="margin:0;padding-left:1rem;color:var(--muted)">
          <li>A. Lee — HR 88 bpm · SpO₂ 96%</li>
          <li>M. Patel — HR 72 bpm · SpO₂ 98%</li>
          <li>L. Gomez — HR 102 bpm · SpO₂ 92% (Alert)</li>
        </ul>
      </div>

      <aside class="glass-card">
        <h5 style="margin:0 0 0.6rem 0">Preferences</h5>
        <div style="color:var(--muted)">Notifications: <strong>Enabled</strong></div>
        <div style="margin-top:0.8rem"><button class="cta" id="pref-btn">Edit</button></div>
      </aside>
    </div>
  </div>

  <script>
  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.cta').forEach(b => b.addEventListener('click', () => {
      const orig = b.textContent;
      b.textContent = 'Done ✓';
      b.disabled = true;
      setTimeout(()=>{ b.textContent = orig; b.disabled = false; }, 1500);
    }));

    if (window.tsParticles) {
      tsParticles.load("tsparticles", {
        fpsLimit: 60,
        particles: {
          number: { value: 40, density: { enable: true, area: 900 } },
          color: { value: ["#7afcff", "#6b46ff"] },
          opacity: { value: 0.12 },
          size: { value: { min: 1, max: 4 } },
          move: { enable: true, speed: 0.6 }
        },
        interactivity: { events: { onHover: { enable: true, mode: "bubble" } }, detectRetina: true }
      });
    }

    if (window.gsap) {
      gsap.registerPlugin(ScrollTrigger);
      gsap.from('.glass-card', { y: 12, opacity: 0, stagger: 0.06, duration: 0.6 });
    }
  });
  </script>
</body>
</html>
"""

components.html(profile_html, height=840, scrolling=True)
