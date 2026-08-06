"""
TechSoul – Executive Website Audit PDF Engine v6
Pure ReportLab canvas renderer. Landscape Letter (792 × 612 pt)
v6: Full alignment fix — no overlaps, generous spacing, correct contrast.
"""

import os, datetime
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.pagesizes import landscape, letter
from typing import Dict, Any, Tuple

# ─── Page geometry ────────────────────────────────────────
W, H   = landscape(letter)   # 792 × 612 pt
MARGIN = 36


# ═══════════════════════════════════════════════════════════
#  PRIMITIVE HELPERS
# ═══════════════════════════════════════════════════════════
def _hex(h: str) -> Tuple[float,float,float]:
    h = h.lstrip("#")
    return int(h[0:2],16)/255, int(h[2:4],16)/255, int(h[4:6],16)/255

def fc(c, h):
    r,g,b = _hex(h); c.setFillColorRGB(r,g,b)

def sc(c, h):
    r,g,b = _hex(h); c.setStrokeColorRGB(r,g,b)

def rect(c, x, y, w, h2, fill="#FFFFFF", r=0, stroke=None, sw=0.5):
    fc(c, fill)
    if stroke:
        sc(c, stroke); c.setLineWidth(sw)
    if r:
        c.roundRect(x, y, w, h2, r, fill=1, stroke=1 if stroke else 0)
    else:
        c.rect(x, y, w, h2, fill=1, stroke=1 if stroke else 0)

def circ(c, cx, cy, radius, fill="#FFFFFF"):
    fc(c, fill); c.circle(cx, cy, radius, fill=1, stroke=0)

def ln(c, x1, y1, x2, y2, col="#CBD5E1", lw=0.6):
    sc(c, col); c.setLineWidth(lw); c.line(x1, y1, x2, y2)

def txt(c, text, x, y, font="Helvetica-Bold", size=11, col="#FFFFFF", align="left"):
    fc(c, col); c.setFont(font, size)
    t = str(text)
    if   align == "center": c.drawCentredString(x, y, t)
    elif align == "right":  c.drawRightString(x, y, t)
    else:                   c.drawString(x, y, t)

def gradient(c, x, y, w, h2, c1, c2, vert=True, steps=60):
    r1,g1,b1 = _hex(c1); r2,g2,b2 = _hex(c2)
    if vert:
        sh = h2 / steps
        for i in range(steps):
            t = i / (steps-1)
            c.setFillColorRGB(r1+(r2-r1)*t, g1+(g2-g1)*t, b1+(b2-b1)*t)
            c.rect(x, y+i*sh, w, sh+0.8, fill=1, stroke=0)
    else:
        sw2 = w / steps
        for i in range(steps):
            t = i / (steps-1)
            c.setFillColorRGB(r1+(r2-r1)*t, g1+(g2-g1)*t, b1+(b2-b1)*t)
            c.rect(x+i*sw2, y, sw2+0.8, h2, fill=1, stroke=0)

def logo(c, path, x, y, w, h2):
    if os.path.exists(path):
        try:
            c.drawImage(path, x, y, width=w, height=h2,
                        preserveAspectRatio=True, mask="auto")
            return True
        except Exception:
            pass
    txt(c, "TECHSOUL", x, y+h2/2-7, "Helvetica-Bold", 14, "#FFFFFF")
    return False

def score_col(s):
    return {"A":"#22C55E","B":"#84CC16","C":"#F59E0B","D":"#F97316","F":"#EF4444"}.get(
        str(s).upper()[:1], "#F97316")

def impact_col(i):
    return {"high":"#EF4444","medium":"#F59E0B","low":"#22C55E"}.get(str(i).lower(),"#F59E0B")

def pill(c, cx, cy, text, bg, fg="#FFFFFF", fs=8):
    """Draw a centred pill badge at (cx, cy). Returns pill width."""
    c.setFont("Helvetica-Bold", fs)
    tw = c.stringWidth(text, "Helvetica-Bold", fs)
    pw, ph = tw + 22, fs + 12
    fc(c, bg)
    c.roundRect(cx - pw/2, cy - ph/2, pw, ph, ph/2, fill=1, stroke=0)
    fc(c, fg)
    c.drawCentredString(cx, cy - fs*0.35, text)
    return pw

def pill_left(c, x, y, text, bg, fg="#FFFFFF", fs=8):
    """Left-anchored pill. Returns pill width."""
    c.setFont("Helvetica-Bold", fs)
    tw = c.stringWidth(text, "Helvetica-Bold", fs)
    pw, ph = tw + 22, fs + 12
    fc(c, bg)
    c.roundRect(x, y - ph/2, pw, ph, ph/2, fill=1, stroke=0)
    fc(c, fg)
    c.drawString(x + 11, y - fs*0.35, text)
    return pw

def wrap(c, text, x, y, font, size, col, maxw, lh=None):
    """Word-wrap text. Returns total height consumed."""
    fc(c, col); c.setFont(font, size)
    lh = lh or size * 1.6
    words = str(text).split()
    lines, buf = [], []
    for w2 in words:
        probe = " ".join(buf + [w2])
        if c.stringWidth(probe, font, size) <= maxw:
            buf.append(w2)
        else:
            if buf: lines.append(" ".join(buf))
            buf = [w2]
    if buf: lines.append(" ".join(buf))
    for i, l in enumerate(lines):
        c.drawString(x, y - i*lh, l)
    return len(lines) * lh


# ═══════════════════════════════════════════════════════════
#  CHROME  — shared header + footer for interior pages 2–7
# ═══════════════════════════════════════════════════════════
def chrome(c, logo_path, client, comp, user, desig, email, phone, web, pg, date, accent="#1B4FE4"):
    # ── top accent bar ──────────────────────────────────
    rect(c, 0, H-5, W, 5, fill=accent)
    rect(c, 0, H-3, 200, 3, fill="#00D4FF")

    # ── logo ────────────────────────────────────────────
    logo(c, logo_path, MARGIN, H-44, 110, 28)   # y=568 → 596

    # ── header right caption ────────────────────────────
    caption = f"{client}  ·  Website Revenue Audit  ·  {date}"
    txt(c, caption, W-MARGIN, H-18, "Helvetica", 7.5, "#64748B", "right")

    # ── header divider line ─────────────────────────────
    ln(c, MARGIN, H-50, W-MARGIN, H-50, col="#E2E8F0", lw=0.8)

    # ── footer divider ──────────────────────────────────
    ln(c, MARGIN, 40, W-MARGIN, 40, col="#E2E8F0", lw=0.8)

    # ── footer left ─────────────────────────────────────
    txt(c, f"{comp.upper()}  —  CONFIDENTIAL AUDIT REPORT",
        MARGIN, 26, "Helvetica-Bold", 7.5, "#1E293B")

    # ── footer right contact ────────────────────────────
    contact = f"{user}, {desig}  ·  {email}  ·  {phone}  ·  {web}"
    txt(c, contact, W-MARGIN, 26, "Helvetica", 7.5, "#64748B", "right")

    # ── page number badge ───────────────────────────────
    circ(c, W/2, 26, 12, accent)
    txt(c, str(pg), W/2, 22, "Helvetica-Bold", 8, "#FFFFFF", "center")


# ═══════════════════════════════════════════════════════════
#  SECTION HEADER  — eyebrow / title / subtitle block
#  Occupies H-54 … H-116 (62 pt).  CONTENT_TOP = H-120.
# ═══════════════════════════════════════════════════════════
def section_head(c, eyebrow, title, subtitle, accent):
    SY = H - 58          # eyebrow baseline

    # Left accent bar
    rect(c, MARGIN, SY-50, 5, 56, fill=accent)

    # Eyebrow
    txt(c, eyebrow, MARGIN+14, SY, "Helvetica-Bold", 7.5, accent)

    # Title (22 pt)
    txt(c, title, MARGIN+14, SY-22, "Helvetica-Bold", 22, "#0D1424")

    # Subtitle (10 pt) — 16 pt below title
    txt(c, subtitle, MARGIN+14, SY-42, "Helvetica", 10, "#475569")

    # Divider
    ln(c, MARGIN, SY-54, W-MARGIN, SY-54, col="#E2E8F0", lw=0.8)


CONTENT_TOP = H - 120    # first usable y below section header


# ═══════════════════════════════════════════════════════════
#  PAGE 1 — COVER
# ═══════════════════════════════════════════════════════════
def draw_cover(c, ad, ci, logo_path, today):
    name  = ad.get("client_name", "Client Website")
    url   = ad.get("client_url", "")
    sc2   = str(ad.get("overall_score", "D")).upper()[:1]
    scol  = score_col(sc2)
    stats = ad.get("stats", {})

    # ── layout split ────────────────────────────────────
    LP  = W * 0.58          # left panel width  = 459 pt
    rpx = LP + (W-LP)/2     # right panel cx    = 626 pt

    # ── backgrounds ─────────────────────────────────────
    gradient(c, 0,  0, W,    H, "#060C1F", "#0C1A38", vert=False)
    gradient(c, LP, 0, W-LP, H, "#0B2060", "#050E3A", vert=False)

    # Dot grid – left panel only
    sc(c, "#1B3A6A"); c.setLineWidth(0.4)
    for gx in range(0, int(LP)+1, 26):
        for gy in range(0, int(H)+1, 26):
            c.circle(gx, gy, 0.7, fill=1, stroke=0)

    # Diagonal accent stripe
    from reportlab.lib import colors as rlc
    c.setFillColor(rlc.HexColor("#1B4FE4"))
    p = c.beginPath()
    p.moveTo(LP-55, H); p.lineTo(LP+18, H)
    p.lineTo(LP-18, 0); p.lineTo(LP-91, 0)
    p.close()
    c.drawPath(p, fill=1, stroke=0)

    # Top accent bars
    rect(c, 0,  H-6, W,       6, fill="#1B4FE4")
    rect(c, 0,  H-3, LP*0.5,  3, fill="#00D4FF")
    rect(c, LP, H-6, W-LP,    6, fill="#1B4FE4")

    # ── Logo ────────────────────────────────────────────
    logo(c, logo_path, MARGIN, H-64, 188, 46)

    # Date chip (top right)
    chip_text = f"AUDIT REPORT  ·  {today.upper()}"
    c.setFont("Helvetica-Bold", 7.5)
    chip_w = c.stringWidth(chip_text, "Helvetica-Bold", 7.5) + 24
    chip_x = W - chip_w - MARGIN
    rect(c, chip_x, H-32, chip_w, 20, fill="#1B4FE4", r=10)
    txt(c, chip_text, chip_x+12, H-25, "Helvetica-Bold", 7.5, "#FFFFFF")

    # ── LEFT CONTENT ────────────────────────────────────
    # Eyebrow (below logo)
    ey_y = H - 82
    txt(c, "CONFIDENTIAL  ·  EXECUTIVE WEBSITE AUDIT REPORT",
        MARGIN, ey_y, "Helvetica-Bold", 7.5, "#00D4FF")
    rect(c, MARGIN, ey_y-8, 48, 2, fill="#1B4FE4")

    # Client name — word-wrapped, 34 pt, start 56 pt below eyebrow
    name_y = ey_y - 52
    parts = name.split()
    c.setFont("Helvetica-Bold", 34)
    fc(c, "#FFFFFF")
    buf, name_lines = [], []
    for p2 in parts:
        probe = " ".join(buf + [p2])
        if c.stringWidth(probe, "Helvetica-Bold", 34) <= LP - 70:
            buf.append(p2)
        else:
            if buf: name_lines.append(" ".join(buf))
            buf = [p2]
    if buf: name_lines.append(" ".join(buf))
    NAME_LH = 44          # line-height for 34 pt font
    for i, l in enumerate(name_lines[:3]):
        c.drawString(MARGIN, name_y - i*NAME_LH, l)
    bot_name = name_y - (len(name_lines)-1) * NAME_LH

    # Tagline
    txt(c, "A Strategic Revenue & UX Analysis of Your Digital Presence",
        MARGIN, bot_name - 34, "Helvetica", 11, "#7B93C8")

    # URL
    txt(c, f"► {url}", MARGIN, bot_name - 54, "Helvetica", 9, "#4A6A9E")

    # Rule
    ln(c, MARGIN, bot_name-66, LP-48, bot_name-66, col="#1B4FE4", lw=1.5)

    # ── STAT CARDS ──────────────────────────────────────
    CARD_W   = 148
    CARD_H   = 90
    CARD_GAP = 12
    CARD_Y   = 46           # bottom of cards (above footer)
    stat_items = [
        (stats.get("pages_reviewed",  5),  "PAGES AUDITED",  "Full customer journey",   "#2563EB", "#EFF6FF"),
        (stats.get("checklist_failed",12), "ISSUES FOUND",   "Hurting your revenue",    "#D97706", "#FFFBEB"),
        (stats.get("broken_elements",  6), "CRITICAL BUGS",  "Destroying client trust", "#DC2626", "#FEF2F2"),
    ]
    for i, (num, label, sub, acc2, bg2) in enumerate(stat_items):
        cx = MARGIN + i*(CARD_W + CARD_GAP)
        # Shadow
        rect(c, cx+3, CARD_Y-3, CARD_W, CARD_H, fill="#000919", r=10)
        # Card
        rect(c, cx, CARD_Y, CARD_W, CARD_H, fill=bg2, r=10)
        # Top colour strip
        rect(c, cx,  CARD_Y+CARD_H-18, CARD_W, 18, fill=acc2, r=10)
        rect(c, cx,  CARD_Y+CARD_H-9,  CARD_W,  9, fill=acc2, r=0)
        # Number  — vertically centred in card body
        num_y = CARD_Y + CARD_H - 18 - 14      # 14pt below strip bottom
        txt(c, str(num), cx+CARD_W/2, num_y-22, "Helvetica-Bold", 38, acc2, "center")
        # Label
        txt(c, label, cx+CARD_W/2, CARD_Y+24, "Helvetica-Bold", 8.5, "#1E293B", "center")
        # Sub
        txt(c, sub,   cx+CARD_W/2, CARD_Y+11, "Helvetica",      7.5, "#64748B", "center")

    # Prepared-by strip
    prep = (f"Prepared by  {ci.get('user_name','AJ')}, {ci.get('designation','Founder')}  ·  "
            f"{ci.get('company_name','TECHSOUL')}  ·  {ci.get('website_url','')}")
    txt(c, prep, MARGIN, 32, "Helvetica", 7.5, "#4A6A9E")

    # ══ RIGHT PANEL ══════════════════════════════════════
    # Panel spans LP … W (width ≈ 333 pt).  rpx = centre ≈ 626.
    # Strict top-to-bottom layout (no overlaps):
    #
    #  y=572  "OVERALL WEBSITE SCORE"  (10 pt bold)
    #  y=556  subtitle                 (8 pt)
    #  y=546  cyan separator line
    #  y=518  item 1   (Mobile Experience | ✗ Fail)
    #  y=499  item 2
    #  y=480  item 3
    #  y=461  item 4
    #  y=450  grey separator line
    #  —— 80 pt gap ——
    #  y=290  Score circle centre  r=80 → top 370, bottom 210
    #  y=192  "YOUR OVERALL GRADE" label
    #  —— 64 pt gap ——
    #  y=110  ACTION REQUIRED badge centre  (height 36)

    # Labels
    txt(c, "OVERALL WEBSITE SCORE",
        rpx, 572, "Helvetica-Bold", 10, "#FFFFFF", "center")
    txt(c, "Based on full UX & revenue audit",
        rpx, 556, "Helvetica", 8, "#6B8DC2", "center")

    ln(c, LP+20, 546, W-20, 546, col="#1B4FE4", lw=1)

    # Breakdown list
    matrix = ad.get("issue_matrix", [{}])
    first  = matrix[0] if matrix else {}
    breakdown = [
        ("Mobile Experience", first.get("mobile_ux",   "Fail")),
        ("Lead Capture",      first.get("cta_clarity", "Fail")),
        ("SEO Visibility",    first.get("seo",         "Fail")),
        ("Trust Signals",     first.get("trust",       "Fail")),
    ]
    ITEM_Y = [518, 499, 480, 461]
    for idx, (lbl, val) in enumerate(breakdown):
        iy = ITEM_Y[idx]
        s  = str(val).lower()
        vc = "#22C55E" if s=="pass" else ("#F59E0B" if s=="partial" else "#EF4444")
        badge = "✓ Pass" if s=="pass" else ("~ Partial" if s=="partial" else "✗ Fail")
        # Left label
        txt(c, lbl, LP+22, iy, "Helvetica", 8.5, "#94A3B8")
        # Right badge (right-aligned to W-MARGIN)
        txt(c, badge, W-MARGIN, iy, "Helvetica-Bold", 8.5, vc, "right")
        # Thin separator
        if idx < 3:
            ln(c, LP+22, iy-8, W-MARGIN, iy-8, col="#1A3060", lw=0.4)

    ln(c, LP+22, 450, W-MARGIN, 450, col="#1B4FE4", lw=0.8)

    # Score circle — centre at y=290, radius 80
    SCORE_CY = 290
    SCORE_R  = 80
    circ(c, rpx, SCORE_CY, SCORE_R+24, "#0F2462")
    circ(c, rpx, SCORE_CY, SCORE_R+8,  "#152E80")
    circ(c, rpx, SCORE_CY, SCORE_R,    "#0D2060")

    # Grade letter — visually centred in circle
    txt(c, sc2, rpx, SCORE_CY-34, "Helvetica-Bold", 90, scol, "center")

    # "YOUR OVERALL GRADE" label below circle
    txt(c, "YOUR OVERALL GRADE",
        rpx, SCORE_CY - SCORE_R - 20, "Helvetica-Bold", 8, "#6B8DC2", "center")

    # ACTION REQUIRED badge — centre at y=110
    BADGE_W, BADGE_H = 168, 40
    rect(c, rpx-BADGE_W/2, 90, BADGE_W, BADGE_H, fill="#EF4444", r=BADGE_H//2)
    txt(c, "⚠  ACTION REQUIRED",               rpx, 118, "Helvetica-Bold", 10,  "#FFFFFF", "center")
    txt(c, "Revenue at risk — every day counts", rpx,  98, "Helvetica",      7.5, "#FFCDD2", "center")


# ═══════════════════════════════════════════════════════════
#  PAGE 2 — BUSINESS LOSSES
# ═══════════════════════════════════════════════════════════
def draw_losses(c, ad, logo_path, ci, today, pg):
    chrome(c, logo_path, ad.get("client_name",""), ci.get("company_name","TECHSOUL"),
           ci.get("user_name","AJ"), ci.get("designation","Founder"),
           ci.get("email",""), ci.get("phone",""), ci.get("website_url",""), pg, today, "#EF4444")

    section_head(c, "BUSINESS IMPACT  ·  PAGE 1 OF 2",
                 "What Is Your Website Costing You Right Now?",
                 "Plain English impact — no tech jargon. These are real revenue losses happening today.",
                 "#EF4444")

    verdict = ad.get("verdict", "NEEDS URGENT ATTENTION")
    vsum    = ad.get("verdict_summary", "")

    # Verdict banner
    BANN_H = 58
    vy     = CONTENT_TOP - 2
    rect(c, MARGIN, vy-BANN_H, W-MARGIN*2, BANN_H, fill="#1A0408", r=8)
    rect(c, MARGIN, vy-BANN_H, 5,          BANN_H, fill="#EF4444",  r=0)
    txt(c, f"VERDICT:  {verdict}", MARGIN+16, vy-18, "Helvetica-Bold", 11, "#EF4444")
    wrap(c, vsum, MARGIN+16, vy-36, "Helvetica", 9, "#E2E8F0", W-MARGIN*2-28, lh=14)

    # Loss cards — 2-column grid
    losses = ad.get("business_losses", [
        "Every visitor who can't find your phone number is a lost client.",
        "Slow mobile load times cost you 40% of visitors immediately.",
        "No testimonials: 7 in 10 new visitors won't contact you.",
        "Invisible on Google — competitors capture all local searches.",
        "No contact form = zero passive lead generation.",
    ])

    COL_W   = (W - MARGIN*2 - 16) / 2
    CARD_H  = 62
    GAP_H   = 10
    grid_y  = vy - BANN_H - 14   # top of first card

    for idx, loss in enumerate(losses[:8]):
        col = idx % 2
        row = idx // 2
        cx2 = MARGIN + col * (COL_W + 16)
        cy2 = grid_y - row * (CARD_H + GAP_H)   # cy2 = top of card
        if cy2 - CARD_H < 44: break

        rect(c, cx2,   cy2-CARD_H, COL_W, CARD_H, fill="#FFF5F5", r=8)
        rect(c, cx2,   cy2-CARD_H, 5,     CARD_H, fill="#EF4444",  r=0)
        rect(c, cx2+5, cy2-CARD_H, COL_W-5, CARD_H, fill="#FFF0F0", r=0)

        # Numbered circle badge
        BDG_CX = cx2 + 26
        BDG_CY = cy2 - CARD_H/2
        circ(c, BDG_CX, BDG_CY, 16, "#EF4444")
        txt(c, f"#{idx+1}", BDG_CX, BDG_CY-5, "Helvetica-Bold", 8.5, "#FFFFFF", "center")

        # Text — starts 14 pt below card top
        wrap(c, loss, cx2+50, cy2-16, "Helvetica-Bold", 9, "#1E293B", COL_W-60, lh=14)


# ═══════════════════════════════════════════════════════════
#  PAGE 3 — COST OF WAITING
# ═══════════════════════════════════════════════════════════
def draw_cost(c, ad, logo_path, ci, today, pg):
    chrome(c, logo_path, ad.get("client_name",""), ci.get("company_name","TECHSOUL"),
           ci.get("user_name","AJ"), ci.get("designation","Founder"),
           ci.get("email",""), ci.get("phone",""), ci.get("website_url",""), pg, today, "#F59E0B")

    section_head(c, "BUSINESS IMPACT  ·  PAGE 2 OF 2",
                 "The Price You Pay Every Day You Wait",
                 "Delaying your website fix is not free — it compounds into real financial and reputation damage.",
                 "#F59E0B")

    items = ad.get("cost_of_waiting", [])
    if not items:
        items = [{"title":"Revenue at Risk","impact":"High",
                  "description":"Your website is not converting visitors into clients."}]

    avail  = CONTENT_TOP - 8 - 44     # space between content_top and footer
    n      = min(len(items), 5)
    ROW_H  = min(80, (avail - (n-1)*10) / n)

    for i, item in enumerate(items[:5]):
        iy  = CONTENT_TOP - 8 - i*(ROW_H+10)   # top of row
        imp = item.get("impact","High")
        ic  = impact_col(imp)

        rect(c, MARGIN, iy-ROW_H, W-MARGIN*2, ROW_H, fill="#FFFDF5", r=8)
        rect(c, MARGIN, iy-ROW_H, 5,          ROW_H, fill=ic)

        # Impact pill — centred vertically on left
        pw = pill_left(c, MARGIN+16, iy-ROW_H/2, imp.upper(), ic, "#FFFFFF", 8)

        tx = MARGIN + 22 + pw
        tw = W - MARGIN*2 - pw - 32

        # Title  — 18 pt below row top
        txt(c, item.get("title",""), tx, iy-18, "Helvetica-Bold", 11.5, "#1E293B")
        # Description — 16 pt below title baseline
        wrap(c, item.get("description",""), tx, iy-36, "Helvetica", 9, "#475569", tw, lh=14)


# ═══════════════════════════════════════════════════════════
#  PAGE 4 — GOOD / BAD / UGLY
# ═══════════════════════════════════════════════════════════
def draw_gbu(c, ad, logo_path, ci, today, pg):
    chrome(c, logo_path, ad.get("client_name",""), ci.get("company_name","TECHSOUL"),
           ci.get("user_name","AJ"), ci.get("designation","Founder"),
           ci.get("email",""), ci.get("phone",""), ci.get("website_url",""), pg, today, "#1B4FE4")

    section_head(c, "DETAILED AUDIT FINDINGS",
                 "The Good, The Bad & The Ugly",
                 "Every finding explained in plain business terms — what it means for your leads and revenue.",
                 "#1B4FE4")

    SECS = [
        ("the_good", "What's Working", "Keep These",       "#059669", "#ECFDF5", "✓"),
        ("the_bad",  "What's Missing", "Losing Leads",     "#D97706", "#FFFBEB", "!"),
        ("the_ugly", "What's Broken",  "Destroying Trust", "#DC2626", "#FFF1F2", "✕"),
    ]
    COL_GAP = 10
    COL_W   = (W - MARGIN*2 - COL_GAP*2) / 3
    HDR_H   = 38
    HDR_Y   = CONTENT_TOP - 4     # top of column headers

    for ci2, (key, title, sub, acol, bg, icon) in enumerate(SECS):
        cx = MARGIN + ci2 * (COL_W + COL_GAP)
        items = ad.get(key, [])

        # ── Column header ──────────────────────────────
        rect(c, cx, HDR_Y-HDR_H, COL_W, HDR_H, fill=acol, r=8)
        circ(c, cx+20, HDR_Y-HDR_H/2, 11, "#FFFFFF")
        txt(c, icon,  cx+20, HDR_Y-HDR_H/2-4, "Helvetica-Bold", 10, acol, "center")
        txt(c, title, cx+37, HDR_Y-14, "Helvetica-Bold", 10.5, "#FFFFFF")
        txt(c, sub,   cx+37, HDR_Y-29, "Helvetica",       8,   "#FFFFFF")

        # ── Item cards ─────────────────────────────────
        card_y = HDR_Y - HDR_H - 8   # top of first card

        for item in items[:5]:
            where = item.get("where","")[:38]
            found = item.get("what_found","")
            why   = item.get("why_matters","")

            # Measure wrapped lines
            c.setFont("Helvetica-Bold", 8.5)
            lines_f = _measure_wrap(c, found, "Helvetica-Bold", 8.5, COL_W-20, 2)

            c.setFont("Helvetica", 8)
            lines_w = _measure_wrap(c, why, "Helvetica", 8, COL_W-20, 2)

            # Card height:  top-pad(10) + where(13) + found-lines + 4-gap + why-lines + bot-pad(10)
            CH = 10 + 13 + len(lines_f)*13 + 4 + len(lines_w)*12 + 10
            CH = max(CH, 52)
            if card_y - CH < 44: break

            rect(c, cx,   card_y-CH, COL_W, CH, fill=bg, r=6)
            rect(c, cx,   card_y-CH, 4,     CH, fill=acol, r=0)

            # Where tag
            txt(c, where, cx+10, card_y-12, "Helvetica-Bold", 6.5, acol)

            # Found text
            y_c = card_y - 27
            fc(c, "#1E293B"); c.setFont("Helvetica-Bold", 8.5)
            for lf in lines_f:
                c.drawString(cx+10, y_c, lf); y_c -= 13

            # Why text
            y_c -= 4
            fc(c, "#475569"); c.setFont("Helvetica", 8)
            for lw2 in lines_w:
                c.drawString(cx+10, y_c, lw2); y_c -= 12

            card_y -= CH + 8


def _measure_wrap(c, text, font, size, maxw, cap):
    """Return capped list of wrapped lines (does not draw)."""
    c.setFont(font, size)
    words = str(text).split()
    lines, buf = [], []
    for w in words:
        if c.stringWidth(" ".join(buf+[w]), font, size) <= maxw:
            buf.append(w)
        else:
            if buf: lines.append(" ".join(buf))
            buf = [w]
    if buf: lines.append(" ".join(buf))
    return lines[:cap]


# ═══════════════════════════════════════════════════════════
#  PAGE 5 — BEFORE vs AFTER CHECKLIST
# ═══════════════════════════════════════════════════════════
def draw_checklist(c, ad, logo_path, ci, today, pg):
    chrome(c, logo_path, ad.get("client_name",""), ci.get("company_name","TECHSOUL"),
           ci.get("user_name","AJ"), ci.get("designation","Founder"),
           ci.get("email",""), ci.get("phone",""), ci.get("website_url",""), pg, today, "#7C3AED")

    section_head(c, "SCORECARD  ·  BEFORE vs AFTER",
                 "Your Website Today vs. After Our Revamp",
                 "Side-by-side comparison of every critical feature that drives leads and revenue.",
                 "#7C3AED")

    items = ad.get("revamp_checklist", [])
    if not items: return

    # Column widths must sum to W - MARGIN*2
    COL_FEAT  = 412
    COL_NOW   = 160
    COL_AFTER = W - MARGIN*2 - COL_FEAT - COL_NOW   # ≈ 160
    COLS = [("FEATURE / CAPABILITY", COL_FEAT),
            ("YOUR SITE NOW",         COL_NOW),
            ("AFTER REVAMP",          COL_AFTER)]

    HDR_H = 28
    hx = MARGIN
    hy = CONTENT_TOP - 4

    for ct2, cw2 in COLS:
        rect(c, hx, hy-HDR_H, cw2-2, HDR_H, fill="#0F172A", r=0)
        txt(c, ct2, hx+10, hy-HDR_H/2-4, "Helvetica-Bold", 8.5, "#FFFFFF")
        hx += cw2

    ROW_H = 28
    ry    = hy - HDR_H - 2

    for i, item in enumerate(items):
        if ry - ROW_H < 44: break
        bg = "#F8FAFF" if i%2==0 else "#FFFFFF"
        rect(c, MARGIN, ry-ROW_H, W-MARGIN*2, ROW_H, fill=bg)
        ln(c, MARGIN, ry-ROW_H, W-MARGIN, ry-ROW_H, col="#E2E8F0", lw=0.4)

        cat  = item.get("category","")
        feat = item.get("item","")
        curr = item.get("current", False)

        # Feature column
        c.setFont("Helvetica-Bold", 8); fc(c, "#7C3AED")
        cat_w = c.stringWidth(f"[{cat}]", "Helvetica-Bold", 8)
        c.drawString(MARGIN+10, ry-ROW_H/2-4, f"[{cat}]")
        txt(c, feat[:72], MARGIN+10+cat_w+6, ry-ROW_H/2-4, "Helvetica", 9, "#1E293B")

        # Status columns (centred)
        cx_now   = MARGIN + COL_FEAT + COL_NOW/2
        cx_after = MARGIN + COL_FEAT + COL_NOW + COL_AFTER/2
        now_txt   = "✓  Present" if curr else "✗  Missing"
        now_col   = "#059669"    if curr else "#DC2626"
        txt(c, now_txt,      cx_now,   ry-ROW_H/2-4, "Helvetica-Bold", 9, now_col,  "center")
        txt(c, "✓  Optimized",cx_after, ry-ROW_H/2-4, "Helvetica-Bold", 9, "#059669","center")

        ry -= ROW_H


# ═══════════════════════════════════════════════════════════
#  PAGE 6 — AUDIT MATRIX
# ═══════════════════════════════════════════════════════════
def draw_matrix(c, ad, logo_path, ci, today, pg):
    chrome(c, logo_path, ad.get("client_name",""), ci.get("company_name","TECHSOUL"),
           ci.get("user_name","AJ"), ci.get("designation","Founder"),
           ci.get("email",""), ci.get("phone",""), ci.get("website_url",""), pg, today, "#1B4FE4")

    section_head(c, "PAGE-BY-PAGE SCORECARD",
                 "Your Complete Site Audit Matrix",
                 "Pass/Fail assessment across every key page and critical business dimension.",
                 "#1B4FE4")

    matrix = ad.get("issue_matrix", [])
    if not matrix: return

    # 7 columns — must sum to W - MARGIN*2 = 720
    COLS = [("PAGE", 178), ("MOBILE UX", 90), ("CLEAR CTA", 90),
            ("CONTACT FORM", 90), ("TRUST", 90), ("SEO", 90), ("SPEED", 92)]

    HDR_H = 28
    hx = MARGIN
    hy = CONTENT_TOP - 4

    for hdr, cw in COLS:
        rect(c, hx, hy-HDR_H, cw-2, HDR_H, fill="#0F172A")
        txt(c, hdr, hx+8, hy-HDR_H/2-4, "Helvetica-Bold", 8, "#FFFFFF")
        hx += cw

    def cv(v):
        s = str(v).lower()
        if s == "pass":    return "✓ Pass",     "#059669"
        if s == "partial": return "~ Partial",   "#D97706"
        return "✗ Fail", "#DC2626"

    ROW_H = 30
    ry    = hy - HDR_H - 2

    for ri, row in enumerate(matrix):
        if ry - ROW_H < 44: break
        bg = "#F4F7FF" if ri%2==0 else "#FFFFFF"
        rect(c, MARGIN, ry-ROW_H, W-MARGIN*2, ROW_H, fill=bg)
        ln(c, MARGIN, ry-ROW_H, W-MARGIN, ry-ROW_H, col="#E2E8F0", lw=0.4)

        txt(c, row.get("page",""), MARGIN+10, ry-ROW_H/2-4, "Helvetica-Bold", 9, "#1E293B")

        vals = [row.get("mobile_ux"), row.get("cta_clarity"), row.get("forms"),
                row.get("trust"), row.get("seo"), row.get("speed","Fail")]
        vx = MARGIN + 178
        for val, (_, cw2) in zip(vals, COLS[1:]):
            t2, vc = cv(val)
            txt(c, t2, vx+cw2/2, ry-ROW_H/2-4, "Helvetica-Bold", 8.5, vc, "center")
            vx += cw2
        ry -= ROW_H


# ═══════════════════════════════════════════════════════════
#  PAGE 7 — 3-PHASE ROADMAP
# ═══════════════════════════════════════════════════════════
def draw_roadmap(c, ad, logo_path, ci, today, pg):
    import re as _re
    chrome(c, logo_path, ad.get("client_name",""), ci.get("company_name","TECHSOUL"),
           ci.get("user_name","AJ"), ci.get("designation","Founder"),
           ci.get("email",""), ci.get("phone",""), ci.get("website_url",""), pg, today, "#059669")

    section_head(c, "YOUR TRANSFORMATION PLAN",
                 "Recommended 3-Phase Revamp Roadmap",
                 "Our proven delivery process — from emergency fixes to a revenue-generating growth engine.",
                 "#059669")

    phases = ad.get("recommended_scope", [])
    if not phases:
        phases = [
            {"phase":"Phase 1 — Emergency Fixes", "timeline":"Week 1",
             "details":"SSL fix, speed optimisation, broken image repair, mobile menu fix, contact details visible"},
            {"phase":"Phase 2 — Conversion Revamp","timeline":"Weeks 2–3",
             "details":"New homepage design, CTA buttons, contact form, testimonials section, brand refresh"},
            {"phase":"Phase 3 — Growth Engine",   "timeline":"Weeks 4–6",
             "details":"Full SEO setup, Google Analytics 4, Google Business Profile, blog strategy, lead tracking"},
        ]

    n      = min(len(phases), 3)
    PH_GAP = 12
    PH_W   = (W - MARGIN*2 - PH_GAP*(n-1)) / n
    PCOLS  = ["#2563EB", "#059669", "#7C3AED"]
    PBGS   = ["#EFF6FF", "#F0FDF4", "#F5F3FF"]
    PLBLS  = ["01 / FIX", "02 / BUILD", "03 / GROW"]

    # ── Timeline strip — 28 pt below section content top
    TL_Y = CONTENT_TOP - 28     # e.g. 492 - 28 = 464

    # Connector bar
    rect(c, MARGIN, TL_Y-4, W-MARGIN*2, 8, fill="#E2E8F0", r=4)

    # ── Per-card geometry ────────────────────────────────
    CARD_BOT   = 48              # footer clearance
    CARD_TOP_Y = TL_Y - 36      # just below circle bottom (r=20 + 16 gap)
    CARD_H2    = CARD_TOP_Y - CARD_BOT

    for i, phase in enumerate(phases[:3]):
        px  = MARGIN + i*(PH_W + PH_GAP)
        pc  = PCOLS[i%3]; pb = PBGS[i%3]; plbl = PLBLS[i%3]
        pcx = px + PH_W/2

        # ── Timeline circle
        circ(c, pcx, TL_Y, 20, pc)
        txt(c, str(i+1), pcx, TL_Y-7, "Helvetica-Bold", 13, "#FFFFFF", "center")

        CT = CARD_TOP_Y          # convenient alias for card top y

        # ── Card background
        rect(c, px, CARD_BOT, PH_W, CARD_H2, fill=pb, r=12)

        # ── Card top accent strip
        rect(c, px, CT-22, PH_W, 22, fill=pc, r=0)
        rect(c, px, CT-26, PH_W, 26, fill=pc, r=12)

        # ── Step label pill
        pill(c, pcx, CT-48, plbl, pc, "#FFFFFF", 8)

        # ── Phase name (bold, phase colour, wrapped)
        wrap(c, phase.get("phase",""), px+12, CT-68,
             "Helvetica-Bold", 11, pc, PH_W-24, lh=15)

        # ── Separator 1
        sep1 = CT - 100
        ln(c, px+12, sep1, px+PH_W-12, sep1, col="#CBD5E1", lw=0.6)

        # ── TIMELINE section
        txt(c, "ESTIMATED TIMELINE", pcx, sep1-16, "Helvetica-Bold", 7, "#94A3B8", "center")
        txt(c, phase.get("timeline",""), pcx, sep1-34, "Helvetica-Bold", 16, "#1E293B", "center")

        # ── Separator 2
        sep2 = sep1 - 52
        ln(c, px+12, sep2, px+PH_W-12, sep2, col="#CBD5E1", lw=0.6)

        # ── DELIVERABLES section
        txt(c, "WHAT WE DELIVER", px+12, sep2-14, "Helvetica-Bold", 7.5, "#94A3B8")

        # Split details string on commas/semicolons into bullets
        raw = phase.get("details","")
        bullets = [b.strip().rstrip(".") for b in _re.split(r"[,;]", raw) if b.strip()]
        bullets = bullets[:6]

        bul_y = sep2 - 32
        for bul in bullets:
            if bul_y < CARD_BOT + 10: break
            circ(c, px+14, bul_y+4, 3, pc)
            # Inline wrap for bullet text (max 2 lines)
            c.setFont("Helvetica", 9); fc(c, "#374151")
            bwords = bul.split()
            bline, blines2 = [], []
            for bw in bwords:
                if c.stringWidth(" ".join(bline+[bw]),"Helvetica",9) <= PH_W-34:
                    bline.append(bw)
                else:
                    if bline: blines2.append(" ".join(bline))
                    bline=[bw]
            if bline: blines2.append(" ".join(bline))
            blines2 = blines2[:2]
            for bi, bl in enumerate(blines2):
                c.drawString(px+24, bul_y-bi*13, bl)
            bul_y -= 16 + (len(blines2)-1)*13 + 6


# ═══════════════════════════════════════════════════════════
#  PAGE 8 — ABOUT + CTA  (Dark creative)
# ═══════════════════════════════════════════════════════════
def draw_about(c, ad, logo_path, ci, today, pg):
    LP2 = W * 0.56          # split x ≈ 443
    rpx = LP2 + (W-LP2)/2  # right panel centre ≈ 618

    # Backgrounds
    gradient(c, 0,   0, W,    H, "#060C1F", "#0B1830", vert=False)
    gradient(c, LP2, 0, W-LP2,H, "#1238B0", "#0A1F7A", vert=False)

    # Diagonal connector
    from reportlab.lib import colors as rlc
    c.setFillColor(rlc.HexColor("#1B4FE4"))
    p = c.beginPath()
    p.moveTo(LP2-50, H); p.lineTo(LP2+20, H)
    p.lineTo(LP2-10, 0); p.lineTo(LP2-80, 0); p.close()
    c.drawPath(p, fill=1, stroke=0)

    # Top accent bars
    rect(c, 0,   H-6, LP2,    6, fill="#1B4FE4")
    rect(c, 0,   H-3, LP2*0.4,3, fill="#00D4FF")
    rect(c, LP2, H-6, W-LP2,  6, fill="#00D4FF")

    # Logo
    logo(c, logo_path, MARGIN, H-68, 180, 46)

    # ── LEFT — Company content ──────────────────────────
    txt(c, "ABOUT TECHSOUL  ·  WHY WE'RE THE RIGHT CHOICE",
        MARGIN, H-82, "Helvetica-Bold", 7.5, "#00D4FF")

    txt(c, "We Don't Just Build Websites.",
        MARGIN, H-104, "Helvetica-Bold", 22, "#FFFFFF")
    txt(c, "We Build Revenue-Generating Machines.",
        MARGIN, H-130, "Helvetica-Bold", 22, "#00D4FF")
    rect(c, MARGIN, H-138, 80, 2, fill="#1B4FE4")

    about = (
        f"{ci.get('full_company','GrowEagles TechSoul Pvt. Ltd.')} is a boutique digital growth studio "
        f"specializing in high-converting website design, branding, and growth optimization. "
        f"We work with businesses across India and globally to transform their digital presence "
        f"from a passive brochure into an active lead-generation engine."
    )
    wrap(c, about, MARGIN, H-154, "Helvetica", 9.5, "#94A3B8", LP2-MARGIN*2-14, lh=16)

    # USP Cards — 4 items, 62 pt step, 56 pt card height
    USPS = [
        ("1", "Business First",  "Every design decision is tied to your revenue goals."),
        ("2", "Fast Delivery",   "Production-ready website delivered in 2–4 weeks."),
        ("3", "Growth Focused",  "Built to increase traffic, trust and conversions."),
        ("4", "Ongoing Support", "We stay accountable after launch with monitoring."),
    ]
    USP_START = H - 248
    USP_STEP  = 62
    USP_H     = 56
    USP_W     = LP2 - MARGIN*2 - 14

    for i, (num, ut, ud) in enumerate(USPS):
        cy3 = USP_START - i*USP_STEP
        if cy3 - USP_H < 42: break
        rect(c, MARGIN, cy3-USP_H, USP_W, USP_H, fill="#0D1F3E", r=8)
        rect(c, MARGIN, cy3-USP_H, 4,     USP_H, fill="#1B4FE4")

        # Number circle
        circ(c, MARGIN+26, cy3-USP_H/2, 15, "#1B4FE4")
        txt(c, num, MARGIN+26, cy3-USP_H/2-5, "Helvetica-Bold", 11, "#FFFFFF", "center")

        # Title + description
        txt(c, ut, MARGIN+50, cy3-18, "Helvetica-Bold", 11, "#FFFFFF")
        txt(c, ud, MARGIN+50, cy3-34, "Helvetica",       9, "#64748B")

    # Footer
    ln(c, MARGIN, 38, LP2-14, 38, col="#1F2D40", lw=0.6)
    txt(c, f"© {datetime.date.today().year} {ci.get('company_name','TECHSOUL')}  ·  Confidential & Proprietary",
        MARGIN, 24, "Helvetica", 7.5, "#4A6080")

    # ── RIGHT — CTA panel ──────────────────────────────
    # Circle centred at SCY.  All content lives INSIDE the outer circle.
    SCY = H * 0.50   # = 306  → outer r=148 → top=454, bottom=158

    circ(c, rpx, SCY, 148, "#0C2070")   # outermost glow ring
    circ(c, rpx, SCY, 124, "#0E2A8A")   # mid ring
    circ(c, rpx, SCY,  94, "#1238B0")   # inner ring
    circ(c, rpx, SCY,  62, "#1B4FE4")   # bright core

    # ── "READY TO TRANSFORM / YOUR WEBSITE?" inside top of circle
    txt(c, "READY TO TRANSFORM", rpx, SCY+122, "Helvetica-Bold", 9.5, "#FFFFFF",  "center")
    txt(c, "YOUR WEBSITE?",       rpx, SCY+106, "Helvetica-Bold", 9.5, "#00D4FF",  "center")

    # ── Thin cyan rule
    rect(c, rpx-50, SCY+96, 100, 1.5, fill="#00D4FF", r=1)

    # ── Main CTA headline
    txt(c, "Book Your FREE",       rpx, SCY+78, "Helvetica-Bold", 19, "#FFFFFF", "center")
    txt(c, "15-Min Strategy Call", rpx, SCY+56, "Helvetica-Bold", 19, "#FFFFFF", "center")

    # ── Contact details (3 lines, 22 pt apart)
    contacts = [
        ("URL:",   ci.get("website_url","https://techsoul.in")),
        ("EMAIL:", ci.get("email","mail@techsoul.in")),
        ("PHONE:", ci.get("phone","+919862542983")),
    ]
    for j, (lbl2, val2) in enumerate(contacts):
        txt(c, f"{lbl2}  {val2}", rpx, SCY+28 - j*22,
            "Helvetica-Bold", 9.5, "#BFD7FF", "center")

    # ── White CTA button
    BTN_W, BTN_H = 180, 40
    rect(c, rpx-BTN_W/2, SCY-90, BTN_W, BTN_H, fill="#FFFFFF", r=BTN_H//2)
    txt(c, "→  Let's Talk Now", rpx, SCY-73, "Helvetica-Bold", 13, "#1B4FE4", "center")

    txt(c, "No obligation  ·  No sales pressure  ·  Just honest advice",
        rpx, SCY-110, "Helvetica", 7.5, "#93C5FD", "center")

    txt(c, f"Page {pg}", W-MARGIN, 24, "Helvetica", 7.5, "#4A6080", "right")


# ═══════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════
def build_pdf_report(audit_data: Dict[str,Any], output_path: str,
                     company_info: Dict[str,Any] = None):
    if not company_info:
        company_info = {
            "user_name":    "AJ",
            "designation":  "Founder",
            "company_name": "TECHSOUL",
            "full_company": "GrowEagles TechSoul Pvt. Ltd.",
            "website_url":  "https://techsoul.in",
            "email":        "mail@techsoul.in",
            "phone":        "+919862542983",
        }

    today    = datetime.date.today().strftime("%B %d, %Y")
    static_d = os.path.join(os.path.dirname(__file__), "..", "static")
    lp_dark  = os.path.join(static_d, "techsoul-logo.png")
    lp_white = os.path.join(static_d, "techsoul-logo-white.png")
    if not os.path.exists(lp_white): lp_white = lp_dark

    cv = pdf_canvas.Canvas(output_path, pagesize=landscape(letter))
    cv.setTitle(f"Website Audit — {audit_data.get('client_name','Client')}")
    cv.setAuthor(f"{company_info.get('user_name','AJ')} · {company_info.get('company_name','TECHSOUL')}")

    draw_cover(cv,     audit_data, company_info, lp_white, today); cv.showPage()
    draw_losses(cv,    audit_data, lp_dark,  company_info, today, 2); cv.showPage()
    draw_cost(cv,      audit_data, lp_dark,  company_info, today, 3); cv.showPage()
    draw_gbu(cv,       audit_data, lp_dark,  company_info, today, 4); cv.showPage()
    draw_checklist(cv, audit_data, lp_dark,  company_info, today, 5); cv.showPage()
    draw_matrix(cv,    audit_data, lp_dark,  company_info, today, 6); cv.showPage()
    draw_roadmap(cv,   audit_data, lp_dark,  company_info, today, 7); cv.showPage()
    draw_about(cv,     audit_data, lp_white, company_info, today, 8); cv.showPage()

    cv.save()
