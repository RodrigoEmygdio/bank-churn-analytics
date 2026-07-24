"""Customer form presentation boundary.

The final Streamlit form and user-facing copy are deferred. This module only
marks the approved presentation boundary.
"""

from __future__ import annotations

from churn_app.domain import CustomerInput


def render_customer_form() -> CustomerInput | None:
    """Render the future customer input form.

    TODO(Prompt 6): Implement the Streamlit customer form.
    """
    raise NotImplementedError("Customer form rendering is deferred to Prompt 6.")
