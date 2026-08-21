import dash
from dash import html, dcc, callback, Output, Input, State, ALL, ctx, no_update

dash.register_page(
    __name__,
    path="/notifications",
    name="Notifications",
    title="Notifications",
)

# ---------------------------------------------------------------------------
# Initial data
# ---------------------------------------------------------------------------

NOTIFICATIONS_INIT = [
    {"id": 0, "status": "New",         "message": "3 investors are unmapped and will be excluded from PF Section 7B calculations.", "type": "Unmapped Tagging",       "source": "Anduin",    "date": "Aug 21, 2024", "actions": ["View", "Resolve", "Assign"]},
    {"id": 1, "status": "New",         "message": "5 portfolio companies lack Level 1 classification.",                             "type": "Unmapped Classification", "source": "Investran", "date": "Aug 21, 2024", "actions": ["View", "Resolve"]},
    {"id": 2, "status": "New",         "message": "2 investors have no funding group assignment.",                                   "type": "Unmapped Mapping",        "source": "Anduin",    "date": "Aug 20, 2024", "actions": ["View", "Resolve"]},
    {"id": 3, "status": "In Progress", "message": "Data quality issue: 2 warnings in QUILT_Q3_2024.csv upload.",                   "type": "Data Issue",              "source": "QUILT",     "date": "Aug 20, 2024", "actions": ["View", "Resolve"]},
    {"id": 4, "status": "New",         "message": "Review pending for 18 metrics. Reviewer: S. Rahman.",                           "type": "Review Pending",          "source": "System",    "date": "Aug 19, 2024", "actions": ["View", "Assign"]},
    {"id": 5, "status": "New",         "message": "Exception detected in PF1B Total Leverage metric.",                             "type": "Calculation Exception",   "source": "System",    "date": "Aug 19, 2024", "actions": ["View", "Resolve"]},
    {"id": 6, "status": "Read",        "message": "ADV Section 1 form generated successfully.",                                    "type": "Generation Complete",     "source": "System",    "date": "Aug 18, 2024", "actions": ["View"]},
]

RECIPIENTS_INIT = [
    {"name": "Compliance Team",    "emails": "compliance@quantum.com\ntax@quantum.com", "types": ["All Notifications"],                                "active": True},
    {"name": "Data Owners",        "emails": "data@quantum.com",                        "types": ["Unmapped Tagging", "Data Issues"],                  "active": True},
    {"name": "Business Operations","emails": "ops@quantum.com",                         "types": ["Unmapped Tagging", "Unmapped Classification"],      "active": True},
]

NOTIFICATION_TYPE_OPTIONS = [
    {"label": "Unmapped Tagging",       "value": "Unmapped Tagging"},
    {"label": "Unmapped Classification","value": "Unmapped Classification"},
    {"label": "Data Issues",            "value": "Data Issues"},
    {"label": "Review Pending",         "value": "Review Pending"},
    {"label": "All Notifications",      "value": "All Notifications"},
]

STATUS_BADGE = {
    "New":         "badge-danger",
    "In Progress": "badge-warning",
    "Read":        "badge-muted",
}

TAB_ITEMS = [
    {"label": "All",        "value": "all"},
    {"label": "Unmapped",   "value": "Unmapped"},
    {"label": "Data Issues","value": "Data Issue"},
    {"label": "System",     "value": "System"},
]

# ---------------------------------------------------------------------------
# Drawer / overlay styles (same pattern as other pages)
# ---------------------------------------------------------------------------

_DRAWER_HIDDEN = {
    "display": "none", "position": "fixed", "top": "0", "right": "0",
    "width": "460px", "height": "100vh", "background": "#ffffff",
    "boxShadow": "-4px 0 24px rgba(0,0,0,0.15)", "zIndex": "1001",
    "overflowY": "auto", "padding": "0",
}
_DRAWER_VISIBLE = {**_DRAWER_HIDDEN, "display": "block"}
_OVL_HIDDEN = {
    "display": "none", "position": "fixed", "inset": "0",
    "background": "rgba(0,0,0,0.35)", "zIndex": "1000",
}
_OVL_VISIBLE = {**_OVL_HIDDEN, "display": "block"}

_LABEL_STYLE = {"fontWeight": "600", "fontSize": "13px", "color": "var(--text-primary)", "marginBottom": "6px"}
_INPUT_STYLE = {
    "width": "100%", "padding": "8px 12px", "border": "1px solid #d1d5db",
    "borderRadius": "6px", "fontSize": "14px", "outline": "none",
    "boxSizing": "border-box",
}

# ---------------------------------------------------------------------------
# Row builders
# ---------------------------------------------------------------------------

def _build_action_buttons(notif):
    buttons = []
    for action in notif["actions"]:
        nid = notif["id"]
        if action == "Resolve":
            buttons.append(
                html.Button(
                    "Resolve",
                    id={"type": "notif-resolve", "index": nid},
                    n_clicks=0,
                    className="action-link danger",
                    style={"background": "none", "border": "none", "cursor": "pointer",
                           "padding": "0", "font": "inherit"},
                )
            )
        elif action == "View":
            buttons.append(
                html.Button(
                    "View",
                    id={"type": "notif-view", "index": nid},
                    n_clicks=0,
                    className="action-link",
                    style={"background": "none", "border": "none", "cursor": "pointer",
                           "padding": "0", "font": "inherit"},
                )
            )
        elif action == "Assign":
            buttons.append(
                html.Button(
                    "Assign",
                    id={"type": "notif-assign", "index": nid},
                    n_clicks=0,
                    className="action-link",
                    style={"background": "none", "border": "none", "cursor": "pointer",
                           "padding": "0", "font": "inherit"},
                )
            )
    return html.Div(buttons, className="row", style={"gap": "12px"})


def _build_notif_row(notif):
    is_read = notif["status"] == "Read"
    row_style = {"opacity": "0.6"} if is_read else {}

    status_badge = html.Span(
        notif["status"],
        className=f"status-badge {STATUS_BADGE.get(notif['status'], 'badge-muted')}",
    )
    type_badge = html.Span(notif["type"], className="status-badge badge-info")

    return html.Tr(
        [
            html.Td(status_badge),
            html.Td(notif["message"], style={"maxWidth": "360px"}),
            html.Td(type_badge),
            html.Td(notif["source"]),
            html.Td(notif["date"]),
            html.Td(_build_action_buttons(notif)),
        ],
        style=row_style,
    )


def _build_recipient_row(group, i):
    status_badge = (
        html.Span("Active",   className="status-badge badge-success")
        if group["active"]
        else html.Span("Inactive", className="status-badge badge-muted")
    )
    types_str = ", ".join(group["types"]) if isinstance(group["types"], list) else group["types"]
    emails_preview = group["emails"].split("\n")[0] if group["emails"] else ""
    email_count    = len([e for e in group["emails"].split("\n") if e.strip()])
    desc_text      = f"{email_count} recipient{'s' if email_count != 1 else ''}"

    return html.Div(
        [
            html.Div(
                [
                    html.Span(group["name"],   style={"fontWeight": "600", "color": "var(--text-primary)"}),
                    html.Span(desc_text,       style={"color": "var(--text-secondary)", "fontSize": "13px"}),
                    html.Span(types_str,       style={"color": "var(--text-secondary)", "fontSize": "13px"}),
                ],
                className="row",
                style={"gap": "24px", "alignItems": "center"},
            ),
            html.Div(
                [
                    status_badge,
                    html.Button(
                        "Edit",
                        id={"type": "notif-rec-edit", "index": i},
                        n_clicks=0,
                        className="btn btn-sm btn-ghost",
                    ),
                ],
                className="row",
                style={"gap": "12px"},
            ),
        ],
        className="row-between",
        style={"padding": "12px 0", "borderBottom": "1px solid var(--border)"},
    )


def _recipients_drawer():
    """Returns the slide-in drawer for Add / Edit recipient."""
    return html.Div(
        [
            # Drawer header
            html.Div(
                [
                    html.Span("Recipient Group", style={"fontWeight": "700", "fontSize": "16px"}),
                    html.Button(
                        "×",
                        id="notif-drawer-close",
                        n_clicks=0,
                        style={
                            "background": "none", "border": "none", "fontSize": "22px",
                            "cursor": "pointer", "color": "#6b7280", "lineHeight": "1",
                        },
                    ),
                ],
                style={
                    "display": "flex", "justifyContent": "space-between", "alignItems": "center",
                    "padding": "20px 24px 16px", "borderBottom": "1px solid #e5e7eb",
                    "position": "sticky", "top": "0", "background": "#ffffff", "zIndex": "1",
                },
            ),

            # Drawer body
            html.Div(
                [
                    # Recipient Group Name
                    html.Div(
                        [
                            html.Label("Recipient Group Name", style=_LABEL_STYLE),
                            dcc.Input(
                                id="notif-drawer-name",
                                type="text",
                                placeholder="e.g. Compliance Team",
                                style=_INPUT_STYLE,
                            ),
                        ],
                        style={"marginBottom": "18px"},
                    ),

                    # Email Addresses
                    html.Div(
                        [
                            html.Label("Email Addresses", style=_LABEL_STYLE),
                            html.P("Enter one email address per line.",
                                   style={"fontSize": "12px", "color": "#6b7280", "margin": "0 0 6px 0"}),
                            dcc.Textarea(
                                id="notif-drawer-emails",
                                placeholder="user@example.com\nanother@example.com",
                                style={**_INPUT_STYLE, "minHeight": "90px", "resize": "vertical"},
                            ),
                        ],
                        style={"marginBottom": "18px"},
                    ),

                    # Notification Types
                    html.Div(
                        [
                            html.Label("Notification Types", style=_LABEL_STYLE),
                            dcc.Checklist(
                                id="notif-drawer-types",
                                options=NOTIFICATION_TYPE_OPTIONS,
                                value=[],
                                labelStyle={"display": "flex", "alignItems": "center", "gap": "8px",
                                            "marginBottom": "8px", "fontSize": "14px", "cursor": "pointer"},
                                inputStyle={"marginRight": "0", "cursor": "pointer"},
                            ),
                        ],
                        style={"marginBottom": "18px"},
                    ),

                    # Active toggle
                    html.Div(
                        [
                            html.Label("Active", style=_LABEL_STYLE),
                            dcc.RadioItems(
                                id="notif-drawer-active",
                                options=[{"label": "Yes", "value": True}, {"label": "No", "value": False}],
                                value=True,
                                labelStyle={"display": "inline-flex", "alignItems": "center",
                                            "gap": "6px", "marginRight": "20px",
                                            "fontSize": "14px", "cursor": "pointer"},
                                inputStyle={"cursor": "pointer"},
                            ),
                        ],
                        style={"marginBottom": "24px"},
                    ),

                    # Save / Cancel buttons
                    html.Div(
                        [
                            html.Button(
                                "Save",
                                id="notif-drawer-save",
                                n_clicks=0,
                                className="btn btn-primary",
                                style={"minWidth": "100px"},
                            ),
                            html.Button(
                                "Cancel",
                                id="notif-drawer-cancel",
                                n_clicks=0,
                                className="btn",
                                style={"minWidth": "100px"},
                            ),
                        ],
                        className="row",
                        style={"gap": "12px"},
                    ),
                ],
                style={"padding": "20px 24px"},
            ),
        ],
        id="notif-recipients-drawer",
        style=_DRAWER_HIDDEN,
    )


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

def layout():
    return html.Div(
        [
            # Stores
            dcc.Store(id="notif-store",            data=NOTIFICATIONS_INIT),
            dcc.Store(id="notif-recipients-store", data=RECIPIENTS_INIT),
            dcc.Store(id="notif-rec-selected-idx", data=None),

            # Overlay
            html.Div(id="notif-drawer-overlay", style=_OVL_HIDDEN, n_clicks=0),

            # Slide-in drawer
            _recipients_drawer(),

            # Toast / feedback banner
            html.Div(id="notif-toast", style={"display": "none"},
                     className="alert-banner"),

            # Page header
            html.Div(
                [
                    html.Div(
                        [
                            html.H1("Notifications", className="page-heading"),
                            html.P(
                                "System alerts, data issues, and workflow notifications",
                                className="page-subheading",
                            ),
                        ]
                    ),
                    html.Div(
                        [
                            html.Button(
                                "Add Recipients",
                                id="notif-add-recipients",
                                n_clicks=0,
                                className="btn btn-primary",
                            ),
                            html.Button(
                                "Mark All Read",
                                id="notif-mark-all-read",
                                n_clicks=0,
                                className="btn",
                            ),
                        ],
                        className="page-actions",
                    ),
                ],
                className="page-header",
            ),

            # Tabs
            html.Div(
                html.Div(
                    [
                        html.Button(
                            [
                                html.Span(item["label"]),
                            ],
                            id={"type": "notif-tab", "index": item["value"]},
                            className="tab-item tab-active" if item["value"] == "all" else "tab-item",
                            n_clicks=0,
                        )
                        for item in TAB_ITEMS
                    ],
                    className="tab-bar",
                ),
                className="row-between",
                style={"marginBottom": "16px"},
            ),

            # Notification table
            html.Div(
                html.Table(
                    [
                        html.Thead(
                            html.Tr(
                                [
                                    html.Th("Status"),
                                    html.Th("Message"),
                                    html.Th("Type"),
                                    html.Th("Source"),
                                    html.Th("Date"),
                                    html.Th("Actions"),
                                ]
                            )
                        ),
                        html.Tbody(id="notif-table-body"),
                    ],
                    className="data-table",
                ),
                className="data-table-wrap",
            ),

            html.Hr(className="divider"),

            # Recipients list
            html.Div(
                [
                    html.H2("Notification Recipients", className="panel-title"),
                    html.Div(id="notif-recipients-list"),
                ],
                className="panel-card",
                style={"marginTop": "24px"},
            ),

            html.Hr(className="divider"),

            # Disclaimer
            html.Div(
                "Email delivery is not active in this environment. "
                "Configure the email service to enable automatic notifications.",
                className="alert-banner",
            ),
        ]
    )


# ---------------------------------------------------------------------------
# Callbacks
# ---------------------------------------------------------------------------

# 1. Mark All Read → update notif-store
@callback(
    Output("notif-store", "data"),
    Input("notif-mark-all-read", "n_clicks"),
    Input({"type": "notif-resolve", "index": ALL}, "n_clicks"),
    State("notif-store", "data"),
    prevent_initial_call=True,
)
def update_notif_store(mark_all_clicks, resolve_clicks, notifications):
    triggered = ctx.triggered_id

    if triggered == "notif-mark-all-read":
        return [{**n, "status": "Read"} for n in notifications]

    # Pattern-match resolve: triggered is a dict {"type": "notif-resolve", "index": <id>}
    if isinstance(triggered, dict) and triggered.get("type") == "notif-resolve":
        nid = triggered["index"]
        return [
            {**n, "status": "Read"} if n["id"] == nid else n
            for n in notifications
        ]

    return no_update


# 2. Tab click + store change → render notification table rows
@callback(
    Output("notif-table-body", "children"),
    Input({"type": "notif-tab", "index": ALL}, "n_clicks"),
    Input("notif-store", "data"),
    prevent_initial_call=False,
)
def update_notif_table(n_clicks_list, notifications):
    active_tab = "all"

    triggered = ctx.triggered_id
    if isinstance(triggered, dict) and triggered.get("type") == "notif-tab":
        active_tab = triggered["index"]

    rows = notifications or []
    if active_tab == "Unmapped":
        rows = [r for r in rows if "Unmapped" in r["type"]]
    elif active_tab == "Data Issue":
        rows = [r for r in rows if "Data Issue" in r["type"]]
    elif active_tab == "System":
        rows = [r for r in rows if r["source"] == "System"]

    return [_build_notif_row(r) for r in rows]


# 3. Store change → render recipient rows
@callback(
    Output("notif-recipients-list", "children"),
    Input("notif-recipients-store", "data"),
    prevent_initial_call=False,
)
def render_recipients(recipients):
    groups = recipients or []
    return [_build_recipient_row(g, i) for i, g in enumerate(groups)]


# 4a. Open drawer: Add Recipients button OR Edit button
@callback(
    Output("notif-recipients-drawer", "style",  allow_duplicate=True),
    Output("notif-drawer-overlay",    "style",  allow_duplicate=True),
    Output("notif-rec-selected-idx",  "data",   allow_duplicate=True),
    Output("notif-drawer-name",       "value",  allow_duplicate=True),
    Output("notif-drawer-emails",     "value",  allow_duplicate=True),
    Output("notif-drawer-types",      "value",  allow_duplicate=True),
    Output("notif-drawer-active",     "value",  allow_duplicate=True),
    Input("notif-add-recipients",                         "n_clicks"),
    Input({"type": "notif-rec-edit", "index": ALL},       "n_clicks"),
    State("notif-recipients-store", "data"),
    prevent_initial_call=True,
)
def open_drawer(add_clicks, edit_clicks, recipients):
    triggered = ctx.triggered_id

    # Add Recipients → open blank
    if triggered == "notif-add-recipients":
        return _DRAWER_VISIBLE, _OVL_VISIBLE, None, "", "", [], True

    # Edit button → open pre-filled
    if isinstance(triggered, dict) and triggered.get("type") == "notif-rec-edit":
        # Ignore initialization fires where no button has actually been clicked
        if not edit_clicks or not any(c and c > 0 for c in edit_clicks):
            return no_update, no_update, no_update, no_update, no_update, no_update, no_update
        idx = triggered["index"]
        groups = recipients or []
        if 0 <= idx < len(groups):
            g = groups[idx]
            types = g["types"] if isinstance(g["types"], list) else [g["types"]]
            return (_DRAWER_VISIBLE, _OVL_VISIBLE, idx,
                    g["name"], g["emails"], types, g["active"])
        return _DRAWER_VISIBLE, _OVL_VISIBLE, None, "", "", [], True

    return no_update, no_update, no_update, no_update, no_update, no_update, no_update


# 4b. Close drawer: X button, overlay click, Cancel, or after Save
@callback(
    Output("notif-recipients-drawer", "style",  allow_duplicate=True),
    Output("notif-drawer-overlay",    "style",  allow_duplicate=True),
    Output("notif-rec-selected-idx",  "data",   allow_duplicate=True),
    Output("notif-drawer-name",       "value",  allow_duplicate=True),
    Output("notif-drawer-emails",     "value",  allow_duplicate=True),
    Output("notif-drawer-types",      "value",  allow_duplicate=True),
    Output("notif-drawer-active",     "value",  allow_duplicate=True),
    Input("notif-drawer-close",   "n_clicks"),
    Input("notif-drawer-overlay", "n_clicks"),
    Input("notif-drawer-cancel",  "n_clicks"),
    Input("notif-drawer-save",    "n_clicks"),
    prevent_initial_call=True,
)
def close_drawer(close_clicks, ovl_clicks, cancel_clicks, save_clicks):
    return _DRAWER_HIDDEN, _OVL_HIDDEN, None, "", "", [], True


# 5. Save drawer → append or update recipients-store
@callback(
    Output("notif-recipients-store", "data"),
    Input("notif-drawer-save", "n_clicks"),
    State("notif-drawer-name",       "value"),
    State("notif-drawer-emails",     "value"),
    State("notif-drawer-types",      "value"),
    State("notif-drawer-active",     "value"),
    State("notif-rec-selected-idx",  "data"),
    State("notif-recipients-store",  "data"),
    prevent_initial_call=True,
)
def save_recipient(n_clicks, name, emails, types, active, selected_idx, recipients):
    if not n_clicks:
        return no_update

    name   = (name   or "").strip()
    emails = (emails or "").strip()
    types  = types or []

    if not name:
        return no_update

    new_group = {"name": name, "emails": emails, "types": types, "active": bool(active)}
    groups = list(recipients or [])

    if selected_idx is not None and 0 <= selected_idx < len(groups):
        groups[selected_idx] = new_group
    else:
        groups.append(new_group)

    return groups


# 6. View button → show toast
@callback(
    Output("notif-toast", "children"),
    Output("notif-toast", "style"),
    Input({"type": "notif-view",   "index": ALL}, "n_clicks"),
    Input({"type": "notif-assign", "index": ALL}, "n_clicks"),
    State("notif-store", "data"),
    prevent_initial_call=True,
)
def handle_view_assign(view_clicks, assign_clicks, notifications):
    triggered = ctx.triggered_id
    if not isinstance(triggered, dict):
        return no_update, no_update

    nid    = triggered["index"]
    action = triggered.get("type", "")

    notif = next((n for n in (notifications or []) if n["id"] == nid), None)
    if notif is None:
        return no_update, no_update

    if action == "notif-view":
        msg = f"Viewing: {notif['message']}"
    elif action == "notif-assign":
        msg = f"Assign action triggered for notification from {notif['source']} ({notif['date']})."
    else:
        return no_update, no_update

    return msg, {"display": "block"}
