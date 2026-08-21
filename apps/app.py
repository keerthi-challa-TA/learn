import dash
from dash import html, dcc, callback, Output, Input

app = dash.Dash(
    __name__,
    use_pages=True,
    assets_folder="assets",
    suppress_callback_exceptions=True,
    title="Quantum Filing Suite",
)
server = app.server

NAV_STRUCTURE = [
    {"type": "item",    "label": "Dashboard",            "href": "/"},
    {"type": "section", "label": "Data Management"},
    {"type": "item",    "label": "Document Upload",       "href": "/document-upload"},
    {"type": "item",    "label": "Data Pull Review",      "href": "/data-pull-review"},
    {"type": "section", "label": "Mappings"},
    {"type": "item",    "label": "Investor Tagging",      "href": "/investor-tagging"},
    {"type": "item",    "label": "Classifications",       "href": "/classifications"},
    {"type": "item",    "label": "Funding Group Mapping", "href": "/funding-group-mapping"},
    {"type": "section", "label": "Notifications"},
    {"type": "item",    "label": "Notifications",         "href": "/notifications"},
    {"type": "section", "label": "Calculations"},
    {"type": "item",    "label": "Metric Summary",        "href": "/metric-summary"},
    {"type": "item",    "label": "Metric Traceability",   "href": "/metric-traceability"},
    {"type": "item",    "label": "Business Rules",        "href": "/business-rules"},
    {"type": "item",    "label": "Review & Feedback",     "href": "/review-feedback"},
    {"type": "section", "label": "Filing Output"},
    {"type": "item",    "label": "Form Generation",       "href": "/form-generation"},
    {"type": "item",    "label": "Email Distribution",    "href": "/email-distribution"},
    {"type": "section", "label": "Compliance"},
    {"type": "item",    "label": "Audit History",         "href": "/audit-history"},
    {"type": "item",    "label": "Admin",                 "href": "/admin"},
]

NAV_ICONS = {
    "/":                    "▦",
    "/document-upload":     "↑",
    "/data-pull-review":    "⊞",
    "/investor-tagging":    "◈",
    "/classifications":     "≡",
    "/funding-group-mapping":"⊕",
    "/notifications":       "◎",
    "/metric-summary":      "∑",
    "/metric-traceability": "⬡",
    "/business-rules":      "⚙",
    "/review-feedback":     "✓",
    "/form-generation":     "⊡",
    "/email-distribution":  "✉",
    "/audit-history":       "⊟",
    "/admin":               "⚙",
}


def build_nav(pathname):
    items = []
    for entry in NAV_STRUCTURE:
        if entry["type"] == "section":
            items.append(html.Div(entry["label"], className="nav-section-label"))
        else:
            href = entry["href"]
            active = pathname == href
            icon = NAV_ICONS.get(href, "·")
            cls = "nav-item nav-item-active" if active else "nav-item"
            items.append(
                dcc.Link(
                    href=href,
                    className="nav-link",
                    children=html.Div(
                        className=cls,
                        children=[
                            html.Span(icon, className="nav-icon"),
                            html.Span(entry["label"], className="nav-label"),
                        ],
                    ),
                )
            )
    return items


app.layout = html.Div(
    className="app-wrapper",
    children=[
        dcc.Location(id="url", refresh=False),
        # ── Sidebar ───────────────────────────────────────────────────────────
        html.Aside(
            className="sidebar",
            children=[
                html.Div(
                    className="sidebar-logo",
                    children=[
                        html.Div("Q", className="logo-mark"),
                        html.Div(
                            children=[
                                html.Div("Quantum", className="logo-name"),
                                html.Div("Filing Suite", className="logo-product"),
                            ],
                            className="logo-text-group",
                        ),
                    ],
                ),
                html.Nav(id="sidebar-nav", className="sidebar-nav"),
                html.Div(
                    className="sidebar-footer",
                    children=[
                        html.Div(
                            className="sidebar-footer-row",
                            children=[
                                html.Span("ADV & PF Automation", className="footer-label"),
                            ],
                        ),
                        html.Div("FY 2024  ·  v2.4.0", className="footer-meta"),
                    ],
                ),
            ],
        ),
        # ── Main ─────────────────────────────────────────────────────────────
        html.Div(
            className="main-content",
            children=[
                html.Header(
                    className="topbar",
                    children=[
                        html.Div(id="topbar-breadcrumb", className="topbar-breadcrumb"),
                        html.Div(
                            className="topbar-right",
                            children=[
                                html.Div(
                                    className="topbar-user",
                                    children=[
                                        html.Div("TM", className="avatar"),
                                        html.Div(
                                            children=[
                                                html.Div("Tax Manager", className="user-name"),
                                                html.Div("Quantum Capital", className="user-org"),
                                            ],
                                        ),
                                    ],
                                )
                            ],
                        ),
                    ],
                ),
                html.Main(
                    className="page-body",
                    children=[dash.page_container],
                ),
            ],
        ),
    ],
)


@callback(
    Output("sidebar-nav", "children"),
    Output("topbar-breadcrumb", "children"),
    Input("url", "pathname"),
)
def sync_nav(pathname):
    nav = build_nav(pathname)
    label = next(
        (e["label"] for e in NAV_STRUCTURE if e.get("href") == pathname),
        "Dashboard",
    )
    section = next(
        (
            NAV_STRUCTURE[i - 1]["label"]
            for i, e in enumerate(NAV_STRUCTURE)
            if e.get("href") == pathname and i > 0 and NAV_STRUCTURE[i - 1]["type"] == "section"
        ),
        None,
    )
    crumb_children = []
    if section:
        crumb_children += [
            html.Span(section, className="breadcrumb-section"),
            html.Span(" / ", className="breadcrumb-sep"),
        ]
    crumb_children.append(html.Span(label, className="breadcrumb-current"))
    return nav, html.Div(crumb_children, className="breadcrumb")


if __name__ == "__main__":
    app.run(debug=True, port=8050)
