from django.urls import path
from .views import ServiceListView, ServiceCreateView, ServiceDeleteView

urlpatterns = [
    path('list/', ServiceListView.as_view(), name='service-list'),
    path('create/', ServiceCreateView.as_view(), name='service-create'),
    path('delete/<int:pk>/', ServiceDeleteView.as_view(), name='service-delete'),
    #
]
