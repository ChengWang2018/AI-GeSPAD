// Figure 1 (AI-GeSPAD) in the style of Figure2_WPs.pptx: white panels, numbered rust circles,
// pill tags, native line plots, italic captions, workflow chain at the bottom. All shapes editable.
const pptxgen = require('pptxgenjs');
const pres = new pptxgen();
const SW = 13.33, SH = 5.35;
pres.defineLayout({ name: 'FIG', width: SW, height: SH }); pres.layout = 'FIG';
pres.title = 'AI-GeSPAD framework (Figure 1)';
const s = pres.addSlide(); s.background = { color: 'FFFFFF' };
const F = 'Arial', RUST = 'B4472A', PINK = 'F8ECE7', GRID = 'C8C8C8', AX = '6B6B6B',
  INK = '1F1F1F', MUTE = '5F5F5F', GRN = '4F7B3A', GRNF = 'EEF3EA', GRYF = 'F3F3F3';
const DIR = '/tmp/claude-0/ppt/';

function runs(str, opt) {
  const out = []; const re = /(_\{[^}]*\}|\^\{[^}]*\})/g;
  const lines = str.split('\n');
  lines.forEach((ln, li) => {
    let last = 0, m; re.lastIndex = 0; const parts = [];
    while ((m = re.exec(ln))) {
      if (m.index > last) parts.push({ text: ln.slice(last, m.index), options: { ...opt } });
      parts.push({ text: m[0].slice(2, -1), options: { ...opt, [m[0][0] == '_' ? 'subscript' : 'superscript']: true } });
      last = re.lastIndex;
    }
    if (last < ln.length) parts.push({ text: ln.slice(last), options: { ...opt } });
    if (!parts.length) parts.push({ text: ' ', options: { ...opt } });
    if (li < lines.length - 1) parts[parts.length - 1].options.breakLine = true;
    out.push(...parts);
  });
  return out;
}
function T(str, x, y, w, h, o = {}) {
  s.addText(runs(str, { fontFace: F, fontSize: o.size || 12, color: o.color || INK, bold: !!o.bold, italic: !!o.italic }),
    { x, y, w, h, margin: 0, align: o.align || 'left', valign: o.valign || 'middle', isTextBox: true,
      lineSpacingMultiple: o.ls || 1.0, rotate: o.rotate, objectName: o.name });
}
function line(x1, y1, x2, y2, o = {}) {
  s.addShape(pres.shapes.LINE, { x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.max(Math.abs(x2 - x1), 0.001),
    h: Math.max(Math.abs(y2 - y1), 0.001), flipH: x2 < x1, flipV: y2 < y1,
    line: { color: o.color || AX, width: o.width || 1, dashType: o.dash, endArrowType: o.arrow ? 'triangle' : undefined } });
}
function poly(pts, o = {}) { // absolute points [[x,y],...]
  const xs = pts.map(p => p[0]), ys = pts.map(p => p[1]);
  const x0 = Math.min(...xs), y0 = Math.min(...ys), w = Math.max(...xs) - x0 || 0.001, h = Math.max(...ys) - y0 || 0.001;
  const points = pts.map(p => ({ x: p[0] - x0, y: p[1] - y0 }));
  if (o.fill) points.push({ close: true });
  s.addShape(pres.shapes.CUSTOM_GEOMETRY, { x: x0, y: y0, w, h, points,
    fill: o.fill ? { color: o.fill, transparency: o.transp || 0 } : { type: 'none' },
    line: o.noline ? { type: 'none' } : { color: o.color || RUST, width: o.width || 2, dashType: o.dash } });
}
function box(x, y, w, h, fill, lc, o = {}) {
  s.addShape(o.square ? pres.shapes.RECTANGLE : pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: o.r ?? 0.08,
    fill: fill ? { color: fill } : { type: 'none' }, line: lc ? { color: lc, width: o.lw || 1 } : { type: 'none' }, objectName: o.name });
}
function dot(x, y, d, fill, lc) {
  s.addShape(pres.shapes.OVAL, { x: x - d / 2, y: y - d / 2, w: d, h: d, fill: { color: fill }, line: { color: lc || fill, width: 1.2 } });
}
function img(n, x, y, w, h) { s.addImage({ path: DIR + n + '.png', x, y, w, h, objectName: n }); }
function axes(ox, oy, w, h, xl, yl) {
  line(ox, oy, ox + w, oy, { arrow: 1, color: AX, width: 1.2 });
  line(ox, oy, ox, oy - h, { arrow: 1, color: AX, width: 1.2 });
  if (xl) T(xl, ox + w - 1.6, oy + 0.02, 1.6, 0.2, { size: 11, color: MUTE, align: 'right' });
  if (yl) T(yl, ox - 0.62, oy - h / 2 - 0.12, 0.9, 0.24, { size: 11, color: MUTE, align: 'center', rotate: 270 });
}
function panel(px, py, w, h, num, title, tag, cap) {
  box(px, py, w, h, 'FFFFFF', GRID, { r: 0.1, lw: 1.2, name: 'panel ' + num });
  dot(px + 0.36, py + 0.38, 0.44, RUST);
  T(String(num), px + 0.14, py + 0.16, 0.44, 0.44, { size: 17, bold: true, color: 'FFFFFF', align: 'center' });
  T(title, px + 0.68, py + 0.08, w - 1.95, 0.62, { size: 16, bold: true, color: RUST, ls: 0.95 });
  box(px + w - 1.22, py + 0.2, 1.1, 0.32, PINK, null, { r: 0.16 });
  T(tag, px + w - 1.22, py + 0.2, 1.1, 0.32, { size: 11, bold: true, color: RUST, align: 'center' });
  if (cap) { line(px, py + h - 0.72, px + w, py + h - 0.72, { color: GRID, width: 1 });
    T(cap, px + 0.1, py + h - 0.69, w - 0.2, 0.64, { size: 11.5, italic: true, color: MUTE, align: 'center', ls: 1.0 }); }
}
const lerp = (a, b, t) => a + (b - a) * t;
function mix(t) { // white -> rust
  const c0 = [255, 255, 255], c1 = [180, 71, 42];
  return c0.map((v, i) => Math.round(lerp(v, c1[i], t)).toString(16).padStart(2, '0')).join('').toUpperCase();
}

// ---------- banner: the core problem ----------
s.addText([
  ...runs('Robust design game:   ', { fontFace: F, fontSize: 13, bold: true, color: RUST }),
  ...runs('max_{x}  min_{δ∈Δ}  ρ(x, δ)   subject to a TCAD budget  Σ n_{ℓ}c_{ℓ} ≤ B', { fontFace: F, fontSize: 13, color: INK }),
  ...runs('      designer maximises over designs x;  challenger minimises over uncertainties δ', { fontFace: F, fontSize: 11.5, italic: true, color: MUTE }),
], { x: 0.08, y: 0.07, w: SW - 0.16, h: 0.38, align: 'center', valign: 'middle', margin: 0, objectName: 'banner' });

const PY = 0.55, PH = 4.72, W1 = 3.75, W2 = 5.2, W3 = 3.75, G = 0.24;
const X1 = 0.075, X2 = X1 + W1 + G, X3 = X2 + W2 + G;

// ---------- WP1 ----------
{ const px = X1, py = PY, PW = W1;
  panel(px, py, PW, PH, 1, 'Physics and\ndata engine', 'WP1 · M1–4',
    'Automate 2D/3D TCAD and calibrate it\nto measured data → uncertainty set Δ');
  T('Automated Silvaco ATLAS (team TCAD)', px, py + 0.76, PW, 0.24, { size: 12, color: MUTE, align: 'center' });
  img('cen_device', px + 0.15, py + 1.04, 3.45, 3.45 / 3.68);
  const ox = px + 0.5, oy = py + 2.95, w = 1.7, h = 0.72;
  const f = t => oy - (0.12 + 0.72 * t) * h;
  const N = 20, up = [], lo = [], mid = [];
  for (let i = 0; i <= N; i++) { const t = i / N, x = ox + 0.08 + t * (w - 0.25), b = 0.08 + 0.1 * Math.abs(t - 0.5) * 2;
    mid.push([x, f(t)]); up.push([x, f(t) - b * h]); lo.push([x, f(t) + b * h]); }
  poly([...up, ...lo.reverse()], { fill: PINK, noline: 1 });
  poly(mid, { color: RUST, width: 2 });
  [[0.12, 0.03], [0.35, -0.05], [0.58, 0.04], [0.82, -0.02]].forEach(([t, e]) => dot(ox + 0.08 + t * (w - 0.25), f(t) + e * h, 0.09, INK));
  axes(ox, oy, w, h, 'excess bias', 'DCR');
  T('posterior p(θ | data)', ox + 0.1, oy - h - 0.06, 1.7, 0.22, { size: 11, italic: true, color: RUST });
  T('Calibration data', px + 2.3, py + 2.13, 1.35, 0.24, { size: 11.5, color: MUTE, align: 'center' });
  box(px + 2.3, py + 2.4, 1.35, 0.3, GRNF, GRN, { lw: 1.2 }); T('HWU SPAD data', px + 2.3, py + 2.4, 1.35, 0.3, { size: 11, align: 'center' });
  box(px + 2.3, py + 2.77, 1.35, 0.3, GRYF, AX, { lw: 1.2 }); T('published APDs', px + 2.3, py + 2.77, 1.35, 0.3, { size: 11, align: 'center' });
  box(px + 0.15, py + 3.32, PW - 0.3, 0.6, PINK, null, { r: 0.08 });
  T('Uncertainty set Δ:  physics θ  ·  process p\n(e.g. ±20 nm W_{P})  ·  bias drift ΔV', px + 0.15, py + 3.32, PW - 0.3, 0.6, { size: 11.5, color: INK, align: 'center', ls: 1.05 });
}

// ---------- WP2 ----------
{ const px = X2, py = PY, PW = W2;
  panel(px, py, PW, PH, 2, 'Graph surrogate, robust\ndesigner and challenger', 'WP2 · M3–10',
    'A GNN predicts fields and SPDE/DCR with uncertainty; the designer\nand challenger play Eq. (2), and top counterexamples are re-simulated');
  // surrogate row
  const r0 = py + 0.8;
  img('cen_field', px + 0.35, r0, 0.98, 0.8);
  T('|E| map (team TCAD)', px + 0.1, r0 + 0.82, 1.5, 0.22, { size: 10, color: MUTE, align: 'center' });
  line(px + 1.45, r0 + 0.4, px + 1.85, r0 + 0.4, { color: RUST, width: 1.5, arrow: 1 });
  const gx = px + 1.95, gy = r0 + 0.02, S = 0.78;
  const nodes = [[0.1, 0.4], [0.35, 0.12], [0.38, 0.62], [0.62, 0.3], [0.66, 0.72], [0.9, 0.48], [0.18, 0.75], [0.85, 0.1]];
  const edges = [[0, 1], [0, 2], [1, 3], [2, 3], [2, 4], [3, 5], [4, 5], [0, 6], [6, 2], [6, 4], [3, 7], [7, 5], [1, 7]];
  edges.forEach(([a, b]) => line(gx + nodes[a][0] * S, gy + nodes[a][1] * S, gx + nodes[b][0] * S, gy + nodes[b][1] * S, { color: 'D9A08F', width: 1.2 }));
  nodes.forEach(([a, b], i) => dot(gx + a * S, gy + b * S, 0.12, i == 3 ? RUST : 'FFFFFF', RUST));
  T('GNN ensemble', gx - 0.2, r0 + 0.82, 1.2, 0.22, { size: 10, color: MUTE, align: 'center' });
  line(px + 2.9, r0 + 0.4, px + 3.3, r0 + 0.4, { color: RUST, width: 1.5, arrow: 1 });
  T('SPDE, DCR, g\nμ ± σ', px + 3.35, r0 + 0.1, 1.6, 0.6, { size: 13, color: RUST, align: 'center', ls: 1.05 });
  line(px + 0.15, py + 1.95, px + PW - 0.15, py + 1.95, { color: GRID, width: 0.8, dash: 'dash' });
  // designer (left)
  T('Designer (max over x)', px + 0.1, py + 2.0, 2.5, 0.24, { size: 11.5, bold: true, color: INK, align: 'center' });
  { const ox = px + 0.45, oy = py + 3.3, w = 2.1, h = 0.92;
    const fr = (t, a) => oy - (0.1 + a * Math.sqrt(t)) * h;
    const nom = [], rob = [], up = [], lo = [];
    for (let i = 0; i <= 20; i++) { const t = i / 20, x = ox + 0.08 + t * (w - 0.35);
      nom.push([x, fr(t, 0.85)]); rob.push([x, fr(t, 0.66)]); up.push([x, fr(t, 0.66) - 0.06 * h]); lo.push([x, fr(t, 0.66) + 0.06 * h]); }
    poly([...up, ...lo.reverse()], { fill: PINK, noline: 1 });
    poly(nom, { color: AX, width: 1.5, dash: 'dash' });
    poly(rob, { color: RUST, width: 2 });
    [0.2, 0.55, 0.9].forEach(t => dot(ox + 0.08 + t * (w - 0.35), fr(t, 0.66), 0.11, 'FFFFFF', RUST));
    T('nominal', ox + 0.9, oy - 1.0 * h - 0.06, 0.8, 0.2, { size: 10.5, color: AX });
    T('robust front', ox + 0.95, oy - 0.4 * h, 1.1, 0.2, { size: 10.5, italic: true, color: RUST });
    axes(ox, oy, w, h, 'DCR', 'SPDE'); }
  // exchange arrows
  line(px + 2.62, py + 2.65, px + 3.02, py + 2.65, { color: INK, width: 1.4, arrow: 1 });
  T('x*', px + 2.62, py + 2.4, 0.4, 0.22, { size: 12, align: 'center' });
  line(px + 3.02, py + 2.95, px + 2.62, py + 2.95, { color: RUST, width: 1.4, arrow: 1 });
  T('δ*, ρ', px + 2.55, py + 2.98, 0.55, 0.22, { size: 12, color: RUST, align: 'center' });
  // challenger (right)
  T('Challenger (min over δ)', px + 2.7, py + 2.0, 2.45, 0.24, { size: 11.5, bold: true, color: INK, align: 'center' });
  { const n = 6, c = 0.165, hx = px + 3.5, hy = py + 2.3;
    for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) {
      const d = Math.hypot(i - 5, j) / 7.1, v = Math.max(0, 0.82 * (1 - d) ** 1.6);
      box(hx + i * c, hy + j * c, c, c, mix(v), 'FFFFFF', { square: 1, lw: 0.6 }); }
    box(hx, hy, n * c, n * c, null, GRID, { square: 1, lw: 0.8 });
    const path = [[1.5, 4.5], [2.4, 3.3], [3.3, 2.2], [4.2, 1.2]];
    for (let k = 0; k < path.length - 1; k++) line(hx + path[k][0] * c, hy + path[k][1] * c, hx + path[k + 1][0] * c, hy + path[k + 1][1] * c, { color: INK, width: 1.3, arrow: k == path.length - 2 });
    path.slice(0, -1).forEach(p => dot(hx + p[0] * c, hy + p[1] * c, 0.08, INK));
    T('✕', hx + 4.6 * c - 0.12, hy + 0.8 * c - 0.14, 0.26, 0.26, { size: 15, bold: true, color: RUST, align: 'center' });
    T('δ*', hx + n * c + 0.04, hy - 0.02, 0.35, 0.24, { size: 12, color: RUST });
    T('Δ W_{P} (process)', hx - 0.2, hy + n * c + 0.01, n * c + 0.4, 0.22, { size: 10, color: MUTE, align: 'center' });
    T('Δ traps', hx - 0.56, hy + n * c / 2 - 0.12, 0.8, 0.24, { size: 10, color: MUTE, align: 'center', rotate: 270 }); }
  T('P_{fail} = Pr[ρ < 0] (share of Δ where the design fails), by Monte Carlo\non the surrogate; top δ* re-run in TCAD; final designs checked at 250–295 K', px + 0.1, py + 3.55, PW - 0.2, 0.42, { size: 10.5, italic: true, color: RUST, align: 'center' });
}

// ---------- WP3 ----------
{ const px = X3, py = PY, PW = W3;
  panel(px, py, PW, PH, 3, 'Explain, validate\nand deliver', 'WP3 · M8–12',
    'Turn the surrogate into design rules, validate\nblind and on test diodes, release the toolkit');
  const items = [
    ['SHAP + symbolic regression → rules', PINK, RUST, 'bars'],
    ['Blind 3D TCAD validation', PINK, RUST],
    ['Si test diodes (HWU cleanroom)', GRNF, GRN],
    ['Open toolkit + GeSPAD-Bench data', GRYF, AX],
    ['Impact: fab roadmap, quantum networks', PINK, RUST],
  ];
  const bx = px + 0.18, bw = PW - 0.36, bh = 0.47, g = 0.18; let by = py + 0.82;
  items.forEach(([t, f, l, extra], k) => {
    box(bx, by, bw, bh, f, l, { lw: 1.3, r: 0.08 });
    if (extra == 'bars') {
      [0.75, 0.95, 0.5, 0.62].forEach((v, i) => box(bx + 0.1, by + 0.07 + i * 0.085, 0.36 * v, 0.06, RUST, null, { square: 1 }));
      T(t, bx + 0.45, by, bw - 0.5, bh, { size: 11.5, align: 'center' });
    } else T(t, bx, by, bw, bh, { size: 11.5, align: 'center' });
    if (k < items.length - 1) line(bx + bw / 2, by + bh + 0.02, bx + bw / 2, by + bh + g - 0.02, { color: RUST, width: 1.5, arrow: 1 });
    by += bh + g;
  });
}

// arrows between panels
[[X1 + W1, X2], [X2 + W2, X3]].forEach(([a, b]) => line(a + 0.03, PY + PH / 2 - 0.3, b - 0.03, PY + PH / 2 - 0.3, { color: RUST, width: 1.8, arrow: 1 }));

pres.writeFile({ fileName: '/mnt/user-data/outputs/Fig1_AI-GeSPAD_editable.pptx' }).then(f => console.log('wrote', f));
