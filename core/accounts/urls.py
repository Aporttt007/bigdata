from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, AreaViewSet, RegionViewSet, TicketListView

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'areas', AreaViewSet)
router.register(r'regions', RegionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('tickets/', TicketListView.as_view(), name='ticket-list'),]
