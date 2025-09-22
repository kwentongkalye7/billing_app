from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from accounts.api import UserViewSet, AuthViewSet
from clients.api import ClientViewSet, ContactViewSet
from engagements.api import EngagementViewSet
from statements.api import BillingStatementViewSet, BillingItemViewSet
from payments.api import PaymentViewSet, PaymentAllocationViewSet, UnappliedCreditViewSet
from sequences.api import SequenceViewSet
from reports.api import AgingReportView, CollectionsRegisterView, UnappliedCreditReportView, AuditLogView
from audit.api import AuditLogViewSet

router = routers.DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"clients", ClientViewSet, basename="client")
router.register(r"contacts", ContactViewSet, basename="contact")
router.register(r"engagements", EngagementViewSet, basename="engagement")
router.register(r"billing-statements", BillingStatementViewSet, basename="billing-statement")
router.register(r"billing-items", BillingItemViewSet, basename="billing-item")
router.register(r"payments", PaymentViewSet, basename="payment")
router.register(r"payment-allocations", PaymentAllocationViewSet, basename="payment-allocation")
router.register(r"unapplied-credits", UnappliedCreditViewSet, basename="unapplied-credit")
router.register(r"sequences", SequenceViewSet, basename="sequence")
router.register(r"audit-logs", AuditLogViewSet, basename="audit-log")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/auth/login/", AuthViewSet.as_view({"post": "login"}), name="auth-login"),
    path("api/auth/logout/", AuthViewSet.as_view({"post": "logout"}), name="auth-logout"),
    path("api/reports/aging/", AgingReportView.as_view(), name="report-aging"),
    path("api/reports/collections/", CollectionsRegisterView.as_view(), name="report-collections"),
    path("api/reports/unapplied-credits/", UnappliedCreditReportView.as_view(), name="report-unapplied"),
    path("api/reports/audit/", AuditLogView.as_view(), name="report-audit"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/docs/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
