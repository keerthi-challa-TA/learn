import dash
from dash import html, dcc, callback, Output, Input, State

dash.register_page(__name__, path="/document-upload", name="Document Upload", title="Data Management – Document Upload")


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

UPLOADED_FILES = [
    {
        "name":       "Investran_FY2024_Q4.xlsx",
        "source":     "Investran",
        "type":       ".xlsx",
        "year":       "2024",
        "by":         "S. Rahman",
        "date":       "Aug 21, 2024",
        "status":     "Valid",
        "row_class":  "",
    },
    {
        "name":       "QUILT_Q3_2024.csv",
        "source":     "QUILT",
        "type":       ".csv",
        "year":       "2024",
        "by":         "S. Rahman",
        "date":       "Aug 20, 2024",
        "status":     "Failed",
        "row_class":  "row-exception",
    },
    {
        "name":       "Anduin_Investors_2024.xlsx",
        "source":     "Anduin",
        "type":       ".xlsx",
        "year":       "2024",
        "by":         "Tax Ops",
        "date":       "Aug 19, 2024",
        "status":     "Valid",
        "row_class":  "",
    },
    {
        "name":       "FinStmt_Q3_2024.xlsx",
        "source":     "Financial Statements",
        "type":       ".xlsx",
        "year":       "2024",
        "by":         "Finance",
        "date":       "Aug 18, 2024",
        "status":     "Valid",
        "row_class":  "",
    },
    {
        "name":       "Stakeholder_Input_2024.xlsx",
        "source":     "Stakeholder Input",
        "type":       ".xlsx",
        "year":       "2024",
        "by":         "Operations",
        "date":       "Aug 17, 2024",
        "status":     "Valid",
        "row_class":  "",
    },
]

HISTORY_ROWS = [
    ("Aug 14, 2024", "Investran_FY2024_Q3.xlsx",       "Investran",           "Valid",  "S. Rahman"),
    ("Aug 10, 2024", "QUILT_Q2_2024.csv",              "QUILT",               "Valid",  "Tax Ops"),
    ("Aug 05, 2024", "Anduin_Investors_H1_2024.xlsx",  "Anduin",              "Valid",  "Tax Ops"),
    ("Jul 31, 2024", "FinStmt_Q2_2024.xlsx",           "Financial Statements","Valid",  "Finance"),
    ("Jul 25, 2024", "QUILT_Q1_2024.csv",              "QUILT",               "Failed", "S. Rahman"),
]

VALIDATIONS = [
    ("val-ok",   "✓", "File format",            "Valid"),
    ("val-warn", "!", "Mandatory columns",       "Warning: 'Investor_ID' missing in QUILT_Q3_2024.csv"),
    ("val-ok",   "✓", "Duplicate records",       "No duplicates found"),
    ("val-warn", "!", "Data quality checks",     "2 warnings detected"),
    ("val-ok",   "✓", "File size",               "Valid"),
    ("val-ok",   "✓", "Filing year",             "Valid: FY 2024 confirmed"),
    ("val-ok",   "✓", "Source identification",   "Valid: QUILT identified"),
]


# ---------------------------------------------------------------------------
# Sub-components
# ---------------------------------------------------------------------------

def file_actions(status):
    if status == "Valid":
        return [
            html.A("Preview",  href="#", className="action-link"),
            html.A("Download", href="#", className="action-link"),
            html.A("Delete",   href="#", className="action-link danger"),
        ]
    return [
        html.A("Preview",         href="#", className="action-link"),
        html.A("View Validation", href="#", className="action-link"),
    ]


def file_table_row(f):
    badge_cls = "badge-success" if f["status"] == "Valid" else "badge-danger"
    return html.Tr(className=f["row_class"], children=[
        html.Td(f["name"],   className="cell-primary"),
        html.Td(f["source"]),
        html.Td(f["type"]),
        html.Td(f["year"]),
        html.Td(f["by"]),
        html.Td(f["date"]),
        html.Td(html.Span(f["status"], className=f"status-badge {badge_cls}")),
        html.Td(html.Div(file_actions(f["status"]), className="row", style={"gap": "12px"})),
    ])


def history_table_row(date, fname, source, status, by):
    badge_cls = "badge-success" if status == "Valid" else "badge-danger"
    return html.Tr([
        html.Td(date),
        html.Td(fname, className="cell-primary"),
        html.Td(source),
        html.Td(html.Span(status, className=f"status-badge {badge_cls}")),
        html.Td(by),
    ])


# ---------------------------------------------------------------------------
# Tab content builders
# ---------------------------------------------------------------------------

def tab_upload_files():
    return html.Div(id="tab-content-upload", children=[

        # Upload zone (styled div — no backend)
        html.Div(className="upload-zone", children=[
            html.Div("↑", className="upload-icon"),
            html.Div("Drag and drop files here", className="upload-title"),
            html.Div("or click to browse",        className="upload-sub"),
            html.Div(".xlsx  .csv  .txt",          className="upload-formats"),
            html.Button("Browse Files", className="btn btn-primary", style={"marginTop": "12px"}),
        ]),

        # Validation checks
        html.H3("Upload Validations", className="section-title", style={"marginTop": "24px"}),
        html.Div(className="validation-list", children=[
            html.Div(className=f"validation-row {cls}", children=[
                html.Span(icon, className="validation-icon"),
                html.Span(name, className="validation-name"),
                html.Span(msg,  className="validation-msg"),
            ])
            for cls, icon, name, msg in VALIDATIONS
        ]),

        # Validation summary
        html.Div(className="panel-card grid-2", style={"marginTop": "24px"}, children=[
            html.Div(className="kpi-row", style={"gap": "12px"}, children=[
                html.Div(className="kpi-card", children=[
                    html.Div("Total Files",  className="kpi-label"),
                    html.Div("5",            className="kpi-value"),
                ]),
                html.Div(className="kpi-card success", children=[
                    html.Div("Valid Files",  className="kpi-label"),
                    html.Div("4",            className="kpi-value"),
                ]),
                html.Div(className="kpi-card exception", children=[
                    html.Div("Files with Issues", className="kpi-label"),
                    html.Div("1",                  className="kpi-value"),
                ]),
            ]),
            html.Div(className="stack", style={"gap": "10px", "justifyContent": "center"}, children=[
                html.Button("View Validation Details", className="btn btn-primary btn-sm"),
                html.A("View Upload History", href="#", className="action-link"),
            ]),
        ]),

        # Uploaded files table
        html.H3("Uploaded Files", className="section-title", style={"marginTop": "24px"}),
        html.Div(className="data-table-wrap", children=[
            html.Table(className="data-table", children=[
                html.Thead(html.Tr([
                    html.Th("File Name"),
                    html.Th("Source"),
                    html.Th("File Type"),
                    html.Th("Filing Year"),
                    html.Th("Uploaded By"),
                    html.Th("Upload Date"),
                    html.Th("Status"),
                    html.Th("Actions"),
                ])),
                html.Tbody([file_table_row(f) for f in UPLOADED_FILES]),
            ]),
        ]),
    ])


def tab_upload_history():
    return html.Div(id="tab-content-history", style={"display": "none"}, children=[
        html.Div(className="data-table-wrap", style={"marginTop": "16px"}, children=[
            html.Table(className="data-table", children=[
                html.Thead(html.Tr([
                    html.Th("Date"),
                    html.Th("File"),
                    html.Th("Source"),
                    html.Th("Status"),
                    html.Th("Uploaded By"),
                ])),
                html.Tbody([
                    history_table_row(date, fname, source, status, by)
                    for date, fname, source, status, by in HISTORY_ROWS
                ]),
            ]),
        ]),
    ])


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

def layout():
    return html.Div(children=[

        # Page header
        html.Div(className="page-header", children=[
            html.H1("Data Management – Document Upload", className="page-heading"),
        ]),

        # Alert banner
        html.Div(className="alert-banner", children=[
            html.Span(
                "1 file failed validation. Please fix the issues and re-upload. "
                "Reason: Mandatory column 'Investor_ID' is missing from QUILT_Q3_2024.csv",
                className="notif-text",
            ),
        ]),

        # Tab bar
        html.Div(className="tab-bar", style={"marginTop": "20px"}, children=[
            html.Div("Upload Files",    id="tab-btn-upload",  className="tab-item tab-active"),
            html.Div("Upload History",  id="tab-btn-history", className="tab-item"),
        ]),

        # Tab panels
        dcc.Store(id="active-tab-du", data="upload"),
        tab_upload_files(),
        tab_upload_history(),
    ])


# ---------------------------------------------------------------------------
# Callbacks
# ---------------------------------------------------------------------------

@callback(
    Output("tab-btn-upload",      "className"),
    Output("tab-btn-history",     "className"),
    Output("tab-content-upload",  "style"),
    Output("tab-content-history", "style"),
    Input("tab-btn-upload",  "n_clicks"),
    Input("tab-btn-history", "n_clicks"),
    State("active-tab-du",   "data"),
    prevent_initial_call=True,
)
def switch_tab(n_upload, n_history, _active):
    from dash import ctx
    triggered = ctx.triggered_id
    if triggered == "tab-btn-history":
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
