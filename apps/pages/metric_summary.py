import io
import csv

import dash
from dash import html, dcc, callback, Output, Input, State, ALL, ctx, no_update

dash.register_page(
    __name__,
    path="/metric-summary",
    name="Metric Summary",
    title="Calculations – Metric Summary",
)

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

METRICS = [
    {
        "id": "PF1A",
        "name": "Total Private Fund Assets",
        "form": "PF",
        "section": "Section A",
        "value": "$1,234,567,890",
        "status": "Reviewed",
        "reviewer": "S. Rahman",
        "rev_date": "Aug 19, 2024",
    },
    {
        "id": "PF1B",
        "name": "Total Leverage",
        "form": "PF",
        "section": "Section A",
        "value": "$345,678,900",
        "status": "Pending Review",
        "reviewer": None,
        "rev_date": None,
    },
    {
        "id": "PF1C",
        "name": "Investor Concentration",
        "form": "PF",
        "section": "Section B",
        "value": "25.4%",
        "status": "Reviewed",
        "reviewer": "S. Rahman",
        "rev_date": "Aug 19, 2024",
    },
    {
        "id": "PF1D",
        "name": "Gross Asset Value",
        "form": "PF",
        "section": "Section A",
        "value": "$1,580,246,790",
        "status": "Exception",
        "reviewer": None,
        "rev_date": None,
    },
    {
        "id": "PF2A",
        "name": "Qualifying Borrowings",
        "form": "PF",
        "section": "Section A",
        "value": "$124,567,000",
        "status": "Calculated",
        "reviewer": None,
        "rev_date": None,
    },
    {
        "id": "ADV1A",
        "name": "Regulatory AUM",
        "form": "ADV",
        "section": "Section 1",
        "value": "$1,245,678,901",
        "status": "Pending Review",
        "reviewer": None,
        "rev_date": None,
    },
    {
        "id": "ADV1B",
        "name": "Non-US AUM",
        "form": "ADV",
        "section": "Section 1",
        "value": "$312,419,725",
        "status": "Reviewed",
        "reviewer": "S. Rahman",
        "rev_date": "Aug 20, 2024",
    },
    {
        "id": "ADV7A",
        "name": "Non-US Ownership %",
        "form": "ADV",
        "section": "Section 7",
        "value": "25.1%",
        "status": "Reviewed",
        "reviewer": "S. Rahman",
        "rev_date": "Aug 20, 2024",
    },
    {
        "id": "PF3A",
        "name": "Fund of Funds Assets",
        "form": "PF",
        "section": "Section B",
        "value": "$78,234,500",
        "status": "Calculated",
        "reviewer": None,
        "rev_date": None,
    },
    {
        "id": "ADV2A",
        "name": "Total Clients",
        "form": "ADV",
        "section": "Section 2",
        "value": "847",
        "status": "Calculated",
        "reviewer": None,
        "rev_date": None,
    },
]

STATUS_BADGE = {
    "Reviewed": "badge-success",
    "Pending Review": "badge-warning",
    "Exception": "badge-danger",
    "Calculated": "badge-primary",
}

KPI_CARDS = [
    {
        "label": "Total Metrics",
        "value": "60",
        "sub": "All metrics",
        "card_class": "kpi-card success",
        "bar_pct": 100,
    },
    {
        "label": "Calculated",
        "value": "60",
        "sub": "100% complete",
        "card_class": "kpi-card success",
        "bar_pct": 100,
    },
    {
        "label": "Reviewed",
        "value": "42",
        "sub": "70% of total",
        "card_class": "kpi-card",
        "bar_pct": 70,
    },
    {
        "label": "Pending Review",
        "value": "18",
        "sub": "30% of total",
        "card_class": "kpi-card warning",
        "bar_pct": 30,
    },
    {
        "label": "Exceptions",
        "value": "5",
        "sub": "Requires attention",
        "card_class": "kpi-card exception",
        "bar_pct": None,
    },
]

SECTIONS = [
    {"label": "All", "value": "all"},
    {"label": "Section A", "value": "Section A"},
    {"label": "Section B", "value": "Section B"},
    {"label": "Section 1", "value": "Section 1"},
    {"label": "Section 7", "value": "Section 7"},
]

FORMS = [
    {"label": "All", "value": "all"},
    {"label": "ADV", "value": "ADV"},
    {"label": "PF", "value": "PF"},
]

# ---------------------------------------------------------------------------
# Drawer style constants
# ---------------------------------------------------------------------------

_DRAWER_HIDDEN = {
    "display": "none",
    "position": "fixed",
    "top": "0",
    "right": "0",
    "width": "460px",
    "height": "100vh",
    "background": "#ffffff",
    "boxShadow": "-4px 0 24px rgba(0,0,0,0.15)",
    "zIndex": "1001",
    "overflowY": "auto",
    "padding": "0",
}
_DRAWER_VISIBLE = {**_DRAWER_HIDDEN, "display": "block"}

_OVL_HIDDEN = {
    "display": "none",
    "position": "fixed",
    "inset": "0",
    "background": "rgba(0,0,0,0.35)",
    "zIndex": "1000",
}
_OVL_VISIBLE = {**_OVL_HIDDEN, "display": "block"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _kpi_card(card):
    bar = (
        html.Div(
            html.Div(
                className="kpi-bar-fill",
                style={"width": f"{card['bar_pct']}%"},
            ),
            className="kpi-bar-track",
        )
        if card["bar_pct"] is not None
        else None
    )
    children = [
        html.Div(card["label"], className="kpi-label"),
        html.Div(card["value"], className="kpi-value"),
        html.Div(card["sub"], className="kpi-sub"),
    ]
    if bar:
        children.append(bar)
    return html.Div(children, className=card["card_class"])


def _dash_cell():
    return html.Td("—", style={"color": "var(--text-muted)"})


def _build_row(metric, i):
    is_exception = metric["status"] == "Exception"
    row_class = "row-exception" if is_exception else ""

    status_badge = html.Span(
        metric["status"],
        className=f"status-badge {STATUS_BADGE.get(metric['status'], 'badge-muted')}",
    )

    reviewer_cell = (
        html.Td(metric["reviewer"])
        if metric["reviewer"]
        else _dash_cell()
    )
    rev_date_cell = (
        html.Td(metric["rev_date"])
        if metric["rev_date"]
        else _dash_cell()
    )

    action_cell = html.Td(
        html.Div(
            [
                html.Button(
                    "View",
                    id={"type": "ms-view-btn", "index": i},
                    n_clicks=0,
                    className="action-link",
                    style={
                        "background": "none",
                        "border": "none",
                        "cursor": "pointer",
                        "color": "#1d4ed8",
                        "fontWeight": "500",
                        "fontSize": "12px",
                        "padding": "2px 7px",
                    },
                ),
                html.A(
                    "Trace",
                    href="/metric-traceability",
                    className="action-link",
                ),
            ],
            className="row",
            style={"gap": "12px"},
        )
    )

    return html.Tr(
        [
            html.Td(
                metric["id"],
                className="cell-primary",
                style={"fontFamily": "monospace"},
            ),
            html.Td(metric["name"]),
            html.Td(
                html.Span(metric["form"], className="status-badge badge-info")
            ),
            html.Td(metric["section"]),
            html.Td(
                metric["value"],
                style={"fontFamily": "monospace", "textAlign": "right"},
            ),
            html.Td(status_badge),
            reviewer_cell,
            rev_date_cell,
            action_cell,
        ],
        className=row_class,
    )


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

def layout():
    return html.Div(
        [
            # Page header
            html.Div(
                [
                    html.Div(
                        [
                            html.H1(
                                "Calculations – Metric Summary",
                                className="page-heading",
                            ),
                            html.P(
                                "All calculated metrics for the current filing. "
                                "Click any row to view traceability.",
                                className="page-subheading",
                            ),
                        ]
                    ),
                    html.Div(
                        [
                            html.Button(
                                "Export Metrics",
                                id="ms-export-btn",
                                className="btn btn-primary",
                            ),
                            dcc.Download(id="ms-download"),
                        ],
                        className="page-actions",
                    ),
                ],
                className="page-header",
            ),

            # Filter bar
            html.Div(
                [
                    html.Label("Filing Type", className="filter-label"),
                    dcc.Dropdown(
                        id="ms-form",
                        options=FORMS,
                        value="all",
                        clearable=False,
                        className="dash-dropdown",
                        style={"minWidth": "120px"},
                    ),
                    html.Label("Section", className="filter-label"),
                    dcc.Dropdown(
                        id="ms-section",
                        options=SECTIONS,
                        value="all",
                        clearable=False,
                        className="dash-dropdown",
                        style={"minWidth": "160px"},
                    ),
                    html.Label("Search", className="filter-label"),
                    dcc.Input(
                        id="ms-search",
                        type="text",
                        placeholder="Search metric ID or name...",
                        className="form-input",
                        debounce=True,
                        style={"minWidth": "220px"},
                    ),
                ],
                className="filter-bar",
            ),

            # KPI row
            html.Div(
                [_kpi_card(c) for c in KPI_CARDS],
                className="kpi-row",
                style={"marginBottom": "24px"},
            ),

            # Metric table
            html.Div(
                html.Table(
                    [
                        html.Thead(
                            html.Tr(
                                [
                                    html.Th("Metric ID"),
                                    html.Th("Metric Name"),
                                    html.Th("Form"),
                                    html.Th("Section"),
                                    html.Th("Calculated Value"),
                                    html.Th("Status"),
                                    html.Th("Reviewed By"),
                                    html.Th("Reviewed Date"),
                                    html.Th("Actions"),
                                ]
                            )
                        ),
                        html.Tbody(id="ms-table-body"),
                    ],
                    className="data-table",
                ),
                className="data-table-wrap",
            ),

            # Pagination
            html.Div(
                [
                    html.Span(
                        "Showing 10 of 60 metrics",
                        style={"color": "var(--text-secondary)", "fontSize": "13px"},
                    ),
                    html.Div(
                        [
                            html.Button("Prev", className="btn btn-sm btn-ghost"),
                            html.Button("Next", className="btn btn-sm btn-ghost"),
                        ],
                        className="row",
                        style={"gap": "8px"},
                    ),
                ],
                className="row-between",
                style={"marginTop": "16px"},
            ),

            html.Hr(className="divider"),

            # Note
            html.P(
                [
                    "Click 'Trace' on any metric to view full data lineage and business "
                    "rule breakdown. Calculations are performed by the Databricks Jobs "
                    "layer — no frontend calculation logic is applied.",
                ],
                style={"color": "var(--text-secondary)", "fontSize": "13px"},
            ),

            # View detail drawer overlay
            html.Div(id="ms-view-overlay", style=_OVL_HIDDEN),

            # View detail drawer
            html.Div(
                [
                    # Drawer header
                    html.Div(
                        [
                            html.Div(
                                id="ms-view-title",
                                style={
                                    "fontWeight": "700",
                                    "fontSize": "16px",
                                    "color": "#111827",
                                    "flex": "1",
                                },
                            ),
                            html.Button(
                                "✕",
                                id="ms-view-close",
                                n_clicks=0,
                                style={
                                    "background": "none",
                                    "border": "none",
                                    "cursor": "pointer",
                                    "fontSize": "18px",
                                    "color": "#6b7280",
                                    "padding": "0 4px",
                                    "lineHeight": "1",
                                },
                            ),
                        ],
                        style={
                            "display": "flex",
                            "alignItems": "center",
                            "padding": "24px 28px 20px",
                            "borderBottom": "1px solid #e5e7eb",
                            "position": "sticky",
                            "top": "0",
                            "background": "#ffffff",
                            "zIndex": "1",
                        },
                    ),
                    # Drawer body
                    html.Div(id="ms-view-body", style={"padding": "28px 28px 28px"}),
                ],
                id="ms-view-drawer",
                style=_DRAWER_HIDDEN,
            ),
        ]
    )


# ---------------------------------------------------------------------------
# Callbacks
# ---------------------------------------------------------------------------

@callback(
    Output("ms-table-body", "children"),
    Input("ms-form", "value"),
    Input("ms-section", "value"),
    Input("ms-search", "value"),
)
def update_table(form_filter, section_filter, search):
    rows = list(enumerate(METRICS))

    if form_filter and form_filter != "all":
        rows = [(i, r) for i, r in rows if r["form"] == form_filter]

    if section_filter and section_filter != "all":
        rows = [(i, r) for i, r in rows if r["section"] == section_filter]

    if search:
        q = search.lower()
        rows = [
            (i, r) for i, r in rows
            if q in r["id"].lower() or q in r["name"].lower()
        ]

    return [_build_row(r, i) for i, r in rows]


@callback(
    Output("ms-download", "data"),
    Input("ms-export-btn", "n_clicks"),
    prevent_initial_call=True,
)
def export_metrics(n_clicks):
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow([
        "Metric ID", "Metric Name", "Form", "Section",
        "Calculated Value", "Status", "Reviewed By", "Reviewed Date",
    ])
    for m in METRICS:
        writer.writerow([
            m["id"],
            m["name"],
            m["form"],
            m["section"],
            m["value"],
            m["status"],
            m["reviewer"] or "",
            m["rev_date"] or "",
        ])
    return dcc.send_string(buf.getvalue(), "metrics.csv")


@callback(
    Output("ms-view-drawer", "style"),
    Output("ms-view-overlay", "style"),
    Output("ms-view-title", "children"),
    Output("ms-view-body", "children"),
    Input({"type": "ms-view-btn", "index": ALL}, "n_clicks"),
    Input("ms-view-close", "n_clicks"),
    prevent_initial_call=True,
)
def toggle_view_drawer(view_clicks, close_clicks):
    triggered = ctx.triggered_id

    if triggered == "ms-view-close":
        return _DRAWER_HIDDEN, _OVL_HIDDEN, no_update, no_update

    if isinstance(triggered, dict) and triggered.get("type") == "ms-view-btn":
        # Ignore initialization fires when table re-renders due to filter changes
        if not view_clicks or not any(c and c > 0 for c in view_clicks):
            return no_update, no_update, no_update, no_update
        idx = triggered["index"]
        metric = METRICS[idx]
        badge_class = STATUS_BADGE.get(metric["status"], "badge-muted")

        title = f"{metric['id']} – {metric['name']}"

        body = html.Div(
            [
                html.Div(
                    [
                        html.Div("Form", className="filter-label"),
                        html.Div(
                            html.Span(metric["form"], className="status-badge badge-info"),
                            style={"marginTop": "4px"},
                        ),
                    ],
                    style={"marginBottom": "16px"},
                ),
                html.Div(
                    [
                        html.Div("Section", className="filter-label"),
                        html.Div(metric["section"], style={"marginTop": "4px"}),
                    ],
                    style={"marginBottom": "16px"},
                ),
                html.Div(
                    [
                        html.Div("Calculated Value", className="filter-label"),
                        html.Div(
                            metric["value"],
                            style={
                                "fontFamily": "monospace",
                                "marginTop": "4px",
                                "fontSize": "15px",
                                "fontWeight": "600",
                            },
                        ),
                    ],
                    style={"marginBottom": "16px"},
                ),
                html.Div(
                    [
                        html.Div("Status", className="filter-label"),
                        html.Div(
                            html.Span(
                                metric["status"],
                                className=f"status-badge {badge_class}",
                            ),
                            style={"marginTop": "4px"},
                        ),
                    ],
                    style={"marginBottom": "16px"},
                ),
                html.Div(
                    [
                        html.Div("Reviewed By", className="filter-label"),
                        html.Div(
                            metric["reviewer"] or "—",
                            style={"marginTop": "4px"},
                        ),
                    ],
                    style={"marginBottom": "16px"},
                ),
                html.Div(
                    [
                        html.Div("Reviewed Date", className="filter-label"),
                        html.Div(
                            metric["rev_date"] or "—",
                            style={"marginTop": "4px"},
                        ),
                    ],
                    style={"marginBottom": "20px"},
                ),
                html.Hr(className="divider"),
                html.A(
                    "View Full Traceability →",
                    href="/metric-traceability",
                    className="action-link",
                    style={"fontSize": "14px", "marginTop": "16px", "display": "inline-block"},
                ),
            ]
        )

        return _DRAWER_VISIBLE, _OVL_VISIBLE, title, body

    return no_update, no_update, no_update, no_update
