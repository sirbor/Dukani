from oscar.apps.offer import models


class ChangesOwnerName(models.Benefit):
    """
    Sandbox demo of a deferred (post-order) benefit.

    Historically this overwrote the customer's first name — kept for fixture
    proxy_class stability but must not mutate user accounts.
    """

    class Meta:
        proxy = True
        app_label = "sandbox"

    def apply(self, basket, condition, offer=None):
        condition.consume_items(offer, basket, ())
        return models.PostOrderAction(
            "A post-order perk was recorded for this basket."
        )

    def apply_deferred(self, basket, order, application):
        return None

    @property
    def description(self):
        return "Deferred sample benefit (no account changes)"

    name = description
