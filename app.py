from __future__ import annotations

import math
import tempfile

import gradio as gr


CSS = """
.gradio-container{max-width:1180px!important;margin:0 auto}.hero{padding:28px 30px;border-radius:22px;background:linear-gradient(135deg,#180f2a,#542b79 58%,#d45ea7);color:#fff;margin-bottom:18px;box-shadow:0 18px 50px rgba(52,22,74,.2)}.hero h1{font-size:2.25rem;margin:0 0 6px;letter-spacing:-.04em}.hero p{margin:0;color:#f6e7ff;font-size:1.02rem}.eyebrow{text-transform:uppercase;letter-spacing:.16em;font-size:.72rem;font-weight:800;color:#f3bfe1;margin-bottom:10px}.metrics{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin:4px 0 16px}.metric{padding:16px;border:1px solid #eadcf1;border-radius:14px;background:#fff}.metric span{display:block;color:#667085;font-size:.78rem;margin-bottom:6px}.metric strong{font-size:1.28rem;color:#431f60}.note{font-size:.78rem;color:#667085}@media(max-width:700px){.metrics{grid-template-columns:1fr 1fr}.hero{padding:22px}.hero h1{font-size:1.8rem}}
"""

CURRENCY = {"USD ($)": "$", "EUR (€)": "€", "GBP (£)": "£", "SGD (S$)": "S$", "AUD (A$)": "A$"}
NICHE_CPM = {"Business / entrepreneurship": 34, "Technology": 36, "Finance": 42, "Beauty / fashion": 25, "Health / wellness": 29, "Food / travel": 23, "Gaming": 24, "Lifestyle": 22}
PLATFORM = {"Instagram": 1.0, "TikTok": .95, "YouTube": 1.25, "LinkedIn": 1.2, "Newsletter": 1.15, "Podcast": 1.1}
DELIVERABLE = {"Short-form video": 1.0, "Long-form integration": 1.8, "Static post / carousel": .65, "Story set": .45, "Newsletter feature": 1.0, "Podcast mention": .8, "Raw footage": .55}
RIGHTS = {"Organic repost only": .10, "30-day paid usage": .35, "90-day paid usage": .65, "12-month paid usage": 1.10, "Perpetual usage": 1.75}
EXCLUSIVITY = {"None": 0, "7 days": .10, "30 days": .30, "90 days": .65}
TIMELINE = {"Standard": 0, "Priority": .12, "Rush": .25}


def price_campaign(followers, avg_views, engagement, niche, platform, deliverables, rights, exclusivity, timeline, production_hours, hourly_floor, hard_costs):
    followers = max(float(followers or 0), 0)
    views = max(float(avg_views or 0), 0)
    engagement = min(max(float(engagement or 0), 0), 100) / 100
    deliverables = deliverables or ["Short-form video"]
    cpm = NICHE_CPM.get(niche, 25)
    quality_views = max(views, followers * engagement * 2.5)
    media_base = max(quality_views / 1000 * cpm * PLATFORM.get(platform, 1), 75)
    workload = sum(DELIVERABLE.get(item, .5) for item in deliverables)
    media_price = media_base * workload
    multiplier = 1 + RIGHTS.get(rights, .1) + EXCLUSIVITY.get(exclusivity, 0) + TIMELINE.get(timeline, 0)
    production_floor = max(float(production_hours or 0), 0) * max(float(hourly_floor or 0), 0) + max(float(hard_costs or 0), 0)
    suggested = max(media_price * multiplier, production_floor)
    suggested = max(math.ceil(suggested / 25) * 25, 100)
    floor = max(math.ceil(max(production_floor, suggested * .75) / 25) * 25, 75)
    premium = math.ceil(suggested * 1.35 / 25) * 25
    return {"suggested": suggested, "floor": floor, "premium": premium, "quality_views": quality_views, "cpm": cpm, "production_floor": production_floor}


def _money(value: float, symbol: str) -> str:
    return f"{symbol}{value:,.0f}"


def build_rate_card(creator, niche, platform, followers, avg_views, engagement, deliverables, rights, exclusivity, timeline, production_hours, hourly_floor, hard_costs, currency, brand, campaign_goal):
    creator = (creator or "Creator").strip()
    brand = (brand or "Brand partner").strip()
    campaign_goal = (campaign_goal or "reach the right audience with trusted, useful content").strip()
    symbol = CURRENCY.get(currency, "$")
    result = price_campaign(followers, avg_views, engagement, niche, platform, deliverables, rights, exclusivity, timeline, production_hours, hourly_floor, hard_costs)
    deliverables = deliverables or ["Short-form video"]
    deliverable_list = "\n".join(f"- {item}" for item in deliverables)
    metrics = f"""<div class="metrics"><div class="metric"><span>Quote to send</span><strong>{_money(result['suggested'], symbol)}</strong></div><div class="metric"><span>Negotiation floor</span><strong>{_money(result['floor'], symbol)}</strong></div><div class="metric"><span>Premium anchor</span><strong>{_money(result['premium'], symbol)}</strong></div><div class="metric"><span>Qualified views</span><strong>{result['quality_views']:,.0f}</strong></div></div>"""

    packages = [
        ["Essential", _money(result["floor"], symbol), "Core deliverables; organic repost rights; one revision"],
        ["Campaign", _money(result["suggested"], symbol), f"Selected deliverables; {rights.lower()}; two revisions"],
        ["Amplify", _money(result["premium"], symbol), "Campaign package plus alternate hook, reporting recap, and priority delivery"],
    ]
    pitch = f"""Subject: {creator} × {brand} — {campaign_goal.capitalize()}

Hi {brand} team,

I’d love to build a {platform} campaign designed to {campaign_goal.rstrip('.')}.

My recent content averages **{float(avg_views or 0):,.0f} views** with **{float(engagement or 0):.1f}% engagement**, and the audience fit is especially strong for {niche.lower()} brands.

For the requested scope, my campaign rate is **{_money(result['suggested'], symbol)}**. That includes the agreed creative production, the deliverables below, and {rights.lower()}:

{deliverable_list}

If that fits your brief, I can send a one-page concept and delivery schedule next.

Best,  
{creator}
"""
    rate_card = f"""# {creator} — partnership rate card

**Primary platform:** {platform}  
**Niche:** {niche}  
**Audience:** {float(followers or 0):,.0f} followers  
**Average views:** {float(avg_views or 0):,.0f}  
**Engagement:** {float(engagement or 0):.1f}%

## Campaign scope

{deliverable_list}

- Usage: {rights}
- Category exclusivity: {exclusivity}
- Timeline: {timeline}

## Investment

- Negotiation floor: **{_money(result['floor'], symbol)}**
- Recommended quote: **{_money(result['suggested'], symbol)}**
- Premium package: **{_money(result['premium'], symbol)}**

Rates are planning estimates and exclude applicable tax. Final pricing depends on the confirmed brief, revisions, licensing, whitelisting, exclusivity, and production requirements.
"""
    target = tempfile.NamedTemporaryFile(mode="w", suffix="-rate-card.md", prefix="sponsorstack-", delete=False, encoding="utf-8")
    with target:
        target.write(rate_card)
    rationale = f"""### Why this rate

The estimate uses the stronger of average views and engagement-qualified reach, a **{symbol}{result['cpm']}/1,000-view** niche planning benchmark, the production workload, licensing, exclusivity, and timeline. Your production floor is **{_money(result['production_floor'], symbol)}**.

Treat the floor as private. Send the recommended quote or lead with the premium package when the brand requests paid usage, exclusivity, raw assets, or rush delivery.
"""
    return metrics, packages, pitch, rationale, target.name


def build_app() -> gr.Blocks:
    with gr.Blocks(title="SponsorStack — Price creator deals with confidence") as demo:
        gr.HTML('<section class="hero"><div class="eyebrow">Creator partnership desk</div><h1>SponsorStack</h1><p>Turn reach, rights, and production effort into a defensible brand-deal rate.</p></section>')
        with gr.Row():
            with gr.Column(scale=5):
                with gr.Row():
                    creator = gr.Textbox(label="Creator / channel", value="Alex Creates")
                    platform = gr.Dropdown(list(PLATFORM), value="Instagram", label="Primary platform")
                niche = gr.Dropdown(list(NICHE_CPM), value="Business / entrepreneurship", label="Niche")
                with gr.Row():
                    followers = gr.Number(label="Followers / subscribers", value=48000)
                    avg_views = gr.Number(label="Average views", value=18500)
                    engagement = gr.Number(label="Engagement %", value=4.8)
                deliverables = gr.CheckboxGroup(list(DELIVERABLE), value=["Short-form video", "Story set"], label="Deliverables")
                with gr.Row():
                    rights = gr.Dropdown(list(RIGHTS), value="30-day paid usage", label="Usage rights")
                    exclusivity = gr.Dropdown(list(EXCLUSIVITY), value="30 days", label="Category exclusivity")
                with gr.Row():
                    timeline = gr.Dropdown(list(TIMELINE), value="Standard", label="Timeline")
                    currency = gr.Dropdown(list(CURRENCY), value="USD ($)", label="Currency")
                with gr.Row():
                    production_hours = gr.Number(label="Production hours", value=10)
                    hourly_floor = gr.Number(label="Minimum hourly value", value=75)
                    hard_costs = gr.Number(label="Hard costs", value=100)
                brand = gr.Textbox(label="Brand", value="Northstar Labs")
                campaign_goal = gr.Textbox(label="Campaign goal", value="help independent founders discover a simpler workflow")
                calculate = gr.Button("Price this partnership", variant="primary")
            with gr.Column(scale=6):
                metrics = gr.HTML()
                packages = gr.Dataframe(headers=["Package", "Rate", "Includes"], interactive=False, wrap=True)
                gr.Markdown("### Ready-to-send pitch")
                pitch = gr.Textbox(show_label=False, lines=12)
                rationale = gr.Markdown()
                download = gr.File(label="Download rate card")
        inputs = [creator, niche, platform, followers, avg_views, engagement, deliverables, rights, exclusivity, timeline, production_hours, hourly_floor, hard_costs, currency, brand, campaign_goal]
        calculate.click(build_rate_card, inputs, [metrics, packages, pitch, rationale, download])
        demo.load(build_rate_card, inputs, [metrics, packages, pitch, rationale, download])
        gr.HTML('<p class="note">Planning aid only. There is no universal creator rate; validate against your audience quality, past conversions, contract, taxes, and current demand.</p>')
    return demo


demo = build_app()

if __name__ == "__main__":
    demo.launch(css=CSS)
