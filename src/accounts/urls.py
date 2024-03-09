from rest_framework.routers import DefaultRouter
from . import views

app_name = "accounts"

router = DefaultRouter()
router.register("", views.AccountViewSet, basename="accounts")
urlpatterns = router.urls