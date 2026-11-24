import html
import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent
data = json.loads((root / "experiments/admission-results.json").read_text(encoding="utf-8-sig"))
style = """
:root { color-scheme: light; font: 17px/1.5 system-ui,sans-serif; color:#162338; background:#f4f6f9; }
body { margin:0; }
main { padding:20px; max-width:800px; margin:auto; }
h1 { font-size:1.3rem; line-height:1.25; margin:0 0 16px; }
p { margin:12px 0; }
button { font:inherit; min-height:44px; padding:6px 14px; border:1px solid #a5b6c6; border-radius:5px; background:white; color:inherit; cursor:pointer; }
button:focus-visible { outline:3px solid #14685f; outline-offset:3px; }
button:disabled { cursor:default; opacity:.45; }
.controls { display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin-top:16px; }
.controls[hidden] { display:none; }
.counter { font-variant-numeric:tabular-nums; }
.lane { margin:20px 0 28px; }
.track { margin:12px 24px 0; height:26px; position:relative; }
.track::before { content:""; position:absolute; top:12px; height:2px; background:#a5b6c6; width:100%; }
.marker { position:absolute; left:0; transform:translateX(-50%); background:#14685f; color:white; border-radius:4px; padding:1px 8px; transition:left .55s ease; }
.ticks { display:flex; justify-content:space-between; }
.values { display:flex; flex-wrap:wrap; gap:10px 24px; font-variant-numeric:tabular-nums; }
.values strong { font-size:1.3rem; }
.status { min-height:3em; font-weight:600; }
.bad { color:#a72525; }
details { margin-top:16px; }
summary { cursor:pointer; }
table { border-collapse:collapse; font-size:.9rem; width:100%; margin-top:10px; }
th,td { text-align:left; padding:7px; border-bottom:1px solid #ccd6df; vertical-align:top; overflow-wrap:anywhere; }
.graph { display:grid; grid-template-columns:1fr 1fr 1fr; gap:24px; align-items:stretch; }
.node { background:#e7eef3; padding:14px; border-radius:5px; position:relative; transition:background-color .4s; }
.node strong,.node span { display:block; }
.node span { margin-top:8px; }
.node.dependent::before { content:"→"; position:absolute; left:-21px; top:22px; }
.node.invalid { background:#fce6e4; }
.independent { margin-top:22px; padding-top:12px; border-top:1px solid #a5b6c6; }
.independent span { display:block; color:#14685f; }
.caption { color:#44566c; font-size:.9rem; }
.sr-only { position:absolute; width:1px; height:1px; padding:0; margin:-1px; overflow:hidden; clip:rect(0,0,0,0); white-space:nowrap; border:0; }
@media(max-width:520px) { main{padding:16px;} .graph{grid-template-columns:1fr;gap:22px;} .node.dependent::before{content:"↓";left:50%;top:-25px;} .node span{margin-top:3px;} }
@media(prefers-reduced-motion:reduce) { .marker,.node{transition:none;} }
"""

script = """
const data = JSON.parse(document.getElementById('experiment-data').textContent);
const kind = document.body.dataset.kind;
const frames = kind === 'race' ? data.trace : [
  {workers:1, evidence:'One worker · invariant established', admission:'ACCEPT', detail:data.decisions[0].decision},
  {workers:2, evidence:'One worker · scope mismatch', admission:'REJECT', detail:data.decisions[1].decision},
  {workers:2, evidence:'Two workers · invariant violated', admission:'REJECT', detail:data.decisions[2].decision}
];
let position = 0;
let timer = null;
const controls = document.querySelector('.controls');
const play = document.getElementById('play');
const previous = document.getElementById('previous');
const next = document.getElementById('next');
const status = document.getElementById('status');
const counter = document.getElementById('counter');
function pause() {
  clearInterval(timer);
  timer = null;
  play.textContent = 'Play';
}
function render(announce) {
  const frame = frames[position];
  previous.disabled = position === 0;
  next.disabled = position === frames.length - 1;
  counter.textContent = (position + 1) + ' / ' + frames.length;
  if (kind === 'race') {
    frame.phases.forEach((phase, index) => {
      document.getElementById('request-' + index).style.left = (phase * 50) + '%';
    });
    document.getElementById('used').textContent = frame.used;
    document.getElementById('accepted').textContent = frame.accepted;
    status.textContent = frame.event + (frame.accepted > data.capacity ? ' — capacity exceeded' : '');
    status.classList.toggle('bad', frame.accepted > data.capacity);
  } else {
    document.getElementById('workers').textContent = frame.workers + (frame.workers === 1 ? ' worker' : ' workers');
    document.getElementById('evidence').textContent = frame.evidence;
    document.getElementById('admission').textContent = frame.admission;
    document.getElementById('evidence-node').classList.toggle('invalid', position > 0);
    document.getElementById('admission-node').classList.toggle('invalid', position > 0);
    status.textContent = frame.detail;
    status.classList.toggle('bad', position > 0);
  }
  if (announce) document.getElementById('announcement').textContent = status.textContent;
}
controls.hidden = false;
play.addEventListener('click', () => {
  if (timer !== null) { pause(); return; }
  if (position === frames.length - 1) position = 0;
  render(false);
  play.textContent = 'Pause';
  timer = setInterval(() => {
    position++;
    render(position === frames.length - 1);
    if (position === frames.length - 1) pause();
  }, 1800);
});
previous.addEventListener('click', () => { pause(); position--; render(true); });
next.addEventListener('click', () => { pause(); position++; render(true); });
document.addEventListener('visibilitychange', () => { if (document.hidden) pause(); });
render(false);
"""

controls = """<div class="controls" hidden>
<button id="play" type="button">Play</button>
<button id="previous" type="button">Previous</button>
<button id="next" type="button">Next</button>
<span id="counter" class="counter"></span>
</div><p id="announcement" aria-live="polite" class="sr-only"></p>"""
race_table = "<table><thead><tr><th>Event</th><th>Used</th><th>Accepted</th></tr></thead><tbody>" + "".join(
    f"<tr><td>{html.escape(row['event'])}</td><td>{row['used']}</td><td>{row['accepted']}</td></tr>"
    for row in data["trace"]
) + "</tbody></table>"
race = """<h1>Two requests, one unit of capacity</h1>
<p class="caption">Split read/write operation · two workers</p>
<div class="lane"><div class="ticks"><span>Pending</span><span>Read</span><span>Commit</span></div>
<div class="track"><span class="marker" id="request-0">R1</span></div></div>
<div class="lane"><div class="ticks"><span>Pending</span><span>Read</span><span>Commit</span></div>
<div class="track"><span class="marker" id="request-1">R2</span></div></div>
<div class="values"><span>Recorded usage <strong id="used">0</strong></span><span>Accepted <strong id="accepted">0</strong></span><span>Capacity <strong>1</strong></span></div>
<p class="status" id="status">Both requests can observe available capacity before either commits.</p>"""
race += controls + "<details><summary>Read the complete counterexample</summary>" + race_table + "</details>"
decisions = "<table><thead><tr><th>Configuration</th><th>Decision</th></tr></thead><tbody>" + "".join(
    f"<tr><td>{html.escape(row['case'])}</td><td>{html.escape(row['decision'])}</td></tr>"
    for row in data["decisions"][:4]
) + "</tbody></table>"
assurance = """<h1>When evidence stops authorizing a change</h1>
<div class="graph" role="group" aria-label="Environment, dependent reservation evidence and admission decision">
<div class="node"><strong>Environment</strong><span id="workers">1 worker</span></div>
<div class="node dependent" id="evidence-node"><strong>Reservation evidence</strong><span id="evidence">One worker · invariant established</span></div>
<div class="node dependent" id="admission-node"><strong>Reservation admission</strong><span id="admission">ACCEPT</span></div>
</div>
<div class="independent"><strong>Arithmetic predicate evidence</strong><span>Independent of worker count</span></div>
<p class="status" id="status">A worker-count change invalidates the applicability of single-worker reservation evidence. Re-verification finds a violation.</p>"""
assurance += controls + "<details><summary>Read the recorded admission decisions</summary>" + decisions + "</details>"
assurance += "<p class='caption'>Arrows show dependencies. The arithmetic evidence covers the unsigned admission predicate alone.</p>"

for kind, content, name in [("race", race, "reservation-trace.html"), ("assurance", assurance, "assurance-graph.html")]:
    document = '<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
    document += f"<title>{'Reservation trace' if kind == 'race' else 'Evidence applicability'} | Generation VII</title><style>{style}</style></head>"
    document += f'<body data-kind="{kind}"><main>{content}</main>'
    document += '<script id="experiment-data" type="application/json">' + json.dumps(data, separators=(",", ":")).replace("<", "\\u003c") + "</script>"
    document += f"<script>{script}</script></body></html>\n"
    (root / "experiments" / name).write_text(document, encoding="utf-8", newline="\n")
