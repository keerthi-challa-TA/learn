import dash
from dash import html, dcc, callback, Output, Input, State, dash_table

dash.register_page(__name__, path="/data-pull-review", name="Data Pull Review", title="Data Pull Review – Delta Table Preview")


# ---------------------------------------------------------------------------
# Mock data
# ---------------------------------------------------------------------------

DELTA_COLUMNS = [
    {"name": "Investor_ID",      "id": "Investor_ID"},
    {"name": "Investor_Name",    "id": "Investor_Name"},
    {"name": "Investor_Type",    "id": "Investor_Type"},
    {"name": "Fund_ID",          "id": "Fund_ID"},
    {"name": "Commitment_Amt",   "id": "Commitment_Amt"},
    {"name": "Currency",         "id": "Currency"},
    {"name": "Status",           "id": "Status"},
]

DELTA_DATA = [
    {"Investor_ID": "INV001", "Investor_Name": "ABC Pension Fund",      "Investor_Type": "LP", "Fund_ID": "FUND I", "Commitment_Amt": "100,000,000", "Currency": "USD", "Status": "Active"},
    {"Investor_ID": "INV002", "Investor_Name": "XYZ Capital Partners",  "Investor_Type": "GP", "Fund_ID": "FUND I", "Commitment_Amt":  "50,000,000", "Currency": "USD", "Status": "Active"},
    {"Investor_ID": "INV003", "Investor_Name": "LMN Foundation",        "Investor_Type": "LP", "Fund_ID": "FUND I", "Commitment_Amt":  "75,000,000", "Currency": "USD", "Status": "Active"},
    {"Investor_ID": "INV004", "Investor_Name": "QRS Family Office",     "Investor_Type": "LP", "Fund_ID": "FUND I", "Commitment_Amt":  "25,000,000", "Currency": "USD", "Status": "Active"},
    {"Investor_ID": "INV005", "Investor_Name": "TUV Holdings",          "Investor_Type": "LP", "Fund_ID": "FUND I", "Commitment_Amt":  "50,000,000", "Currency": "USD", "Status": "Active"},
]

QUALITY_CARDS = [
    ("Missing Values",    "0 flagged",              "badge-success"),
    ("Duplicate Records", "0 found",                "badge-success"),
    ("Invalid Values",    "0 detected",             "badge-success"),
    ("Unmapped Records",  "0",                      "badge-success"),
    ("Source Freshness",  "Current (last refresh 06:00 UTC)", "badge-info"),
]


# ---------------------------------------------------------------------------
# DataTable styling helpers
# ---------------------------------------------------------------------------

TABLE_STYLE_TABLE = {
    "overflowX":    "auto",
    "border":       "1px solid #e5e7eb",
    "borderRadius": "8px",
}

TABLE_STYLE_HEADER = {
    "backgroundColor": "#f9fafb",
    "color":           "#6b7280",
    "fontSize":        "11px",
    "fontWeight":      "600",
    "textTransform":   "uppercase",
    "letterSpacing":   "0.07em",
    "border":          "none",
}

TABLE_STYLE_CELL = {
    "backgroundColor": "#ffffff",
    "color":           "#374151",
    "fontSize":        "13px",
    "border":          "none",
    "borderBottom":    "1px solid #e5e7eb",
    "padding":         "10px 14px",
}

TABLE_STYLE_DATA_CONDITIONAL = [
    {
        "if":              {"row_index": "odd"},
        "backgroundColor": "#f9fafb",
    },
]


# ---------------------------------------------------------------------------
# Tab content builders
# ---------------------------------------------------------------------------

def tab_table_preview():
    return html.Div(id="tab-content-preview", children=[

        # Controls row above table
        html.Div(className="row row-between", style={"marginTop": "16px", "marginBottom": "12px", "flexWrap": "wrap", "gap": "12px"}, children=[
            html.Div(className="row", style={"gap": "12px", "alignItems": "center"}, children=[
                dcc.Dropdown(
                    options=[
                        {"label": "investran__investors",   "value": "investran__investors"},
                        {"label": "quilt__positions",       "value": "quilt__positions"},
                        {"label": "anduin__commitments",    "value": "anduin__commitments"},
                    ],
                    value="investran__investors",
                    clearable=False,
                    style={"minWidth": "220px"},
                ),
                html.Span("Last Loaded: 2024-08-21 06:00 UTC", style={"color": "#6b7280", "fontSize": "13px"}),
                html.Span("Records: --",                        style={"color": "#6b7280", "fontSize": "13px"}),
            ]),
            html.Button("View Data Lineage", className="btn btn-ghost btn-sm"),
        ]),

        # Values populate when connected to Databricks Delta tables
        dash_table.DataTable(
            id="delta-preview-table",
            columns=DELTA_COLUMNS,
            data=DELTA_DATA,
            page_size=10,
            filter_action="native",
            sort_action="native",
            style_table=TABLE_STYLE_TABLE,
            style_header=TABLE_STYLE_HEADER,
            style_cell=TABLE_STYLE_CELL,
            style_data_conditional=TABLE_STYLE_DATA_CONDITIONAL,
        ),

        # Info banner
        html.Div(className="info-banner", style={"marginTop": "12px"}, children=[
            html.Span(
                "Showing 1 to 5 of 45,678 records. Data is read-only. "
                "Connect to Databricks Delta tables to load live data.",
            ),
        ]),
    ])


def tab_data_quality():
    return html.Div(id="tab-content-quality", style={"display": "none"}, children=[
        html.Div(className="grid-2", style={"marginTop": "16px"}, children=[
            html.Div(className="panel-card", children=[
                html.Div(className="row row-between", children=[
                    html.Span(label, className="panel-title", style={"fontSize": "14px"}),
                    html.Span(value, className=f"status-badge {badge}"),
                ]),
            ])
            for label, value, badge in QUALITY_CARDS
        ]),
    ])


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

def layout():
    return html.Div(children=[

        # Page header
        html.Div(className="page-header", children=[
            html.Div(children=[
                html.H1("Data Pull Review – Delta Table Preview", className="page-heading"),
                html.P(
                    "Review data from Delta tables before calculations are performed",
                    className="page-subheading",
                ),
            ]),
        ]),

        # Filter bar
        html.Div(className="filter-bar", children=[
            html.Label("Source System", className="filter-label"),
            dcc.Dropdown(
                id="dpr-dd-source",
                options=[
                    {"label": "Investran",             "value": "Investran"},
                    {"label": "QUILT",                 "value": "QUILT"},
                    {"label": "Anduin",                "value": "Anduin"},
                    {"label": "Financial Statements",  "value": "Financial Statements"},
                    {"label": "All",                   "value": "All"},
                ],
                value="All",
                clearable=False,
                style={"minWidth": "190px"},
            ),
            html.Div(className="filter-divider"),
            html.Label("Delta Table", className="filter-label"),
            dcc.Dropdown(
                id="dpr-dd-table",
                options=[
                    {"label": "investran__investors",  "value": "investran__investors"},
                    {"label": "quilt__positions",      "value": "quilt__positions"},
                    {"label": "anduin__commitments",   "value": "anduin__commitments"},
                    {"label": "All",                   "value": "All"},
                ],
                value="All",
                clearable=False,
                style={"minWidth": "210px"},
            ),
            html.Div(className="filter-divider"),
            html.Label("Filing Year", className="filter-label"),
            dcc.Dropdown(
                id="dpr-dd-year",
                options=[
                    {"label": "2024", "value": "2024"},
                    {"label": "2023", "value": "2023"},
                ],
                value="2024",
                clearable=False,
                style={"minWidth": "100px"},
            ),
            html.Div(className="filter-divider"),
            html.Label("As-of Date", className="filter-label"),
            dcc.Input(
                id="dpr-input-date",
                type="text",
                value="2024-08-21",
                className="form-input",
                style={"width": "130px"},
            ),
            html.Button("Refresh", className="btn btn-ghost", style={"marginLeft": "8px"}),
        ]),

        # KPI row — values populate when connected to Databricks Delta tables
        html.Div(className="kpi-row", style={"marginTop": "20px"}, children=[
            html.Div(className="kpi-card", children=[
                html.Div("Total Tables",   className="kpi-label"),
                html.Div("0",              className="kpi-value"),
            ]),
            html.Div(className="kpi-card", children=[
                html.Div("Tables Loaded",  className="kpi-label"),
                html.Div("0",              className="kpi-value"),
            ]),
            html.Div(className="kpi-card", children=[
                html.Div("Records",        className="kpi-label"),
                html.Div("0",              className="kpi-value"),
            ]),
            html.Div(className="kpi-card", children=[
                html.Div("Data Quality Issues", className="kpi-label"),
                html.Div("0",                   className="kpi-value"),
            ]),
        ]),

        # Tabs
        html.Div(className="tab-bar", style={"marginTop": "24px"}, children=[
            html.Div("Table Preview", id="tab-btn-preview", className="tab-item tab-active"),
            html.Div("Data Quality",  id="tab-btn-quality", className="tab-item"),
        ]),

        dcc.Store(id="active-tab-dpr", data="preview"),

        tab_table_preview(),
        tab_data_quality(),
    ])


# ---------------------------------------------------------------------------
# Callbacks
# ---------------------------------------------------------------------------

@callback(
    Output("tab-btn-preview",      "className"),
    Output("tab-btn-quality",      "className"),
    Output("tab-content-preview",  "style"),
    Output("tab-content-quality",  "style"),
    Input("tab-btn-preview", "n_clicks"),
    Input("tab-btn-quality", "n_clicks"),
    State("active-tab-dpr",  "data"),
    prevent_initial_call=True,
)
def switch_tab(n_preview, n_quality, _active):
    from dash import ctx
    triggered = ctx.triggered_id
    if triggered == "tab-btn-quality":
        return (
            "tab-item",
            "tab-item tab-active",
            {"display": "none"},
            {"display": "block"},
        )
    return (
        "tab-item tab-active",
        "tab-item",
        {"display": "block"},
        {"display": "none"},
    )
