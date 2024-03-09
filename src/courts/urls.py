from rest_framework.routers import DefaultRouter
from . import views

app_name = "courts"

router = DefaultRouter()
router.register("", views.CourtsViewSet, "courts")
urlpatterns = router.urls