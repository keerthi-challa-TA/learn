import dash
from dash import html, dcc, callback, Output, Input, State

dash.register_page(
    __name__,
    path="/business-rules",
    name="Business Rules",
    title="Business Rule Explorer",
)


# ---------------------------------------------------------------------------
# Question data
# ---------------------------------------------------------------------------

QUESTIONS = {
    "none": {
        "panel_title": "No Business Rules Defined for This Selection",
        "rule_meta": "Select ADV · Section 7 to view available business rules.",
        "question_text": "No rules are defined for the selected form and section combination. Change the Form to ADV and Section to Section 7 to view rules.",
        "metric_formula": "—",
        "result": "—",
        "rule_id": "—",
        "calc_nodes": [("N/A", "No Rules", "Select ADV · Section 7")],
        "rule_metadata": [],
    },
    "q16": {
        "panel_title": "ADV Section 7.B.(1)  —  Question 16: Non-US Ownership %",
        "rule_meta": "Rule version 3.1  ·  Effective Jan 1, 2024  ·  Last updated Aug 1, 2024 by S. Rahman",
        "question_text": "What percentage of the regulatory assets under management are attributable to non-US investors?",
        "metric_formula": "Non-US Investor Commitments ÷ Total Investor Commitments × 100",
        "result": "25.1%  (FY 2024)",
        "rule_id": "ADV-7B1-Q16",
        "calc_nodes": [
            ("QUESTION",     "ADV Q16",                           "Non-US Ownership %"),
            ("NUMERATOR",    "Non-US Investor Commitments",       "$312,419,725"),
            ("DENOMINATOR",  "Total Investor Commitments",        "$1,245,678,901"),
            ("RULE APPLIED", "Numerator ÷ Denominator × 100",    "Business rule ADV-7B1-Q16"),
            ("OUTPUT",       "25.1%",                             "badge-success"),
        ],
        "rule_metadata": [
            ("Rule ID",       "ADV-7B1-Q16"),
            ("Rule Version",  "3.1"),
            ("Status",        "Active"),
            ("Effective Date","Jan 1, 2024"),
            ("Last Updated",  "Aug 1, 2024"),
            ("Updated By",    "S. Rahman"),
            ("Form",          "ADV"),
            ("Section",       "7.B.(1)"),
            ("Question",      "16"),
        ],
    },
    "q17": {
        "panel_title": "ADV Section 7.B.(2)  —  Question 17: Total AUM",
        "rule_meta": "Rule version 2.1  ·  Effective Jan 1, 2024  ·  Last updated Jul 15, 2024 by Tax Ops",
        "question_text": "What is the total regulatory assets under management for the current filing period?",
        "metric_formula": "Sum of all qualifying investor commitments across all funds",
        "result": "$1,245,678,901  (FY 2024)",
        "rule_id": "ADV-7B2-Q17",
        "calc_nodes": [
            ("QUESTION",     "ADV Q17",               "Total AUM"),
            ("NUMERATOR",    "All Investor Commitments","$1,245,678,901"),
            ("DENOMINATOR",  "N/A",                   "Not applicable"),
            ("RULE APPLIED", "Direct Sum",             "Business rule ADV-7B2-Q17"),
            ("OUTPUT",       "$1,245,678,901",         "badge-success"),
        ],
        "rule_metadata": [
            ("Rule ID",       "ADV-7B2-Q17"),
            ("Rule Version",  "2.1"),
            ("Status",        "Active"),
            ("Effective Date","Jan 1, 2024"),
            ("Last Updated",  "Jul 15, 2024"),
            ("Updated By",    "Tax Ops"),
            ("Form",          "ADV"),
            ("Section",       "7.B.(2)"),
            ("Question",      "17"),
        ],
    },
    "q18": {
        "panel_title": "ADV Section 7.B.(3)  —  Question 18: Qualifying AUM",
        "rule_meta": "Rule version 1.4  ·  Effective Jan 1, 2024  ·  Last updated Jun 1, 2024 by S. Rahman",
        "question_text": "What portion of total AUM qualifies under regulatory reporting criteria?",
        "metric_formula": "Qualifying AUM ÷ Total AUM × 100",
        "result": "89.3%  (FY 2024)",
        "rule_id": "ADV-7B3-Q18",
        "calc_nodes": [
            ("QUESTION",     "ADV Q18",                        "Qualifying AUM %"),
            ("NUMERATOR",    "Qualifying AUM",                 "$1,112,191,758"),
            ("DENOMINATOR",  "Total AUM",                      "$1,245,678,901"),
            ("RULE APPLIED", "Numerator ÷ Denominator × 100", "Business rule ADV-7B3-Q18"),
            ("OUTPUT",       "89.3%",                          "badge-success"),
        ],
        "rule_metadata": [
            ("Rule ID",       "ADV-7B3-Q18"),
            ("Rule Version",  "1.4"),
            ("Status",        "Active"),
            ("Effective Date","Jan 1, 2024"),
            ("Last Updated",  "Jun 1, 2024"),
            ("Updated By",    "S. Rahman"),
            ("Form",          "ADV"),
            ("Section",       "7.B.(3)"),
            ("Question",      "18"),
        ],
    },
    "pf_s1_q1": {
        "panel_title": "PF Section 1.A — Question 1: Total Private Fund Assets",
        "rule_meta": "Rule version 2.0  ·  Effective Jan 1, 2024  ·  Last updated Aug 1, 2024",
        "question_text": "What is the gross asset value of the private fund as of the reporting date?",
        "metric_formula": "Sum of fair values of all portfolio investments + Cash and Equivalents",
        "result": "$2,456,789,012  (FY 2024)",
        "rule_id": "PF-S1A-Q1",
        "calc_nodes": [
            ("QUESTION",    "PF Q1",                "Total Private Fund Assets"),
            ("NUMERATOR",   "Portfolio Fair Values", "$2,378,554,512"),
            ("ADDEND",      "Cash & Equivalents",    "$78,234,500"),
            ("RULE APPLIED","Direct Sum",            "Business rule PF-S1A-Q1"),
            ("OUTPUT",      "$2,456,789,012",        "badge-success"),
        ],
        "rule_metadata": [
            ("Rule ID",       "PF-S1A-Q1"),
            ("Rule Version",  "2.0"),
            ("Status",        "Active"),
            ("Effective Date","Jan 1, 2024"),
            ("Last Updated",  "Aug 1, 2024"),
            ("Updated By",    "Tax Ops"),
            ("Form",          "PF"),
            ("Section",       "1.A"),
            ("Question",      "1"),
        ],
    },
    "pf_s1_q2": {
        "panel_title": "PF Section 1.B — Question 2: Total Leverage",
        "rule_meta": "Rule version 1.0  ·  Effective Jan 1, 2024  ·  Last updated Jun 15, 2024",
        "question_text": "What is the total leverage (borrowings) of the private fund?",
        "metric_formula": "Sum of all outstanding borrowings at fund level and portfolio level",
        "result": "$345,678,900  (FY 2024)",
        "rule_id": "PF-S1B-Q2",
        "calc_nodes": [
            ("QUESTION",    "PF Q2",           "Total Leverage"),
            ("NUMERATOR",   "Fund-Level Debt",  "$220,000,000"),
            ("ADDEND",      "Portfolio Debt",   "$125,678,900"),
            ("RULE APPLIED","Direct Sum",       "Business rule PF-S1B-Q2"),
            ("OUTPUT",      "$345,678,900",     "badge-success"),
        ],
        "rule_metadata": [
            ("Rule ID",       "PF-S1B-Q2"),
            ("Rule Version",  "1.0"),
            ("Status",        "Active"),
            ("Effective Date","Jan 1, 2024"),
            ("Last Updated",  "Jun 15, 2024"),
            ("Updated By",    "S. Rahman"),
            ("Form",          "PF"),
            ("Section",       "1.B"),
            ("Question",      "2"),
        ],
    },
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def badge(text, cls):
    return html.Span(text, className=f"status-badge {cls}")


def action_link(text, href="#"):
    return html.A(text, href=href, className="action-link")


def kv_pair(label, value):
    """Key-value item used inside grid metadata panels."""
    return html.Div([
        html.Div(label, style={"color": "#6b7280", "fontSize": "11px", "textTransform": "uppercase", "letterSpacing": "0.4px", "marginBottom": "2px"}),
        html.Div(value, style={"color": "#111827", "fontSize": "13px", "fontWeight": "500"}),
    ], style={"padding": "4px 0"})


# ---------------------------------------------------------------------------
# Filter bar
# ---------------------------------------------------------------------------

filter_bar = html.Div([
    html.Div([
        html.Label("Form", className="filter-label"),
        dcc.Dropdown(
            id="br-form",
            options=[{"label": "ADV", "value": "ADV"}, {"label": "PF", "value": "PF"}],
            value="ADV",
            clearable=False,
            style={"minWidth": "100px"},
        ),
    ]),
    html.Div([
        html.Label("Section", className="filter-label"),
        dcc.Dropdown(
            id="br-section",
            options=[
                {"label": "All",        "value": "all"},
                {"label": "Section 1",  "value": "s1"},
                {"label": "Section 2",  "value": "s2"},
                {"label": "Section 5",  "value": "s5"},
                {"label": "Section 7",  "value": "s7"},
                {"label": "Schedule D", "value": "sd"},
            ],
            value="s7",
            clearable=False,
            style={"minWidth": "145px"},
        ),
    ]),
    html.Div([
        html.Label("Question", className="filter-label"),
        dcc.Dropdown(
            id="br-question",
            options=[
                {"label": "Q16 – Non-US Ownership %", "value": "q16"},
                {"label": "Q17 – Total AUM",           "value": "q17"},
                {"label": "Q18 – Qualifying AUM",      "value": "q18"},
            ],
            value="q16",
            clearable=False,
            style={"minWidth": "220px"},
        ),
    ]),
    html.Div([
        html.Label("Metric", className="filter-label"),
        dcc.Dropdown(
            id="br-metric",
            options=[
                {"label": "Non-US Ownership %",    "value": "non_us"},
                {"label": "Total AUM",             "value": "total_aum"},
                {"label": "RAUM",                  "value": "raum"},
                {"label": "Investor Concentration","value": "inv_conc"},
            ],
            value="non_us",
            clearable=False,
            style={"minWidth": "200px"},
        ),
    ]),
], className="filter-bar")


# ---------------------------------------------------------------------------
# Calculation Flow helpers
# ---------------------------------------------------------------------------

def calc_node(label, title, sub, active=False):
    border_color = "#3b82f6" if active else "#e5e7eb"
    bg_color = "#eff6ff" if active else "#f8fafc"
    text_color = "#1d4ed8" if active else "#111827"
    return html.Div([
        html.Div(
            label,
            style={"fontSize": "10px", "color": "#6b7280", "textTransform": "uppercase", "letterSpacing": "0.5px"},
        ),
        html.Div(
            title,
            style={"fontSize": "13px", "fontWeight": "600", "color": text_color, "margin": "5px 0 4px"},
        ),
        html.Div(sub) if isinstance(sub, html.Base) else html.Div(
            sub,
            style={"fontSize": "11px", "color": "#6b7280"},
        ),
    ], style={
        "background": bg_color,
        "border": f"1px solid {border_color}",
        "borderRadius": "6px",
        "padding": "14px",
        "textAlign": "center",
        "minWidth": "150px",
        "flex": "1",
    })


def flow_arrow():
    return html.Span(
        "→",
        style={"fontSize": "20px", "color": "#9ca3af", "padding": "0 8px", "marginTop": "28px", "flexShrink": "0"},
    )


def build_calc_nodes(q):
    nodes = []
    for i, (label, title, sub) in enumerate(q["calc_nodes"]):
        is_output = (i == len(q["calc_nodes"]) - 1)
        nodes.append(calc_node(label, title, sub, active=is_output))
        if i < len(q["calc_nodes"]) - 1:
            nodes.append(flow_arrow())
    return nodes


# ---------------------------------------------------------------------------
# Source Information Panel
# ---------------------------------------------------------------------------

SOURCE_ROWS = [
    ("Anduin",    "anduin__commitments",  "commitment_amount", "investor_type = 'Non-US'", "2,341", "Aug 20, 2024"),
    ("Investran", "investran__investors", "commitment_amount", "ALL",                      "8,901", "Aug 21, 2024"),
]

source_rows_html = []
for system, table, col, filt, count, refresh in SOURCE_ROWS:
    source_rows_html.append(html.Tr([
        html.Td(system,  className="cell-primary"),
        html.Td(table,   style={"fontFamily": "monospace", "fontSize": "12px"}),
        html.Td(col,     style={"fontFamily": "monospace", "fontSize": "12px"}),
        html.Td(filt,    style={"fontFamily": "monospace", "fontSize": "12px"}),
        html.Td(count),
        html.Td(refresh),
    ]))

source_info_panel = html.Div([
    html.Div("Source Information", className="panel-title"),
    html.Div(
        html.Table([
            html.Thead(html.Tr([
                html.Th("Source System"),
                html.Th("Delta Table"),
                html.Th("Column"),
                html.Th("Filter Applied"),
                html.Th("Record Count"),
                html.Th("Last Refresh"),
            ])),
            html.Tbody(source_rows_html),
        ], className="data-table"),
        className="data-table-wrap",
        style={"marginTop": "12px"},
    ),
], className="panel-card")


# ---------------------------------------------------------------------------
# Technical Details (collapsible)
# ---------------------------------------------------------------------------

SQL_QUERY = """\
SELECT
    SUM(CASE WHEN investor_type = 'Non-US' THEN commitment_amount ELSE 0 END)
      / NULLIF(SUM(commitment_amount), 0) * 100 AS non_us_ownership_pct
FROM anduin__commitments ac
JOIN investran__investors ii ON ac.investor_id = ii.investor_id
WHERE filing_year = 2024"""

technical_details = html.Details([
    html.Summary(
        "Technical Details (Operations Role Required)",
        style={"cursor": "pointer", "fontWeight": "600", "color": "#111827", "fontSize": "14px", "padding": "4px 0"},
    ),
    html.Div([
        html.Div("SQL Query (Read-Only — for reference only):", className="section-title", style={"marginBottom": "10px"}),
        html.Div(
            SQL_QUERY,
            style={
                "fontFamily": "monospace",
                "fontSize": "12px",
                "background": "#f1f5f9",
                "border": "1px solid #e5e7eb",
                "borderRadius": "4px",
                "padding": "14px",
                "color": "#374151",
                "whiteSpace": "pre-wrap",
                "overflowX": "auto",
                "lineHeight": "1.7",
            },
        ),
        html.Div(
            "SQL is read-only. Modifications to business rules are made through the rule management "
            "workflow. Contact the Operations team.",
            style={"color": "#9ca3af", "fontSize": "12px", "marginTop": "10px"},
        ),
    ], className="panel-card", style={"marginTop": "12px"}),
], style={"marginTop": "4px"})


# ---------------------------------------------------------------------------
# Business Rule Statuses Key
# ---------------------------------------------------------------------------

status_key = html.Div([
    badge("Active",     "badge-success"),
    badge("Draft",      "badge-warning"),
    badge("Deprecated", "badge-muted"),
    html.Span(
        "Only Active rules are used in calculations",
        style={"color": "#6b7280", "fontSize": "12px", "marginLeft": "8px"},
    ),
], className="row", style={"gap": "8px", "marginTop": "16px", "alignItems": "center", "flexWrap": "wrap"})


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

def layout():
    q = QUESTIONS["q16"]
    return html.Div([
        # Page header
        html.Div([
            html.H1("Business Rule Explorer", className="page-heading"),
            html.P(
                "Explore the business logic behind each calculated metric. "
                "Designed for transparency and auditability.",
                className="page-subheading",
            ),
        ], className="page-header"),

        # Filter bar
        filter_bar,

        # Content stack
        html.Div([
            # Question Detail Panel
            html.Div([
                # Panel header row
                html.Div([
                    html.Div([
                        html.Div(
                            q["panel_title"],
                            id="br-panel-title",
                            className="panel-title",
                            style={"marginBottom": "2px"},
                        ),
                        html.Div(
                            q["rule_meta"],
                            id="br-rule-meta",
                            style={"color": "#6b7280", "fontSize": "12px"},
                        ),
                    ]),
                    html.Div([
                        badge("Active", "badge-success"),
                        html.Span(
                            f"Rule ID: {q['rule_id']}",
                            id="br-rule-id",
                            style={"color": "#9ca3af", "fontSize": "12px", "fontFamily": "monospace", "marginLeft": "12px"},
                        ),
                    ], style={"display": "flex", "alignItems": "center", "gap": "4px", "flexShrink": "0"}),
                ], className="row-between", style={"alignItems": "flex-start"}),

                html.Hr(className="divider"),

                # Grid-2: Business Question | Business Metric
                html.Div([
                    # Left – Business Question
                    html.Div([
                        html.Div("Business Question", className="section-title"),
                        html.Div(
                            f'"{q["question_text"]}"',
                            id="br-question-text",
                            style={
                                "fontStyle": "italic",
                                "fontSize": "14px",
                                "color": "#111827",
                                "background": "#f8fafc",
                                "border": "1px solid #e5e7eb",
                                "borderRadius": "6px",
                                "padding": "14px",
                                "marginTop": "8px",
                                "lineHeight": "1.6",
                            },
                        ),
                    ]),

                    # Right – Business Metric
                    html.Div([
                        html.Div("Business Metric", className="section-title"),
                        html.Div(
                            q["metric_formula"],
                            id="br-metric-formula",
                            style={"fontSize": "14px", "fontWeight": "600", "color": "#111827", "marginTop": "8px", "lineHeight": "1.5"},
                        ),
                        html.Div(
                            f"Result: {q['result']}",
                            id="br-result",
                            style={"color": "#22c55e", "fontSize": "13px", "marginTop": "6px"},
                        ),
                    ]),
                ], className="grid-2", style={"marginTop": "4px"}),
            ], className="panel-card"),

            # Calculation Flow Panel
            html.Div([
                html.Div("Calculation Flow", className="panel-title", style={"marginBottom": "16px"}),
                html.Div(
                    build_calc_nodes(q),
                    id="br-calc-flow-nodes",
                    style={
                        "display": "flex",
                        "flexDirection": "row",
                        "alignItems": "flex-start",
                        "gap": "0",
                        "overflowX": "auto",
                    },
                ),
            ], className="panel-card"),

            source_info_panel,

            # Rule Metadata Panel (dynamic)
            html.Div([
                html.Div("Rule Metadata", className="panel-title"),
                html.Div(id="br-metadata-grid", className="grid-3",
                         style={"marginTop": "12px", "gap": "10px 24px"}),
            ], className="panel-card"),

            technical_details,
            status_key,
        ], className="stack", style={"marginTop": "20px"}),
    ])


# ---------------------------------------------------------------------------
# Callbacks
# ---------------------------------------------------------------------------

_ADV_S7_QUESTIONS = [
    {"label": "Q16 – Non-US Ownership %", "value": "q16"},
    {"label": "Q17 – Total AUM",           "value": "q17"},
    {"label": "Q18 – Qualifying AUM",      "value": "q18"},
]
_PF_S1_QUESTIONS = [
    {"label": "Q1 – Total Private Fund Assets", "value": "pf_s1_q1"},
    {"label": "Q2 – Total Leverage",             "value": "pf_s1_q2"},
]
_NO_QUESTIONS = [{"label": "No rules defined for this selection", "value": "none"}]


@callback(
    Output("br-question", "options"),
    Output("br-question", "value"),
    Input("br-form",    "value"),
    Input("br-section", "value"),
)
def filter_questions(form, section):
    if form == "ADV" and section == "s7":
        return _ADV_S7_QUESTIONS, "q16"
    if form == "PF" and section == "s1":
        return _PF_S1_QUESTIONS, "pf_s1_q1"
    return _NO_QUESTIONS, "none"


@callback(
    Output("br-panel-title",     "children"),
    Output("br-rule-meta",       "children"),
    Output("br-question-text",   "children"),
    Output("br-metric-formula",  "children"),
    Output("br-result",          "children"),
    Output("br-calc-flow-nodes", "children"),
    Output("br-rule-id",         "children"),
    Output("br-metadata-grid",   "children"),
    Input("br-question", "value"),
)
def update_rule(question):
    q = QUESTIONS.get(question, QUESTIONS["none"])
    nodes = []
    for i, (label, title, sub) in enumerate(q["calc_nodes"]):
        is_output = (i == len(q["calc_nodes"]) - 1)
        nodes.append(calc_node(label, title, sub, active=is_output))
        if i < len(q["calc_nodes"]) - 1:
            nodes.append(flow_arrow())

    meta_items = []
    for label, value in q.get("rule_metadata", []):
        if label == "Status":
            val = badge(value, "badge-success") if value == "Active" else badge(value, "badge-muted")
        else:
            val = value
        meta_items.append(kv_pair(label, val))

    return (
        q["panel_title"],
        q["rule_meta"],
        f'"{q["question_text"]}"',
        q["metric_formula"],
        f"Result: {q['result']}",
        nodes,
        f"Rule ID: {q['rule_id']}",
        meta_items,
    )
