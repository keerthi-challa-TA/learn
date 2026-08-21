import dash
from dash import html, dcc, callback, Output, Input, State
import plotly.graph_objects as go

dash.register_page(__name__, path="/review-feedback", name="Review & Feedback", title="Review & Feedback – Metric Level")

metric_options = [
    {"label": "PF1A – Total Private Fund Assets", "value": "PF1A"},
    {"label": "PF1B – Total Leverage", "value": "PF1B"},
    {"label": "PF1C – Investor Concentration", "value": "PF1C"},
    {"label": "ADV1A – Regulatory AUM", "value": "ADV1A"},
    {"label": "ADV7A – Non-US Ownership %", "value": "ADV7A"},
]

year_options = [
    {"label": "2024", "value": "2024"},
    {"label": "2023", "value": "2023"},
]

status_options = [
    {"label": "Pending Review", "value": "Pending Review"},
    {"label": "Reviewed", "value": "Reviewed"},
    {"label": "Approved", "value": "Approved"},
    {"label": "Rejected", "value": "Rejected"},
    {"label": "Override Required", "value": "Override Required"},
]

reviewer_options = [
    {"label": "S. Rahman", "value": "S. Rahman"},
    {"label": "Tax Manager", "value": "Tax Manager"},
    {"label": "Compliance Lead", "value": "Compliance Lead"},
    {"label": "Tax Director", "value": "Tax Director"},
]

history_rows = [
    {
        "datetime": "Aug 21, 2024 11:30 AM",
        "action": "Approved",
        "action_badge": "badge-success",
        "user": "S. Rahman",
        "comment": "Difference is due to timing of capital call recorded in Investran vs. PCAP cut-off date.",
    },
    {
        "datetime": "Aug 21, 2024 10:45 AM",
        "action": "Pending Review",
        "action_badge": "badge-warning",
        "user": "System",
        "comment": "Metric PF1A calculated successfully. Value: $1,234,567,890",
    },
    {
        "datetime": "Aug 20, 2024 03:00 PM",
        "action": "Data Loaded",
        "action_badge": "badge-info",
        "user": "System",
        "comment": "Source data refreshed from Investran Delta table.",
    },
]


def make_comparison_cards():
    cards = [
        {
            "border_color": "#22c55e",
            "label": "Calculated Value",
            "value": "$1,234,567,890",
            "value_color": "#111827",
            "sub": "PF1A – Total Private Fund Assets",
            "sub2": "Calculated: Aug 21, 2024",
            "badge": None,
        },
        {
            "border_color": "#3b82f6",
            "label": "PCAP / Financial Statement Value",
            "value": "$1,200,000,000",
            "value_color": "#111827",
            "sub": "Source: PCAP Q3 2024",
            "sub2": None,
            "badge": None,
        },
        {
            "border_color": "#ef4444",
            "label": "Variance",
            "value": "$34,567,890",
            "value_color": "#ef4444",
            "sub": "2.88% variance — Material",
            "sub2": None,
            "badge": ("badge-danger", "Material Variance"),
        },
    ]

    children = []
    for card in cards:
        body = [
            html.Div(card["label"], className="section-title", style={"marginBottom": "10px"}),
            html.Div(
                card["value"],
                style={
                    "fontSize": "28px",
                    "fontWeight": "700",
                    "color": card["value_color"],
                    "marginBottom": "6px",
                },
            ),
            html.Div(card["sub"], className="text-muted", style={"fontSize": "12px", "marginBottom": "4px"}),
        ]
        if card["sub2"]:
            body.append(html.Div(card["sub2"], className="text-muted", style={"fontSize": "12px", "marginBottom": "4px"}))
        if card["badge"]:
            badge_cls, badge_text = card["badge"]
            body.append(
                html.Span(badge_text, className=f"status-badge {badge_cls}", style={"marginTop": "8px", "display": "inline-block"})
            )
        children.append(
            html.Div(
                body,
                className="panel-card",
                style={"borderTop": f"2px solid {card['border_color']}"},
            )
        )

    return html.Div(children, className="grid-3")


def make_review_form():
    return html.Div(
        [
            html.Div("Review Decision", className="panel-title"),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Label("Review Status", className="form-label"),
                                    dcc.Dropdown(
                                        id="dd-status",
                                        options=status_options,
                                        value="Pending Review",
                                        clearable=False,
                                        className="form-input",
                                    ),
                                ],
                                className="form-group",
                            ),
                            html.Div(
                                [
                                    html.Label("Reviewer", className="form-label"),
                                    dcc.Dropdown(
                                        options=reviewer_options,
                                        value="S. Rahman",
                                        clearable=False,
                                        className="form-input",
                                    ),
                                ],
                                className="form-group",
                            ),
                        ],
                        className="grid-2",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Label("Review Date", className="form-label"),
                                    dcc.DatePickerSingle(
                                        id="date-review",
                                        date="2024-08-21",
                                        display_format="MMM D, YYYY",
                                        style={"width": "100%"},
                                    ),
                                ],
                                className="form-group",
                            ),
                            html.Div(
                                [
                                    html.Label("Override Reason", className="form-label"),
                                    dcc.Input(
                                        placeholder="Required if Override — explain the business justification",
                                        disabled=True,
                                        className="form-input",
                                        style={"width": "100%"},
                                    ),
                                ],
                                className="form-group",
                            ),
                        ],
                        className="grid-2",
                    ),
                    html.Div(
                        [
                            html.Label("Comments", className="form-label"),
                            dcc.Textarea(
                                id="comments",
                                placeholder='e.g. "Difference is due to timing of capital call recorded in Investran vs. PCAP cut-off date."',
                                className="form-textarea",
                                style={"width": "100%", "minHeight": "90px"},
                            ),
                        ],
                        className="form-group",
                    ),
                    html.Div(
                        [
                            html.Button("Approve", className="btn btn-success"),
                            html.Button("Reject", className="btn btn-danger"),
                            html.Button("Request Review", className="btn"),
                            html.Button("Save", className="btn btn-primary"),
                            html.Button("Override", className="btn btn-ghost"),
                        ],
                        className="row",
                        style={"justifyContent": "flex-end", "gap": "8px"},
                    ),
                ]
            ),
        ],
        className="panel-card",
        style={"marginTop": "20px"},
    )


def make_history_table():
    header = html.Tr([
        html.Th("Date & Time"),
        html.Th("Action"),
        html.Th("User"),
        html.Th("Comment"),
    ])
    rows = []
    for r in history_rows:
        rows.append(
            html.Tr([
                html.Td(r["datetime"]),
                html.Td(html.Span(r["action"], className=f"status-badge {r['action_badge']}")),
                html.Td(r["user"]),
                html.Td(r["comment"]),
            ])
        )
    return html.Div(
        [
            html.Div("Review History", className="panel-title"),
            html.Div(
                html.Table(
                    [html.Thead(header), html.Tbody(rows)],
                    className="data-table",
                ),
                className="data-table-wrap",
            ),
        ],
        className="panel-card",
        style={"marginTop": "20px"},
    )


def make_attachments():
    return html.Div(
        [
            html.Div("Supporting Documents", className="panel-title"),
            html.Div(
                "No files attached yet.",
                className="text-muted",
                style={"fontSize": "14px", "marginBottom": "12px"},
            ),
            html.Button("Attach Document", className="btn"),
        ],
        className="panel-card",
        style={"marginTop": "20px"},
    )


layout = html.Div(
    [
        html.Div(
            [
                html.Div(
                    [
                        html.H1("Review & Feedback – Metric Level", className="page-heading"),
                        html.Div(
                            "Reviewer: Sharmin Rahman  ·  FY 2024",
                            className="page-subheading",
                        ),
                    ]
                ),
            ],
            className="page-header",
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Span("Metric", className="filter-label"),
                        dcc.Dropdown(
                            id="dd-metric",
                            options=metric_options,
                            value="PF1A",
                            clearable=False,
                            style={"minWidth": "340px"},
                        ),
                        html.Span("Filing Year", className="filter-label", style={"marginLeft": "16px"}),
                        dcc.Dropdown(
                            options=year_options,
                            value="2024",
                            clearable=False,
                            style={"minWidth": "120px"},
                        ),
                    ],
                    className="filter-bar",
                    style={"display": "flex", "alignItems": "center", "gap": "8px"},
                ),
            ]
        ),
        make_comparison_cards(),
        make_review_form(),
        make_history_table(),
        make_attachments(),
    ]
)
