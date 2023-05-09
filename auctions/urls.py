from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.createListing, name='create'),
    path("listing/<int:id>", views.view_listing, name='listing'),
    path("addwatchers/<int:id>", views.addwatchers, name='addwatchers'),
    path("removewatchers/<int:id>", views.removewatchers, name='removewatchers'),
    path("watchlist", views.watchlist, name="watchlist"),
    path("addcomment/<int:id>", views.addComment, name="addcomment"),
    path("addbid/<int:id>", views.addBid, name="addBid"),
    path("closeauction/<int:id>", views.closeAuction, name="closeauction"),
    path("openauction/<int:id>", views.openAuction, name="openauction"),
]
