import dash
from dash import html, dcc, callback, Output, Input, State, ALL, ctx, no_update

dash.register_page(__name__, path="/classifications", name="Classifications", title="Mapping – Classifications")

# ── Mock data ─────────────────────────────────────────────────────────────────
ROWS_INIT = [
    {"company": "Acme Industrial Corp",    "l1": "Private Equity", "l2": "Buyout",        "l3": "Operating",  "cost": "Yes", "cash": "No",  "status": "Mapped",   "updated": "Aug 18, 2024"},
    {"company": "BlueSky Ventures Ltd",    "l1": "Private Equity", "l2": "Growth",         "l3": "Expansion",  "cost": "No",  "cash": "No",  "status": "Mapped",   "updated": "Aug 17, 2024"},
    {"company": "Coral Bay Credit",        "l1": "Private Debt",   "l2": "Direct Lending", "l3": "Senior",     "cost": "Yes", "cash": "No",  "status": "Mapped",   "updated": "Aug 16, 2024"},
    {"company": "Delta Real Estate Trust", "l1": "Real Estate",    "l2": "Core",           "l3": "Office",     "cost": "No",  "cash": "No",  "status": "Mapped",   "updated": "Aug 15, 2024"},
    {"company": "Eastern Capital Fund",    "l1": "Private Equity", "l2": "Buyout",         "l3": "Operating",  "cost": "Yes", "cash": "No",  "status": "Mapped",   "updated": "Aug 14, 2024"},
    {"company": "Frontier Infrastructure", "l1": None, "l2": None, "l3": None, "cost": None, "cash": None, "status": "Unmapped", "updated": None},
    {"company": "Granite Holdings",        "l1": None, "l2": None, "l3": None, "cost": None, "cash": None, "status": "Unmapped", "updated": None},
    {"company": "Harbor Bridge LLC",       "l1": None, "l2": None, "l3": None, "cost": None, "cash": None, "status": "Unmapped", "updated": None},
]

L1_OPTIONS = ["Private Equity", "Private Debt", "Real Estate", "Infrastructure", "Hedge Fund", "Other"]
L2_MAP = {
    "Private Equity":  ["Buyout", "Growth", "Venture", "Distressed"],
    "Private Debt":    ["Direct Lending", "Mezzanine", "CLO", "Special Situations"],
    "Real Estate":     ["Core", "Core-Plus", "Value-Add", "Opportunistic"],
    "Infrastructure":  ["Core", "Core-Plus", "Greenfield"],
    "Hedge Fund":      ["Long/Short", "Global Macro", "Arbitrage"],
    "Other":           ["Other"],
}
L3_OPTIONS = ["Operating", "Expansion", "Senior", "Junior", "Office", "Industrial",
              "Retail", "Greenfield", "Brownfield", "Other"]

MUTED = {"color": "#9ca3af"}

_DRAWER_HIDDEN = {"display": "none", "position": "fixed", "top": "0", "right": "0",
                  "width": "460px", "height": "100vh", "background": "#ffffff",
                  "boxShadow": "-4px 0 24px rgba(0,0,0,0.15)", "zIndex": "1001",
                  "overflowY": "auto", "padding": "0"}
_DRAWER_VISIBLE = {**_DRAWER_HIDDEN, "display": "block"}
_OVL_HIDDEN     = {"display": "none",  "position": "fixed", "inset": "0",
                   "background": "rgba(0,0,0,0.35)", "zIndex": "1000"}
_OVL_VISIBLE    = {**_OVL_HIDDEN, "display": "block"}
_SHOW = {"display": "block"}
_HIDE = {"display": "none"}

# ── Row helpers ───────────────────────────────────────────────────────────────

def _d(val):
    return val if val else html.Span("—", style=MUTED)

def _build_row(row, idx):
    unmapped  = row["status"] == "Unmapped"
    label     = "Add Classification" if unmapped else "Edit"
    badge_cls = "badge-warning" if unmapped else "badge-success"
    return html.Tr(
        className="row-unmapped" if unmapped else "",
        children=[
            html.Td(row["company"], className="cell-primary"),
            html.Td(_d(row["l1"])), html.Td(_d(row["l2"])), html.Td(_d(row["l3"])),
            html.Td(_d(row["cost"])), html.Td(_d(row["cash"])),
            html.Td(html.Span(row["status"], className=f"status-badge {badge_cls}")),
            html.Td(_d(row["updated"])),
            html.Td(html.Button(
                label,
                id={"type": "clf-btn", "index": idx},
                n_clicks=0,
                style={"background": "none", "border": "none", "cursor": "pointer",
                       "color": "#1d4ed8", "fontWeight": "500", "fontSize": "12px",
                       "padding": "2px 7px"},
            )),
        ],
    )

def _filter_rows(rows, search, status_val):
    out = []
    for i, r in enumerate(rows):
        if search and search.lower() not in r["company"].lower():
            continue
        if status_val and status_val != "all" and r["status"] != status_val:
            continue
        out.append((i, r))
    return out

def _dropdown(field_id, options, value, placeholder="Select…"):
    return dcc.Dropdown(id=field_id,
                        options=[{"label": o, "value": o} for o in options],
                        value=value, placeholder=placeholder,
                        clearable=False, className="dash-dropdown",
                        style={"width": "100%"})

def _yesno(field_id, value):
    return dcc.Dropdown(id=field_id,
                        options=[{"label": "Yes", "value": "Yes"},
                                 {"label": "No",  "value": "No"}],
                        value=value, clearable=False, className="dash-dropdown")

# ── Layout ────────────────────────────────────────────────────────────────────

def layout():
    unmapped_count = sum(1 for r in ROWS_INIT if r["status"] == "Unmapped")
    return html.Div([
        dcc.Store(id="clf-rows-store",   data=ROWS_INIT),
        dcc.Store(id="clf-selected-idx", data=None),

        html.Div(id="clf-bulk-toast", style={"display": "none"},
                 className="alert-banner",
                 children="Bulk update applied — 3 records updated successfully."),

        html.Div(id="clf-overlay", style=_OVL_HIDDEN),

        # ── Slide-in drawer ───────────────────────────────────────────────────
        html.Div(id="clf-drawer", style=_DRAWER_HIDDEN, children=[
            html.Div(className="row-between",
                     style={"padding": "20px 24px 16px",
                            "borderBottom": "1px solid #e5e7eb", "background": "#f8fafc"},
                     children=[
                         html.Div([
                             html.Div(id="clf-drawer-title",
                                      style={"fontWeight": "700", "fontSize": "15px",
                                             "color": "#111827"}),
                             html.Div(id="clf-drawer-sub",
                                      style={"fontSize": "12px", "color": "#6b7280",
                                             "marginTop": "2px"}),
                         ]),
                         html.Button("✕", id="clf-close", n_clicks=0,
                                     style={"background": "none", "border": "none",
                                            "fontSize": "18px", "color": "#6b7280",
                                            "cursor": "pointer", "padding": "4px 8px",
                                            "borderRadius": "4px"}),
                     ]),
            html.Div(style={"padding": "20px 24px"}, children=[
                html.Div(id="clf-save-msg", style={"marginBottom": "12px"}),

                # ── New company name input — shown when adding ─────────────
                html.Div(id="clf-new-company-wrap", style=_HIDE, children=[
                    html.Div(className="form-group", style={"marginBottom": "16px"}, children=[
                        html.Label("Portfolio Company Name", className="form-label"),
                        dcc.Input(id="clf-new-company", type="text",
                                  placeholder="Enter company name…",
                                  className="form-input", style={"width": "100%"}),
                    ]),
                ]),

                # ── Static company display — shown when editing ────────────
                html.Div(id="clf-static-company-wrap", style=_HIDE, children=[
                    html.Div("Portfolio Company", className="form-label",
                             style={"marginBottom": "4px"}),
                    html.Div(id="clf-company-display",
                             style={"padding": "8px 12px", "background": "#f8fafc",
                                    "border": "1px solid #e5e7eb", "borderRadius": "5px",
                                    "fontSize": "13px", "color": "#111827",
                                    "fontWeight": "600", "marginBottom": "16px"}),
                ]),

                html.Div(className="form-group", style={"marginBottom": "14px"}, children=[
                    html.Label("Level 1 — Asset Class", className="form-label"),
                    _dropdown("clf-l1", L1_OPTIONS, None, "Select Level 1…"),
                ]),
                html.Div(className="form-group", style={"marginBottom": "14px"}, children=[
                    html.Label("Level 2 — Sub-Class", className="form-label"),
                    _dropdown("clf-l2", [], None, "Select Level 2…"),
                ]),
                html.Div(className="form-group", style={"marginBottom": "14px"}, children=[
                    html.Label("Level 3 — Strategy", className="form-label"),
                    _dropdown("clf-l3", L3_OPTIONS, None, "Select Level 3…"),
                ]),
                html.Div(className="grid-2", style={"gap": "12px", "marginBottom": "14px"}, children=[
                    html.Div(className="form-group", children=[
                        html.Label("Cost Based", className="form-label"),
                        _yesno("clf-cost", None),
                    ]),
                    html.Div(className="form-group", children=[
                        html.Label("Cash & Cash Equivalent", className="form-label"),
                        _yesno("clf-cash", None),
                    ]),
                ]),

                html.Div(style={"height": "1px", "background": "#e5e7eb", "margin": "20px 0"}),
                html.Div(className="row",
                         style={"gap": "10px", "justifyContent": "flex-end"}, children=[
                    html.Button("Cancel", id="clf-cancel", n_clicks=0, className="btn btn-ghost"),
                    html.Button("Save Classification", id="clf-save", n_clicks=0,
                                className="btn btn-primary"),
                ]),
            ]),
        ]),

        # ── Page header ───────────────────────────────────────────────────────
        html.Div(className="page-header", children=[
            html.Div([
                html.H1("Mapping – Classifications", className="page-heading"),
                html.P("Maintain portfolio company classifications across all required levels for PF calculation",
                       className="page-subheading"),
            ]),
            html.Div(className="page-actions", children=[
                html.Button("Add / Edit Classification", id="clf-add-top", n_clicks=0,
                            className="btn btn-primary"),
                html.Button("Bulk Update", id="clf-bulk-update", n_clicks=0, className="btn btn-ghost"),
            ]),
        ]),

        html.Div(className="notification-banner", children=[
            html.Span(id="clf-unmapped-banner",
                      children=(f"{unmapped_count} portfolio companies are unmapped. "
                                "Level 1/2/3 classification required for PF calculations.")),
        ]),

        html.Div(className="filter-bar", children=[
            dcc.Input(id="clf-search", type="text", debounce=True,
                      placeholder="Search portfolio company…",
                      className="form-input", style={"minWidth": "240px", "flex": "1"}),
            html.Div(className="filter-divider"),
            html.Label("Status", className="filter-label"),
            dcc.Dropdown(id="clf-status",
                         options=[{"label": "All",      "value": "all"},
                                  {"label": "Mapped",   "value": "Mapped"},
                                  {"label": "Unmapped", "value": "Unmapped"}],
                         value="all", clearable=False,
                         className="dash-dropdown", style={"minWidth": "140px"}),
        ]),

        html.Div(className="data-table-wrap", children=[
            html.Table(className="data-table", children=[
                html.Thead(html.Tr([
                    html.Th("Portfolio Company"), html.Th("Level 1"), html.Th("Level 2"),
                    html.Th("Level 3"), html.Th("Cost Based"), html.Th("Cash & Equiv."),
                    html.Th("Status"), html.Th("Last Updated"), html.Th("Actions"),
                ])),
                html.Tbody(id="clf-table-body"),
            ]),
        ]),

        html.Div(className="row-between", style={"marginTop": "14px"}, children=[
            html.Span(id="clf-count", style={"color": "#6b7280", "fontSize": "12.5px"}),
            html.Div(className="row", style={"gap": "8px"}, children=[
                html.Button("Prev", className="btn btn-ghost btn-sm"),
                html.Button("Next", className="btn btn-ghost btn-sm"),
            ]),
        ]),
    ])


# ── Callbacks ─────────────────────────────────────────────────────────────────

# 1. Render table
@callback(
    Output("clf-table-body",      "children"),
    Output("clf-count",           "children"),
    Output("clf-unmapped-banner", "children"),
    Input("clf-rows-store", "data"),
    Input("clf-search",     "value"),
    Input("clf-status",     "value"),
)
def update_table(rows, search, status_val):
    results = _filter_rows(rows, search, status_val)
    table_rows = [_build_row(r, i) for i, r in results]
    if not table_rows:
        table_rows = [html.Tr(html.Td("No matching companies found.", colSpan=9,
                                      style={"textAlign": "center", "padding": "32px",
                                             "color": "#9ca3af"}))]
    shown = len(results)
    is_default = not search and (not status_val or status_val == "all")
    count_label = (f"Showing {shown} of 312 portfolio companies" if is_default
                   else f"Showing {shown} filtered result{'s' if shown != 1 else ''}")
    unmapped_n = sum(1 for r in rows if r["status"] == "Unmapped")
    banner = (f"{unmapped_n} portfolio "
              f"{'company is' if unmapped_n == 1 else 'companies are'} unmapped. "
              "Level 1/2/3 classification required for PF calculations."
              if unmapped_n else "All portfolio companies are classified.")
    return table_rows, count_label, banner


# 2. Manage drawer
@callback(
    Output("clf-drawer",               "style"),
    Output("clf-overlay",              "style"),
    Output("clf-drawer-title",         "children"),
    Output("clf-drawer-sub",           "children"),
    Output("clf-new-company-wrap",     "style"),   # show for add new
    Output("clf-static-company-wrap",  "style"),   # show for edit
    Output("clf-company-display",      "children"),
    Output("clf-new-company",          "value"),
    Output("clf-l1",                   "value"),
    Output("clf-l2",                   "value"),
    Output("clf-l2",                   "options"),
    Output("clf-l3",                   "value"),
    Output("clf-cost",                 "value"),
    Output("clf-cash",                 "value"),
    Output("clf-selected-idx",         "data"),
    Output("clf-save-msg",             "children"),
    Output("clf-rows-store",           "data"),
    Input({"type": "clf-btn", "index": ALL}, "n_clicks"),
    Input("clf-add-top",  "n_clicks"),
    Input("clf-close",    "n_clicks"),
    Input("clf-cancel",   "n_clicks"),
    Input("clf-save",     "n_clicks"),
    State("clf-selected-idx",  "data"),
    State("clf-new-company",   "value"),
    State("clf-l1",            "value"),
    State("clf-l2",            "value"),
    State("clf-l3",            "value"),
    State("clf-cost",          "value"),
    State("clf-cash",          "value"),
    State("clf-rows-store",    "data"),
    prevent_initial_call=True,
)
def manage_drawer(row_clicks, add_top, close_n, cancel_n, save_n,
                  selected_idx, new_company_val,
                  l1_val, l2_val, l3_val, cost_val, cash_val, rows):

    triggered = ctx.triggered_id
    NO = no_update
    EMPTY_L2 = []

    def _close():
        return (_DRAWER_HIDDEN, _OVL_HIDDEN,
                NO, NO, _HIDE, _HIDE, NO, NO,
                NO, NO, NO, NO, NO, NO, None, "", NO)

    # ── Close / Cancel ────────────────────────────────────────────────────────
    if triggered in ("clf-close", "clf-cancel"):
        return _close()

    # ── Save ─────────────────────────────────────────────────────────────────
    if triggered == "clf-save":
        updated = list(rows)
        if selected_idx is not None:
            # Edit existing row
            updated[selected_idx] = {
                **updated[selected_idx],
                "l1": l1_val, "l2": l2_val, "l3": l3_val,
                "cost": cost_val, "cash": cash_val,
                "status": "Mapped" if l1_val else updated[selected_idx]["status"],
                "updated": "Aug 21, 2024",
            }
        else:
            # Append new portfolio company
            company_name = (new_company_val or "").strip()
            if not company_name:
                msg = html.Div("Please enter a portfolio company name.",
                               style={"background": "#fee2e2", "color": "#7f1d1d",
                                      "border": "1px solid #fca5a5", "borderRadius": "5px",
                                      "padding": "8px 14px", "fontSize": "13px"})
                return (_DRAWER_VISIBLE, _OVL_VISIBLE,
                        NO, NO, _SHOW, _HIDE, NO, NO,
                        NO, NO, NO, NO, NO, NO, None, msg, NO)
            updated.append({
                "company": company_name,
                "l1": l1_val, "l2": l2_val, "l3": l3_val,
                "cost": cost_val, "cash": cash_val,
                "status": "Mapped" if l1_val else "Unmapped",
                "updated": "Aug 21, 2024",
            })
        msg = html.Div(
            "Classification saved successfully.",
            style={"background": "#dcfce7", "color": "#14532d",
                   "border": "1px solid #86efac", "borderRadius": "5px",
                   "padding": "8px 14px", "fontSize": "13px", "fontWeight": "600"},
        )
        return (_DRAWER_HIDDEN, _OVL_HIDDEN,
                NO, NO, _HIDE, _HIDE, NO, NO,
                NO, NO, NO, NO, NO, NO, None, msg, updated)

    # ── Open from row button (Edit or Add Classification) ────────────────────
    if isinstance(triggered, dict) and triggered.get("type") == "clf-btn":
        if not row_clicks or not any(row_clicks):
            return _close()
        idx = triggered["index"]
        row = rows[idx]
        is_new = row["status"] == "Unmapped"
        title = "Add Classification" if is_new else "Edit Classification"
        sub   = "Fill in all levels below." if is_new else f"Last updated: {row['updated']}"
        l1    = row["l1"]
        l2_opts = [{"label": o, "value": o} for o in L2_MAP.get(l1 or "", [])]
        return (_DRAWER_VISIBLE, _OVL_VISIBLE,
                title, sub,
                _HIDE, _SHOW,                 # hide name input, show static label
                row["company"], "",           # company display, clear new-company input
                l1, row["l2"], l2_opts, row["l3"],
                row["cost"], row["cash"],
                idx, "", NO)

    # ── Open from top "Add / Edit Classification" button ─────────────────────
    if triggered == "clf-add-top":
        return (_DRAWER_VISIBLE, _OVL_VISIBLE,
                "Add New Classification",
                "Enter the portfolio company name and fill in the classification levels.",
                _SHOW, _HIDE,                 # show name input, hide static label
                "", "",                       # clear both company fields
                None, None, EMPTY_L2, None,   # clear all dropdowns
                None, None,
                None, "", NO)

    return _close()


# 3. Cascade Level 2 options from Level 1
@callback(
    Output("clf-l2", "options", allow_duplicate=True),
    Output("clf-l2", "value",   allow_duplicate=True),
    Input("clf-l1", "value"),
    State("clf-selected-idx", "data"),
    State("clf-rows-store",   "data"),
    prevent_initial_call=True,
)
def cascade_l2(l1_val, selected_idx, rows):
    opts = [{"label": o, "value": o} for o in L2_MAP.get(l1_val or "", [])]
    current_row = rows[selected_idx] if (selected_idx is not None and rows) else None
    keep = (current_row["l2"] if current_row and current_row["l1"] == l1_val else None)
    return opts, keep


@callback(
    Output("clf-bulk-toast", "style"),
    Input("clf-bulk-update", "n_clicks"),
    prevent_initial_call=True,
)
def bulk_update_clf(n_clicks):
    return {"display": "block"}
