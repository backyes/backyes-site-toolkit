#!/usr/bin/env python3
"""
Convert report HTML files from dark/custom style to warm paper style.
Usage: python3 convert_to_warm_paper.py <file1.html> [file2.html] ...
"""
import sys
import os
import shutil
import re

WARM_PAPER_CSS = r"""<style>
:root {
  --paper: #f6f3ec;
  --paper-light: #fcfaf6;
  --surface: rgba(255,255,255,0.86);
  --surface-strong: #ffffff;
  --line: rgba(17,17,17,0.12);
  --ink: #111111;
  --ink-soft: #4d4d4d;
  --ink-mute: #6a6a6a;
  --green: #0f5d44;
  --green-deep: #0a3f30;
  --green-soft: rgba(15,93,68,0.10);
  --green-line: rgba(15,93,68,0.25);
  --gold: #bf8b2c;
  --gold-soft: rgba(191,139,44,0.14);
  --blue: #163e7a;
  --blue-soft: rgba(22,62,122,0.08);
  --red: #c0392b;
  --red-soft: rgba(192,57,43,0.08);
  --accent: #0f5d44;
  --accent2: #163e7a;
  --warn: #b26500;
  --code-bg: rgba(15,93,68,0.05);
  --quote-bg: rgba(22,62,122,0.05);
  --font-serif: 'Libre Baskerville', Georgia, serif;
  --font-sans: 'Manrope', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-mono: 'JetBrains Mono', ui-monospace, monospace;
  --shadow-sm: 0 2px 8px rgba(17,17,17,0.06);
  --shadow-md: 0 4px 16px rgba(17,17,17,0.08);
  --radius-md: 14px;
  --radius-sm: 10px;
}
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; -webkit-text-size-adjust: 100%; }
body {
  font-family: var(--font-sans);
  font-size: 16px;
  line-height: 1.75;
  color: var(--ink);
  background:
    radial-gradient(1200px 600px at 80% -5%, rgba(191,139,44,.06), transparent 60%),
    radial-gradient(1000px 500px at 0% 10%, rgba(15,93,68,.05), transparent 55%),
    linear-gradient(180deg, #fcfaf6 0%, var(--paper) 42%, #ffffff 100%);
  background-attachment: fixed;
  -webkit-font-smoothing: antialiased;
  padding: 0 0 80px;
}
a { color: var(--accent); text-decoration: none; word-break: break-all; }
a:hover { text-decoration: underline; }
.wrap, .container { max-width: 820px; margin: 0 auto; padding: 0 16px; }

/* Hero / Header */
header.hero, header {
  background: linear-gradient(135deg, var(--green-deep) 0%, var(--green) 100%);
  color: #fff;
  padding: 28px 16px 24px;
  margin-bottom: 20px;
}
header.hero h1, header h1 {
  margin: 0 0 8px;
  font-family: var(--font-serif);
  font-size: 24px;
  line-height: 1.35;
  font-weight: 700;
  color: #fff;
  -webkit-text-fill-color: #fff;
  background: none;
}
header.hero .sub, header .sub { font-size: 14px; opacity: 0.92; margin-bottom: 8px; }
header.hero .meta, header .meta {
  font-size: 12px;
  opacity: 0.88;
  display: flex;
  flex-wrap: wrap;
  gap: 6px 14px;
}
header .tag, header.hero .tag {
  background: rgba(255,255,255,0.18);
  padding: 2px 9px;
  border-radius: 10px;
  font-size: 11px;
  color: #fff;
}

/* Section headers */
h1 {
  font-family: var(--font-serif);
  font-size: 1.6rem;
  text-align: center;
  margin: 20px 0 8px;
  color: var(--ink);
  background: none;
  -webkit-text-fill-color: var(--ink);
  -webkit-background-clip: unset;
}
h2 {
  font-family: var(--font-serif);
  font-size: 20px;
  margin: 28px 0 12px;
  padding-bottom: 8px;
  border-bottom: 2px solid var(--green-line);
  color: var(--green-deep);
  display: flex;
  align-items: center;
  gap: 8px;
}
h2 .num, h2 .n {
  background: var(--green);
  color: #fff;
  font-family: var(--font-sans);
  font-size: 13px;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
h3 {
  font-size: 16.5px;
  margin: 18px 0 8px;
  color: var(--ink);
  font-weight: 600;
}
h4 {
  font-size: 15px;
  margin: 14px 0 6px;
  color: var(--ink-soft);
  font-weight: 600;
}
p { margin: 8px 0; }

/* Cards */
.card, section.card {
  background: var(--surface-strong);
  border: 1px solid var(--line);
  border-radius: var(--radius-md);
  padding: 18px 16px;
  margin: 14px 0;
  box-shadow: var(--shadow-sm);
}
.card.nv { border-left: 3px solid #0f5d44; }
.card.amd { border-left: 3px solid #163e7a; }
.card.ualink { border-left: 3px solid #bf8b2c; }
.card.cpo { border-left: 3px solid #0a3f30; }
.card h2, .card h3 { margin-top: 0; }

/* Lead / summary */
.lead {
  font-size: 15px;
  color: var(--ink-soft);
  background: var(--blue-soft);
  padding: 12px 14px;
  border-radius: var(--radius-sm);
  border-left: 4px solid var(--green);
  margin: 12px 0;
}
.exec-summary {
  background: linear-gradient(135deg, var(--green-soft), var(--gold-soft));
  border: 1px solid var(--green-line);
  border-radius: var(--radius-md);
  padding: 16px;
  margin: 16px 0;
}
.exec-summary h3 { margin-top: 0; color: var(--green-deep); }
.tldr {
  background: var(--gold-soft);
  border: 1px solid rgba(191,139,44,0.25);
  border-radius: var(--radius-md);
  padding: 14px 16px;
  margin: 14px 0;
}
.tldr h3 { color: var(--gold); margin: 0 0 6px; }

/* Tables */
.table-wrap { overflow-x: auto; margin: 10px 0; }
table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  margin: 10px 0;
}
th, td {
  border: 1px solid var(--line);
  padding: 8px 10px;
  text-align: left;
  vertical-align: top;
}
th {
  background: var(--green-soft);
  font-weight: 600;
  color: var(--green-deep);
}
tr:nth-child(even) td { background: var(--paper-light); }
tr:hover td { background: rgba(15,93,68,0.04); }

/* Tags */
.tag, .pill, .chip {
  display: inline-block;
  padding: 2px 9px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 500;
  margin: 2px;
  border: none;
}
.tag, .pill { background: var(--green-soft); color: var(--green-deep); }
.chip { background: var(--paper-light); color: var(--ink-mute); border: 1px solid var(--line); }
.tag.blue, .pill.s { background: var(--green-soft); color: var(--green-deep); }
.tag.purple, .pill.a { background: var(--gold-soft); color: var(--gold); }
.tag.green { background: var(--green-soft); color: var(--green-deep); }
.tag.orange, .pill.w { background: var(--gold-soft); color: var(--gold); }
.tag-nv { background: var(--green-soft); color: var(--green-deep); }
.tag-amd { background: var(--blue-soft); color: var(--blue); }
.tag-open { background: var(--gold-soft); color: var(--gold); }
.tag-frontier { background: rgba(10,63,48,0.08); color: var(--green-deep); }
.tag-warn { background: var(--red-soft); color: var(--red); }

/* Source / citation */
.source, .src {
  display: block;
  font-size: 12px;
  color: var(--ink-mute);
  margin: 4px 0 8px;
  padding-left: 10px;
  border-left: 3px solid var(--green);
  word-break: break-all;
  line-height: 1.55;
}
.source::before, .src::before { content: "📎 来源: "; color: var(--green); }
.source a, .src a { color: var(--green); }
.source b, .src b { color: var(--ink); }

/* Quote */
.quote {
  display: block;
  background: var(--quote-bg);
  border-left: 3px solid var(--green);
  padding: 10px 14px;
  margin: 10px 0;
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  font-size: 14px;
  color: var(--ink-soft);
  font-style: italic;
}
.quote::before { content: "" }
.quote::after { content: "" }

/* Callouts */
.callout, .insight {
  padding: 12px 14px;
  border-radius: var(--radius-sm);
  margin: 12px 0;
  font-size: 14px;
}
.callout.insight, .insight {
  background: var(--blue-soft);
  border-left: 4px solid var(--blue);
}
.callout.warn {
  background: var(--red-soft);
  border-left: 4px solid var(--red);
}
.callout.tip {
  background: var(--green-soft);
  border-left: 4px solid var(--green);
}
.insight::before { content: "🎯 芯片/系统启示"; display: block; font-weight: 700; color: var(--blue); font-size: 13px; margin-bottom: 4px; }
.callout b { display: block; margin-bottom: 4px; }

/* KPI / stats */
.kpi-grid, .stat-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 8px;
  margin: 12px 0;
}
.kpi, .stat {
  background: var(--paper-light);
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  padding: 10px;
  text-align: center;
  flex: 1;
  min-width: 100px;
}
.kpi .v, .stat .num {
  font-size: 22px;
  font-weight: 700;
  color: var(--green);
  display: block;
}
.kpi .l, .stat .label {
  font-size: 11px;
  color: var(--ink-mute);
  margin-top: 2px;
}
.stat.warn .num { color: var(--warn); }
.stat.ok .num { color: var(--green-deep); }

/* Data box */
.data-box {
  background: var(--code-bg);
  border-radius: var(--radius-sm);
  padding: 14px;
  margin: 10px 0;
  font-size: 13px;
  border: 1px solid var(--line);
}
.data-box strong { color: var(--green); }

/* Metric badges */
.metric {
  display: inline-block;
  border-radius: 6px;
  padding: 2px 8px;
  font-size: 13px;
  font-weight: 600;
  margin: 2px 4px 2px 0;
  border: 1px solid var(--line);
  background: var(--paper-light);
  color: var(--ink);
}
.metric.g { background: var(--green-soft); color: var(--green-deep); border-color: var(--green-line); }
.metric.o { background: var(--gold-soft); color: var(--gold); border-color: rgba(191,139,44,0.25); }
.metric.r { background: var(--red-soft); color: var(--red); border-color: rgba(192,57,43,0.25); }

/* Code */
code {
  background: var(--code-bg);
  padding: 1px 5px;
  border-radius: 4px;
  font-size: 13px;
  font-family: var(--font-mono);
  color: var(--green-deep);
}

/* Diagram */
.diagram {
  background: var(--code-bg);
  border-radius: var(--radius-sm);
  padding: 16px;
  margin: 12px 0;
  font-family: var(--font-mono);
  font-size: 12px;
  line-height: 1.5;
  white-space: pre;
  overflow-x: auto;
  border: 1px solid var(--line);
}

/* Bar chart */
.bar-container { display: flex; align-items: center; margin: 4px 0; font-size: 0.78rem; }
.bar-label { min-width: 100px; color: var(--ink-soft); }
.bar-track { flex: 1; height: 8px; background: var(--line); border-radius: 4px; margin: 0 8px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 4px; background: var(--green); }

/* Timeline */
.tl, .timeline {
  position: relative;
  padding-left: 24px;
  margin: 10px 0;
}
.tl::before, .timeline::before {
  content: '';
  position: absolute;
  left: 8px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: var(--green-line);
}
.tl .ev, .tl-item {
  position: relative;
  margin: 16px 0;
}
.tl .ev::before, .tl-item::before {
  content: '';
  position: absolute;
  left: -20px;
  top: 6px;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--green);
  border: 2px solid #fff;
  box-shadow: 0 0 0 2px var(--green);
}
.tl .yr { font-weight: 700; color: var(--green); font-size: 13px; }

/* Compare grid */
.compare-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }

/* TOC */
.toc {
  background: var(--paper-light);
  border: 1px solid var(--line);
  border-radius: var(--radius-md);
  padding: 14px 16px;
  margin-bottom: 16px;
  font-size: 14px;
}
.toc h3 { margin: 0 0 8px; color: var(--green-deep); font-size: 15px; }
.toc ol { margin: 0; padding-left: 20px; }
.toc li { margin: 3px 0; font-size: 13.5px; }
.toc a { color: var(--green); text-decoration: none; display: block; padding: 3px 0; }
.toc a:hover { text-decoration: underline; }

/* Details / summary */
details {
  background: var(--paper-light);
  border-radius: var(--radius-sm);
  padding: 8px 12px;
  margin: 8px 0;
  border: 1px solid var(--line);
}
summary { cursor: pointer; font-weight: 600; color: var(--green); font-size: 14px; }
details[open] summary { margin-bottom: 6px; }

/* Highlight / key */
.highlight { background: linear-gradient(180deg, transparent 60%, var(--gold-soft) 60%); }
.key { font-weight: 700; color: var(--green); }

/* Utility colors */
.bad { color: var(--red); font-weight: 600; }
.good { color: var(--green-deep); font-weight: 600; }
.amber { color: var(--gold); font-weight: 600; }

/* Footer */
footer, .footer {
  text-align: center;
  color: var(--ink-mute);
  font-size: 12px;
  margin-top: 30px;
  border-top: 1px solid var(--line);
  padding-top: 16px;
}

/* Appendix */
.appendix { font-size: 13px; }
.appendix a { color: var(--green); word-break: break-all; }

/* Responsive */
@media (max-width: 480px) {
  body { font-size: 15px; }
  header.hero h1, header h1 { font-size: 19px; }
  h1 { font-size: 1.4rem; }
  h2 { font-size: 18px; }
  .kpi-grid, .stat-row { grid-template-columns: repeat(2, 1fr); }
  table { font-size: 12px; }
  th, td { padding: 6px 5px; }
  .compare-grid { grid-template-columns: 1fr; }
}
</style>"""


def convert_file(filepath):
    """Convert a single HTML file to warm paper style."""
    if not os.path.exists(filepath):
        print(f"  SKIP: {filepath} not found")
        return False

    # Backup original
    backup_path = filepath.replace('.html', '.bak_dark')
    if not os.path.exists(backup_path):
        shutil.copy2(filepath, backup_path)
        print(f"  Backup: {backup_path}")

    # Read original
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace the <style>...</style> block
    # Match from <style> to the first </style>
    new_content = re.sub(
        r'<style>.*?</style>',
        WARM_PAPER_CSS,
        content,
        count=1,
        flags=re.DOTALL
    )

    if new_content == content:
        print(f"  WARN: No <style> block found in {filepath}")
        return False

    # Write converted
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"  Converted: {filepath}")
    return True


def main():
    files = sys.argv[1:]
    if not files:
        print("Usage: python3 convert_to_warm_paper.py <file1.html> [file2.html] ...")
        sys.exit(1)

    print(f"Converting {len(files)} file(s) to warm paper style...\n")
    for fp in files:
        convert_file(fp)
    print("\nDone.")


if __name__ == '__main__':
    main()
