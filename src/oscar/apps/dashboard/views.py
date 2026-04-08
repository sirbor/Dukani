import json
from datetime import datetime, timedelta
from decimal import ROUND_UP
from decimal import Decimal as D

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Avg, Count, Sum
from django.template.response import TemplateResponse
from django.urls import reverse_lazy
from django.utils import formats
from django.utils.dateparse import parse_date
from django.utils.timezone import get_current_timezone, localdate, localtime, make_aware, now
from django.utils.translation import get_language, to_locale
from django.views.generic import TemplateView

from oscar.core.compat import get_user_model
from oscar.core.loading import get_class, get_model

RelatedFieldWidgetWrapper = get_class("dashboard.widgets", "RelatedFieldWidgetWrapper")
ConditionalOffer = get_model("offer", "ConditionalOffer")
Voucher = get_model("voucher", "Voucher")
Basket = get_model("basket", "Basket")
StockAlert = get_model("partner", "StockAlert")
Product = get_model("catalogue", "Product")
Order = get_model("order", "Order")
Line = get_model("order", "Line")
User = get_user_model()


def dashboard_chart_intl_locale():
    """
    BCP 47 locale for Chart.js Intl formatting (tooltips / axis).
    """
    code = getattr(settings, "OSCAR_DEFAULT_CURRENCY", "") or ""
    if str(code).upper() == "KES":
        return "en-KE"
    loc = to_locale(get_language() or settings.LANGUAGE_CODE)
    return str(loc).replace("_", "-")


class IndexView(TemplateView):
    """
    An overview view which displays several reports about the shop.

    Supports the permission-based dashboard. It is recommended to add a
    :file:`oscar/dashboard/index_nonstaff.html` template because Oscar's
    default template will display potentially sensitive store information.
    """

    def get_template_names(self):
        if self.request.user.is_staff:
            return [
                "oscar/dashboard/index.html",
            ]
        else:
            return ["oscar/dashboard/index_nonstaff.html", "oscar/dashboard/index.html"]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        chart_start, chart_end = self._parse_sales_chart_range()
        ctx.update(self.get_stats(chart_start, chart_end))
        ctx["sales_chart_start"] = chart_start
        ctx["sales_chart_end"] = chart_end
        ctx["dashboard_currency"] = settings.OSCAR_DEFAULT_CURRENCY
        ctx["dashboard_chart_locale"] = dashboard_chart_intl_locale()
        return ctx

    def _parse_sales_chart_range(self):
        """
        Inclusive calendar date range from GET (``chart_start``, ``chart_end``),
        bounded and validated. Default: last 7 local calendar days ending today.
        """
        today = localdate()
        default_start = today - timedelta(days=6)
        default_end = today
        max_span_days = getattr(settings, "OSCAR_DASHBOARD_SALES_CHART_MAX_DAYS", 366)

        request = getattr(self, "request", None)
        if request is None:
            return default_start, default_end

        raw_start = request.GET.get("chart_start")
        raw_end = request.GET.get("chart_end")
        if not raw_start or not raw_end:
            return default_start, default_end

        start_d = parse_date(raw_start)
        end_d = parse_date(raw_end)
        if not start_d or not end_d or start_d > end_d:
            return default_start, default_end

        span = (end_d - start_d).days + 1
        if span > max_span_days:
            end_d = start_d + timedelta(days=max_span_days - 1)

        return start_d, end_d

    def get_active_vouchers(self):
        """
        Get all active vouchers. The returned ``Queryset`` of vouchers
        is filtered by end date greater then the current date.
        """
        return Voucher.objects.filter(end_datetime__gt=now())

    def get_hourly_report(self, orders, hours=24, segments=10):
        """
        Get report of order revenue split up in hourly chunks. A report is
        generated for the last *hours* (default=24) from the current time.
        The report provides ``max_revenue`` of the hourly order revenue sum,
        ``y-range`` as the labelling for the y-axis in a template and
        ``order_total_hourly``, a list of properties for hourly chunks.
        *segments* defines the number of labelling segments used for the y-axis
        when generating the y-axis labels (default=10).
        """
        # Get datetime for 24 hours ago
        time_now = now().replace(minute=0, second=0)
        start_time = time_now - timedelta(hours=hours - 1)

        order_total_hourly = []
        for _ in range(0, hours, 2):
            end_time = start_time + timedelta(hours=2)
            hourly_orders = orders.filter(
                date_placed__gte=start_time, date_placed__lt=end_time
            )
            total = hourly_orders.aggregate(Sum("total_incl_tax"))[
                "total_incl_tax__sum"
            ] or D("0.0")
            order_total_hourly.append({"end_time": end_time, "total_incl_tax": total})
            start_time = end_time

        max_value = max([x["total_incl_tax"] for x in order_total_hourly])
        divisor = 1
        while divisor < max_value / 50:
            divisor *= 10
        max_value = (max_value / divisor).quantize(D("1"), rounding=ROUND_UP)
        max_value *= divisor
        if max_value:
            segment_size = (max_value) / D("100.0")
            for item in order_total_hourly:
                item["percentage"] = int(item["total_incl_tax"] / segment_size)

            y_range = []
            y_axis_steps = max_value / D(str(segments))
            for idx in reversed(range(segments + 1)):
                y_range.append(idx * y_axis_steps)
        else:
            y_range = []
            for item in order_total_hourly:
                item["percentage"] = 0

        ctx = {
            "order_total_hourly": order_total_hourly,
            "max_revenue": max_value,
            "y_range": y_range,
        }
        return ctx

    def _finalize_chart_bars(self, bars, segments=10):
        """
        Shared y-axis scaling for bar lists with ``total_incl_tax`` and ``label``.
        """
        if not bars:
            return {
                "order_total_hourly": [],
                "max_revenue": D("0.0"),
                "y_range": [],
            }

        max_value = max(x["total_incl_tax"] for x in bars)
        divisor = 1
        while divisor < max_value / 50:
            divisor *= 10
        max_value = (max_value / divisor).quantize(D("1"), rounding=ROUND_UP)
        max_value *= divisor
        if max_value:
            segment_size = max_value / D("100.0")
            for item in bars:
                item["percentage"] = int(item["total_incl_tax"] / segment_size)

            y_range = []
            y_axis_steps = max_value / D(str(segments))
            for idx in reversed(range(segments + 1)):
                y_range.append(idx * y_axis_steps)
        else:
            y_range = []
            for item in bars:
                item["percentage"] = 0

        return {
            "order_total_hourly": bars,
            "max_revenue": max_value,
            "y_range": y_range,
        }

    def _chart_intraday_buckets(self, orders, day):
        """Twelve 2-hour buckets covering one local calendar day."""
        tz = get_current_timezone()
        day_start = make_aware(datetime.combine(day, datetime.min.time()), tz)
        bars = []
        cursor = day_start
        for _ in range(12):
            end_t = cursor + timedelta(hours=2)
            chunk = orders.filter(date_placed__gte=cursor, date_placed__lt=end_t)
            total = chunk.aggregate(Sum("total_incl_tax"))["total_incl_tax__sum"] or D(
                "0.0"
            )
            label = formats.date_format(localtime(end_t), format="TIME_FORMAT")
            bars.append(
                {"end_time": end_t, "label": label, "total_incl_tax": total},
            )
            cursor = end_t
        return bars

    def _chart_daily_buckets(self, orders, start_date, end_date):
        """One bar per local calendar day (inclusive)."""
        tz = get_current_timezone()
        bars = []
        cursor = start_date
        while cursor <= end_date:
            day_start = make_aware(datetime.combine(cursor, datetime.min.time()), tz)
            day_end = day_start + timedelta(days=1)
            chunk = orders.filter(date_placed__gte=day_start, date_placed__lt=day_end)
            total = chunk.aggregate(Sum("total_incl_tax"))["total_incl_tax__sum"] or D(
                "0.0"
            )
            label = formats.date_format(cursor, use_l10n=True)
            bars.append(
                {"end_time": day_end, "label": label, "total_incl_tax": total},
            )
            cursor = cursor + timedelta(days=1)
        return bars

    def get_sales_chart_report(self, orders, start_date, end_date, segments=10):
        """
        Revenue bars for the sales chart: hourly-ish buckets for a single day,
        otherwise one bucket per day between ``start_date`` and ``end_date`` (inclusive).
        """
        if start_date > end_date:
            start_date, end_date = end_date, start_date

        if start_date == end_date:
            bars = self._chart_intraday_buckets(orders, start_date)
        else:
            bars = self._chart_daily_buckets(orders, start_date, end_date)

        return self._finalize_chart_bars(bars, segments=segments)

    def get_stats(self, chart_start=None, chart_end=None):
        datetime_24hrs_ago = now() - timedelta(hours=24)

        orders = Order.objects.all()
        alerts = StockAlert.objects.all()
        baskets = Basket.objects.filter(status=Basket.OPEN)
        customers = User.objects.filter(orders__isnull=False).distinct()
        lines = Line.objects.filter()
        products = Product.objects.all()

        user = self.request.user
        if not user.is_staff:
            partners_ids = tuple(user.partners.values_list("id", flat=True))
            orders = orders.filter(lines__partner_id__in=partners_ids).distinct()
            alerts = alerts.filter(stockrecord__partner_id__in=partners_ids)
            baskets = baskets.filter(
                lines__stockrecord__partner_id__in=partners_ids
            ).distinct()
            customers = customers.filter(
                orders__lines__partner_id__in=partners_ids
            ).distinct()
            lines = lines.filter(partner_id__in=partners_ids)
            products = products.filter(stockrecords__partner_id__in=partners_ids)

        orders_last_day = orders.filter(date_placed__gt=datetime_24hrs_ago)

        if chart_start is None or chart_end is None:
            chart_start, chart_end = self._parse_sales_chart_range()

        open_alerts = alerts.filter(status=StockAlert.OPEN)
        closed_alerts = alerts.filter(status=StockAlert.CLOSED)

        total_lines_last_day = lines.filter(order__in=orders_last_day).count()
        stats = {
            "total_orders_last_day": orders_last_day.count(),
            "total_lines_last_day": total_lines_last_day,
            "average_order_costs": orders_last_day.aggregate(Avg("total_incl_tax"))[
                "total_incl_tax__avg"
            ]
            or D("0.00"),
            "total_revenue_last_day": orders_last_day.aggregate(Sum("total_incl_tax"))[
                "total_incl_tax__sum"
            ]
            or D("0.00"),
            "hourly_report_dict": self.get_sales_chart_report(
                orders, chart_start, chart_end
            ),
            "total_customers_last_day": customers.filter(
                date_joined__gt=datetime_24hrs_ago,
            ).count(),
            "total_open_baskets_last_day": baskets.filter(
                date_created__gt=datetime_24hrs_ago
            ).count(),
            "total_products": products.count(),
            "total_open_stock_alerts": open_alerts.count(),
            "total_closed_stock_alerts": closed_alerts.count(),
            "total_customers": customers.count(),
            "total_open_baskets": baskets.count(),
            "total_orders": orders.count(),
            "total_lines": lines.count(),
            "total_revenue": orders.aggregate(Sum("total_incl_tax"))[
                "total_incl_tax__sum"
            ]
            or D("0.00"),
            "order_status_breakdown": orders.order_by("status")
            .values("status")
            .annotate(freq=Count("id")),
        }
        if user.is_staff:
            stats.update(
                offer_maps=(
                    ConditionalOffer.objects.filter(end_datetime__gt=now())
                    .values("offer_type")
                    .annotate(count=Count("id"))
                    .order_by("offer_type")
                ),
                total_vouchers=self.get_active_vouchers().count(),
            )
        return stats


class PopUpWindowMixin:
    @property
    def is_popup(self):
        return self.request.GET.get(
            RelatedFieldWidgetWrapper.IS_POPUP_VAR,
            self.request.POST.get(RelatedFieldWidgetWrapper.IS_POPUP_VAR),
        )

    @property
    def is_popup_var(self):
        return RelatedFieldWidgetWrapper.IS_POPUP_VAR

    def add_success_message(self, message):
        if not self.is_popup:
            messages.info(self.request, message)


class PopUpWindowCreateUpdateMixin(PopUpWindowMixin):
    @property
    def to_field(self):
        return self.request.GET.get(
            RelatedFieldWidgetWrapper.TO_FIELD_VAR,
            self.request.POST.get(RelatedFieldWidgetWrapper.TO_FIELD_VAR),
        )

    @property
    def to_field_var(self):
        return RelatedFieldWidgetWrapper.TO_FIELD_VAR

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        if self.is_popup:
            ctx["to_field"] = self.to_field
            ctx["to_field_var"] = self.to_field_var
            ctx["is_popup"] = self.is_popup
            ctx["is_popup_var"] = self.is_popup_var

        return ctx


class PopUpWindowCreateMixin(PopUpWindowCreateUpdateMixin):
    def popup_response(self, obj):
        if self.to_field:
            attr = str(self.to_field)
        else:
            attr = obj._meta.pk.attname
        value = obj.serializable_value(attr)
        popup_response_data = json.dumps(
            {
                "value": str(value),
                "obj": str(obj),
            }
        )
        return TemplateResponse(
            self.request,
            "oscar/dashboard/widgets/popup_response.html",
            {
                "popup_response_data": popup_response_data,
            },
        )


class PopUpWindowUpdateMixin(PopUpWindowCreateUpdateMixin):
    def popup_response(self, obj):
        opts = obj._meta
        if self.to_field:
            attr = str(self.to_field)
        else:
            attr = opts.pk.attname
        # Retrieve the `object_id` from the resolved pattern arguments.
        value = self.request.resolver_match.kwargs["pk"]
        new_value = obj.serializable_value(attr)
        popup_response_data = json.dumps(
            {
                "action": "change",
                "value": str(value),
                "obj": str(obj),
                "new_value": str(new_value),
            }
        )
        return TemplateResponse(
            self.request,
            "oscar/dashboard/widgets/popup_response.html",
            {
                "popup_response_data": popup_response_data,
            },
        )


class PopUpWindowDeleteMixin(PopUpWindowMixin):
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        if self.is_popup:
            ctx["is_popup"] = self.is_popup
            ctx["is_popup_var"] = self.is_popup_var

        return ctx

    def delete(self, request, *args, **kwargs):
        """
        Calls the delete() method on the fetched object and then
        redirects to the success URL, or closes the popup, it it is one.
        """
        obj = self.get_object()

        response = super().delete(request, *args, **kwargs)

        if self.is_popup:
            obj_id = obj.pk
            popup_response_data = json.dumps(
                {
                    "action": "delete",
                    "value": str(obj_id),
                }
            )
            return TemplateResponse(
                request,
                "oscar/dashboard/widgets/popup_response.html",
                {
                    "popup_response_data": popup_response_data,
                },
            )
        else:
            return response

    def post(self, request, *args, **kwargs):
        """
        Calls the delete() method on the fetched object and then
        redirects to the success URL, or closes the popup, it it is one.
        """
        return self.delete(request, *args, **kwargs)


class LoginView(auth_views.LoginView):
    template_name = "oscar/dashboard/login.html"
    authentication_form = AuthenticationForm
    login_redirect_url = reverse_lazy("dashboard:index")

    def get_success_url(self):
        url = self.get_redirect_url()
        return url or self.login_redirect_url
