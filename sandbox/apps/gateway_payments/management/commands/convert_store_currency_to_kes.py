"""
Maintenance: convert persisted GBP money amounts to KES (default: 1 GBP = 171 KES).

Rows **tagged** ``GBP`` (case-insensitive) are converted on stock, basket lines, orders,
and payment intents. Oscar offers/vouchers and shipping charges have no per-row currency;
use ``--include-offers`` / ``--include-shipping`` only if those numbers were still pounds.
"""

from decimal import Decimal

from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import F

GBP_Q = "gbp"
TARGET_CCY = "KES"

# `offer.Benefit.type` values where `value` is a money amount (not % or multibuy).
BENEFIT_MONEY_TYPES = (
    "Absolute",
    "Fixed",
    "Fixed price",
    "Shipping absolute",
    "Shipping fixed price",
)


class Command(BaseCommand):
    help = (
        "Multiply GBP-priced rows by the KES rate and set currency to KES. "
        "Stock records, basket lines, and (by default) GBP orders and gateway intents."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--rate",
            default="171",
            help="How many KES for one GBP (default: 171).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print row counts only; do not write to the database.",
        )
        parser.add_argument(
            "--skip-orders",
            action="store_true",
            help="Skip orders, line prices, discounts, surcharges, payment events/sources/transactions.",
        )
        parser.add_argument(
            "--skip-payment-intents",
            action="store_true",
            help="Skip gateway PaymentIntent rows marked GBP.",
        )
        parser.add_argument(
            "--include-shipping",
            action="store_true",
            help=(
                "Also scale shipping.OrderAndItemCharges and shipping.WeightBand "
                "charges (no per-row currency—only if these were still in pounds)."
            ),
        )
        parser.add_argument(
            "--include-offers",
            action="store_true",
            help=(
                "Also scale offer.ConditionalOffer (max/total discount), monetary "
                "offer.Benefit values, offer.Condition 'Value' thresholds, and "
                "voucher.Voucher total_discount (no currency columns—only if these "
                "were configured in pounds)."
            ),
        )

    def handle(self, *args, **options):
        rate = Decimal(str(options["rate"]))
        dry_run = options["dry_run"]
        skip_orders = options["skip_orders"]
        skip_intents = options["skip_payment_intents"]
        include_shipping = options["include_shipping"]
        include_offers = options["include_offers"]

        def line(msg):
            self.stdout.write(msg)

        StockRecord = apps.get_model("partner", "StockRecord")
        BasketLine = apps.get_model("basket", "Line")

        stock_qs = StockRecord.objects.filter(price_currency__iexact=GBP_Q)
        basket_qs = BasketLine.objects.filter(price_currency__iexact=GBP_Q)

        line(f"Stock records (GBP): {stock_qs.count()}")
        line(f"Basket lines (GBP): {basket_qs.count()}")

        order_ids = []
        if not skip_orders:
            Order = apps.get_model("order", "Order")
            order_ids = list(
                Order.objects.filter(currency__iexact=GBP_Q).values_list("pk", flat=True)
            )
            line(f"Orders (GBP): {len(order_ids)}")

        intent_qs = None
        if not skip_intents:
            try:
                PaymentIntent = apps.get_model("gateway_payments", "PaymentIntent")
            except LookupError:
                PaymentIntent = None
            if PaymentIntent is not None:
                intent_qs = PaymentIntent.objects.filter(currency__iexact=GBP_Q)
                line(f"PaymentIntent (GBP): {intent_qs.count()}")

        shipping_oaic = shipping_wb = None
        if include_shipping:
            OrderAndItemCharges = apps.get_model("shipping", "OrderAndItemCharges")
            WeightBand = apps.get_model("shipping", "WeightBand")
            shipping_oaic = OrderAndItemCharges.objects.all()
            shipping_wb = WeightBand.objects.all()
            line(f"Shipping OrderAndItemCharges (all): {shipping_oaic.count()}")
            line(f"Shipping WeightBand rows (all): {shipping_wb.count()}")

        if include_offers:
            ConditionalOffer = apps.get_model("offer", "ConditionalOffer")
            Benefit = apps.get_model("offer", "Benefit")
            Condition = apps.get_model("offer", "Condition")
            Voucher = apps.get_model("voucher", "Voucher")
            line(f"ConditionalOffer (all): {ConditionalOffer.objects.count()}")
            line(
                "offer.Benefit (monetary types): "
                f"{Benefit.objects.filter(type__in=BENEFIT_MONEY_TYPES).count()}"
            )
            line(f"offer.Condition (Value): {Condition.objects.filter(type='Value').count()}")
            line(f"voucher.Voucher (all): {Voucher.objects.count()}")

        if dry_run:
            line(self.style.WARNING("Dry run — no changes written."))
            return

        with transaction.atomic():
            updated_sr = stock_qs.update(
                price=F("price") * rate,
                price_currency=TARGET_CCY,
            )
            updated_bl = basket_qs.update(
                price_excl_tax=F("price_excl_tax") * rate,
                price_incl_tax=F("price_incl_tax") * rate,
                price_currency=TARGET_CCY,
            )
            line(
                self.style.SUCCESS(
                    f"Updated {updated_sr} stock record(s), {updated_bl} basket line(s)."
                )
            )

            if order_ids:
                LinePrice = apps.get_model("order", "LinePrice")
                OrderLine = apps.get_model("order", "Line")
                PaymentEvent = apps.get_model("order", "PaymentEvent")
                OrderDiscount = apps.get_model("order", "OrderDiscount")
                OrderLineDiscount = apps.get_model("order", "OrderLineDiscount")
                Surcharge = apps.get_model("order", "Surcharge")
                Source = apps.get_model("payment", "Source")
                Transaction = apps.get_model("payment", "Transaction")
                Order = apps.get_model("order", "Order")

                LinePrice.objects.filter(order_id__in=order_ids).update(
                    price_incl_tax=F("price_incl_tax") * rate,
                    price_excl_tax=F("price_excl_tax") * rate,
                    shipping_incl_tax=F("shipping_incl_tax") * rate,
                    shipping_excl_tax=F("shipping_excl_tax") * rate,
                )
                OrderLine.objects.filter(order_id__in=order_ids).update(
                    line_price_incl_tax=F("line_price_incl_tax") * rate,
                    line_price_excl_tax=F("line_price_excl_tax") * rate,
                    line_price_before_discounts_incl_tax=F(
                        "line_price_before_discounts_incl_tax"
                    )
                    * rate,
                    line_price_before_discounts_excl_tax=F(
                        "line_price_before_discounts_excl_tax"
                    )
                    * rate,
                    unit_price_incl_tax=F("unit_price_incl_tax") * rate,
                    unit_price_excl_tax=F("unit_price_excl_tax") * rate,
                )
                PaymentEvent.objects.filter(order_id__in=order_ids).update(
                    amount=F("amount") * rate,
                )
                OrderDiscount.objects.filter(order_id__in=order_ids).update(
                    amount=F("amount") * rate,
                )
                OrderLineDiscount.objects.filter(line__order_id__in=order_ids).update(
                    amount=F("amount") * rate,
                )
                Surcharge.objects.filter(order_id__in=order_ids).update(
                    incl_tax=F("incl_tax") * rate,
                    excl_tax=F("excl_tax") * rate,
                )
                Source.objects.filter(order_id__in=order_ids).update(
                    amount_allocated=F("amount_allocated") * rate,
                    amount_debited=F("amount_debited") * rate,
                    amount_refunded=F("amount_refunded") * rate,
                    currency=TARGET_CCY,
                )
                Transaction.objects.filter(source__order_id__in=order_ids).update(
                    amount=F("amount") * rate,
                )
                updated_ord = Order.objects.filter(pk__in=order_ids).update(
                    total_incl_tax=F("total_incl_tax") * rate,
                    total_excl_tax=F("total_excl_tax") * rate,
                    shipping_incl_tax=F("shipping_incl_tax") * rate,
                    shipping_excl_tax=F("shipping_excl_tax") * rate,
                    currency=TARGET_CCY,
                )
                line(self.style.SUCCESS(f"Updated {updated_ord} order(s) and related rows."))

            if intent_qs is not None:
                n = intent_qs.update(amount=F("amount") * rate, currency=TARGET_CCY)
                line(self.style.SUCCESS(f"Updated {n} payment intent(s)."))

            if include_shipping and shipping_oaic is not None:
                n1 = shipping_oaic.update(
                    price_per_order=F("price_per_order") * rate,
                    price_per_item=F("price_per_item") * rate,
                    free_shipping_threshold=F("free_shipping_threshold") * rate,
                )
                n2 = shipping_wb.update(charge=F("charge") * rate)
                line(
                    self.style.SUCCESS(
                        f"Shipping: {n1} order/item charge method(s), {n2} weight band(s)."
                    )
                )

            if include_offers:
                ConditionalOffer = apps.get_model("offer", "ConditionalOffer")
                Benefit = apps.get_model("offer", "Benefit")
                Condition = apps.get_model("offer", "Condition")
                Voucher = apps.get_model("voucher", "Voucher")

                n_co = ConditionalOffer.objects.update(
                    max_discount=F("max_discount") * rate,
                    total_discount=F("total_discount") * rate,
                )
                n_ben = Benefit.objects.filter(type__in=BENEFIT_MONEY_TYPES).update(
                    value=F("value") * rate,
                )
                n_cond = Condition.objects.filter(type="Value").update(
                    value=F("value") * rate,
                )
                n_v = Voucher.objects.update(total_discount=F("total_discount") * rate)
                line(
                    self.style.SUCCESS(
                        "Offers: "
                        f"{n_co} conditional offer(s), {n_ben} benefit(s), "
                        f"{n_cond} value condition(s), {n_v} voucher(s)."
                    )
                )

        line(self.style.SUCCESS("Done."))
