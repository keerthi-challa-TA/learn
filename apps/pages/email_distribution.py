import dash
from dash import html, dcc, callback, Output, Input, State
import plotly.graph_objects as go

dash.register_page(__name__, path="/email-distribution", name="Email Distribution", title="Email Distribution")

filing_type_options = [
    {"label": "ADV", "value": "ADV"},
    {"label": "PF", "value": "PF"},
]

year_options = [
    {"label": "2024", "value": "2024"},
    {"label": "2023", "value": "2023"},
]

recipient_options = [
    {"label": "Compliance Group (7 recipients)", "value": "compliance"},
    {"label": "Operations Group (5 recipients)", "value": "operations"},
    {"label": "Custom Group", "value": "custom"},
    {"label": "All Groups", "value": "all"},
]

delivery_history_rows = [
    {"date": "Aug 18, 2024 11:15 AM", "filing_type": "ADV", "recipients": "Compliance Group (7)", "sent_by": "S. Rahman", "status": "Sent", "status_badge": "badge-success"},
    {"date": "Aug 17, 2024 03:00 PM", "filing_type": "PF", "recipients": "Operations Group (5)", "sent_by": "Tax Ops", "status": "Failed", "status_badge": "badge-danger"},
    {"date": "Aug 15, 2024 10:00 AM", "filing_type": "ADV", "recipients": "All Groups (12)", "sent_by": "S. Rahman", "status": "Sent", "status_badge": "badge-success"},
    {"date": "Aug 10, 2024 09:30 AM", "filing_type": "PF", "recipients": "Compliance Group (7)", "sent_by": "System", "status": "Sent", "status_badge": "badge-success"},
]

recipient_group_rows = [
    {"name": "Compliance Group", "email": "compliance@quantumcapital.com (group)", "count": "7 recipients", "status": "Active"},
    {"name": "Operations Group", "email": "operations@quantumcapital.com (group)", "count": "5 recipients", "status": "Active"},
    {"name": "Custom Group", "email": "custom-list", "count": "3 recipients", "status": "Active"},
]


def make_compose_panel():
    return html.Div(
        [
            html.Div("Compose Distribution", className="panel-title"),
            html.Div(
                [
                    html.Span("Filing Type", className="filter-label"),
                    dcc.Dropdown(
                        options=filing_type_options,
                        value="ADV",
                        clearable=False,
                        style={"minWidth": "120px"},
                    ),
                    html.Span("Filing Year", className="filter-label", style={"marginLeft": "16px"}),
                    dcc.Dropdown(
                        options=year_options,
                        value="2024",
                        clearable=False,
                        style={"minWidth": "120px"},
                    ),
                ],
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "gap": "8px",
                    "marginBottom": "16px",
                },
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Label("Recipient Group", className="form-label"),
                            html.Div(
                                [
                                    dcc.Dropdown(
                                        id="dd-recipients",
                                        options=recipient_options,
                                        value="compliance",
                                        clearable=False,
                                        style={"flex": "1"},
                                    ),
                                    html.Button("Add Recipients", className="btn btn-sm", style={"marginLeft": "8px", "whiteSpace": "nowrap"}),
                                ],
                                style={"display": "flex", "alignItems": "center"},
                            ),
                        ],
                        className="form-group",
                    ),
                    html.Div(
                        [
                            html.Label("Email Subject", className="form-label"),
                            dcc.Input(
                                id="email-subject",
                                value="ADV Filing – 2024",
                                className="form-input",
                                style={"width": "100%"},
                            ),
                        ],
                        className="form-group",
                    ),
                    html.Div(
                        [
                            html.Label("Message", className="form-label"),
                            dcc.Textarea(
                                id="email-body",
                                value="Please find attached the ADV filing workbook for the fiscal year 2024. This document contains all reviewed and approved metrics. Please review and confirm receipt.",
                                className="form-textarea",
                                rows=5,
                                style={"width": "100%"},
                            ),
                        ],
                        className="form-group",
                    ),
                    html.Div(
                        [
                            html.Label("Attachment", className="form-label"),
                            html.Div(
                                [
                                    html.Span("📎", style={"marginRight": "6px", "fontSize": "16px"}),
                                    html.Span("ADV_2024_v1.2.xlsx", style={"color": "#111827", "fontSize": "13px", "flex": "1"}),
                                    html.Span(
                                        "✕",
                                        style={
                                            "color": "#6b7280",
                                            "cursor": "pointer",
                                            "fontSize": "13px",
                                            "marginLeft": "8px",
                                        },
                                    ),
                                ],
                                className="panel-card",
                                style={
                                    "display": "inline-flex",
                                    "alignItems": "center",
                                    "padding": "6px 12px",
                                    "borderRadius": "6px",
                                    "background": "#f9fafb",
                                    "border": "1px solid #e5e7eb",
                                    "maxWidth": "300px",
                                },
                            ),
                        ],
                        className="form-group",
                    ),
                    html.Div(
                        [
                            html.Button("Send Email", className="btn btn-primary"),
                            html.Button("Save Draft", className="btn btn-ghost", style={"marginLeft": "8px"}),
                        ],
                        className="row",
                        style={"justifyContent": "flex-start", "gap": "8px"},
                    ),
                ],
                className="stack",
                style={"gap": "12px"},
            ),
        ],
        className="panel-card",
    )


def make_recipient_groups_panel():
    rows = []
    for r in recipient_group_rows:
        rows.append(
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(r["name"], style={"fontWeight": "600", "color": "#111827", "fontSize": "14px"}),
                            html.Div(r["email"], className="text-muted", style={"fontSize": "12px"}),
                        ],
                        style={"flex": "1"},
                    ),
                    html.Div(r["count"], className="text-muted", style={"fontSize": "12px", "marginRight": "12px", "whiteSpace": "nowrap"}),
                    html.Span("Active", className="status-badge badge-success", style={"marginRight": "8px"}),
                    html.Button("Edit", className="btn btn-sm btn-ghost"),
                ],
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "padding": "10px 0",
                    "borderBottom": "1px solid #e5e7eb",
                },
            )
        )

    return html.Div(
        [
            html.Div("Configured Recipients", className="panel-title"),
            html.Div(rows),
            html.Div(
                "Email addresses are managed by administrators. Contact Admin to add or modify recipients.",
                className="text-muted",
                style={"fontSize": "12px", "marginTop": "12px"},
            ),
            html.Button("Add Recipient Group", className="btn", style={"marginTop": "12px"}),
        ],
        className="panel-card",
    )


def make_delivery_history():
    header = html.Tr([
        html.Th("Date"),
        html.Th("Filing Type"),
        html.Th("Recipients"),
        html.Th("Sent By"),
        html.Th("Status"),
    ])
    rows = []
    for r in delivery_history_rows:
        rows.append(
            html.Tr([
                html.Td(r["date"]),
                html.Td(r["filing_type"]),
                html.Td(r["recipients"]),
                html.Td(r["sent_by"]),
                html.Td(html.Span(r["status"], className=f"status-badge {r['status_badge']}")),
            ])
        )
    return html.Div(
        [
            html.Div("Email Delivery History", className="panel-title"),
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


layout = html.Div(
    [
        html.Div(
            [
                html.Div(
                    [
                        html.H1("Email Distribution", className="page-heading"),
                        html.Div(
                            "Distribute filing workbooks to compliance and operations teams",
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
                    "Email delivery requires enterprise email service configuration. This interface prepares the distribution — actual send is performed by the backend service.",
                    className="info-banner",
                    style={"marginBottom": "20px"},
                ),
            ]
        ),
        html.Div(
            [make_compose_panel(), make_recipient_groups_panel()],
            className="grid-2",
        ),
        make_delivery_history(),
    ]
)
