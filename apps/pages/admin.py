import dash
from dash import html, dcc, callback, Output, Input, State
import plotly.graph_objects as go

dash.register_page(__name__, path="/admin", name="Admin", title="Admin – Notification Recipients")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def badge(text, cls):
    return html.Span(text, className=f"status-badge {cls}")


def action_link(text, danger=False, href="#"):
    cls = "action-link danger" if danger else "action-link"
    return html.A(text, href=href, className=cls)


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

RECIPIENT_ROWS = [
    ("Compliance Team",     "ADV & PF compliance reviewers",      "7", "All Notifications"),
    ("Data Owners",         "Source data owners and stewards",    "4", "Unmapped / Data Issues"),
    ("Business Operations", "Tax operations team",                "5", "Unmapped / Mapping"),
    ("Tax Directors",       "Senior tax leadership",              "2", "Exceptions / Approvals"),
    ("System Admins",       "Technical administrators",           "2", "System Events"),
]

PERMISSION_MATRIX = [
    ("Dashboard",          "Read/Write", "Read",       "Read",    "Read"),
    ("Data Management",    "Admin",      "Read/Write",  "Read",    "Read"),
    ("Mappings",           "Admin",      "Read/Write",  "Read",    "Read"),
    ("Notifications",      "Admin",      "Read/Write",  "Read",    "Read"),
    ("Calculations",       "Read",       "Read",        "Read",    "Read"),
    ("Review & Feedback",  "Admin",      "Write",       "Approve", "Read"),
    ("Form Generation",    "Admin",      "Write",       "Read",    "Read"),
    ("Email Distribution", "Admin",      "Write",       "Read",    "Read"),
    ("Audit History",      "Admin",      "Read",        "Read",    "Read"),
]

PERM_BADGE = {
    "Admin":      "badge-danger",
    "Read/Write": "badge-primary",
    "Approve":    "badge-success",
    "Write":      "badge-info",
    "Read":       "badge-muted",
}

NOTIFICATION_TYPES = [
    "Unmapped Tagging",
    "Unmapped Classification",
    "Unmapped Funding Group",
    "Data Quality Issue",
    "Calculation Exception",
    "Review Pending",
    "Generation Complete",
]


# ---------------------------------------------------------------------------
# Tab 1 – Notification Recipients
# ---------------------------------------------------------------------------

def build_recipients_tab():
    # Table rows
    rows = []
    for name, desc, count, mapped in RECIPIENT_ROWS:
        rows.append(html.Tr([
            html.Td(name, className="cell-primary"),
            html.Td(desc),
            html.Td(count),
            html.Td(mapped),
            html.Td(badge("Active", "badge-success")),
            html.Td(html.Div([
                action_link("Edit"),
                action_link("Delete", danger=True),
                action_link("View"),
            ], className="row", style={"gap": "10px"})),
        ]))

    recipients_table = html.Div(
        html.Table([
            html.Thead(html.Tr([
                html.Th("Group Name"),
                html.Th("Description"),
                html.Th("Recipients"),
                html.Th("Mapped To"),
                html.Th("Status"),
                html.Th("Actions"),
            ])),
            html.Tbody(rows),
        ], className="data-table"),
        className="data-table-wrap",
        style={"marginTop": "16px"},
    )

    # Notification type selector (uses dcc.Checklist — html.Input not available in Dash 4)
    checkbox_items = dcc.Checklist(
        options=[{"label": f"  {t}", "value": t} for t in NOTIFICATION_TYPES],
        value=[],
        labelStyle={"display": "flex", "alignItems": "center", "fontSize": "13px",
                    "color": "#111827", "cursor": "pointer", "gap": "6px"},
        inputStyle={"accentColor": "#3b82f6"},
        style={"display": "grid", "gridTemplateColumns": "1fr 1fr 1fr", "gap": "8px"},
    )

    # Collapsible add-group panel
    add_panel = html.Details([
        html.Summary(
            html.Div([
                html.Div(
                    "Configure New Recipient Group",
                    style={"fontWeight": "600", "color": "#111827", "fontSize": "15px"},
                ),
                html.Div(
                    "Fill in the group details below.",
                    style={"color": "#6b7280", "fontSize": "13px", "marginTop": "2px"},
                ),
            ]),
            style={"cursor": "pointer", "listStyle": "none", "WebkitAppearance": "none"},
        ),
        html.Div([
            html.Div([
                html.Div([
                    html.Label("Group Name", className="form-label"),
                    dcc.Input(
                        type="text",
                        className="form-input",
                        placeholder="Enter group name",
                        style={"width": "100%"},
                    ),
                ], className="form-group"),
                html.Div([
                    html.Label("Description", className="form-label"),
                    dcc.Input(
                        type="text",
                        className="form-input",
                        placeholder="Enter description",
                        style={"width": "100%"},
                    ),
                ], className="form-group"),
            ], className="grid-2"),
            html.Div([
                html.Label("Recipients", className="form-label"),
                dcc.Input(
                    type="text",
                    className="form-input",
                    placeholder="Enter email addresses, comma-separated",
                    style={"width": "100%"},
                ),
            ], className="form-group"),
            html.Div([
                html.Label("Notification Types", className="form-label"),
                html.Div(checkbox_items, style={"marginTop": "8px"}),
            ], className="form-group"),
            html.Div([
                html.Button("Save Group", className="btn btn-primary"),
                html.Button("Cancel", className="btn btn-ghost"),
            ], className="row", style={"gap": "10px", "marginTop": "16px"}),
        ], style={"marginTop": "16px"}),
    ], className="panel-card", id="add-group-panel", style={"marginTop": "20px"})

    return html.Div([
        html.Div([
            html.Div("Recipient Groups", className="section-title", style={"margin": "0"}),
            html.Button("Add Recipient Group", className="btn btn-primary"),
        ], className="row-between"),
        recipients_table,
        add_panel,
    ], id="recipients-content")


# ---------------------------------------------------------------------------
# Tab 2 – Roles & Permissions
# ---------------------------------------------------------------------------

def build_roles_tab():
    rows = []
    for module, adm, ops, rev, comp in PERMISSION_MATRIX:
        rows.append(html.Tr([
            html.Td(module, className="cell-primary"),
            html.Td(badge(adm,  PERM_BADGE.get(adm,  "badge-muted"))),
            html.Td(badge(ops,  PERM_BADGE.get(ops,  "badge-muted"))),
            html.Td(badge(rev,  PERM_BADGE.get(rev,  "badge-muted"))),
            html.Td(badge(comp, PERM_BADGE.get(comp, "badge-muted"))),
        ]))

    roles_table = html.Div(
        html.Table([
            html.Thead(html.Tr([
                html.Th("Module"),
                html.Th("Admin"),
                html.Th("Operations"),
                html.Th("Reviewer"),
                html.Th("Compliance"),
            ])),
            html.Tbody(rows),
        ], className="data-table"),
        className="data-table-wrap",
        style={"marginTop": "16px"},
    )

    return html.Div([
        html.Div("Role Permissions Matrix", className="section-title"),
        html.Div(
            "Permissions are managed at the platform level. "
            "Contact your system administrator to modify role assignments.",
            style={"color": "#6b7280", "fontSize": "13px", "marginBottom": "16px"},
        ),
        roles_table,
    ], id="roles-content", style={"display": "none"})


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

layout = html.Div([
    dcc.Store(id="admin-tab", data="recipients"),

    # Page header
    html.Div([
        html.H1("Admin – Configuration", className="page-heading"),
        html.P(
            "Manage notification recipients and role-based access permissions",
            className="page-subheading",
        ),
    ], className="page-header"),

    # Tab bar
    html.Div([
        html.Div(
            "Notification Recipients",
            id="tab-recipients-btn",
            className="tab-item tab-active",
            n_clicks=0,
        ),
        html.Div(
            "Roles & Permissions",
            id="tab-roles-btn",
            className="tab-item",
            n_clicks=0,
        ),
    ], className="tab-bar"),

    # Tab content (both rendered; toggled via callback)
    build_recipients_tab(),
    build_roles_tab(),
])


# ---------------------------------------------------------------------------
# Callbacks
# ---------------------------------------------------------------------------

@callback(
    Output("admin-tab", "data"),
    Output("tab-recipients-btn", "className"),
    Output("tab-roles-btn", "className"),
    Input("tab-recipients-btn", "n_clicks"),
    Input("tab-roles-btn", "n_clicks"),
    prevent_initial_call=True,
)
def switch_tab(n_recipients, n_roles):
    ctx = dash.callback_context
    if not ctx.triggered:
        return "recipients", "tab-item tab-active", "tab-item"
    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if triggered_id == "tab-recipients-btn":
        return "recipients", "tab-item tab-active", "tab-item"
    return "roles", "tab-item", "tab-item tab-active"


@callback(
    Output("recipients-content", "style"),
    Output("roles-content", "style"),
    Input("admin-tab", "data"),
)
def show_tab_content(tab):
    if tab == "recipients":
        return {"display": "block"}, {"display": "none"}
    return {"display": "none"}, {"display": "block"}
