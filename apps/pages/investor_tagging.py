import dash
from dash import html, dcc, callback, Output, Input, State, ALL, ctx, no_update

dash.register_page(__name__, path="/investor-tagging", name="Investor Tagging",
                   title="Mapping – Investor Tagging")

# ── Mock data — history embedded per investor ─────────────────────────────────
INVESTORS_INIT = [
    {"name": "ABC Pension Fund",     "id": "INV001", "tagging": ["LP"],
     "status": "Mapped",   "updated": "Aug 18, 2024", "by": "S. Rahman",
     "history": [
         {"date": "Aug 18, 2024", "by": "S. Rahman", "action": "Tag updated", "detail": "LP added"},
         {"date": "Jul 10, 2024", "by": "Tax Ops",   "action": "Investor created", "detail": "Initial setup"},
     ]},
    {"name": "XYZ Capital Partners", "id": "INV002", "tagging": ["GP"],
     "status": "Mapped",   "updated": "Aug 18, 2024", "by": "S. Rahman",
     "history": [
         {"date": "Aug 18, 2024", "by": "S. Rahman", "action": "Tag updated", "detail": "GP added"},
     ]},
    {"name": "LMN Foundation",       "id": "INV003", "tagging": ["LP"],
     "status": "Mapped",   "updated": "Aug 17, 2024", "by": "Tax Ops",
     "history": [
         {"date": "Aug 17, 2024", "by": "Tax Ops", "action": "Tag updated", "detail": "LP added"},
     ]},
    {"name": "QRS Family Office",    "id": "INV004", "tagging": ["LP", "US"],
     "status": "Mapped",   "updated": "Aug 16, 2024", "by": "Tax Ops",
     "history": [
         {"date": "Aug 16, 2024", "by": "Tax Ops",   "action": "Tag updated",    "detail": "LP, US added"},
         {"date": "Jun 02, 2024", "by": "S. Rahman", "action": "Investor created", "detail": "Initial setup"},
     ]},
    {"name": "TUV Holdings",         "id": "INV005", "tagging": [],
     "status": "Unmapped", "updated": None, "by": None, "history": []},
    {"name": "Meridian Capital",     "id": "INV006", "tagging": [],
     "status": "Unmapped", "updated": None, "by": None, "history": []},
    {"name": "Northern Trust Fund",  "id": "INV007", "tagging": [],
     "status": "Unmapped", "updated": None, "by": None, "history": []},
]

TAGGING_OPTIONS  = ["GP", "LP", "Related", "Fund of Funds",
                    "Internal Private Fund", "US", "Non-US"]
TOTAL_INVESTORS  = 245

_MUTED           = {"color": "#9ca3af"}
_DRAWER_HIDDEN   = {"display": "none",  "position": "fixed", "top": "0", "right": "0",
                    "width": "460px",   "height": "100vh",   "background": "#ffffff",
                    "boxShadow": "-4px 0 24px rgba(0,0,0,0.15)", "zIndex": "1001",
                    "overflowY": "auto", "padding": "0"}
_DRAWER_VISIBLE  = {**_DRAWER_HIDDEN, "display": "block"}
_OVL_HIDDEN      = {"display": "none",  "position": "fixed", "inset": "0",
                    "background": "rgba(0,0,0,0.35)", "zIndex": "1000"}
_OVL_VISIBLE     = {**_OVL_HIDDEN, "display": "block"}
_HIST_HIDDEN     = {"display": "none",  "position": "fixed", "top": "50%", "left": "50%",
                    "transform": "translate(-50%,-50%)", "width": "480px",
                    "maxHeight": "70vh", "background": "#ffffff", "borderRadius": "10px",
                    "boxShadow": "0 8px 32px rgba(0,0,0,0.18)", "zIndex": "1002",
                    "overflowY": "auto", "padding": "0"}
_HIST_VISIBLE    = {**_HIST_HIDDEN, "display": "block"}
_SHOW            = {"display": "block"}
_HIDE            = {"display": "none"}


# ── Row helpers ───────────────────────────────────────────────────────────────

def _d(val):
    return val if val else html.Span("—", style=_MUTED)

def _tag_badges(tags):
    if not tags:
        return html.Td(_d(None))
    return html.Td([html.Span(t, className="status-badge badge-primary",
                              style={"marginRight": "4px"}) for t in tags])

def _build_row(inv, idx):
    unmapped = inv["status"] == "Unmapped"
    if unmapped:
        actions = html.Td(html.Button(
            "Add Tagging", id={"type": "it-add-btn", "index": idx}, n_clicks=0,
            style={"background": "#eff6ff", "border": "1px solid #bfdbfe",
                   "color": "#1d4ed8", "fontWeight": "600", "fontSize": "12px",
                   "padding": "4px 12px", "borderRadius": "4px", "cursor": "pointer"},
        ))
    else:
        actions = html.Td(html.Div([
            html.Button("Edit", id={"type": "it-edit-btn", "index": idx}, n_clicks=0,
                        style={"background": "none", "border": "none", "cursor": "pointer",
                               "color": "#1d4ed8", "fontWeight": "500",
                               "fontSize": "12px", "padding": "2px 7px"}),
            html.Button("History", id={"type": "it-hist-btn", "index": idx}, n_clicks=0,
                        style={"background": "none", "border": "none", "cursor": "pointer",
                               "color": "#6b7280", "fontWeight": "500",
                               "fontSize": "12px", "padding": "2px 7px"}),
        ], className="row", style={"gap": "6px"}))

    return html.Tr(className="row-unmapped" if unmapped else "", children=[
        html.Td(inv["name"], className="cell-primary"),
        html.Td(inv["id"], style={"color": "#6b7280", "fontFamily": "monospace"}),
        _tag_badges(inv["tagging"]),
        html.Td(html.Span(inv["status"],
                          className="status-badge " +
                          ("badge-warning" if unmapped else "badge-success"))),
        html.Td(_d(inv["updated"])),
        html.Td(_d(inv["by"])),
        actions,
    ])

def _filter_investors(investors, search, tagging, status):
    search = (search or "").strip().lower()
    out = []
    for i, inv in enumerate(investors):
        if search and search not in inv["name"].lower() and search not in inv["id"].lower():
            continue
        if tagging and tagging != "All" and tagging not in inv["tagging"]:
            continue
        if status and status != "All" and inv["status"] != status:
            continue
        out.append((i, inv))
    return out

def _make_selector_opts(investors):
    return [{"label": f"{inv['name']}  ({inv['id']})", "value": i}
            for i, inv in enumerate(investors)]

def _hist_entry(h):
    return html.Div(className="row-between",
                    style={"padding": "10px 12px", "borderRadius": "6px",
                           "border": "1px solid #e5e7eb", "marginBottom": "8px",
                           "background": "#f8fafc"},
                    children=[
                        html.Div([
                            html.Div(h["action"],
                                     style={"fontWeight": "600", "fontSize": "13px",
                                            "color": "#111827"}),
                            html.Div(h["detail"],
                                     style={"fontSize": "12px", "color": "#6b7280",
                                            "marginTop": "2px"}),
                        ]),
                        html.Div([
                            html.Div(h["date"],
                                     style={"fontSize": "12px", "color": "#6b7280",
                                            "textAlign": "right"}),
                            html.Div(f"by {h['by']}",
                                     style={"fontSize": "11px", "color": "#9ca3af",
                                            "textAlign": "right", "marginTop": "2px"}),
                        ]),
                    ])

def _build_history_detail(old_tags, new_tags):
    added   = [t for t in new_tags if t not in old_tags]
    removed = [t for t in old_tags if t not in new_tags]
    parts   = []
    if added:   parts.append(f"Added: {', '.join(added)}")
    if removed: parts.append(f"Removed: {', '.join(removed)}")
    return "; ".join(parts) if parts else "No tag changes"


# ── Layout ────────────────────────────────────────────────────────────────────

def layout():
    unmapped_count = sum(1 for i in INVESTORS_INIT if i["status"] == "Unmapped")
    selector_opts  = _make_selector_opts(INVESTORS_INIT)

    # shared mode-toggle style
    _tab_base = {"padding": "6px 16px", "border": "1px solid #e5e7eb",
                 "borderRadius": "5px", "fontSize": "12.5px", "cursor": "pointer",
                 "fontWeight": "500", "background": "#f8fafc", "color": "#6b7280"}
    _tab_on   = {**_tab_base, "background": "#3b82f6", "color": "#ffffff",
                 "border": "1px solid #3b82f6", "fontWeight": "600"}

    return html.Div([
        dcc.Store(id="it-investors-store", data=INVESTORS_INIT),
        dcc.Store(id="it-selected-idx",    data=None),

        html.Div(id="it-bulk-toast", style={"display": "none"},
                 className="alert-banner",
                 children="Bulk update applied — tags refreshed for selected investors."),

        html.Div(id="it-overlay", style=_OVL_HIDDEN),

        # ── Drawer ────────────────────────────────────────────────────────────
        html.Div(id="it-drawer", style=_DRAWER_HIDDEN, children=[
            # Header
            html.Div(className="row-between",
                     style={"padding": "20px 24px 16px",
                            "borderBottom": "1px solid #e5e7eb", "background": "#f8fafc"},
                     children=[
                         html.Div([
                             html.Div(id="it-drawer-title",
                                      style={"fontWeight": "700", "fontSize": "15px",
                                             "color": "#111827"}),
                             html.Div(id="it-drawer-sub",
                                      style={"fontSize": "12px", "color": "#6b7280",
                                             "marginTop": "2px"}),
                         ]),
                         html.Button("✕", id="it-close", n_clicks=0,
                                     style={"background": "none", "border": "none",
                                            "fontSize": "18px", "color": "#6b7280",
                                            "cursor": "pointer", "padding": "4px 8px",
                                            "borderRadius": "4px"}),
                     ]),

            # Body
            html.Div(style={"padding": "20px 24px"}, children=[
                html.Div(id="it-save-msg", style={"marginBottom": "12px"}),

                # ── Mode toggle (shown only from top button) ──────────────────
                html.Div(id="it-mode-wrap", style=_HIDE, children=[
                    html.Div("Mode", className="form-label",
                             style={"marginBottom": "6px"}),
                    html.Div(className="row", style={"gap": "6px", "marginBottom": "16px"},
                             children=[
                                 html.Button("Edit Existing", id="it-mode-existing",
                                             n_clicks=0, style=_tab_on),
                                 html.Button("Add New Investor", id="it-mode-new",
                                             n_clicks=0, style=_tab_base),
                             ]),
                ]),

                # ── Select existing investor ──────────────────────────────────
                html.Div(id="it-selector-wrap", style=_HIDE, children=[
                    html.Div(className="form-group", style={"marginBottom": "16px"}, children=[
                        html.Label("Select Investor", className="form-label"),
                        dcc.Dropdown(id="it-investor-selector",
                                     options=selector_opts,
                                     placeholder="Search and select an investor…",
                                     clearable=True, className="dash-dropdown",
                                     style={"width": "100%"}),
                    ]),
                ]),

                # ── New investor inputs ───────────────────────────────────────
                html.Div(id="it-new-investor-wrap", style=_HIDE, children=[
                    html.Div(className="grid-2", style={"gap": "12px", "marginBottom": "14px"},
                             children=[
                                 html.Div(className="form-group", children=[
                                     html.Label("Investor Name", className="form-label"),
                                     dcc.Input(id="it-new-name", type="text",
                                               placeholder="Full legal name…",
                                               className="form-input",
                                               style={"width": "100%"}),
                                 ]),
                                 html.Div(className="form-group", children=[
                                     html.Label("Investor ID", className="form-label"),
                                     dcc.Input(id="it-new-id", type="text",
                                               placeholder="e.g. INV008",
                                               className="form-input",
                                               style={"width": "100%"}),
                                 ]),
                             ]),
                ]),

                # ── Static display (row button opens) ─────────────────────────
                html.Div(id="it-static-wrap", style=_HIDE, children=[
                    html.Div("Investor", className="form-label", style={"marginBottom": "4px"}),
                    html.Div(id="it-investor-display",
                             style={"padding": "8px 12px", "background": "#f8fafc",
                                    "border": "1px solid #e5e7eb", "borderRadius": "5px",
                                    "fontSize": "13px", "color": "#111827",
                                    "fontWeight": "600", "marginBottom": "4px"}),
                    html.Div(id="it-investor-id-display",
                             style={"fontSize": "11px", "color": "#6b7280",
                                    "fontFamily": "monospace", "marginBottom": "16px"}),
                ]),

                # ── Tagging checklist ─────────────────────────────────────────
                html.Div(className="form-group", style={"marginBottom": "20px"}, children=[
                    html.Label("Investor Tagging", className="form-label",
                               style={"marginBottom": "8px", "display": "block"}),
                    html.P("Select all applicable tags for ADV and PF reporting:",
                           style={"fontSize": "12px", "color": "#6b7280", "marginBottom": "10px"}),
                    dcc.Checklist(
                        id="it-tags-checklist",
                        options=[{"label": t, "value": t} for t in TAGGING_OPTIONS],
                        value=[],
                        inline=False,
                        inputStyle={"marginRight": "8px"},
                        labelStyle={"display": "flex", "alignItems": "center",
                                    "padding": "8px 12px", "marginBottom": "4px",
                                    "borderRadius": "5px", "border": "1px solid #e5e7eb",
                                    "background": "#f8fafc", "cursor": "pointer",
                                    "fontSize": "13px", "color": "#111827"},
                    ),
                ]),

                html.Div(className="form-group", style={"marginBottom": "16px"}, children=[
                    html.Label("Updated By", className="form-label"),
                    dcc.Input(id="it-updated-by", type="text",
                              placeholder="Your name…",
                              className="form-input", style={"width": "100%"}),
                ]),

                html.Div(style={"height": "1px", "background": "#e5e7eb", "margin": "20px 0"}),
                html.Div(className="row", style={"gap": "10px", "justifyContent": "flex-end"},
                         children=[
                    html.Button("Cancel", id="it-cancel", n_clicks=0, className="btn btn-ghost"),
                    html.Button("Save Tagging", id="it-save", n_clicks=0,
                                className="btn btn-primary"),
                ]),
            ]),
        ]),

        # ── History modal ─────────────────────────────────────────────────────
        html.Div(id="it-hist-modal", style=_HIST_HIDDEN, children=[
            html.Div(className="row-between",
                     style={"padding": "18px 22px 14px",
                            "borderBottom": "1px solid #e5e7eb", "background": "#f8fafc"},
                     children=[
                         html.Div(id="it-hist-title",
                                  style={"fontWeight": "700", "fontSize": "14px",
                                         "color": "#111827"}),
                         html.Button("✕", id="it-hist-close", n_clicks=0,
                                     style={"background": "none", "border": "none",
                                            "fontSize": "18px", "color": "#6b7280",
                                            "cursor": "pointer", "padding": "4px 8px",
                                            "borderRadius": "4px"}),
                     ]),
            html.Div(id="it-hist-body", style={"padding": "16px 22px"}),
        ]),

        # ── Page header ───────────────────────────────────────────────────────
        html.Div(className="page-header", children=[
            html.Div([
                html.H1("Mapping – Investor Tagging", className="page-heading"),
                html.P("Tag investors with the appropriate classification for ADV and PF reporting",
                       className="page-subheading"),
            ]),
            html.Div(className="page-actions", children=[
                html.Button("Add / Edit Tagging", id="it-add-top", n_clicks=0,
                            className="btn btn-primary"),
                html.Button("Bulk Update", id="it-bulk-update", n_clicks=0, className="btn btn-ghost"),
                html.Button("Export",      className="btn btn-ghost"),
            ]),
        ]),

        html.Div(className="alert-banner", children=[
            html.Span(id="it-unmapped-banner",
                      children=(f"{unmapped_count} investors are unmapped. "
                                "Configure notifications to alert the team.")),
            html.A("Configure notifications", href="/notifications",
                   className="notif-link", style={"marginLeft": "12px"}),
        ]),

        html.Div(className="filter-bar", children=[
            dcc.Input(id="it-search", type="text",
                      placeholder="Search by name or ID...",
                      debounce=True, className="form-input",
                      style={"minWidth": "220px", "flex": "1"}),
            html.Div(className="filter-divider"),
            html.Label("Tagging", className="filter-label"),
            dcc.Dropdown(id="it-tagging",
                         options=[{"label": t, "value": t}
                                  for t in ["All"] + TAGGING_OPTIONS],
                         value="All", clearable=False,
                         className="dash-dropdown", style={"minWidth": "190px"}),
            html.Div(className="filter-divider"),
            html.Label("Status", className="filter-label"),
            dcc.Dropdown(id="it-status",
                         options=[{"label": "All",      "value": "All"},
                                  {"label": "Mapped",   "value": "Mapped"},
                                  {"label": "Unmapped", "value": "Unmapped"}],
                         value="All", clearable=False,
                         className="dash-dropdown", style={"minWidth": "130px"}),
        ]),

        html.Div(className="data-table-wrap", children=[
            html.Table(className="data-table", children=[
                html.Thead(html.Tr([
                    html.Th("Investor Name"), html.Th("Investor ID"), html.Th("Tagging"),
                    html.Th("Status"), html.Th("Last Updated"),
                    html.Th("Updated By"), html.Th("Actions"),
                ])),
                html.Tbody(id="it-tbody"),
            ]),
        ]),

        html.Div(className="row-between", style={"marginTop": "14px"}, children=[
            html.Span(id="it-count", style={"color": "#6b7280", "fontSize": "12.5px"}),
            html.Div(className="row", style={"gap": "8px"}, children=[
                html.Button("Prev", className="btn btn-ghost btn-sm"),
                html.Button("Next", className="btn btn-ghost btn-sm"),
            ]),
        ]),
    ])


# ── Callbacks ─────────────────────────────────────────────────────────────────

# 1. Render table
@callback(
    Output("it-tbody",           "children"),
    Output("it-count",           "children"),
    Output("it-unmapped-banner", "children"),
    Input("it-investors-store",  "data"),
    Input("it-search",  "value"),
    Input("it-tagging", "value"),
    Input("it-status",  "value"),
)
def update_table(investors, search, tagging, status):
    results = _filter_investors(investors, search, tagging, status)
    rows = [_build_row(inv, i) for i, inv in results]
    if not rows:
        rows = [html.Tr(html.Td("No investors match the current filters.",
                                colSpan=7, style={"textAlign": "center",
                                                  "padding": "32px", "color": "#9ca3af"}))]
    shown      = len(results)
    is_default = (not search and (not tagging or tagging == "All")
                  and (not status or status == "All"))
    count  = (f"Showing {shown} of {TOTAL_INVESTORS} investors" if is_default
              else f"Showing {shown} filtered result{'s' if shown != 1 else ''}")
    unmapped_n = sum(1 for inv in investors if inv["status"] == "Unmapped")
    banner = (f"{unmapped_n} investor{'s are' if unmapped_n != 1 else ' is'} unmapped. "
              "Configure notifications to alert the team." if unmapped_n
              else "All investors are tagged.")
    return rows, count, banner


# 2. Update selector options whenever store changes (new investors added)
@callback(
    Output("it-investor-selector", "options"),
    Input("it-investors-store", "data"),
)
def refresh_selector(investors):
    return _make_selector_opts(investors)


# 3. Mode toggle buttons — switch between Edit Existing and Add New
_TAB_ON  = {"padding": "6px 16px", "border": "1px solid #3b82f6", "borderRadius": "5px",
            "fontSize": "12.5px", "cursor": "pointer", "fontWeight": "600",
            "background": "#3b82f6", "color": "#ffffff"}
_TAB_OFF = {"padding": "6px 16px", "border": "1px solid #e5e7eb", "borderRadius": "5px",
            "fontSize": "12.5px", "cursor": "pointer", "fontWeight": "500",
            "background": "#f8fafc", "color": "#6b7280"}

@callback(
    Output("it-mode-existing",      "style"),
    Output("it-mode-new",           "style"),
    Output("it-selector-wrap",      "style"),
    Output("it-new-investor-wrap",  "style"),
    Output("it-investor-selector",  "value"),
    Output("it-new-name",           "value"),
    Output("it-new-id",             "value"),
    Output("it-tags-checklist",     "value", allow_duplicate=True),
    Input("it-mode-existing", "n_clicks"),
    Input("it-mode-new",      "n_clicks"),
    prevent_initial_call=True,
)
def switch_mode(ec, nc):
    if ctx.triggered_id == "it-mode-new":
        return _TAB_OFF, _TAB_ON, _HIDE, _SHOW, None, "", "", []
    return _TAB_ON, _TAB_OFF, _SHOW, _HIDE, None, "", "", []


# 4. Pre-fill tags when an existing investor is selected from dropdown
@callback(
    Output("it-tags-checklist", "value",    allow_duplicate=True),
    Output("it-updated-by",     "value",    allow_duplicate=True),
    Output("it-drawer-sub",     "children", allow_duplicate=True),
    Input("it-investor-selector", "value"),
    State("it-investors-store",   "data"),
    prevent_initial_call=True,
)
def prefill_from_selector(idx, investors):
    if idx is None:
        return [], "", "Select an investor, then choose their tags."
    inv = investors[int(idx)]
    sub = (f"Last updated: {inv['updated']}" if inv["updated"]
           else "No tagging history — new entry.")
    return inv["tagging"], inv.get("by") or "", sub


# 5. Main drawer controller — open, close, save
@callback(
    Output("it-drawer",            "style"),
    Output("it-overlay",           "style"),
    Output("it-drawer-title",      "children"),
    Output("it-drawer-sub",        "children"),
    # section visibility
    Output("it-mode-wrap",         "style"),
    Output("it-selector-wrap",     "style",  allow_duplicate=True),
    Output("it-static-wrap",       "style"),
    Output("it-new-investor-wrap", "style",  allow_duplicate=True),
    # field values
    Output("it-investor-display",  "children"),
    Output("it-investor-id-display","children"),
    Output("it-investor-selector", "value",  allow_duplicate=True),
    Output("it-new-name",          "value",  allow_duplicate=True),
    Output("it-new-id",            "value",  allow_duplicate=True),
    Output("it-tags-checklist",    "value",  allow_duplicate=True),
    Output("it-updated-by",        "value",  allow_duplicate=True),
    Output("it-mode-existing",     "style",  allow_duplicate=True),
    Output("it-mode-new",          "style",  allow_duplicate=True),
    # state / store
    Output("it-selected-idx",      "data"),
    Output("it-save-msg",          "children"),
    Output("it-investors-store",   "data"),
    # inputs
    Input({"type": "it-edit-btn", "index": ALL}, "n_clicks"),
    Input({"type": "it-add-btn",  "index": ALL}, "n_clicks"),
    Input("it-add-top",  "n_clicks"),
    Input("it-close",    "n_clicks"),
    Input("it-cancel",   "n_clicks"),
    Input("it-save",     "n_clicks"),
    # states
    State("it-selected-idx",     "data"),
    State("it-investor-selector","value"),
    State("it-new-name",         "value"),
    State("it-new-id",           "value"),
    State("it-tags-checklist",   "value"),
    State("it-updated-by",       "value"),
    State("it-investors-store",  "data"),
    prevent_initial_call=True,
)
def manage_drawer(edit_clicks, add_clicks, add_top,
                  close_n, cancel_n, save_n,
                  selected_idx, selector_val,
                  new_name_val, new_id_val,
                  tags_val, updated_by_val, investors):

    triggered = ctx.triggered_id
    NO        = no_update

    def _close():
        return (_DRAWER_HIDDEN, _OVL_HIDDEN,
                NO, NO,
                _HIDE, _HIDE, _HIDE, _HIDE,
                NO, NO, None, NO, NO, NO, NO,
                NO, NO,
                None, "", NO)

    # ── Close / Cancel ────────────────────────────────────────────────────────
    if triggered in ("it-close", "it-cancel"):
        return _close()

    # ── Save ─────────────────────────────────────────────────────────────────
    if triggered == "it-save":
        updated  = list(investors)
        save_by  = (updated_by_val or "").strip() or "Tax Ops"
        new_tags = tags_val or []
        today    = "Aug 21, 2024"

        # Determine target: existing row or brand-new investor
        actual_idx = selected_idx if selected_idx is not None else (
            int(selector_val) if selector_val is not None else None
        )

        if actual_idx is not None:
            # ── Edit / tag existing investor ──────────────────────────────────
            old_tags = updated[actual_idx]["tagging"]
            detail   = _build_history_detail(old_tags, new_tags)
            new_hist = {"date": today, "by": save_by,
                        "action": "Tag updated", "detail": detail}
            updated[actual_idx] = {
                **updated[actual_idx],
                "tagging": new_tags,
                "status":  "Mapped" if new_tags else "Unmapped",
                "updated": today,
                "by":      save_by,
                "history": [new_hist] + updated[actual_idx].get("history", []),
            }
        else:
            # ── Add brand-new investor ────────────────────────────────────────
            name = (new_name_val or "").strip()
            if not name:
                err = html.Div("Please enter an investor name.",
                               style={"background": "#fee2e2", "color": "#7f1d1d",
                                      "border": "1px solid #fca5a5", "borderRadius": "5px",
                                      "padding": "8px 14px", "fontSize": "13px"})
                return (_DRAWER_VISIBLE, _OVL_VISIBLE,
                        NO, NO,
                        _SHOW, _HIDE, _HIDE, _SHOW,
                        NO, NO, None, NO, NO, NO, NO,
                        NO, NO,
                        None, err, NO)
            inv_id = (new_id_val or "").strip() or f"INV{len(updated)+1:03d}"
            detail = f"Tags: {', '.join(new_tags) if new_tags else 'None'}"
            updated.append({
                "name":    name,
                "id":      inv_id,
                "tagging": new_tags,
                "status":  "Mapped" if new_tags else "Unmapped",
                "updated": today,
                "by":      save_by,
                "history": [{"date": today, "by": save_by,
                             "action": "Investor created", "detail": detail}],
            })

        msg = html.Div("Tagging saved successfully.",
                       style={"background": "#dcfce7", "color": "#14532d",
                              "border": "1px solid #86efac", "borderRadius": "5px",
                              "padding": "8px 14px", "fontSize": "13px", "fontWeight": "600"})
        return (_DRAWER_HIDDEN, _OVL_HIDDEN,
                NO, NO,
                _HIDE, _HIDE, _HIDE, _HIDE,
                NO, NO, None, NO, NO, NO, NO,
                NO, NO,
                None, msg, updated)

    # ── Open from Edit row button ─────────────────────────────────────────────
    if isinstance(triggered, dict) and triggered.get("type") == "it-edit-btn":
        if not edit_clicks or not any(edit_clicks):
            return _close()
        idx = triggered["index"]
        inv = investors[idx]
        return (_DRAWER_VISIBLE, _OVL_VISIBLE,
                "Edit Investor Tagging", f"Last updated: {inv['updated']}",
                _HIDE, _HIDE, _SHOW, _HIDE,
                inv["name"], f"ID: {inv['id']}",
                None, "", "", inv["tagging"], inv.get("by") or "",
                _TAB_ON, _TAB_OFF,
                idx, "", NO)

    # ── Open from Add Tagging button (unmapped row) ───────────────────────────
    if isinstance(triggered, dict) and triggered.get("type") == "it-add-btn":
        if not add_clicks or not any(add_clicks):
            return _close()
        idx = triggered["index"]
        inv = investors[idx]
        return (_DRAWER_VISIBLE, _OVL_VISIBLE,
                "Add Investor Tagging", "Select tags for this investor.",
                _HIDE, _HIDE, _SHOW, _HIDE,
                inv["name"], f"ID: {inv['id']}",
                None, "", "", [], "",
                _TAB_ON, _TAB_OFF,
                idx, "", NO)

    # ── Open from top "Add / Edit Tagging" button ─────────────────────────────
    if triggered == "it-add-top":
        return (_DRAWER_VISIBLE, _OVL_VISIBLE,
                "Add / Edit Tagging",
                "Select an investor, choose their tags, then save.",
                _SHOW, _SHOW, _HIDE, _HIDE,
                "", "",
                None, "", "", [], "",
                _TAB_ON, _TAB_OFF,
                None, "", NO)

    return _close()


# 6. History modal — reads history from store, not static dict
@callback(
    Output("it-hist-modal", "style"),
    Output("it-overlay",    "style", allow_duplicate=True),
    Output("it-hist-title", "children"),
    Output("it-hist-body",  "children"),
    Input({"type": "it-hist-btn", "index": ALL}, "n_clicks"),
    Input("it-hist-close", "n_clicks"),
    State("it-investors-store", "data"),
    prevent_initial_call=True,
)
def manage_history(hist_clicks, close_n, investors):
    triggered = ctx.triggered_id
    if triggered == "it-hist-close":
        return _HIST_HIDDEN, _OVL_HIDDEN, no_update, no_update
    if isinstance(triggered, dict) and triggered.get("type") == "it-hist-btn":
        if not hist_clicks or not any(hist_clicks):
            return _HIST_HIDDEN, _OVL_HIDDEN, no_update, no_update
        idx   = triggered["index"]
        inv   = investors[idx]
        hist  = inv.get("history", [])
        title = f"Tagging History — {inv['name']}"
        body  = (html.P("No history available.",
                        style={"color": "#9ca3af", "fontSize": "13px"})
                 if not hist
                 else html.Div([_hist_entry(h) for h in hist]))
        return _HIST_VISIBLE, _OVL_VISIBLE, title, body
    return _HIST_HIDDEN, _OVL_HIDDEN, no_update, no_update


@callback(
    Output("it-bulk-toast", "style"),
    Input("it-bulk-update", "n_clicks"),
    prevent_initial_call=True,
)
def bulk_update_it(n_clicks):
    return {"display": "block"}
