import dash
from dash import html, dcc, callback, Output, Input, State
import plotly.graph_objects as go

dash.register_page(__name__, path="/", name="Dashboard", title="Dashboard – Overview")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

YEAR_DATA = {
    "2024": {"reviewed": 42, "pending": 18, "exceptions": 5,  "total": 65},
    "2023": {"reviewed": 48, "pending":  7, "exceptions": 2,  "total": 57},
    "2022": {"reviewed": 50, "pending":  2, "exceptions": 1,  "total": 53},
}

TOTAL_METRICS = {"2024": 60, "2023": 60, "2022": 55}


def make_donut(d):
    fig = go.Figure(go.Pie(
        labels=["Reviewed", "Pending Review", "Exceptions"],
        values=[d["reviewed"], d["pending"], d["exceptions"]],
        hole=0.65,
        marker_colors=["#22c55e", "#f59e0b", "#ef4444"],
        textinfo="none",
        hovertemplate="%{label}: %{value}<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=10, b=10, l=10, r=10),
        height=260,
        showlegend=True,
        legend=dict(
            font=dict(color="#374151", size=12),
            bgcolor="rgba(0,0,0,0)",
            orientation="v",
            x=1.02, y=0.5,
        ),
        annotations=[dict(
            text=str(d["total"]),
            x=0.5, y=0.5,
            font=dict(size=32, color="#111827", family="inherit"),
            showarrow=False,
        )],
    )
    return fig


def make_kpi_cards(year_str):
    d = YEAR_DATA[year_str]
    total = TOTAL_METRICS.get(year_str, 60)
    reviewed_pct  = round(d["reviewed"]  / total * 100)
    pending_pct   = round(d["pending"]   / total * 100)

    def bar(pct, color):
        return html.Div(className="kpi-bar-track", children=[
            html.Div(className="kpi-bar-fill", style={"width": f"{pct}%", "background": color}),
        ])

    return [
        html.Div(className="kpi-card success", children=[
            html.Div("Total Metrics",      className="kpi-label"),
            html.Div(str(total),           className="kpi-value"),
            html.Div("All metrics loaded", className="kpi-sub"),
            bar(100, "#22c55e"),
        ]),
        html.Div(className="kpi-card success", children=[
            html.Div("Calculated Metrics", className="kpi-label"),
            html.Div(str(total),           className="kpi-value"),
            html.Div("100% calculated",    className="kpi-sub"),
            bar(100, "#22c55e"),
        ]),
        html.Div(className="kpi-card", children=[
            html.Div("Reviewed Metrics",           className="kpi-label"),
            html.Div(str(d["reviewed"]),            className="kpi-value"),
            html.Div(f"{reviewed_pct}% complete",  className="kpi-sub"),
            bar(reviewed_pct, "#3b82f6"),
        ]),
        html.Div(className="kpi-card warning", children=[
            html.Div("Pending Review",            className="kpi-label"),
            html.Div(str(d["pending"]),            className="kpi-value"),
            html.Div(f"{pending_pct}% of total",  className="kpi-sub"),
            bar(pending_pct, "#f59e0b"),
        ]),
        html.Div(className="kpi-card exception", children=[
            html.Div("Exceptions",        className="kpi-label"),
            html.Div(str(d["exceptions"]), className="kpi-value"),
            html.Div("Requires attention", className="kpi-sub"),
        ]),
    ]


def workflow_row(name, state, pct):
    if state == "completed":
        dot_cls   = "status-dot dot-success"
        badge_cls = "status-badge badge-success"
        bar_color = "#22c55e"
        label     = "Completed"
    elif state in ("in_progress", "pending"):
        dot_cls   = "status-dot dot-warning"
        badge_cls = "status-badge badge-warning"
        bar_color = "#f59e0b"
        label     = "In Progress" if state == "in_progress" else "Pending"
    else:
        dot_cls   = "status-dot dot-muted"
        badge_cls = "status-badge badge-muted"
        bar_color = "#4b5563"
        label     = "Not Started"

    return html.Div(className="workflow-row", children=[
        html.Span(className=dot_cls),
        html.Span(name, className="workflow-name"),
        html.Span(label, className=badge_cls),
        html.Div(className="wf-bar-track", style={"flex": "1", "margin": "0 8px"}, children=[
            html.Div(className="wf-bar-fill", style={"width": f"{pct}%", "background": bar_color}),
        ]),
        html.Span(f"{pct}%", style={"color": "#8896ae", "fontSize": "12px", "minWidth": "32px", "textAlign": "right"}),
    ])


def activity_badge(status):
    mapping = {
        "Completed":  ("badge-success",  "Completed"),
        "Exception":  ("badge-danger",   "Exception"),
        "Approved":   ("badge-primary",  "Approved"),
        "In Progress":("badge-info",     "In Progress"),
    }
    cls, label = mapping.get(status, ("badge-muted", status))
    return html.Span(label, className=f"status-badge {cls}")


ACTIVITY_ROWS = [
    ("PF Section A metric calculation completed", "Calculations",     "Aug 21, 2024", "Completed"),
    ("ADV metric PF1D flagged for exception",     "Review",           "Aug 20, 2024", "Exception"),
    ("PF Section B metrics approved by S. Rahman","Review",           "Aug 19, 2024", "Approved"),
    ("Data load from Investran completed",        "Data Management",  "Aug 18, 2024", "Completed"),
    ("Review cycle initiated by tax team",        "Review",           "Aug 17, 2024", "In Progress"),
]


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

def layout():
    return html.Div(children=[

        # Notification banner
        html.Div(className="notification-banner", children=[
            html.Span("You have 12 new notifications.", className="notif-text"),
            html.A("View all", href="#", className="notif-link"),
        ]),

        # Page header
        html.Div(className="page-header", children=[
            html.Div(children=[
                html.H1("Dashboard – Overview", className="page-heading"),
                html.P(
                    "Real-time summary of the FY2024 ADV & PF filing lifecycle",
                    className="page-subheading",
                ),
            ]),
            html.Div(className="page-actions", children=[
                html.Button("Refresh", id="btn-refresh", className="btn btn-ghost"),
                html.Button("Export", id="btn-export", className="btn btn-primary"),
                dcc.Download(id="download-dashboard"),
            ]),
        ]),

        # Filter bar
        html.Div(className="filter-bar", children=[
            html.Label("Filing Year", className="filter-label"),
            dcc.Dropdown(
                id="dd-year",
                options=[
                    {"label": "FY 2024", "value": "2024"},
                    {"label": "FY 2023", "value": "2023"},
                    {"label": "FY 2022", "value": "2022"},
                ],
                value="2024",
                clearable=False,
                style={"minWidth": "140px"},
            ),
            html.Div(className="filter-divider"),
            html.Label("Filing Type", className="filter-label"),
            dcc.Dropdown(
                id="dd-type",
                options=[
                    {"label": "ADV",     "value": "ADV"},
                    {"label": "PF",      "value": "PF"},
                    {"label": "ADV & PF","value": "ALL"},
                ],
                value="ALL",
                clearable=False,
                style={"minWidth": "160px"},
            ),
        ]),

        # KPI row (populated by callback)
        html.Div(id="kpi-row", className="kpi-row"),

        # Middle grid: donut + workflow
        html.Div(className="grid-2", style={"marginTop": "24px"}, children=[

            # Overall status – donut chart
            html.Div(className="panel-card", children=[
                html.H3("Overall Status", className="panel-title"),
                dcc.Graph(
                    id="donut-chart",
                    config={"displayModeBar": False},
                    style={"height": "260px"},
                ),
            ]),

            # Workflow status
            html.Div(className="panel-card", children=[
                html.H3("Workflow Status", className="panel-title"),
                html.Div(className="workflow-list", children=[
                    workflow_row("Data Load",        "completed",   100),
                    workflow_row("Calculation",      "completed",   100),
                    workflow_row("Review",           "in_progress",  70),
                    workflow_row("Approval",         "pending",       0),
                    workflow_row("Form Generation",  "not_started",   0),
                ]),
            ]),
        ]),

        # Recent activity table
        html.Div(className="panel-card", style={"marginTop": "24px"}, children=[
            html.H3("Recent Activity", className="panel-title"),
            html.Div(className="data-table-wrap", children=[
                html.Table(className="data-table", children=[
                    html.Thead(html.Tr([
                        html.Th("Event"),
                        html.Th("Module"),
                        html.Th("Date"),
                        html.Th("Status"),
                    ])),
                    html.Tbody([
                        html.Tr([
                            html.Td(event, className="cell-primary"),
                            html.Td(module),
                            html.Td(date),
                            html.Td(activity_badge(status)),
                        ])
                        for event, module, date, status in ACTIVITY_ROWS
                    ]),
                ]),
            ]),
        ]),
    ])


# ---------------------------------------------------------------------------
# Callbacks
# ---------------------------------------------------------------------------

@callback(
    Output("kpi-row",    "children"),
    Output("donut-chart", "figure"),
    Input("dd-year",  "value"),
    Input("dd-type",  "value"),
)
def update_dashboard(year, _filing_type):
    year = year or "2024"
    return make_kpi_cards(year), make_donut(YEAR_DATA[year])


@callback(
    Output("download-dashboard", "data"),
    Input("btn-export", "n_clicks"),
    prevent_initial_call=True,
)
def export_csv(n_clicks):
    csv_content = (
        "Event,Module,Date,Status\n"
        + "\n".join(
            f'"{e}","{m}","{d}","{s}"'
            for e, m, d, s in ACTIVITY_ROWS
        )
    )
    return dict(content=csv_content, filename="dashboard_activity.csv")
