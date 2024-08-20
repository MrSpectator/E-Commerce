from django.urls import path

from . import views

from django.conf import settings

from django.conf.urls.static import static

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("create/", views.create_listing, name="listing"),
    path("active/", views.listing_view, name="active"),
    path("<int:listing_id>", views.listing, name="listing"),
    path('watchlist/add/<int:listing_id>/', views.add_watchlist, name='add_watchlist'),
    path('watchlist/remove/<int:listing_id>/', views.remove_watchlist, name='remove_watchlist'),
    path('bid/<int:listing_id>/', views.bid, name='bid'),
    path('listings/<int:pk>/', views.close_listing, name='close_listing'),
    path('comments/<int:pk>/', views.comments, name='comments'),
    path('watchlist/', views.watchlist, name='watchlist'),
    path('categories/', views.categories, name='categories'),
    path('categories/<str:category_name>', views.category, name='category'),
]