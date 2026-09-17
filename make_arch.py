import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch

fig, ax = plt.subplots(figsize=(18, 22))
fig.patch.set_facecolor('#0f172a')
ax.set_facecolor('#0f172a')
ax.set_xlim(0, 18)
ax.set_ylim(0, 22)
ax.axis('off')

def box(x, y, w, h, color, lines, sizes=None, bold_first=True):
    p = FancyBboxPatch((x, y), w, h,
        boxstyle="round,pad=0.05,rounding_size=0.25",
        facecolor=color, edgecolor='#475569', linewidth=1.5, zorder=3)
    ax.add_patch(p)
    if isinstance(lines, str):
        lines = [lines]
    if sizes is None:
        sizes = [10] * len(lines)
    total = len(lines)
    for i, (line, sz) in enumerate(zip(lines, sizes)):
        offset = h/2 + (total/2 - i - 0.5) * (sz * 0.035 + 0.04)
        fw = 'bold' if (i == 0 and bold_first) else 'normal'
        ax.text(x + w/2, y + offset, line, ha='center', va='center',
                fontsize=sz, color='white', fontweight=fw, zorder=4)

def arrow(x1, y1, x2, y2, color='#6366f1', style='->'):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle=style, color=color, lw=2.2), zorder=5)

def tag(x, y, text, color='#94a3b8', size=8):
    ax.text(x, y, text, ha='center', va='center', fontsize=size, color=color, zorder=5)

# ── TITLE ─────────────────────────────────────────────────────────────────────
ax.text(9, 21.4, 'SkyAssist  --  System Architecture', ha='center',
        fontsize=20, color='white', fontweight='bold')
ax.text(9, 21.0, 'AI-Powered Airline Disruption Resolution Agent  |  AIONOS Assignment 3  |  Python + FastAPI + Groq',
        ha='center', fontsize=9.5, color='#94a3b8')

# ── 1. CUSTOMER ───────────────────────────────────────────────────────────────
box(5.5, 19.8, 7, 0.9, '#1e293b', ['CUSTOMER  (Browser)'], [13])
arrow(9, 19.8, 9, 19.0, '#06b6d4')
tag(10.2, 19.4, 'User request', '#06b6d4', 8)

# ── 2. FRONTEND ───────────────────────────────────────────────────────────────
box(2.5, 18.1, 13, 0.8,  '#312e81',
    ['FRONTEND  --  HTML / CSS / JS  --  Gen-Z Dark UI'], [12])
tag(16.5, 18.5, ':8001', '#818cf8', 8)
arrow(9, 18.1, 9, 17.4, '#6366f1')
tag(10.0, 17.75, 'POST /chat', '#6366f1', 8)

# ── 3. FASTAPI ────────────────────────────────────────────────────────────────
box(2.5, 16.5, 13, 0.8, '#0c4a6e',
    ['FastAPI Server  --  Python  --  CORS + Validation + Error Handling'], [12])
tag(16.5, 16.9, ':8000', '#06b6d4', 8)
arrow(9, 16.5, 9, 15.7, '#06b6d4')

# ── 4. AGENT ORCHESTRATOR ─────────────────────────────────────────────────────
box(1.5, 14.8, 15, 0.8, '#164e63', ['AGENT ORCHESTRATOR  --  agent.py'], [13])

# Step boxes inside orchestrator
steps = [
    (1.7,  13.5, 4.5, 0.9, '#1e3a5f', ['Step 1', 'Extract Booking Ref'], [8,9]),
    (6.4,  13.5, 4.5, 0.9, '#1e3a5f', ['Step 2', 'Detect Sentiment'], [8,9]),
    (11.1, 13.5, 4.5, 0.9, '#1e3a5f', ['Step 3', 'Lookup Customer & Flight'], [8,9]),
    (1.7,  12.3, 4.5, 0.9, '#1e3a5f', ['Step 4', 'Apply Policy Rules'], [8,9]),
    (6.4,  12.3, 4.5, 0.9, '#1e3a5f', ['Step 5', 'Check Escalation'], [8,9]),
    (11.1, 12.3, 4.5, 0.9, '#1e3a5f', ['Step 6', 'Generate LLM Response'], [8,9]),
]
for args in steps:
    box(*args)

arrow(9, 14.8, 9, 14.4, '#94a3b8')
arrow(9, 12.3, 9, 11.5, '#94a3b8')

# ── 5. THREE SERVICES ─────────────────────────────────────────────────────────
box(0.3, 9.8, 5.5, 1.5, '#14532d',
    ['GROQ LLM SERVICE', 'Fast:  groq/compound-mini',
     'Smart: openai/gpt-oss-120b', 'Fallback: openai/gpt-oss-20b'], [11,8,8,8])

box(6.25, 9.8, 5.5, 1.5, '#7c2d12',
    ['POLICY ENGINE', 'Delay compensation rules',
     'Cancellation rebooking', 'Fare difference + escalation'], [11,8,8,8])

box(12.2, 9.8, 5.5, 1.5, '#1e3a5f',
    ['DATA LAYER', 'Customer Profiles',
     'Booking & Flight Data', 'Service Policies'], [11,8,8,8])

# arrows orchestrator -> services
for sx in [3.05, 9.0, 14.95]:
    arrow(sx, 11.5 if sx == 9.0 else 12.3, sx, 11.3, '#475569')
    arrow(sx, 11.3, sx, 9.8+1.5, '#475569')

# ── 6. AUDIT LOGGER ───────────────────────────────────────────────────────────
box(5.5, 8.3, 7, 0.8, '#312e81', ['AUDIT LOGGER  --  Full Interaction Trail'], [11])
arrow(9, 9.8, 9, 9.1, '#818cf8')
arrow(9, 8.3, 9, 7.6, '#94a3b8')

# ── 7. ESCALATION + RESOLUTION ───────────────────────────────────────────────
box(0.3, 6.1, 8, 1.3, '#7f1d1d',
    ['ESCALATION ENGINE',
     'Legal threats  ->  Immediate escalate',
     'Policy exception  ->  Supervisor',
     'Fare diff > Rs.1500  ->  Human review'], [11,8,8,8])

box(9.7, 6.1, 8, 1.3, '#14532d',
    ['RESOLUTION ENGINE',
     'Meal voucher issued',
     'Lounge access granted',
     'Hotel arranged / Rebooking confirmed'], [11,8,8,8])

arrow(5.0, 7.6, 4.3, 7.4, '#ef4444')
arrow(13.0, 7.6, 13.7, 7.4, '#10b981')

# ── 8. HUMAN HANDOFF ──────────────────────────────────────────────────────────
box(0.3, 4.5, 8, 0.9, '#450a0a',
    ['HUMAN AGENT HANDOFF', 'Specialist notified + history transferred'], [11,8])
arrow(4.3, 6.1, 4.3, 5.4, '#ef4444')

# ── 9. RESPONSE ───────────────────────────────────────────────────────────────
box(3.5, 3.2, 11, 0.9, '#312e81',
    ['RESPONSE TO CUSTOMER  --  Chat UI Updated'], [13])
arrow(9, 4.5, 9, 4.1, '#6366f1')

# ── 10. SCENARIOS ─────────────────────────────────────────────────────────────
ax.text(9, 2.7, 'DEMO SCENARIOS', ha='center', fontsize=12,
        color='white', fontweight='bold')

box(0.3,  1.2, 5.5, 1.2, '#7f1d1d',
    ['Scenario 1  --  Priya Nair  (Gold)',
     'Flight Cancelled',
     'Wants refund + business upgrade'], [9,8,8])
box(6.25, 1.2, 5.5, 1.2, '#78350f',
    ['Scenario 2  --  Arvind Kulkarni  (Silver)',
     'Delayed 4h',
     'Wants hotel  ->  Denied (needs 5h+)'], [9,8,8])
box(12.2, 1.2, 5.5, 1.2, '#14532d',
    ['Scenario 3  --  Meher Kaur  (Platinum)',
     'Delayed 6h',
     'Rs.2000 fare diff  ->  Escalated'], [9,8,8])

# ── LEGEND ────────────────────────────────────────────────────────────────────
handles = [
    mpatches.Patch(color='#312e81', label='Frontend / API'),
    mpatches.Patch(color='#164e63', label='Agent Core'),
    mpatches.Patch(color='#14532d', label='LLM / Resolution'),
    mpatches.Patch(color='#7c2d12', label='Policy Engine'),
    mpatches.Patch(color='#7f1d1d', label='Escalation'),
    mpatches.Patch(color='#1e3a5f', label='Data / Steps'),
]
ax.legend(handles=handles, loc='lower right', facecolor='#1e293b',
          edgecolor='#475569', labelcolor='white', fontsize=8.5, framealpha=0.95)

plt.tight_layout(pad=0.3)
plt.savefig('docs/screenshots/architecture.png', dpi=150,
            bbox_inches='tight', facecolor='#0f172a')
print("Saved -> docs/screenshots/architecture.png")
