import dash
from dash import html, dcc, callback, Output, Input, State
import plotly.graph_objects as go

dash.register_page(__name__, path="/audit-history", name="Audit History", title="Audit History")

module_options = [
    {"label": "All", "value": "All"},
    {"label": "Data Management", "value": "Data Management"},
    {"label": "Mappings", "value": "Mappings"},
    {"label": "Calculations", "value": "Calculations"},
    {"label": "Review", "value": "Review"},
    {"label": "Form Generation", "value": "Form Generation"},
    {"label": "Email", "value": "Email"},
    {"label": "Admin", "value": "Admin"},
]

action_options = [
    {"label": "All", "value": "All"},
    {"label": "Upload", "value": "Upload"},
    {"label": "Calculate", "value": "Calculate"},
    {"label": "Approve", "value": "Approve"},
    {"label": "Reject", "value": "Reject"},
    {"label": "Override", "value": "Override"},
    {"label": "Generate", "value": "Generate"},
    {"label": "Send", "value": "Send"},
    {"label": "Configure", "value": "Configure"},
]

user_options = [
    {"label": "All", "value": "All"},
    {"label": "S. Rahman", "value": "S. Rahman"},
    {"label": "Tax Manager", "value": "Tax Manager"},
    {"label": "Tax Ops", "value": "Tax Ops"},
    {"label": "System", "value": "System"},
    {"label": "Finance", "value": "Finance"},
]

audit_rows = [
    {
        "datetime": "Aug 21, 2024 11:30 AM",
        "user": "S. Rahman",
        "module": "Review",
        "action": "Approve",
        "action_badge": "badge-success",
        "details": "Approved metric PF1A — Total Private Fund Assets. Value: $1,234,567,890",
        "source": "App",
        "source_badge": "badge-primary",
        "is_exception": False,
    },
    {
        "datetime": "Aug 21, 2024 11:20 AM",
        "user": "S. Rahman",
        "module": "Review",
        "action": "Comment",
        "action_badge": "badge-muted",
        "details": 'Added review comment on PF1A: "Timing difference from PCAP cut-off."',
        "source": "App",
        "source_badge": "badge-primary",
        "is_exception": False,
    },
    {
        "datetime": "Aug 21, 2024 10:45 AM",
        "user": "System",
        "module": "Calculations",
        "action": "Calculate",
        "action_badge": "badge-muted",
        "details": "PF Section A metric calculation job completed. 15 metrics updated.",
        "source": "Job",
        "source_badge": "badge-info",
        "is_exception": False,
    },
    {
        "datetime": "Aug 21, 2024 09:15 AM",
        "user": "Tax Ops",
        "module": "Data Management",
        "action": "Upload",
        "action_badge": "badge-muted",
        "details": "Uploaded Investran_FY2024_Q4.xlsx (Source: Investran, 4,521 records)",
        "source": "App",
        "source_badge": "badge-primary",
        "is_exception": False,
    },
    {
        "datetime": "Aug 20, 2024 04:30 PM",
        "user": "S. Rahman",
        "module": "Review",
        "action": "Reject",
        "action_badge": "badge-danger",
        "details": "Rejected PF1D — Gross Asset Value. Reason: Source data mismatch.",
        "source": "App",
        "source_badge": "badge-primary",
        "is_exception": True,
    },
    {
        "datetime": "Aug 20, 2024 02:00 PM",
        "user": "Tax Ops",
        "module": "Form Generation",
        "action": "Generate",
        "action_badge": "badge-muted",
        "details": "Generated PF workbook v2.1. Filing Year: 2024.",
        "source": "App",
        "source_badge": "badge-primary",
        "is_exception": False,
    },
    {
        "datetime": "Aug 20, 2024 09:00 AM",
        "user": "S. Rahman",
        "module": "Email",
        "action": "Send",
        "action_badge": "badge-muted",
        "details": "Distributed ADV_2024_v1.2.xlsx to Compliance Group (7 recipients).",
        "source": "App",
        "source_badge": "badge-primary",
        "is_exception": False,
    },
    {
        "datetime": "Aug 19, 2024 03:00 PM",
        "user": "System",
        "module": "Data Management",
        "action": "Refresh",
        "action_badge": "badge-muted",
        "details": "Delta table refresh completed. investran__investors: 45,678 records.",
        "source": "Job",
        "source_badge": "badge-info",
        "is_exception": False,
    },
    {
        "datetime": "Aug 18, 2024 11:00 AM",
        "user": "S. Rahman",
        "module": "Form Generation",
        "action": "Generate",
        "action_badge": "badge-muted",
        "details": "Generated ADV workbook v1.2. Filing Year: 2024.",
        "source": "App",
        "source_badge": "badge-primary",
        "is_exception": False,
    },
    {
        "datetime": "Aug 17, 2024 02:15 PM",
        "user": "Tax Ops",
        "module": "Mappings",
        "action": "Update",
        "action_badge": "badge-muted",
        "details": "Updated investor tagging: INV004 QRS Family Office → LP, US",
        "source": "App",
        "source_badge": "badge-primary",
        "is_exception": False,
    },
]


def make_filter_bar():
    return html.Div(
        [
            html.Span("Module", className="filter-label"),
            dcc.Dropdown(
                options=module_options,
                value="All",
                clearable=False,
                style={"minWidth": "180px"},
            ),
            html.Span("Action", className="filter-label", style={"marginLeft": "12px"}),
            dcc.Dropdown(
                options=action_options,
                value="All",
                clearable=False,
                style={"minWidth": "150px"},
            ),
            html.Span("User", className="filter-label", style={"marginLeft": "12px"}),
            dcc.Dropdown(
                options=user_options,
                value="All",
                clearable=False,
                style={"minWidth": "150px"},
            ),
            html.Span("From", className="filter-label", style={"marginLeft": "12px"}),
            dcc.Input(
                type="text",
                value="2024-07-22",
                placeholder="YYYY-MM-DD",
                className="form-input",
                style={"width": "130px"},
            ),
            html.Span("To", className="filter-label", style={"marginLeft": "8px"}),
            dcc.Input(
                type="text",
                value="2024-08-21",
                placeholder="YYYY-MM-DD",
                className="form-input",
                style={"width": "130px"},
            ),
            html.Button("Search", className="btn btn-primary", style={"marginLeft": "12px"}),
            html.Button("Export Audit", className="btn", style={"marginLeft": "8px"}),
        ],
        className="filter-bar",
        style={"display": "flex", "alignItems": "center", "flexWrap": "wrap", "gap": "6px", "marginBottom": "20px"},
    )


def make_kpi_row():
    kpis = [
        {"label": "Total Events", "value": "247", "sub": "Past 30 days", "cls": "kpi-card"},
        {"label": "User Actions", "value": "183", "sub": "74.1% of total", "cls": "kpi-card success"},
        {"label": "System Events", "value": "64", "sub": "25.9% of total", "cls": "kpi-card"},
        {"label": "Exceptions", "value": "3", "sub": "Requires attention", "cls": "kpi-card exception"},
    ]
    cards = []
    for k in kpis:
        cards.append(
            html.Div(
                [
                    html.Div(k["label"], className="kpi-label"),
                    html.Div(k["value"], className="kpi-value"),
                    html.Div(k["sub"], className="kpi-sub"),
                ],
                className=k["cls"],
            )
        )
    return html.Div(cards, className="kpi-row", style={"marginBottom": "20px"})


def make_audit_table():
    header = html.Tr([
        html.Th("Date & Time"),
        html.Th("User"),
        html.Th("Module"),
        html.Th("Action"),
        html.Th("Details"),
        html.Th("Source"),
    ])
    rows = []
    for r in audit_rows:
        row_cls = "row-exception" if r["is_exception"] else ""
        rows.append(
            html.Tr(
                [
                    html.Td(r["datetime"]),
                    html.Td(r["user"], className="cell-primary"),
                    html.Td(r["module"]),
                    html.Td(html.Span(r["action"], className=f"status-badge {r['action_badge']}")),
                    html.Td(r["details"], style={"maxWidth": "380px", "whiteSpace": "normal", "lineHeight": "1.4"}),
                    html.Td(html.Span(r["source"], className=f"status-badge {r['source_badge']}")),
                ],
                className=row_cls,
            )
        )
    return html.Div(
        html.Table(
            [html.Thead(header), html.Tbody(rows)],
            className="data-table",
        ),
        className="data-table-wrap",
    )


def make_detail_panel():
    return html.Div(
        html.Div(
            "Click any audit row to view full event details including before/after values and related filing context.",
            className="text-muted",
            style={"textAlign": "center", "padding": "24px 0", "fontSize": "14px"},
        ),
        className="panel-card",
        style={"marginTop": "16px"},
    )


def make_pagination():
    return html.Div(
        [
            html.Span(
                "Showing 10 of 247 audit events",
                className="text-muted",
                style={"fontSize": "13px"},
            ),
            html.Div(
                [
                    html.Button("Prev", className="btn btn-sm btn-ghost", disabled=True),
                    html.Button("Next", className="btn btn-sm btn-ghost", style={"marginLeft": "6px"}),
                ],
            ),
        ],
        className="row-between",
        style={"marginTop": "16px", "alignItems": "center"},
    )


layout = html.Div(
    [
        html.Div(
            [
                html.Div(
                    [
                        html.H1("Audit History", className="page-heading"),
                        html.Div(
                            "Complete traceability of all actions performed in the Quantum Filing Suite",
                            className="page-subheading",
                        ),
                    ]
                ),
            ],
            className="page-header",
        ),
        make_filter_bar(),
        make_kpi_row(),
        html.Div(
            [
                html.Div("Audit Log", className="panel-title"),
                make_audit_table(),
                make_pagination(),
            ],
            className="panel-card",
        ),
        make_detail_panel(),
    ]
)
