from django.urls import path, include
from . import views
from django.views.generic import TemplateView

from .views import CustomPasswordResetView, CustomPasswordResetDoneView, CustomPasswordResetConfirmView, CustomPasswordResetCompleteView




app_name = 'tabelog'

urlpatterns = [
    path('', views.TopView.as_view(), name='index'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('mypage/<int:pk>/', views.MyPage.as_view(), name='mypage'),
    path('signup/', views.Signup.as_view(), name='signup'),
    path('member/<int:pk>/', views.MemberView.as_view(), name='member'),
    path('list/', views.StoreListView.as_view(), name='storelist'),
    path('detail/<int:pk>', views.StoreDetailView.as_view(), name='store_detail'),
    path('detail/<int:pk>/reservation/', views.ReservationView.as_view(), name='reservation'),
    path('mypage/<int:pk>/reservations/', views.ReservationListView.as_view(), name='reservation_list'),
    path('reservation/cancel/<int:pk>/', views.ReservationDeleteView.as_view(), name='cancel_reservation'),
    path('reservation/update/<int:pk>/', views.ReservationUpdateView.as_view(), name='update_reservation'),
    path('store/<int:pk>/reviews/', views.ReviewListView.as_view(), name='review_list'),
    path('store/<int:pk>/review/create/', views.ReviewCreateView.as_view(), name='review_create'),
    path('review/<int:pk>/edit/', views.ReviewUpdateView.as_view(), name='review_edit'),  # ここが重要
    path('review/<int:pk>/delete/', views.ReviewDeleteView.as_view(), name='review_delete'),
    path('mypage/<int:pk>/favorites/', views.FavoriteListView.as_view(), name='favorite_list'),
    path('mypage/<int:pk>/favorites/', views.FavoriteListView.as_view(), name='favorite_list'),
    path('store/<int:pk>/favorite/add/', views.AddFavoriteView.as_view(), name='add_favorite'),
    path('store/<int:pk>/favorite/remove/', views.RemoveFavoriteView.as_view(), name='remove_favorite'),
    path('subscribe/', views.SubscriptionView.as_view(), name='subscribe'),
    path('subscription_success/', TemplateView.as_view(template_name="subscription_success.html"), name='subscription_success'),
    path('unsubscribe/', views.UnsubscribeView.as_view(), name='unsubscribe'),
    path('delete_account/', views.DeleteAccountView.as_view(), name='delete_account'),
    path('update_user/', views.UserUpdateView.as_view(), name='update_user'),
    path('password_change/', views.PasswordChange.as_view(), name='password_change'),
    path('password_change/done/', views.PasswordChangeDone.as_view(), name='password_change_done'),
    path('password_reset/', views.PasswordReset.as_view(), name='password_reset'), #追加
    path('password_reset/done/', views.PasswordResetDone.as_view(), name='password_reset_done'), #追加
    path('reset/<uidb64>/<token>/', views.PasswordResetConfirm.as_view(), name='password_reset_confirm'), #追加
    path('reset/done/', views.PasswordResetComplete.as_view(), name='password_reset_complete'), #追加
]