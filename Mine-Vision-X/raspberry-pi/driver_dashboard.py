<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MINE VISION X — HEMM Safety Monitoring System</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.css" />
<style>
  :root{
    --bg-0:#050b16;
    --bg-1:#08111f;
    --panel:#0a1526;
    --panel-2:#0d1c33;
    --line:#1d3a5f;
    --accent:#2ea1ff;
    --accent-2:#5ec8ff;
    --text-0:#eaf3ff;
    --text-1:#9fb6cf;
    --text-2:#6d8299;
    --green:#22e07a;
    --amber:#ffc12b;
    --amber-2:#ffd873;
    --red:#ff3b3b;
    --red-2:#ff6b6b;
    --radius-lg:14px;
    --radius-md:10px;
    --radius-sm:6px;
    --theme-accent:var(--accent);
    --theme-line:var(--line);
    --theme-glow:0 0 18px rgba(46,161,255,.35);
    --transition-theme: background-color .3s ease, border-color .3s ease, box-shadow .3s ease, color .3s ease;
  }

  *{box-sizing:border-box; margin:0; padding:0;}

  html,body{ height:100%; }
  body{
    background:
      radial-gradient(ellipse at 20% -10%, rgba(46,161,255,.10), transparent 45%),
      radial-gradient(ellipse at 100% 0%, rgba(46,161,255,.06), transparent 40%),
      var(--bg-0);
    color:var(--text-0);
    font-family: 'Rajdhani','Segoe UI',Arial, sans-serif;
    transition: var(--transition-theme);
    position:relative;
  }

  /* ---------- WARNING (yellow) & CRITICAL (red) theme states ---------- */
  body.warning-mode{
    --theme-accent:var(--amber);
    --theme-line:#6b4e0a;
    --theme-glow:0 0 22px rgba(255,193,43,.45);
  }
  body.critical-mode{
    --theme-accent:var(--red);
    --theme-line:#5c1414;
    --theme-glow:0 0 22px rgba(255,59,59,.45);
  }

  /* Full-viewport blink overlay: gives the "whole dashboard blinks" effect
     without destroying panel content, using a real on/off flash (steps). */
  #blinkOverlay{
    position:fixed; inset:0; pointer-events:none; z-index:500;
    opacity:0;
    background: rgba(255,193,43,.16);
    mix-blend-mode:screen;
  }
  body.warning-mode #blinkOverlay{
    background: rgba(255,193,43,.20);
    animation: blinkFlash 1s steps(1,end) infinite;
  }
  body.critical-mode #blinkOverlay{
    background: rgba(255,59,59,.22);
    animation: blinkFlash .6s steps(1,end) infinite;
  }
  @keyframes blinkFlash{
    0%, 49%{ opacity:1; }
    50%, 100%{ opacity:0; }
  }

  /* Also flash the outer app border/background subtly in sync */
  body.warning-mode #app{ animation: bgFlashAmber 1s steps(1,end) infinite; }
  body.critical-mode #app{ animation: bgFlashRed .6s steps(1,end) infinite; }
  @keyframes bgFlashAmber{
    0%,49%{ box-shadow: inset 0 0 0 1px rgba(255,193,43,.0); }
    50%,100%{ box-shadow: inset 0 0 60px rgba(255,193,43,.10); }
  }
  @keyframes bgFlashRed{
    0%,49%{ box-shadow: inset 0 0 0 1px rgba(255,59,59,.0); }
    50%,100%{ box-shadow: inset 0 0 60px rgba(255,59,59,.12); }
  }

  #app{
    max-width:1600px;
    margin:0 auto;
    padding:18px 22px 26px;
    display:flex;
    flex-direction:column;
    gap:16px;
    min-height:100vh;
    position:relative;
  }

  /* ---------- Shared panel chrome ---------- */
  .panel{
    position:relative;
    background:linear-gradient(180deg, var(--panel-2), var(--panel));
    border:1px solid var(--theme-line);
    border-radius:var(--radius-lg);
    box-shadow: inset 0 0 0 1px rgba(255,255,255,.02), 0 8px 24px rgba(0,0,0,.35);
    transition: var(--transition-theme);
  }
  .panel::before, .panel::after{
    content:"";
    position:absolute;
    width:26px;height:26px;
    border:2px solid var(--theme-accent);
    opacity:.85;
    transition: var(--transition-theme);
  }
  .panel::before{ top:-1px; left:-1px; border-right:none; border-bottom:none; border-top-left-radius:var(--radius-lg); }
  .panel::after{ bottom:-1px; right:-1px; border-left:none; border-top:none; border-bottom-right-radius:var(--radius-lg); }

  /* ---------- Header ---------- */
  header.panel{
    display:flex;
    align-items:center;
    justify-content:space-between;
    padding:14px 28px;
    gap:20px;
    flex-wrap:wrap;
  }
  .brand{ display:flex; flex-direction:column; align-items:center; text-align:center; }
  .brand h1{
    font-size:clamp(24px,3vw,38px);
    font-weight:800;
    letter-spacing:3px;
    color:var(--text-0);
    line-height:1;
    font-family:'Orbitron','Rajdhani',sans-serif;
  }
  .brand h1 span{ color:var(--theme-accent); text-shadow: var(--theme-glow); transition: var(--transition-theme); }
  .brand .sub{ margin-top:6px; font-size:12px; letter-spacing:5px; color:var(--text-1); font-weight:600; }
  .header-side{ display:flex; align-items:center; gap:18px; min-width:170px; }
  .header-side.left{ justify-content:flex-start; }
  .header-side.right{ justify-content:flex-end; }
  .clock{ text-align:right; font-size:13px; color:var(--text-1); line-height:1.3; font-weight:600; }
  .icon-btn{
    width:38px;height:38px; display:flex;align-items:center;justify-content:center;
    border:1px solid var(--theme-line); border-radius:var(--radius-sm);
    color:var(--theme-accent); background:rgba(255,255,255,.02); transition: var(--transition-theme);
  }
  .wifi-icon svg, .gear-icon svg{ width:20px; height:20px; stroke:var(--theme-accent); transition:var(--transition-theme);}

  .chevron-deco{ position:absolute; top:10px; width:70px;height:70px; pointer-events:none; opacity:.9; }
  .chevron-deco.left{ left:14px; }
  .chevron-deco.right{ right:14px; transform:scaleX(-1); }

  /* ---------- Alert banner (shared by warning + critical) ---------- */
  #warningBanner{
    display:flex; align-items:center; gap:20px; padding:18px 28px;
    border-radius:var(--radius-lg);
    background:linear-gradient(180deg, rgba(58,15,15,.9), rgba(15,4,4,.9));
    border:1px solid var(--red);
    box-shadow: 0 0 26px rgba(255,59,59,.35), inset 0 0 30px rgba(255,59,59,.08);
    max-height:0; opacity:0; overflow:hidden; padding-top:0; padding-bottom:0; border-width:0;
    transition: max-height .3s ease, opacity .25s ease, padding .3s ease, border-width .3s ease;
  }
  body.warning-mode #warningBanner.show{
    max-height:140px; opacity:1; padding:18px 28px; border-width:1px;
    background:linear-gradient(180deg, rgba(74,54,4,.92), rgba(24,17,2,.92));
    border-color:var(--amber);
    box-shadow: 0 0 26px rgba(255,193,43,.35), inset 0 0 30px rgba(255,193,43,.08);
  }
  body.critical-mode #warningBanner.show{
    max-height:140px; opacity:1; padding:18px 28px; border-width:1px;
    background:linear-gradient(180deg, rgba(58,15,15,.92), rgba(15,4,4,.92));
    border-color:var(--red);
    box-shadow: 0 0 26px rgba(255,59,59,.35), inset 0 0 30px rgba(255,59,59,.08);
  }
  #warningBanner .warn-icon{ flex:0 0 auto; width:52px;height:52px; color:#fff; }
  #warningBanner .warn-icon svg{ width:100%; height:100%; filter: drop-shadow(0 0 10px rgba(255,80,80,.8)); }
  body.warning-mode #warningBanner .warn-icon svg{ filter: drop-shadow(0 0 10px rgba(255,193,43,.8)); }
  #warningBanner .warn-divider{ width:1px; align-self:stretch; background:rgba(255,255,255,.25); }
  #warningBanner .warn-text{ display:flex; flex-direction:column; gap:6px; }
  #warningBanner .warn-title{ font-size:clamp(20px,3vw,34px); font-weight:800; letter-spacing:1px; color:#fff; }
  #warningBanner .warn-sub{ font-size:clamp(14px,1.6vw,19px); color:#ffd0d0; font-weight:600; letter-spacing:.5px; }
  body.warning-mode #warningBanner .warn-sub{ color:#ffe9b0; }
  #warningBanner .warn-sub b{ color:#fff; font-size:1.15em; text-shadow:0 0 10px rgba(255,80,80,.8); }
  body.warning-mode #warningBanner .warn-sub b{ text-shadow:0 0 10px rgba(255,193,43,.8); }
  #warningBanner .warn-tag{
    margin-left:auto; align-self:flex-start;
    font-size:11px; font-weight:800; letter-spacing:1.5px;
    padding:5px 10px; border-radius:5px;
    background:rgba(255,59,59,.18); border:1px solid var(--red); color:#fff;
  }
  body.warning-mode #warningBanner .warn-tag{ background:rgba(255,193,43,.18); border-color:var(--amber); color:#2a1c00; }

  /* ---------- Main grid ---------- */
  .main-grid{
    display:grid;
    grid-template-columns: 1.35fr 1fr;
    gap:16px;
    align-items:stretch;
  }
  @media (max-width:980px){ .main-grid{ grid-template-columns:1fr; } }

  .section-panel{ padding:16px; display:flex; flex-direction:column; gap:12px; min-height:440px; }
  .section-head{ display:flex; align-items:center; justify-content:space-between; }
  .section-title{ display:flex; align-items:center; gap:10px; font-weight:700; letter-spacing:1.5px; font-size:15px; color:var(--text-0); }
  .section-title svg{ width:20px;height:20px; stroke:var(--text-0); fill:none; }
  .live-badge{ display:flex; align-items:center; gap:6px; font-size:12px; font-weight:700; letter-spacing:1px; color:var(--green); }
  .live-dot{ width:9px;height:9px;border-radius:50%; background:var(--green); box-shadow:0 0 8px var(--green); animation: blink 1.4s infinite; }
  body.critical-mode .live-badge{ color:var(--red-2); }
  body.critical-mode .live-dot{ background:var(--red-2); box-shadow:0 0 8px var(--red-2); }
  body.warning-mode .live-badge{ color:var(--amber-2); }
  body.warning-mode .live-dot{ background:var(--amber-2); box-shadow:0 0 8px var(--amber-2); }
  @keyframes blink{ 0%,100%{opacity:1;} 50%{opacity:.35;} }

  /* Camera views */
  .camera-grid{ display:grid; grid-template-columns:1fr 1fr; gap:12px; flex:1; min-height:260px; }
  .cam-feed{ position:relative; border-radius:var(--radius-md); overflow:hidden; border:1px solid var(--theme-line); background:#0d1420; min-height:220px; }
  .cam-label{
    position:absolute; top:10px; left:10px; background:rgba(6,12,22,.75); border:1px solid rgba(255,255,255,.15);
    color:#fff; font-size:11px; font-weight:700; letter-spacing:1.5px; padding:5px 10px; border-radius:4px; z-index:5;
  }
  .cam-scene{ position:absolute; inset:0; }
  .cam-scene svg{ width:100%; height:100%; display:block; }

  .bbox{
    position:absolute; border:2px solid var(--red); box-shadow:0 0 12px rgba(255,59,59,.8);
    display:none; z-index:6; animation: bboxPulse 1s infinite;
  }
  .bbox.warn{ border-color:var(--amber); box-shadow:0 0 12px rgba(255,193,43,.8); }
  @keyframes bboxPulse{ 0%,100%{ box-shadow:0 0 8px rgba(255,59,59,.6);} 50%{ box-shadow:0 0 18px rgba(255,59,59,1);} }
  .bbox .bbox-tag{ position:absolute; top:-24px; left:-2px; background:var(--red); color:#fff; font-size:10.5px; font-weight:800; letter-spacing:.5px; padding:3px 7px; white-space:nowrap; }
  .bbox.warn .bbox-tag{ background:var(--amber); color:#2a1c00; }
  .bbox .bbox-tag small{ display:block; font-size:9px; font-weight:700; opacity:.9; }
  .cam-feed.obstacle-active .bbox{ display:block; }

  .cam-vignette{ position:absolute; inset:0; background: radial-gradient(ellipse at 50% 40%, transparent 55%, rgba(0,0,0,.55) 100%); pointer-events:none; }
  .cam-scanlines{ position:absolute; inset:0; background: repeating-linear-gradient(0deg, rgba(255,255,255,.025) 0px, rgba(255,255,255,.025) 1px, transparent 1px, transparent 3px); mix-blend-mode:overlay; pointer-events:none; }

  /* Map panel */
  #mapWrap{ flex:1; min-height:300px; position:relative; border-radius:var(--radius-md); border:1px solid var(--theme-line); overflow:hidden; }
  #map{ position:absolute; inset:0; width:100%; height:100%; }
  .leaflet-container{ background:#0d1420; }
  #mapFallback{
    position:absolute; inset:0; display:none; align-items:center; justify-content:center; text-align:center;
    padding:20px; font-size:13px; color:var(--text-1); background:#0d1420;
  }

  /* Status / RPM panel */
  #statusPanel{
    display:flex; align-items:center; justify-content:space-between; padding:20px 30px;
    border-radius:var(--radius-lg);
    background:linear-gradient(180deg, rgba(15,58,36,.55), rgba(6,15,10,.6));
    border:1px solid var(--green);
    box-shadow:0 0 20px rgba(34,224,122,.18), inset 0 0 26px rgba(34,224,122,.05);
    gap:20px; flex-wrap:wrap;
    transition: max-height .3s ease, opacity .25s ease, padding .3s ease, margin .3s ease, border-color .3s ease, background .3s ease;
    max-height:220px; opacity:1; overflow:hidden;
  }
  #statusPanel.hidden-panel{ max-height:0; opacity:0; padding-top:0; padding-bottom:0; border-width:0; margin:0; }
  #statusPanel.state-warning{
    border-color:var(--amber);
    background:linear-gradient(180deg, rgba(74,54,4,.55), rgba(20,15,2,.6));
    box-shadow:0 0 20px rgba(255,193,43,.20), inset 0 0 26px rgba(255,193,43,.06);
  }
  .speed-left{ display:flex; align-items:center; gap:18px; }
  .gauge-wrap{ position:relative; width:78px; height:78px; }
  .gauge-wrap svg{ width:100%; height:100%; }
  .gauge-cog{ position:absolute; bottom:2px; right:2px; width:22px;height:22px; color:var(--green); }
  #statusPanel.state-warning .gauge-cog{ color:var(--amber); }
  .speed-label{ display:flex; flex-direction:column; gap:2px; }
  .speed-label .sp-title{ font-size:19px; font-weight:800; letter-spacing:1px; color:var(--text-0); }
  .speed-label .sp-sub{ font-size:12px; font-weight:700; letter-spacing:2px; color:var(--text-2); }
  .speed-value{ display:flex; align-items:baseline; gap:8px; font-family:'Orbitron','Rajdhani',sans-serif; }
  .speed-value .num{ font-size:clamp(46px,6vw,74px); font-weight:800; color:#fff; line-height:1; text-shadow:0 0 18px rgba(34,224,122,.35); }
  .speed-value .unit{ font-size:20px; font-weight:700; color:var(--text-1); }
  .status-right{ display:flex; align-items:center; gap:16px; }
  .status-divider{ width:1px; height:46px; background:rgba(255,255,255,.15); }
  .status-check{ width:40px;height:40px; color:var(--green); }
  #statusPanel.state-warning .status-check{ color:var(--amber); }
  .status-text{ display:flex; flex-direction:column; }
  .status-text .st-label{ font-size:11px; letter-spacing:2px; color:var(--text-2); font-weight:700; }
  .status-text .st-value{ font-size:20px; font-weight:800; color:var(--green); letter-spacing:1px; }

  /* Report button */
  #reportBtn{
    display:flex; align-items:center; justify-content:center; gap:12px; width:100%; padding:18px;
    border-radius:var(--radius-lg); border:1px solid #ff5b5b;
    background:linear-gradient(180deg,#ff4b4b,#c81f1f); color:#fff; font-family:inherit;
    font-size:clamp(18px,2.4vw,26px); font-weight:800; letter-spacing:2px; cursor:pointer;
    box-shadow:0 8px 22px rgba(200,20,20,.35), inset 0 1px 0 rgba(255,255,255,.25);
    transition:transform .15s ease, box-shadow .2s ease;
  }
  #reportBtn:hover{ transform:translateY(-2px); box-shadow:0 12px 28px rgba(200,20,20,.5); }
  #reportBtn:active{ transform:translateY(0); }
  #reportBtn svg{ width:24px;height:24px; }

  /* Demo controls */
  #demoControls{
    position:fixed; right:16px; bottom:16px; z-index:999;
    background:rgba(6,12,22,.94); border:1px solid var(--theme-line); border-radius:10px; padding:10px;
    display:flex; flex-direction:column; gap:6px; box-shadow:0 8px 20px rgba(0,0,0,.5);
    font-size:11px; backdrop-filter:blur(6px); max-width:170px; transition: var(--transition-theme);
  }
  #demoControls .dc-title{
    font-size:9.5px; letter-spacing:1.5px; color:var(--text-2); font-weight:700; margin-bottom:2px;
    display:flex; justify-content:space-between; align-items:center; cursor:pointer; user-select:none;
  }
  #demoControls .dc-body{ display:flex; flex-direction:column; gap:6px; }
  #demoControls.collapsed .dc-body{ display:none; }
  #demoControls button{
    font-family:inherit; font-size:11px; font-weight:700; letter-spacing:.5px; padding:7px 8px;
    border-radius:6px; border:1px solid var(--theme-line); background:rgba(255,255,255,.03); color:var(--text-1);
    cursor:pointer; text-align:left; transition:background .15s ease, color .15s ease, border-color .15s ease;
  }
  #demoControls button:hover{ background:rgba(255,255,255,.08); color:#fff; }
  #demoControls button.active{ color:#fff; border-color:var(--theme-accent); background:rgba(46,161,255,.12); }
  #demoControls .dc-toggle{ background:none; border:none; color:var(--text-2); font-size:13px; padding:0; }

  .footnote{ text-align:center; font-size:11px; color:var(--text-2); letter-spacing:1px; padding-top:2px; }

  .leaflet-popup-content-wrapper{ background:#0a1526; color:#eaf3ff; }
  .leaflet-popup-tip{ background:#0a1526; }
</style>
</head>
<body>

<div id="blinkOverlay"></div>

<div id="app">

  <!-- HEADER -->
  <header class="panel">
    <svg class="chevron-deco left" viewBox="0 0 70 70" fill="none"><path d="M2 30 L28 2 M10 40 L36 12 M18 50 L44 22" stroke="var(--theme-accent)" stroke-width="2.5" stroke-linecap="round" opacity="0.85"/></svg>
    <svg class="chevron-deco right" viewBox="0 0 70 70" fill="none"><path d="M2 30 L28 2 M10 40 L36 12 M18 50 L44 22" stroke="var(--theme-accent)" stroke-width="2.5" stroke-linecap="round" opacity="0.85"/></svg>

    <div class="header-side left"></div>

    <div class="brand">
      <h1>MINE V<span>I</span>SION <span>X</span></h1>
      <div class="sub">HEMM SAFETY MONITORING SYSTEM</div>
    </div>

    <div class="header-side right">
      <div class="wifi-icon icon-btn" title="Connected">
        <svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5a11 11 0 0 1 14 0"/><path d="M8.5 16a6 6 0 0 1 7 0"/><circle cx="12" cy="19.5" r="1" fill="currentColor" stroke="none"/></svg>
      </div>
      <div class="clock">
        <div id="dateStr">--</div>
        <div id="timeStr">--:--</div>
      </div>
      <div class="gear-icon icon-btn" title="Settings">
        <svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.6a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
      </div>
    </div>
  </header>

  <!-- ALERT BANNER (warning = yellow, critical = red) -->
  <div id="warningBanner">
    <div class="warn-icon">
      <svg viewBox="0 0 24 24" fill="currentColor"><path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/></svg>
    </div>
    <div class="warn-divider"></div>
    <div class="warn-text">
      <div class="warn-title" id="warnTitle">OBSTACLE DETECTED AHEAD</div>
      <div class="warn-sub" id="warnSub">DISTANCE : <b id="warnValue">28 m</b></div>
    </div>
    <div class="warn-tag" id="warnTag">CRITICAL</div>
  </div>

  <!-- MAIN GRID -->
  <div class="main-grid">

    <!-- CAMERA -->
    <section class="panel section-panel">
      <div class="section-head">
        <div class="section-title">
          <svg viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M23 7l-7 5 7 5V7z"/><rect x="1" y="5" width="15" height="14" rx="2"/></svg>
          VEHICLE CAMERA VIEW
        </div>
        <div class="live-badge"><span class="live-dot"></span>LIVE</div>
      </div>

      <div class="camera-grid">
        <div class="cam-feed" id="frontCam">
          <div class="cam-label">FRONT VIEW</div>
          <div class="cam-scene" id="frontScene"></div>
          <div class="cam-vignette"></div>
          <div class="cam-scanlines"></div>
          <div class="bbox" id="frontBbox" style="left:38%; top:34%; width:22%; height:52%;">
            <div class="bbox-tag">PERSON<small id="bboxDist">28 m</small></div>
          </div>
        </div>
        <div class="cam-feed" id="rearCam">
          <div class="cam-label">REAR VIEW</div>
          <div class="cam-scene" id="rearScene"></div>
          <div class="cam-vignette"></div>
          <div class="cam-scanlines"></div>
        </div>
      </div>
    </section>

    <!-- MAP -->
    <section class="panel section-panel">
      <div class="section-head">
        <div class="section-title">
          <svg viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
          LIVE MAP
        </div>
        <div class="live-badge"><span class="live-dot"></span>LIVE</div>
      </div>
      <div id="mapWrap">
        <div id="map"></div>
        <div id="mapFallback">Map tiles need an internet connection to load (OpenStreetMap).<br>The HEMM_01 marker and alert radius still update live below once tiles connect.</div>
      </div>
    </section>
  </div>

  <!-- STATUS / RPM -->
  <div id="statusPanel">
    <div class="speed-left">
      <div class="gauge-wrap">
        <svg viewBox="0 0 100 100">
          <path d="M15 78 A40 40 0 0 1 85 78" fill="none" stroke="rgba(255,255,255,.08)" stroke-width="9" stroke-linecap="round"/>
          <path id="gaugeArc" d="M15 78 A40 40 0 0 1 85 78" fill="none" stroke="#22e07a" stroke-width="9" stroke-linecap="round" stroke-dasharray="126" stroke-dashoffset="60"/>
          <line id="gaugeNeedle" x1="50" y1="78" x2="50" y2="40" stroke="#eaf3ff" stroke-width="3" stroke-linecap="round" transform="rotate(-45 50 78)"/>
          <circle cx="50" cy="78" r="4" fill="#eaf3ff"/>
        </svg>
        <svg class="gauge-cog" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.6a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
      </div>
      <div class="speed-label">
        <div class="sp-title">SPEED</div>
        <div class="sp-sub">(RPM)</div>
      </div>
    </div>

    <div class="speed-value">
      <span class="num" id="rpmValue">38</span>
      <span class="unit">RPM</span>
    </div>

    <div class="status-right">
      <div class="status-divider"></div>
      <svg class="status-check" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M8 12.5l2.5 2.5L16 9"/></svg>
      <div class="status-text">
        <div class="st-label">STATUS</div>
        <div class="st-value" id="statusValue">NORMAL</div>
      </div>
    </div>
  </div>

  <!-- REPORT -->
  <button id="reportBtn">
    <svg viewBox="0 0 24 24" fill="currentColor"><path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/></svg>
    REPORT
  </button>

  <div class="footnote">HEMM_01 &nbsp;•&nbsp; Simulated telemetry for demonstration &nbsp;•&nbsp; Mine Vision X v1.1</div>
</div>

<!-- DEMO CONTROLS -->
<div id="demoControls">
  <div class="dc-title" id="dcToggle">DEMO CONTROLS <span class="dc-toggle">▾</span></div>
  <div class="dc-body">
    <button data-mode="auto" class="active">Auto Simulation</button>
    <button data-mode="normal">Force Normal (&gt;50m)</button>
    <button data-mode="obstacle-warn">Obstacle Warning (20–50m)</button>
    <button data-mode="obstacle-crit">Obstacle Critical (0–19m)</button>
    <button data-mode="rpm">RPM Alert (&gt;40)</button>
    <button data-mode="impact">Impact Alert</button>
  </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.js"></script>
<script>
(function(){
  "use strict";

  /* ============ CAMERA SCENES (SVG) ============ */
  function roadScene(withPerson, withTruck){
    return `
    <svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice">
      <defs>
        <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#8fa9bf"/>
          <stop offset="100%" stop-color="#c9d3d6"/>
        </linearGradient>
        <linearGradient id="ground" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#a99c8c"/>
          <stop offset="100%" stop-color="#6b6157"/>
        </linearGradient>
      </defs>
      <rect x="0" y="0" width="400" height="150" fill="url(#sky)"/>
      <polygon points="0,150 90,90 160,150" fill="#7d7568"/>
      <polygon points="140,150 230,80 330,150" fill="#6f6759"/>
      <rect x="0" y="140" width="400" height="160" fill="url(#ground)"/>
      <polygon points="140,300 175,150 225,150 260,300" fill="#8a8072"/>
      ${withTruck? `
      <g transform="translate(150,175) scale(1.15)">
        <rect x="0" y="10" width="70" height="30" rx="3" fill="#f2b705"/>
        <rect x="8" y="-14" width="30" height="26" rx="2" fill="#e0a500"/>
        <rect x="12" y="-9" width="22" height="12" fill="#3a3a3a"/>
        <circle cx="14" cy="42" r="11" fill="#1a1a1a"/>
        <circle cx="56" cy="42" r="11" fill="#1a1a1a"/>
        <circle cx="14" cy="42" r="4" fill="#555"/>
        <circle cx="56" cy="42" r="4" fill="#555"/>
        <rect x="-4" y="18" width="8" height="6" fill="#c0392b"/>
      </g>` : ``}
      ${withPerson? `
      <g transform="translate(178,168)">
        <circle cx="12" cy="0" r="7" fill="#e8b98a"/>
        <path d="M2 -4 a10 8 0 0 1 20 0 z" fill="#fff"/>
        <rect x="0" y="7" width="24" height="26" rx="3" fill="#ff8a00"/>
        <rect x="0" y="7" width="24" height="26" rx="3" fill="none" stroke="#fff" stroke-width="2" stroke-dasharray="4 3"/>
        <rect x="2" y="33" width="8" height="24" fill="#2b2b2b"/>
        <rect x="14" y="33" width="8" height="24" fill="#2b2b2b"/>
      </g>` : ``}
      <polygon points="0,300 60,300 40,220 20,220" fill="#c9a227" opacity=".9"/>
      <polygon points="340,300 400,300 380,215 355,215" fill="#c9a227" opacity=".9"/>
      <rect x="0" y="260" width="400" height="40" fill="#4a4238"/>
    </svg>`;
  }

  document.getElementById('frontScene').innerHTML = roadScene(false, true);
  document.getElementById('rearScene').innerHTML = roadScene(false, true);

  function setFrontScene(hasPerson){
    document.getElementById('frontScene').innerHTML = roadScene(!!hasPerson, true);
  }

  /* ============ CLOCK ============ */
  function pad(n){ return n.toString().padStart(2,'0'); }
  function updateClock(){
    const d = new Date();
    const months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
    document.getElementById('dateStr').textContent = `${pad(d.getDate())} ${months[d.getMonth()]} ${d.getFullYear()}`;
    let h = d.getHours();
    const ampm = h >= 12 ? 'PM' : 'AM';
    h = h % 12; if(h===0) h = 12;
    document.getElementById('timeStr').textContent = `${pad(h)}:${pad(d.getMinutes())} ${ampm}`;
  }
  updateClock();
  setInterval(updateClock, 1000);

  /* ============ MAP ============ */
  const baseLat = 23.6345, baseLng = 85.3803; // representative mining-belt coordinates
  let lat = baseLat, lng = baseLng;
  let map = null, marker = null, dangerCircle = null;

  function makeIcon(color){
    return L.divIcon({
      className:'',
      html:`<div style="position:relative;width:34px;height:44px;">
              <svg viewBox="0 0 24 32" width="34" height="44">
                <path d="M12 0C5.4 0 0 5.4 0 12c0 9 12 20 12 20s12-11 12-20C24 5.4 18.6 0 12 0z" fill="${color}" stroke="#fff" stroke-width="1"/>
                <circle cx="12" cy="12" r="5" fill="#0a1526"/>
              </svg>
            </div>`,
      iconSize:[34,44],
      iconAnchor:[17,44]
    });
  }

  let normalIcon, warnIcon, critIcon;

  function initMap(){
    try{
      map = L.map('map', { zoomControl:false, attributionControl:false }).setView([lat, lng], 16);

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom:19,
        crossOrigin:true
      }).addTo(map);

      L.control.zoom({ position:'topright' }).addTo(map);
      L.control.attribution({ position:'bottomright', prefix:false }).addAttribution('© OpenStreetMap contributors').addTo(map);

      normalIcon = makeIcon('#2ea1ff');
      warnIcon = makeIcon('#ffc12b');
      critIcon = makeIcon('#ff3b3b');

      marker = L.marker([lat,lng], {icon:normalIcon}).addTo(map).bindPopup('<b>HEMM_01</b>').openPopup();

      dangerCircle = L.circle([lat,lng], {
        radius: 45, color:'#ff3b3b', fillColor:'#ff3b3b', fillOpacity:0.18, weight:2, opacity:0
      }).addTo(map);

      // Leaflet needs a correctly-sized container; force a couple of
      // re-checks after layout/fonts settle so the map always paints.
      setTimeout(()=> map.invalidateSize(), 150);
      setTimeout(()=> map.invalidateSize(), 500);
      window.addEventListener('resize', ()=> map && map.invalidateSize());
      window.addEventListener('load', ()=> map && map.invalidateSize());

    }catch(err){
      document.getElementById('mapFallback').style.display = 'flex';
      console.error('Map init failed:', err);
    }
  }
  initMap();

  function updateMap(level){ // 'normal' | 'warning' | 'critical'
    if(!map || !marker) return;
    marker.setIcon(level==='critical' ? critIcon : (level==='warning' ? warnIcon : normalIcon));
    marker.setLatLng([lat,lng]);
    if(level === 'critical'){
      dangerCircle.setLatLng([lat,lng]);
      dangerCircle.setStyle({opacity:0.85, fillOpacity:0.20, color:'#ff3b3b', fillColor:'#ff3b3b'});
    } else if(level === 'warning'){
      dangerCircle.setLatLng([lat,lng]);
      dangerCircle.setStyle({opacity:0.75, fillOpacity:0.16, color:'#ffc12b', fillColor:'#ffc12b'});
    } else {
      dangerCircle.setStyle({opacity:0, fillOpacity:0});
    }
  }

  /* ============ GAUGE ============ */
  function setGauge(rpm, color){
    const pct = Math.max(0, Math.min(1, rpm/60));
    const offset = 126 - pct*126;
    const arc = document.getElementById('gaugeArc');
    arc.style.strokeDashoffset = offset.toFixed(1);
    arc.setAttribute('stroke', color);
    const angle = -135 + pct*180;
    document.getElementById('gaugeNeedle').setAttribute('transform', `rotate(${angle} 50 78)`);
  }

  /* ============ STATE ============ */
  // Distance thresholds (meters): >50 normal | 20-50 warning | 0-19 critical
  // RPM: >40 => critical blink red. <=40 => no RPM-driven alert.
  // Impact: |IMU x or y| > 2.0g => critical blink red.
  let mode = 'auto';
  let forcedUntil = 0;
  let sim = { distance: 85, rpm: 36, imu: {x:0.2,y:-0.1,z:0.98} };

  const body = document.body;
  const warningBanner = document.getElementById('warningBanner');
  const statusPanel = document.getElementById('statusPanel');
  const frontCam = document.getElementById('frontCam');
  const frontBbox = document.getElementById('frontBbox');
  const rpmValueEl = document.getElementById('rpmValue');
  const statusValueEl = document.getElementById('statusValue');
  const warnTitle = document.getElementById('warnTitle');
  const warnSub = document.getElementById('warnSub');
  const warnTag = document.getElementById('warnTag');

  function rand(min,max){ return Math.random()*(max-min)+min; }

  function classify(){
    const impact = Math.abs(sim.imu.x) > 2.0 || Math.abs(sim.imu.y) > 2.0;
    if(impact) return {level:'critical', type:'impact'};
    if(sim.rpm > 40) return {level:'critical', type:'rpm'};
    if(sim.distance < 20) return {level:'critical', type:'obstacle'};
    if(sim.distance <= 50) return {level:'warning', type:'obstacle'};
    return {level:'normal', type:'none'};
  }

  function step(){
    const now = Date.now();

    if(mode !== 'auto'){
      if(now > forcedUntil){ mode = 'auto'; setActiveDemoBtn('auto'); }
      else{
        if(mode === 'obstacle-warn'){ sim.distance = 35 + rand(-8,8); sim.rpm = 30+rand(-3,3); sim.imu.x=0.3; sim.imu.y=-0.2; }
        else if(mode === 'obstacle-crit'){ sim.distance = 10 + rand(-4,4); sim.rpm = 30+rand(-3,3); sim.imu.x=0.3; sim.imu.y=-0.2; }
        else if(mode === 'rpm'){ sim.rpm = 46 + rand(-2,5); sim.distance = 90+rand(-10,10); sim.imu.x=0.2; sim.imu.y=0.1; }
        else if(mode === 'impact'){ sim.imu.x = 2.4*(Math.random()<0.5?-1:1); sim.imu.y = 2.2*(Math.random()<0.5?-1:1); sim.rpm=34+rand(-3,3); sim.distance=90+rand(-10,10); }
        else if(mode === 'normal'){ sim.distance = 90+rand(-10,10); sim.rpm = 34+rand(-3,3); sim.imu.x=0.2; sim.imu.y=-0.1; }
      }
    }

    if(mode === 'auto'){
      sim.distance += rand(-9,9);
      sim.distance = Math.max(3, Math.min(140, sim.distance));
      sim.rpm += rand(-2.5,2.5);
      sim.rpm = Math.max(18, Math.min(52, sim.rpm));
      sim.imu.x += rand(-0.15,0.15); sim.imu.x = Math.max(-2.6, Math.min(2.6, sim.imu.x));
      sim.imu.y += rand(-0.15,0.15); sim.imu.y = Math.max(-2.6, Math.min(2.6, sim.imu.y));
      sim.imu.z = 0.98 + rand(-0.1,0.1);

      if(Math.random() < 0.03) sim.distance = rand(3,18);
      else if(Math.random() < 0.05) sim.distance = rand(20,50);
      if(Math.random() < 0.02) sim.rpm = rand(41,52);
      if(Math.random() < 0.012){ sim.imu.x = rand(2.1,2.6) * (Math.random()<0.5?-1:1); }
    }

    lat += rand(-0.00004, 0.00004);
    lng += rand(-0.00004, 0.00004);

    render(classify());
  }

  function setActiveDemoBtn(m){
    document.querySelectorAll('#demoControls button[data-mode]').forEach(b=>{
      b.classList.toggle('active', b.dataset.mode === m);
    });
  }

  function render(cls){
    const level = cls.level;
    const type = cls.type;

    body.classList.toggle('warning-mode', level==='warning');
    body.classList.toggle('critical-mode', level==='critical');

    warningBanner.classList.toggle('show', level !== 'normal');
    statusPanel.classList.toggle('hidden-panel', level==='critical');
    statusPanel.classList.toggle('state-warning', level==='warning');

    const showBbox = (type === 'obstacle');
    frontCam.classList.toggle('obstacle-active', showBbox);
    setFrontScene(showBbox);
    frontBbox.classList.toggle('warn', level==='warning');

    if(level !== 'normal'){
      warnTag.textContent = level.toUpperCase();
      if(type === 'obstacle'){
        warnTitle.textContent = level==='critical' ? 'OBSTACLE DETECTED AHEAD' : 'OBSTACLE APPROACHING';
        warnSub.innerHTML = 'DISTANCE : <b>' + Math.round(sim.distance) + ' m</b>';
        document.getElementById('bboxDist').textContent = Math.round(sim.distance) + ' m';
      } else if(type === 'rpm'){
        warnTitle.textContent = 'VEHICLE SPEED ALERT';
        warnSub.innerHTML = 'RPM : <b>' + Math.round(sim.rpm) + ' RPM</b> — EXCEEDS SAFE LIMIT (40)';
      } else if(type === 'impact'){
        const peak = Math.max(Math.abs(sim.imu.x), Math.abs(sim.imu.y)).toFixed(2);
        warnTitle.textContent = 'IMPACT / TILT ALERT';
        warnSub.innerHTML = 'IMU DEVIATION : <b>' + peak + ' g</b> — OUTSIDE SAFE RANGE (±2.0g)';
      }
    }

    rpmValueEl.textContent = Math.round(sim.rpm);
    const gaugeColor = sim.rpm > 40 ? '#ff3b3b' : '#22e07a';
    setGauge(sim.rpm, gaugeColor);

    if(level === 'critical'){
      statusValueEl.textContent = type==='obstacle' ? 'OBSTACLE' : (type==='rpm' ? 'OVERSPEED' : 'IMPACT');
      statusValueEl.style.color = 'var(--red-2)';
    } else if(level === 'warning'){
      statusValueEl.textContent = 'CAUTION';
      statusValueEl.style.color = 'var(--amber)';
    } else {
      statusValueEl.textContent = 'NORMAL';
      statusValueEl.style.color = 'var(--green)';
    }

    updateMap(level);
  }

  /* ============ DEMO CONTROLS WIRING ============ */
  document.querySelectorAll('#demoControls button[data-mode]').forEach(btn=>{
    btn.addEventListener('click', ()=>{
      const m = btn.dataset.mode;
      mode = m;
      if(m !== 'auto'){ forcedUntil = Date.now() + 6000; }
      setActiveDemoBtn(m);
    });
  });

  document.getElementById('dcToggle').addEventListener('click', ()=>{
    document.getElementById('demoControls').classList.toggle('collapsed');
  });

  document.getElementById('reportBtn').addEventListener('click', ()=>{
    alert('Incident report generated for HEMM_01 at ' + new Date().toLocaleString());
  });

  /* ============ LOOP ============ */
  step();
  setInterval(step, 1000);

})();
</script>
</body>
</html>