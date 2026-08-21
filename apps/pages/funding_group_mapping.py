import dash
from dash import html, dcc, callback, Output, Input, State, ALL, ctx, no_update
import io
import csv

dash.register_page(
    __name__,
    path="/funding-group-mapping",
    name="Funding Group Mapping",
    title="Mapping – Funding Group Mapping",
)

# ── Initial data — history embedded per row ───────────────────────────────────
ROWS_INIT = [
    {"investor": "ABC Pension Fund",     "inv_id": "INV001", "group": "Group 1 – Domestic LP",  "status": "Mapped",   "updated": "Aug 18, 2024", "updated_by": "S. Rahman", "history": [{"date": "Aug 18, 2024", "by": "S. Rahman", "action": "Group updated", "detail": "Group 1 – Domestic LP"}]},
    {"investor": "XYZ Capital Partners", "inv_id": "INV002", "group": "Group 2 – GP Affiliate", "status": "Mapped",   "updated": "Aug 18, 2024", "updated_by": "S. Rahman", "history": [{"date": "Aug 18, 2024", "by": "S. Rahman", "action": "Group assigned", "detail": "Group 2 – GP Affiliate"}]},
    {"investor": "LMN Foundation",       "inv_id": "INV003", "group": "Group 1 – Domestic LP",  "status": "Mapped",   "updated": "Aug 17, 2024", "updated_by": "Tax Ops",   "history": [{"date": "Aug 17, 2024", "by": "Tax Ops",   "action": "Group updated", "detail": "Group 1 – Domestic LP"}]},
    {"investor": "QRS Family Office",    "inv_id": "INV004", "group": "Group 3 – Family Office", "status": "Mapped",  "updated": "Aug 16, 2024", "updated_by": "Tax Ops",   "history": [{"date": "Aug 16, 2024", "by": "Tax Ops",   "action": "Group assigned", "detail": "Group 3 – Family Office"}]},
    {"investor": "TUV Holdings",         "inv_id": "INV005", "group": None, "status": "Unmapped", "updated": None, "updated_by": None, "history": []},
    {"investor": "Meridian Capital",     "inv_id": "INV006", "group": None, "status": "Unmapped", "updated": None, "updated_by": None, "history": []},
]

FUNDING_GROUPS = [
    "Group 1 – Domestic LP",
    "Group 2 – GP Affiliate",
    "Group 3 – Family Office",
    "Group 4 – International LP",
    "Group 5 – Co-Invest",
]

TOTAL_INVESTORS = 245

# ── Style constants ────────────────────────────────────────────────────────────
_MUTED          = {"color": "#9ca3af"}
_DRAWER_HIDDEN  = {"display": "none",  "position": "fixed", "top": "0", "right": "0",
                   "width": "460px",   "height": "100vh",   "background": "#ffffff",
                   "boxShadow": "-4px 0 24px rgba(0,0,0,0.15)", "zIndex": "1001",
                   "overflowY": "auto", "padding": "0"}
_DRAWER_VISIBLE = {**_DRAWER_HIDDEN, "display": "block"}
_OVL_HIDDEN     = {"display": "none",  "position": "fixed", "inset": "0",
                   "background": "rgba(0,0,0,0.35)", "zIndex": "1000"}
_OVL_VISIBLE    = {**_OVL_HIDDEN, "display": "block"}
_HIST_HIDDEN    = {"display": "none",  "position": "fixed", "top": "50%", "left": "50%",
                   "transform": "translate(-50%,-50%)", "width": "480px",
                   "maxHeight": "70vh", "background": "#ffffff", "borderRadius": "10px",
                   "boxShadow": "0 8px 32px rgba(0,0,0,0.18)", "zIndex": "1002",
                   "overflowY": "auto", "padding": "0"}
_HIST_VISIBLE   = {**_HIST_HIDDEN, "display": "block"}
_SHOW           = {"display": "block"}
_HIDE           = {"display": "none"}

_TAB_ON  = {"padding": "6px 16px", "border": "1px solid #3b82f6", "borderRadius": "5px",
            "fontSize": "12.5px", "cursor": "pointer", "fontWeight": "600",
            "background": "#3b82f6", "color": "#ffffff"}
_TAB_OFF = {"padding": "6px 16px", "border": "1px solid #e5e7eb", "borderRadius": "5px",
            "fontSize": "12.5px", "cursor": "pointer", "fontWeight": "500",
            "background": "#f8fafc", "color": "#6b7280"}


# ── Row helpers ───────────────────────────────────────────────────────────────

def _d(val):
    return val if val else html.Span("—", style=_MUTED)


def _build_row(row, idx):
    unmapped = row["status"] == "Unmapped"

    if unmapped:
        group_cell      = html.Td(_d(None))
        updated_cell    = html.Td(_d(None))
        updated_by_cell = html.Td(_d(None))
        action_cell     = html.Td(
            html.Button(
                "Assign Group",
                id={"type": "fgm-assign-btn", "index": idx},
                n_clicks=0,
                style={"background": "#eff6ff", "border": "1px solid #bfdbfe",
                       "color": "#1d4ed8", "fontWeight": "600", "fontSize": "12px",
                       "padding": "4px 12px", "borderRadius": "4px", "cursor": "pointer"},
            )
        )
    else:
        group_cell      = html.Td(row["group"])
        updated_cell    = html.Td(_d(row["updated"]))
        updated_by_cell = html.Td(_d(row["updated_by"]))
        action_cell     = html.Td(
            html.Div([
                html.Button(
                    "Edit",
                    id={"type": "fgm-edit-btn", "index": idx},
                    n_clicks=0,
                    style={"background": "none", "border": "none", "cursor": "pointer",
                           "color": "#1d4ed8", "fontWeight": "500",
                           "fontSize": "12px", "padding": "2px 7px"},
                ),
                html.Button(
                    "History",
                    id={"type": "fgm-hist-btn", "index": idx},
                    n_clicks=0,
                    style={"background": "none", "border": "none", "cursor": "pointer",
                           "color": "#6b7280", "fontWeight": "500",
                           "fontSize": "12px", "padding": "2px 7px"},
                ),
            ], className="row", style={"gap": "6px"})
        )

    return html.Tr(
        className="row-unmapped" if unmapped else "",
        children=[
            html.Td(row["investor"], className="cell-primary"),
            html.Td(row["inv_id"], style={"color": "#6b7280", "fontFamily": "monospace"}),
            group_cell,
            html.Td(html.Span(
                row["status"],
                className="status-badge " + ("badge-warning" if unmapped else "badge-success"),
            )),
            updated_cell,
            updated_by_cell,
            action_cell,
        ],
    )


def _filter_rows(rows, search, status_filter):
    search = (search or "").strip().lower()
    out = []
    for i, row in enumerate(rows):
        if search and search not in row["investor"].lower() and search not in row["inv_id"].lower():
            continue
        if status_filter and status_filter != "all" and row["status"] != status_filter:
            continue
        out.append((i, row))
    return out


def _make_selector_opts(rows):
    return [
        {"label": f"{row['investor']}  ({row['inv_id']})", "value": i}
        for i, row in enumerate(rows)
    ]


def _hist_entry(h):
    return html.Div(
        className="row-between",
        style={"padding": "10px 12px", "borderRadius": "6px",
               "border": "1px solid #e5e7eb", "marginBottom": "8px",
               "background": "#f8fafc"},
        children=[
            html.Div([
                html.Div(h["action"],
                         style={"fontWeight": "600", "fontSize": "13px", "color": "#111827"}),
                html.Div(h["detail"],
                         style={"fontSize": "12px", "color": "#6b7280", "marginTop": "2px"}),
            ]),
            html.Div([
                html.Div(h["date"],
                         style={"fontSize": "12px", "color": "#6b7280", "textAlign": "right"}),
                html.Div(f"by {h['by']}",
                         style={"fontSize": "11px", "color": "#9ca3af",
                                "textAlign": "right", "marginTop": "2px"}),
            ]),
        ],
    )


# ── Layout ────────────────────────────────────────────────────────────────────

def layout():
    unmapped_count = sum(1 for r in ROWS_INIT if r["status"] == "Unmapped")
    selector_opts  = _make_selector_opts(ROWS_INIT)

    return html.Div([
        dcc.Store(id="fgm-rows-store",    data=ROWS_INIT),
        dcc.Store(id="fgm-selected-idx",  data=None),
        dcc.Download(id="fgm-download"),

        html.Div(id="fgm-overlay", style=_OVL_HIDDEN),

        # ── Drawer ────────────────────────────────────────────────────────────
        html.Div(id="fgm-drawer", style=_DRAWER_HIDDEN, children=[
            # Header
            html.Div(
                className="row-between",
                style={"padding": "20px 24px 16px",
                       "borderBottom": "1px solid #e5e7eb", "background": "#f8fafc"},
                children=[
                    html.Div([
                        html.Div(id="fgm-drawer-title",
                                 style={"fontWeight": "700", "fontSize": "15px",
                                        "color": "#111827"}),
                        html.Div(id="fgm-drawer-sub",
                                 style={"fontSize": "12px", "color": "#6b7280",
                                        "marginTop": "2px"}),
                    ]),
                    html.Button("✕", id="fgm-close", n_clicks=0,
                                style={"background": "none", "border": "none",
                                       "fontSize": "18px", "color": "#6b7280",
                                       "cursor": "pointer", "padding": "4px 8px",
                                       "borderRadius": "4px"}),
                ],
            ),

            # Body
            html.Div(style={"padding": "20px 24px"}, children=[
                html.Div(id="fgm-save-msg", style={"marginBottom": "12px"}),

                # Mode toggle (shown only when opened from top button)
                html.Div(id="fgm-mode-wrap", style=_HIDE, children=[
                    html.Div("Mode", className="form-label",
                             style={"marginBottom": "6px"}),
                    html.Div(className="row", style={"gap": "6px", "marginBottom": "16px"},
                             children=[
                                 html.Button("Edit Existing", id="fgm-mode-existing",
                                             n_clicks=0, style=_TAB_ON),
                                 html.Button("Add New Investor", id="fgm-mode-new",
                                             n_clicks=0, style=_TAB_OFF),
                             ]),
                ]),

                # Selector (Edit Existing mode — top button)
                html.Div(id="fgm-selector-wrap", style=_HIDE, children=[
                    html.Div(className="form-group", style={"marginBottom": "16px"}, children=[
                        html.Label("Select Investor", className="form-label"),
                        dcc.Dropdown(
                            id="fgm-investor-selector",
                            options=selector_opts,
                            placeholder="Search and select an investor…",
                            clearable=True,
                            className="dash-dropdown",
                            style={"width": "100%"},
                        ),
                    ]),
                ]),

                # New investor inputs (Add New Investor mode)
                html.Div(id="fgm-new-investor-wrap", style=_HIDE, children=[
                    html.Div(
                        className="grid-2",
                        style={"gap": "12px", "marginBottom": "14px"},
                        children=[
                            html.Div(className="form-group", children=[
                                html.Label("Investor Name", className="form-label"),
                                dcc.Input(id="fgm-new-name", type="text",
                                          placeholder="Full legal name…",
                                          className="form-input",
                                          style={"width": "100%"}),
                            ]),
                            html.Div(className="form-group", children=[
                                html.Label("Investor ID", className="form-label"),
                                dcc.Input(id="fgm-new-id", type="text",
                                          placeholder="e.g. INV007",
                                          className="form-input",
                                          style={"width": "100%"}),
                            ]),
                        ],
                    ),
                ]),

                # Static display (row button opens)
                html.Div(id="fgm-static-wrap", style=_HIDE, children=[
                    html.Div("Investor", className="form-label",
                             style={"marginBottom": "4px"}),
                    html.Div(id="fgm-investor-display",
                             style={"padding": "8px 12px", "background": "#f8fafc",
                                    "border": "1px solid #e5e7eb", "borderRadius": "5px",
                                    "fontSize": "13px", "color": "#111827",
                                    "fontWeight": "600", "marginBottom": "4px"}),
                    html.Div(id="fgm-investor-id-display",
                             style={"fontSize": "11px", "color": "#6b7280",
                                    "fontFamily": "monospace", "marginBottom": "16px"}),
                ]),

                # Funding group dropdown
                html.Div(className="form-group", style={"marginBottom": "20px"}, children=[
                    html.Label("Funding Group", className="form-label",
                               style={"marginBottom": "8px", "display": "block"}),
                    html.P(
                        "Select the funding group for reporting and aggregation:",
                        style={"fontSize": "12px", "color": "#6b7280", "marginBottom": "10px"},
                    ),
                    dcc.Dropdown(
                        id="fgm-group-dropdown",
                        options=[{"label": g, "value": g} for g in FUNDING_GROUPS],
                        placeholder="Select a funding group…",
                        clearable=True,
                        className="dash-dropdown",
                        style={"width": "100%"},
                    ),
                ]),

                html.Div(className="form-group", style={"marginBottom": "16px"}, children=[
                    html.Label("Updated By", className="form-label"),
                    dcc.Input(id="fgm-updated-by", type="text",
                              placeholder="Your name…",
                              className="form-input", style={"width": "100%"}),
                ]),

                html.Div(style={"height": "1px", "background": "#e5e7eb", "margin": "20px 0"}),
                html.Div(className="row", style={"gap": "10px", "justifyContent": "flex-end"},
                         children=[
                    html.Button("Cancel", id="fgm-cancel", n_clicks=0, className="btn btn-ghost"),
                    html.Button("Save Mapping", id="fgm-save", n_clicks=0,
                                className="btn btn-primary"),
                ]),
            ]),
        ]),

        # ── History modal ─────────────────────────────────────────────────────
        html.Div(id="fgm-hist-modal", style=_HIST_HIDDEN, children=[
            html.Div(
                className="row-between",
                style={"padding": "18px 22px 14px",
                       "borderBottom": "1px solid #e5e7eb", "background": "#f8fafc"},
                children=[
                    html.Div(id="fgm-hist-title",
                             style={"fontWeight": "700", "fontSize": "14px",
                                    "color": "#111827"}),
                    html.Button("✕", id="fgm-hist-close", n_clicks=0,
                                style={"background": "none", "border": "none",
                                       "fontSize": "18px", "color": "#6b7280",
                                       "cursor": "pointer", "padding": "4px 8px",
                                       "borderRadius": "4px"}),
                ],
            ),
            html.Div(id="fgm-hist-body", style={"padding": "16px 22px"}),
        ]),

        # ── Info banner ───────────────────────────────────────────────────────
        html.Div(
            "Funding group mappings support reporting fund and reporting group "
            "calculations for PF and ADV submissions.",
            className="info-banner",
        ),

        # ── Alert banner (unmapped count) ─────────────────────────────────────
        html.Div(className="alert-banner", children=[
            html.Span(id="fgm-unmapped-banner",
                      children=(f"{unmapped_count} investor{'s have' if unmapped_count != 1 else ' has'} "
                                "no funding group assignment. "
                                "These investors will be excluded from aggregated calculations.")),
            html.A("Configure notifications", href="/notifications",
                   className="notif-link", style={"marginLeft": "12px"}),
        ]),

        # ── Page header ───────────────────────────────────────────────────────
        html.Div(className="page-header", children=[
            html.Div([
                html.H1("Mapping – Funding Group Mapping", className="page-heading"),
                html.P(
                    "Map investors to funding groups used for reporting and aggregation",
                    className="page-subheading",
                ),
            ]),
            html.Div(className="page-actions", children=[
                html.Button("Add / Edit Mapping", id="fgm-add-top", n_clicks=0,
                            className="btn btn-primary"),
                html.Button("Bulk Mapping", className="btn btn-ghost"),
                html.Button("Export", id="fgm-export-btn", n_clicks=0,
                            className="btn btn-ghost"),
            ]),
        ]),

        # ── Filter bar ────────────────────────────────────────────────────────
        html.Div(className="filter-bar", children=[
            dcc.Input(
                id="fgm-search", type="text",
                placeholder="Search by investor name or ID...",
                debounce=True, className="form-input",
                style={"minWidth": "220px", "flex": "1"},
            ),
            html.Div(className="filter-divider"),
            html.Label("Status", className="filter-label"),
            dcc.Dropdown(
                id="fgm-status",
                options=[
                    {"label": "All",      "value": "all"},
                    {"label": "Mapped",   "value": "Mapped"},
                    {"label": "Unmapped", "value": "Unmapped"},
                ],
                value="all", clearable=False,
                className="dash-dropdown", style={"minWidth": "140px"},
            ),
        ]),

        # ── Table ─────────────────────────────────────────────────────────────
        html.Div(className="data-table-wrap", children=[
            html.Table(className="data-table", children=[
                html.Thead(html.Tr([
                    html.Th("Investor Name"),
                    html.Th("Investor ID"),
                    html.Th("Funding Group"),
                    html.Th("Status"),
                    html.Th("Last Updated"),
                    html.Th("Updated By"),
                    html.Th("Actions"),
                ])),
                html.Tbody(id="fgm-table-body"),
            ]),
        ]),

        # ── Pagination row ────────────────────────────────────────────────────
        html.Div(className="row-between", style={"marginTop": "14px"}, children=[
            html.Span(id="fgm-count",
                      style={"color": "#6b7280", "fontSize": "12.5px"}),
            html.Div(className="row", style={"gap": "8px"}, children=[
                html.Button("Prev", className="btn btn-ghost btn-sm"),
                html.Button("Next", className="btn btn-ghost btn-sm"),
            ]),
        ]),
    ])


# ── Callbacks ─────────────────────────────────────────────────────────────────

# 1. Render table + update count + banner
@callback(
    Output("fgm-table-body",       "children"),
    Output("fgm-count",            "children"),
    Output("fgm-unmapped-banner",  "children"),
    Input("fgm-rows-store",  "data"),
    Input("fgm-search",      "value"),
    Input("fgm-status",      "value"),
)
def update_table(rows, search, status_filter):
    results = _filter_rows(rows, search, status_filter)
    table_rows = [_build_row(row, i) for i, row in results]
    if not table_rows:
        table_rows = [html.Tr(html.Td(
            "No investors match the current filters.",
            colSpan=7,
            style={"textAlign": "center", "padding": "32px", "color": "#9ca3af"},
        ))]
    shown      = len(results)
    is_default = (not search and (not status_filter or status_filter == "all"))
    count = (f"Showing {shown} of {TOTAL_INVESTORS} investors" if is_default
             else f"Showing {shown} filtered result{'s' if shown != 1 else ''}")
    unmapped_n = sum(1 for r in rows if r["status"] == "Unmapped")
    if unmapped_n:
        banner = (f"{unmapped_n} investor{'s have' if unmapped_n != 1 else ' has'} "
                  "no funding group assignment. "
                  "These investors will be excluded from aggregated calculations.")
    else:
        banner = "All investors have a funding group assignment."
    return table_rows, count, banner


# 2. Refresh selector options when store changes
@callback(
    Output("fgm-investor-selector", "options"),
    Input("fgm-rows-store", "data"),
)
def refresh_selector(rows):
    return _make_selector_opts(rows)


# 3. Mode toggle — Edit Existing / Add New Investor
@callback(
    Output("fgm-mode-existing",      "style"),
    Output("fgm-mode-new",           "style"),
    Output("fgm-selector-wrap",      "style"),
    Output("fgm-new-investor-wrap",  "style"),
    Output("fgm-investor-selector",  "value"),
    Output("fgm-new-name",           "value"),
    Output("fgm-new-id",             "value"),
    Output("fgm-group-dropdown",     "value", allow_duplicate=True),
    Input("fgm-mode-existing", "n_clicks"),
    Input("fgm-mode-new",      "n_clicks"),
    prevent_initial_call=True,
)
def switch_mode(ec, nc):
    if ctx.triggered_id == "fgm-mode-new":
        return _TAB_OFF, _TAB_ON, _HIDE, _SHOW, None, "", "", None
    return _TAB_ON, _TAB_OFF, _SHOW, _HIDE, None, "", "", None


# 4. Pre-fill group when existing investor selected from dropdown
@callback(
    Output("fgm-group-dropdown", "value",    allow_duplicate=True),
    Output("fgm-updated-by",     "value",    allow_duplicate=True),
    Output("fgm-drawer-sub",     "children", allow_duplicate=True),
    Input("fgm-investor-selector", "value"),
    State("fgm-rows-store", "data"),
    prevent_initial_call=True,
)
def prefill_from_selector(idx, rows):
    if idx is None:
        return None, "", "Select an investor, then choose their funding group."
    row = rows[int(idx)]
    sub = (f"Last updated: {row['updated']}" if row["updated"]
           else "No mapping history — new entry.")
    return row["group"], row.get("updated_by") or "", sub


# 5. Main drawer controller — open, close, save
@callback(
    Output("fgm-drawer",             "style"),
    Output("fgm-overlay",            "style"),
    Output("fgm-drawer-title",       "children"),
    Output("fgm-drawer-sub",         "children"),
    # section visibility
    Output("fgm-mode-wrap",          "style"),
    Output("fgm-selector-wrap",      "style",  allow_duplicate=True),
    Output("fgm-static-wrap",        "style"),
    Output("fgm-new-investor-wrap",  "style",  allow_duplicate=True),
    # field values
    Output("fgm-investor-display",   "children"),
    Output("fgm-investor-id-display","children"),
    Output("fgm-investor-selector",  "value",  allow_duplicate=True),
    Output("fgm-new-name",           "value",  allow_duplicate=True),
    Output("fgm-new-id",             "value",  allow_duplicate=True),
    Output("fgm-group-dropdown",     "value",  allow_duplicate=True),
    Output("fgm-updated-by",         "value",  allow_duplicate=True),
    Output("fgm-mode-existing",      "style",  allow_duplicate=True),
    Output("fgm-mode-new",           "style",  allow_duplicate=True),
    # store / state
    Output("fgm-selected-idx",       "data"),
    Output("fgm-save-msg",           "children"),
    Output("fgm-rows-store",         "data"),
    # inputs
    Input({"type": "fgm-edit-btn",   "index": ALL}, "n_clicks"),
    Input({"type": "fgm-assign-btn", "index": ALL}, "n_clicks"),
    Input("fgm-add-top",  "n_clicks"),
    Input("fgm-close",    "n_clicks"),
    Input("fgm-cancel",   "n_clicks"),
    Input("fgm-save",     "n_clicks"),
    # states
    State("fgm-selected-idx",      "data"),
    State("fgm-investor-selector", "value"),
    State("fgm-new-name",          "value"),
    State("fgm-new-id",            "value"),
    State("fgm-group-dropdown",    "value"),
    State("fgm-updated-by",        "value"),
    State("fgm-rows-store",        "data"),
    prevent_initial_call=True,
)
def manage_drawer(
    edit_clicks, assign_clicks, add_top,
    close_n, cancel_n, save_n,
    selected_idx, selector_val,
    new_name_val, new_id_val,
    group_val, updated_by_val, rows,
):
    triggered = ctx.triggered_id
    NO = no_update

    def _close():
        return (
            _DRAWER_HIDDEN, _OVL_HIDDEN,
            NO, NO,
            _HIDE, _HIDE, _HIDE, _HIDE,
            NO, NO, None, NO, NO, NO, NO,
            NO, NO,
            None, "", NO,
        )

    # ── Close / Cancel ────────────────────────────────────────────────────────
    if triggered in ("fgm-close", "fgm-cancel"):
        return _close()

    # ── Save ─────────────────────────────────────────────────────────────────
    if triggered == "fgm-save":
        updated  = list(rows)
        save_by  = (updated_by_val or "").strip() or "Tax Ops"
        new_group = group_val
        today     = "Aug 21, 2024"

        actual_idx = selected_idx if selected_idx is not None else (
            int(selector_val) if selector_val is not None else None
        )

        if actual_idx is not None:
            # Edit / assign group for existing investor
            old_group = updated[actual_idx]["group"]
            action    = "Group updated" if old_group else "Group assigned"
            detail    = f"Group: {new_group}" if new_group else "Group cleared"
            new_hist  = {"date": today, "by": save_by, "action": action, "detail": detail}
            updated[actual_idx] = {
                **updated[actual_idx],
                "group":      new_group,
                "status":     "Mapped" if new_group else "Unmapped",
                "updated":    today,
                "updated_by": save_by,
                "history":    [new_hist] + updated[actual_idx].get("history", []),
            }
        else:
            # Add brand-new investor
            name = (new_name_val or "").strip()
            if not name:
                err = html.Div(
                    "Please enter an investor name.",
                    style={"background": "#fee2e2", "color": "#7f1d1d",
                           "border": "1px solid #fca5a5", "borderRadius": "5px",
                           "padding": "8px 14px", "fontSize": "13px"},
                )
                return (
                    _DRAWER_VISIBLE, _OVL_VISIBLE,
                    NO, NO,
                    _SHOW, _HIDE, _HIDE, _SHOW,
                    NO, NO, None, NO, NO, NO, NO,
                    NO, NO,
                    None, err, NO,
                )
            inv_id = (new_id_val or "").strip() or f"INV{len(updated)+1:03d}"
            detail = f"Group: {new_group}" if new_group else "No group assigned"
            updated.append({
                "investor":   name,
                "inv_id":     inv_id,
                "group":      new_group,
                "status":     "Mapped" if new_group else "Unmapped",
                "updated":    today,
                "updated_by": save_by,
                "history":    [{"date": today, "by": save_by,
                                "action": "Group assigned", "detail": detail}],
            })

        msg = html.Div(
            "Mapping saved successfully.",
            style={"background": "#dcfce7", "color": "#14532d",
                   "border": "1px solid #86efac", "borderRadius": "5px",
                   "padding": "8px 14px", "fontSize": "13px", "fontWeight": "600"},
        )
        return (
            _DRAWER_HIDDEN, _OVL_HIDDEN,
            NO, NO,
            _HIDE, _HIDE, _HIDE, _HIDE,
            NO, NO, None, NO, NO, NO, NO,
            NO, NO,
            None, msg, updated,
        )

    # ── Open from Edit row button (mapped rows) ───────────────────────────────
    if isinstance(triggered, dict) and triggered.get("type") == "fgm-edit-btn":
        if not edit_clicks or not any(edit_clicks):
            return _close()
        idx = triggered["index"]
        row = rows[idx]
        return (
            _DRAWER_VISIBLE, _OVL_VISIBLE,
            "Edit Funding Group Mapping", f"Last updated: {row['updated']}",
            _HIDE, _HIDE, _SHOW, _HIDE,
            row["investor"], f"ID: {row['inv_id']}",
            None, "", "", row["group"], row.get("updated_by") or "",
            _TAB_ON, _TAB_OFF,
            idx, "", NO,
        )

    # ── Open from Assign Group button (unmapped rows) ─────────────────────────
    if isinstance(triggered, dict) and triggered.get("type") == "fgm-assign-btn":
        if not assign_clicks or not any(assign_clicks):
            return _close()
        idx = triggered["index"]
        row = rows[idx]
        return (
            _DRAWER_VISIBLE, _OVL_VISIBLE,
            "Assign Funding Group", "Select a funding group for this investor.",
            _HIDE, _HIDE, _SHOW, _HIDE,
            row["investor"], f"ID: {row['inv_id']}",
            None, "", "", None, "",
            _TAB_ON, _TAB_OFF,
            idx, "", NO,
        )

    # ── Open from top "Add / Edit Mapping" button ─────────────────────────────
    if triggered == "fgm-add-top":
        return (
            _DRAWER_VISIBLE, _OVL_VISIBLE,
            "Add / Edit Mapping",
            "Select an investor, choose their funding group, then save.",
            _SHOW, _SHOW, _HIDE, _HIDE,
            "", "",
            None, "", "", None, "",
            _TAB_ON, _TAB_OFF,
            None, "", NO,
        )

    return _close()


# 6. History modal
@callback(
    Output("fgm-hist-modal",  "style"),
    Output("fgm-overlay",     "style", allow_duplicate=True),
    Output("fgm-hist-title",  "children"),
    Output("fgm-hist-body",   "children"),
    Input({"type": "fgm-hist-btn", "index": ALL}, "n_clicks"),
    Input("fgm-hist-close", "n_clicks"),
    State("fgm-rows-store", "data"),
    prevent_initial_call=True,
)
def manage_history(hist_clicks, close_n, rows):
    triggered = ctx.triggered_id
    if triggered == "fgm-hist-close":
        return _HIST_HIDDEN, _OVL_HIDDEN, no_update, no_update
    if isinstance(triggered, dict) and triggered.get("type") == "fgm-hist-btn":
        if not hist_clicks or not any(hist_clicks):
            return _HIST_HIDDEN, _OVL_HIDDEN, no_update, no_update
        idx   = triggered["index"]
        row   = rows[idx]
        hist  = row.get("history", [])
        title = f"Mapping History — {row['investor']}"
        body  = (
            html.P("No history available.",
                   style={"color": "#9ca3af", "fontSize": "13px"})
            if not hist
            else html.Div([_hist_entry(h) for h in hist])
        )
        return _HIST_VISIBLE, _OVL_VISIBLE, title, body
    return _HIST_HIDDEN, _OVL_HIDDEN, no_update, no_update


# 7. Export CSV
@callback(
    Output("fgm-download", "data"),
    Input("fgm-export-btn", "n_clicks"),
    State("fgm-rows-store", "data"),
    prevent_initial_call=True,
)
def export_csv(n_clicks, rows):
    if not n_clicks:
        return no_update
    buf = io.StringIO()
    writer = csv.DictWriter(
        buf,
        fieldnames=["investor", "inv_id", "group", "status", "updated", "updated_by"],
        extrasaction="ignore",
    )
    writer.writeheader()
    writer.writerows(rows)
    return dcc.send_string(buf.getvalue(), filename="funding_group_mapping.csv")
