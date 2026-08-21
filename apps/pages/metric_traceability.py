import dash
from dash import html, dcc, callback, Output, Input

dash.register_page(
    __name__,
    path="/metric-traceability",
    name="Metric Traceability",
    title="Metric Traceability",
)


# ---------------------------------------------------------------------------
# Metric data
# ---------------------------------------------------------------------------

METRIC_DATA = {
    "raum": {
        "title": "RAUM — Regulatory Assets Under Management",
        "calc_title": "Regulatory Assets Under Management",
        "node2_title": "RAUM Calculation Components",
        "node2_count": "8 components defined",
        "value": "$1,234,567,890",
        "job": "pf_raum_calc_v4",
        "reviewer": "Sharmin Rahman",
        "approval_date": "Aug 21, 2024",
        "status": "Approved",
        "formula": "Sum of qualifying investor commitments",
        "form_ref": "ADV Form Section 7.B.(1)  ·  Rule version 4.2",
        "formula_label": "RAUM — Regulatory Assets Under Management",
        "formula_desc": "Sum of qualifying investor commitments across all funds",
        "components": [
            "Contributions", "Recyclable", "Recallable", "Level 1 Assets",
            "Level 2 Assets", "Level 3 Assets", "Cost-Based Assets", "Cash & Cash Equiv.",
        ],
        "review_decision": "Approved",
        "review_comment": "Difference due to timing of capital call in Investran vs PCAP cut-off.",
        "review_datetime": "Aug 21, 2024 11:30 AM",
    },
    "total_pf_assets": {
        "title": "Total Private Fund Assets",
        "calc_title": "Total Private Fund Assets",
        "node2_title": "PF Asset Calculation Components",
        "node2_count": "5 components defined",
        "value": "$2,456,789,012",
        "job": "pf_assets_calc_v2",
        "reviewer": "S. Rahman",
        "approval_date": "Aug 20, 2024",
        "status": "Reviewed",
        "formula": "Fair value of all fund assets",
        "form_ref": "PF Form Section 1.A  ·  Rule version 2.0",
        "formula_label": "Total Private Fund Assets",
        "formula_desc": "Sum of fair value of all portfolio company assets",
        "components": [
            "Portfolio Company Equity", "Portfolio Company Debt",
            "Fund-of-Funds NAV", "Cash & Equivalents", "Accrued Income",
        ],
        "review_decision": "Reviewed",
        "review_comment": "Reconciled against PCAP statements. Minor timing difference of $1.2M within threshold.",
        "review_datetime": "Aug 20, 2024 09:15 AM",
    },
    "total_leverage": {
        "title": "Total Leverage",
        "calc_title": "Total Leverage",
        "node2_title": "Leverage Calculation Components",
        "node2_count": "3 components defined",
        "value": "$345,678,900",
        "job": "pf_leverage_calc_v1",
        "reviewer": None,
        "approval_date": None,
        "status": "Pending Review",
        "formula": "Total borrowings / NAV",
        "form_ref": "PF Form Section 1.B  ·  Rule version 1.0",
        "formula_label": "Total Leverage",
        "formula_desc": "Total outstanding borrowings divided by NAV",
        "components": ["Senior Debt", "Subordinated Debt", "Fund-Level Leverage"],
        "review_decision": "Pending Review",
        "review_comment": None,
        "review_datetime": None,
    },
    "investor_concentration": {
        "title": "Investor Concentration",
        "calc_title": "Investor Concentration",
        "node2_title": "Concentration Calculation Components",
        "node2_count": "4 components defined",
        "value": "25.4%",
        "job": "pf_conc_calc_v3",
        "reviewer": "S. Rahman",
        "approval_date": "Aug 19, 2024",
        "status": "Reviewed",
        "formula": "Largest investor / Total AUM",
        "form_ref": "PF Form Section 2.A  ·  Rule version 3.0",
        "formula_label": "Investor Concentration",
        "formula_desc": "Largest single investor commitment as % of total AUM",
        "components": ["Top Investor Commitment", "Total AUM"],
        "review_decision": "Reviewed",
        "review_comment": "Concentration calculated using Aug 21 snapshot. LP schedule reconciled.",
        "review_datetime": "Aug 19, 2024 14:00 PM",
    },
    "non_us_ownership": {
        "title": "Non-US Ownership %",
        "calc_title": "Non-US Ownership Percentage",
        "node2_title": "Non-US Ownership Components",
        "node2_count": "2 components defined",
        "value": "25.1%",
        "job": "adv_non_us_calc_v2",
        "reviewer": "S. Rahman",
        "approval_date": "Aug 20, 2024",
        "status": "Approved",
        "formula": "Non-US commitments / Total commitments × 100",
        "form_ref": "ADV Form Section 7.B.(1)  ·  Rule version 2.0",
        "formula_label": "Non-US Ownership %",
        "formula_desc": "Non-US investor commitments as % of total commitments",
        "components": ["Non-US Investor Commitments", "Total Investor Commitments"],
        "review_decision": "Approved",
        "review_comment": "Non-US flagged per Anduin investor_type field. Cross-checked against Investran.",
        "review_datetime": "Aug 20, 2024 16:45 PM",
    },
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def badge(text, cls):
    return html.Span(text, className=f"status-badge {cls}")


def action_link(text, href="#", danger=False):
    cls = "action-link danger" if danger else "action-link"
    return html.A(text, href=href, className=cls)


def kv_row(label, value, value_style=None):
    """Single key-value row used inside panels."""
    return html.Div([
        html.Span(label, style={"color": "#6b7280", "fontSize": "12px", "minWidth": "140px"}),
        html.Span(value, style={"color": "#111827", "fontSize": "13px", **(value_style or {})}),
    ], style={"display": "flex", "alignItems": "flex-start", "gap": "12px", "padding": "4px 0"})


def audit_row(dot_cls, timestamp, description):
    return html.Div([
        html.Span(className=f"status-dot {dot_cls}"),
        html.Span(
            timestamp,
            style={"color": "#6b7280", "fontSize": "12px", "minWidth": "120px", "flexShrink": "0"},
        ),
        html.Span(description, style={"color": "#111827", "fontSize": "13px"}),
    ], style={"display": "flex", "alignItems": "center", "gap": "10px", "padding": "6px 0"})


def make_arrow():
    return html.Div("↓", className="trace-arrow")


# ---------------------------------------------------------------------------
# Dynamic right-panels builder
# ---------------------------------------------------------------------------

_SOURCE_ROWS = [
    ("Investran",            "investran__investors",  "Aug 21, 2024 06:00 UTC", "45,678", "Current"),
    ("QUILT",                "quilt__positions",      "Aug 21, 2024 06:00 UTC", "12,234", "Current"),
    ("Anduin",               "anduin__commitments",   "Aug 20, 2024 22:00 UTC", "8,901",  "Stale (>6h)"),
    ("Financial Statements", "pcap_q3_2024.xlsx",     "Aug 18, 2024",           "1 file", "Loaded"),
]

_SOURCE_STATUS_MAP = {
    "Current":     ("badge-success", "Current"),
    "Stale (>6h)": ("badge-warning", "Stale (>6h)"),
    "Loaded":      ("badge-success", "Loaded"),
}


def _build_right_panels(d):
    # Panel A – Source Data Detail (static)
    source_rows_html = []
    for src, table, refresh, records, status in _SOURCE_ROWS:
        badge_cls, badge_lbl = _SOURCE_STATUS_MAP.get(status, ("badge-muted", status))
        source_rows_html.append(html.Tr([
            html.Td(src,    className="cell-primary"),
            html.Td(table,  style={"fontFamily": "monospace", "fontSize": "12px"}),
            html.Td(refresh),
            html.Td(records),
            html.Td(badge(badge_lbl, badge_cls)),
        ]))

    panel_a = html.Div([
        html.Div("Source Data Detail", className="panel-title"),
        html.Div(
            html.Table([
                html.Thead(html.Tr([
                    html.Th("Source"),
                    html.Th("Table / File"),
                    html.Th("Last Refresh"),
                    html.Th("Records"),
                    html.Th("Status"),
                ])),
                html.Tbody(source_rows_html),
            ], className="data-table"),
            className="data-table-wrap",
            style={"marginTop": "12px"},
        ),
    ], className="panel-card")

    # Panel B – Business Rule Definition (dynamic)
    components_html = [
        html.Div(
            html.Span(comp, style={"color": "#111827", "fontSize": "13px"}),
            style={"padding": "3px 0"}
        )
        for comp in d.get("components", [])
    ]

    panel_b = html.Div([
        html.Div("Business Rule Definition", className="panel-title"),
        html.Div(
            d["formula_label"],
            style={"fontWeight": "600", "color": "#111827", "fontSize": "14px", "marginTop": "12px"},
        ),
        html.Div(
            d["form_ref"],
            style={"color": "#6b7280", "fontSize": "12px", "marginTop": "2px"},
        ),
        html.Div(
            d["formula_desc"],
            style={"color": "#374151", "fontSize": "13px", "marginTop": "6px"},
        ),
        html.Hr(className="divider"),
        html.Div(components_html, className="grid-2", style={"gap": "2px 20px", "marginTop": "8px"}),
        html.Div(
            "Technical SQL and calculation logic available in Business Rule Explorer. "
            "Access requires Operations role.",
            className="info-banner",
            style={"marginTop": "12px"},
        ),
    ], className="panel-card")

    # Panel C – Review & Approval (dynamic)
    reviewer = d.get("reviewer")
    review_decision = d.get("review_decision", "Pending Review")
    review_datetime = d.get("review_datetime")
    review_comment = d.get("review_comment")

    decision_cls = {
        "Approved": "badge-success",
        "Reviewed": "badge-primary",
        "Pending Review": "badge-warning",
    }.get(review_decision, "badge-muted")

    if reviewer is None:
        reviewer_display = html.Span("Pending", style={"color": "#9ca3af"})
        date_display = html.Span("—", style={"color": "#9ca3af"})
        comment_display = html.Span("No comments yet.", style={"color": "#9ca3af"})
    else:
        reviewer_display = reviewer
        date_display = review_datetime or "—"
        comment_display = review_comment or "—"

    panel_c = html.Div([
        html.Div("Review & Approval", className="panel-title"),
        html.Div([
            kv_row("Reviewer",    reviewer_display),
            kv_row("Decision",    badge(review_decision, decision_cls)),
            kv_row("Review Date", date_display),
            kv_row("Comments",    comment_display),
        ], style={"marginTop": "12px"}),
        html.Div([
            action_link("View Full Review"),
            html.Span("·", style={"color": "#9ca3af", "margin": "0 4px"}),
            action_link("View in Audit History"),
        ], style={"marginTop": "14px", "display": "flex", "alignItems": "center", "gap": "4px"}),
    ], className="panel-card")

    # Panel D – Audit Trail (dynamic)
    if review_datetime is None:
        dot1 = "dot-warning"
        entry1_time = "Pending"
        entry1_desc = review_decision
    else:
        dot1 = "dot-success" if review_decision == "Approved" else "dot-primary"
        entry1_time = review_datetime
        entry1_desc = f"{review_decision} by {reviewer or 'Reviewer'}"

    panel_d = html.Div([
        html.Div("Audit Trail", className="panel-title"),
        html.Div([
            audit_row(dot1, entry1_time, entry1_desc),
            html.Hr(style={"borderColor": "#d1d5db", "margin": "2px 0"}),
            audit_row("dot-warning", "—", "Metric calculated — pending review"),
            html.Hr(style={"borderColor": "#d1d5db", "margin": "2px 0"}),
            audit_row("dot-primary", "Aug 21 06:00 AM", "Source data refreshed (4 tables)"),
        ], style={"marginTop": "12px"}),
    ], className="panel-card")

    return [panel_a, panel_b, panel_c, panel_d]


# ---------------------------------------------------------------------------
# Callbacks
# ---------------------------------------------------------------------------

@callback(
    Output("mt-metric", "options"),
    Output("mt-metric", "value"),
    Input("mt-filing-type", "value"),
)
def cascade_metric_options(filing_type):
    if filing_type == "ADV":
        opts = [
            {"label": "RAUM",              "value": "raum"},
            {"label": "Non-US Ownership %", "value": "non_us_ownership"},
        ]
        return opts, "raum"
    else:  # PF
        opts = [
            {"label": "Total Private Fund Assets", "value": "total_pf_assets"},
            {"label": "Total Leverage",             "value": "total_leverage"},
            {"label": "Investor Concentration",     "value": "investor_concentration"},
        ]
        return opts, "total_pf_assets"


@callback(
    Output("mt-page-subtitle",  "children"),
    Output("mt-node2-title",    "children"),
    Output("mt-node2-badge",    "children"),
    Output("mt-node3-title",    "children"),
    Output("mt-node3-value",    "children"),
    Output("mt-node3-job",      "children"),
    Output("mt-node5-status",   "children"),
    Output("mt-final-reviewer", "children"),
    Output("mt-final-date",     "children"),
    Output("mt-right-panels",   "children"),
    Input("mt-filing-type",  "value"),
    Input("mt-filing-year",  "value"),
    Input("mt-fund",         "value"),
    Input("mt-metric",       "value"),
)
def update_traceability(filing_type, year, fund, metric):
    d = METRIC_DATA.get(metric, METRIC_DATA["raum"])
    subtitle = [html.Strong("Reviewer:"), f" {d['reviewer'] or 'Pending'}  ·  FY {year}  ·  Aug 21, 2024"]
    return (
        subtitle,
        d["node2_title"],
        badge(d["node2_count"], "badge-info"),
        d["calc_title"],
        d["value"],
        f"Calculated: Aug 21, 2024  ·  Databricks Job: {d['job']}",
        f"{d['title']} — {d['status']}",
        f"Reviewer: {d['reviewer'] or '—'}",
        f"Approval Date: {d['approval_date'] or 'Pending'}",
        _build_right_panels(d),
    )


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

def layout():
    # Filter bar
    filter_bar = html.Div([
        html.Div([
            html.Label("Filing Type", className="filter-label"),
            dcc.Dropdown(
                id="mt-filing-type",
                options=[{"label": "PF", "value": "PF"}, {"label": "ADV", "value": "ADV"}],
                value="PF",
                clearable=False,
                style={"minWidth": "110px"},
            ),
        ]),
        html.Div([
            html.Label("Filing Year", className="filter-label"),
            dcc.Dropdown(
                id="mt-filing-year",
                options=[{"label": "2024", "value": "2024"}, {"label": "2023", "value": "2023"}],
                value="2024",
                clearable=False,
                style={"minWidth": "100px"},
            ),
        ]),
        html.Div([
            html.Label("Fund", className="filter-label"),
            dcc.Dropdown(
                id="mt-fund",
                options=[
                    {"label": "Fund VII", "value": "fund_vii"},
                    {"label": "Fund V",   "value": "fund_v"},
                    {"label": "Fund III", "value": "fund_iii"},
                    {"label": "All",      "value": "all"},
                ],
                value="fund_vii",
                clearable=False,
                style={"minWidth": "130px"},
            ),
        ]),
        html.Div([
            html.Label("Metric", className="filter-label"),
            dcc.Dropdown(
                id="mt-metric",
                options=[
                    {"label": "Total Private Fund Assets", "value": "total_pf_assets"},
                    {"label": "Total Leverage",            "value": "total_leverage"},
                    {"label": "Investor Concentration",    "value": "investor_concentration"},
                ],
                value="total_pf_assets",
                clearable=False,
                style={"minWidth": "220px"},
            ),
        ]),
    ], className="filter-bar")

    # ---------------------------------------------------------------------------
    # Left column — Traceability Flow nodes
    # ---------------------------------------------------------------------------

    node_1 = html.Div([
        html.Div("01 — SOURCE DATA", className="trace-node-label"),
        html.Div("Multi-Source Aggregation", className="trace-node-title"),
        html.Div([
            badge("Investran",       "badge-primary"),
            badge("QUILT",           "badge-primary"),
            badge("Anduin",          "badge-info"),
            badge("Fin. Statements", "badge-muted"),
        ], className="row", style={"flexWrap": "wrap", "gap": "6px", "marginTop": "10px"}),
        html.Div(badge("4/4 Sources Loaded", "badge-success"), style={"marginTop": "10px"}),
    ], className="trace-node active")

    node_2 = html.Div([
        html.Div("02 — BUSINESS RULES", className="trace-node-label"),
        html.Div("RAUM Calculation Components", id="mt-node2-title", className="trace-node-title"),
        html.Div([
            html.Div([
                html.Span("Contributions",      style={"color": "#6b7280", "fontSize": "12px"}),
                html.Span("Recyclable",         style={"color": "#6b7280", "fontSize": "12px"}),
                html.Span("Recallable",         style={"color": "#6b7280", "fontSize": "12px"}),
                html.Span("Level 1 Assets",     style={"color": "#6b7280", "fontSize": "12px"}),
                html.Span("Level 2 Assets",     style={"color": "#6b7280", "fontSize": "12px"}),
                html.Span("Level 3 Assets",     style={"color": "#6b7280", "fontSize": "12px"}),
                html.Span("Cost-Based Assets",  style={"color": "#6b7280", "fontSize": "12px"}),
                html.Span("Cash & Cash Equiv.", style={"color": "#6b7280", "fontSize": "12px"}),
            ], className="grid-2", style={"marginTop": "10px", "gap": "6px 16px"}),
        ]),
        html.Div(badge("8 components defined", "badge-info"), id="mt-node2-badge", style={"marginTop": "10px"}),
    ], className="trace-node")

    node_3 = html.Div([
        html.Div("03 — CALCULATION", className="trace-node-label"),
        html.Div("Regulatory Assets Under Management", id="mt-node3-title", className="trace-node-title"),
        html.Div(
            "$1,234,567,890",
            id="mt-node3-value",
            style={"fontSize": "24px", "fontWeight": "700", "color": "#111827", "marginTop": "10px"},
        ),
        html.Div(
            "Calculated: Aug 21, 2024  ·  Databricks Job: pf_raum_calc_v4",
            id="mt-node3-job",
            style={"fontSize": "11px", "color": "#9ca3af", "marginTop": "4px"},
        ),
        html.Div(badge("Calculation Complete", "badge-success"), style={"marginTop": "10px"}),
    ], className="trace-node active")

    node_4 = html.Div([
        html.Div("04 — VALIDATION", className="trace-node-label"),
        html.Div([
            html.Div([
                html.Div([
                    html.Div("Calculated Value", style={"fontSize": "11px", "color": "#6b7280"}),
                    html.Div("$1,234,567,890",   style={"fontSize": "13px", "color": "#111827", "fontWeight": "600"}),
                ]),
                html.Div([
                    html.Div("PCAP Source Value", style={"fontSize": "11px", "color": "#6b7280"}),
                    html.Div("$1,200,000,000",    style={"fontSize": "13px", "color": "#111827", "fontWeight": "600"}),
                ]),
                html.Div([
                    html.Div("Variance",    style={"fontSize": "11px", "color": "#6b7280"}),
                    html.Div("$34,567,890", style={"fontSize": "13px", "color": "#ef4444", "fontWeight": "600"}),
                ]),
                html.Div([
                    html.Div("Variance %", style={"fontSize": "11px", "color": "#6b7280"}),
                    html.Div("2.88%",      style={"fontSize": "13px", "color": "#ef4444", "fontWeight": "600"}),
                ]),
            ], className="grid-2", style={"marginTop": "10px", "gap": "10px 20px"}),
        ]),
        html.Div(badge("Material Variance — Under Review", "badge-warning"), style={"marginTop": "12px"}),
    ], className="trace-node")

    node_5 = html.Div([
        html.Div("05 — FINAL METRIC", className="trace-node-label"),
        html.Div([
            html.Span("RAUM — Approved", id="mt-node5-status", className="trace-node-title"),
            html.Span(badge("Approved", "badge-success"), style={"marginLeft": "8px"}),
        ], style={"display": "flex", "alignItems": "center", "flexWrap": "wrap", "gap": "4px"}),
        html.Div(
            "Reviewer: Sharmin Rahman",
            id="mt-final-reviewer",
            style={"color": "#6b7280", "fontSize": "12px", "marginTop": "8px"},
        ),
        html.Div(
            "Approval Date: Aug 21, 2024",
            id="mt-final-date",
            style={"color": "#6b7280", "fontSize": "12px", "marginTop": "2px"},
        ),
    ], className="trace-node active")

    trace_flow = html.Div([
        node_1,
        make_arrow(),
        node_2,
        make_arrow(),
        node_3,
        make_arrow(),
        node_4,
        make_arrow(),
        node_5,
    ], className="trace-flow", style={
        "display": "flex",
        "flexDirection": "column",
        "alignItems": "center",
        "gap": "0",
    })

    # Bottom navigation links
    nav_links = html.Div([
        action_link("View Source Tables",  href="/data-pull-review"),
        html.Span("·", style={"color": "#9ca3af"}),
        action_link("View Business Rules", href="/business-rules"),
        html.Span("·", style={"color": "#9ca3af"}),
        action_link("View Review",         href="/review-feedback"),
        html.Span("·", style={"color": "#9ca3af"}),
        action_link("View Audit History",  href="/audit-history"),
        html.Span("·", style={"color": "#9ca3af"}),
        action_link("View Metric Summary", href="/metric-summary"),
    ], className="row", style={"gap": "8px", "marginTop": "16px", "alignItems": "center"})

    # ---------------------------------------------------------------------------
    # Full page
    # ---------------------------------------------------------------------------

    return html.Div([
        # Page header
        html.Div([
            html.Div([
                html.Div([
                    html.H1("Metric Traceability", className="page-heading", style={"display": "inline"}),
                    html.Span(
                        badge("Approved", "badge-success"),
                        id="mt-page-badge",
                        style={"marginLeft": "12px", "verticalAlign": "middle"},
                    ),
                ]),
                html.P(
                    [
                        html.Strong("Reviewer:"),
                        " Sharmin Rahman  ·  FY 2024  ·  Aug 21, 2024",
                    ],
                    id="mt-page-subtitle",
                    className="page-subheading",
                ),
            ]),
        ], className="page-header"),

        # Filter bar
        filter_bar,

        # Main 2-column layout: trace flow (35%) + detail panels (65%)
        html.Div([
            # Left – trace flow
            html.Div([
                html.Div("Data Lineage Pipeline", className="section-title", style={"marginBottom": "16px"}),
                trace_flow,
                nav_links,
            ]),

            # Right – stacked detail panels (dynamic via callback)
            html.Div(
                _build_right_panels(METRIC_DATA["raum"]),
                id="mt-right-panels",
                className="stack",
            ),
        ], className="grid-2", style={"gridTemplateColumns": "35% 1fr", "alignItems": "start", "marginTop": "20px"}),
    ])
