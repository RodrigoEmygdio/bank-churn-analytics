"""Result presentation boundary.

The final risk presentation, model-disagreement explanation, recommendation,
and disclaimer are deferred to later stages.
"""

from __future__ import annotations

from churn_app.domain import OrchestrationResult


def render_result(result: OrchestrationResult) -> None:
    """Render the future decision-support result.

    TODO(Prompt 6): Implement Streamlit result presentation.
    """
    raise NotImplementedError("Result rendering is deferred to Prompt 6.")
