from django.conf import settings
from typing import Any
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model, login, authenticate, logout
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView, 
    PasswordResetCompleteView, PasswordResetConfirmView, PasswordResetView, 
    PasswordResetDoneView
)
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views import generic, View
from django.views.generic.edit import FormView, DeleteView
from django.urls import reverse_lazy, reverse
from django.db.models import Q, Avg
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import TemplateView, UpdateView
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import PasswordResetForm
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

import stripe

from .forms import (
    SignupForm, MyPasswordChangeForm, LoginForm, StoreSearchForm, 
    ReservationForm, ReviewForm, UserUpdateForm, PaymentForm
)
from .models import User, Store, Category, Reservation, Review, Favorite, Subscription


# 有料会員専用ビューのアクセス制御用Mixin
class PremiumUserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.member_type == '2'

'''トップページ'''
class TopView(generic.TemplateView):
    template_name = 'tabelog/index.html'
    form_class = StoreSearchForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class()
        
        high_rating_stores = Store.objects.annotate(average_score=Avg('review__score')).order_by('-average_score')[:6]
        categories = Category.objects.all()
        new_stores = Store.objects.order_by('-created_at')[:6]

        context['high_rating_stores'] = high_rating_stores
        context['categories'] = categories
        context['new_stores'] = new_stores
        
        return context

'''サインアップ'''
class Signup(FormView):
    template_name = 'tabelog/signup.html'
    form_class = SignupForm
    success_url = reverse_lazy('tabelog:index')  # ホームページのURL名前を適宜修正

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)
'''
class Signup(generic.CreateView):
    template_name = 'tabelog/signup.html'
    form_class = SignupForm
    success_url = reverse_lazy("tabelog:index") 

    def  form_valid(self, form):
        # ユーザー作成後にそのままログイン状態にする設定
        response = super().form_valid(form)
        mail_address = form.cleaned_data.get("mail_address")
        password = form.cleaned_data.get("password1")
        user = authenticate(mail_address=mail_address, password=password)
        login(self.request, user)
        return response
        
         # return redirect('tabelog:signup_done')

    # データ送信
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['process_name'] = '新規会員登録'
        return context
'''

'''ログイン'''
class Login(LoginView):
    template_name = 'tabelog/login.html'
    form_class = LoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('tabelog:index')

'''ログアウト'''
class Logout(LogoutView):
    success_url = reverse_lazy('tabelog:index')
    '''
    template_name = 'tabelog/logout.html'
    '''

'''マイページ'''
class MyPage(generic.DetailView):
    model = User
    template_name = 'tabelog/mypage.html'
    context_object_name = 'user'

    def get_queryset(self):
        return User.objects.all()


'''会員情報ページ'''
class MemberView(generic.DetailView):
    model = User
    template_name = 'tabelog/member.html'
    context_object_name = 'user'

    def get_queryset(self):
        return User.objects.all() 
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(context['user'].furigana)  # デバッグ用
        print(context['user'].postal_code)  # デバッグ用
        print(context['user'].address)  # デバッグ用
        print(context['user'].phone_number)  # デバッグ用
        return context


'''キーワード検索'''
class StoreListView(generic.ListView):
    model = Store
    template_name = 'tabelog/storelist.html'
    context_object_name = 'stores'
    paginate_by = 10
        
    def get_queryset(self):
        queryset = Store.objects.all()
        keyword = self.request.GET.get('keyword')
        category_id = self.request.GET.get('category')
        budget = self.request.GET.get('budget')
        sort_by = self.request.GET.get('sort_by')

        if keyword:
            # ForeignKeyのフィールドを指定
            queryset = queryset.filter(
                Q(name__icontains=keyword) |
                Q(description__icontains=keyword) |
                Q(address__icontains=keyword) |
                Q(category__name__icontains=keyword)
            ).distinct()

        if category_id:
            queryset = queryset.filter(category_id=category_id)

        if budget:
            if budget == '1':
                queryset = queryset.filter(
                    Q(lowest_price__lte=999) | Q(highest_price__lte=999)
                )
            elif budget == '2':
                queryset = queryset.filter(
                    Q(lowest_price__gte=1000, highest_price__lte=2999) |
                    Q(lowest_price__lte=2999, highest_price__gte=1000) |
                    Q(lowest_price__gte=1000, lowest_price__lte=2999) |
                    Q(highest_price__gte=1000, highest_price__lte=2999)
                )
            elif budget == '3':
                queryset = queryset.filter(
                    Q(lowest_price__gte=3000, highest_price__lte=4999) |
                    Q(lowest_price__lte=4999, highest_price__gte=3000) |
                    Q(lowest_price__gte=3000, lowest_price__lte=4999) |
                    Q(highest_price__gte=3000, highest_price__lte=4999)
                )
            elif budget == '4':
                queryset = queryset.filter(
                    Q(lowest_price__gte=5000, highest_price__lte=9999) |
                    Q(lowest_price__lte=9999, highest_price__gte=5000) |
                    Q(lowest_price__gte=5000, lowest_price__lte=9999) |
                    Q(highest_price__gte=5000, highest_price__lte=9999)
                )
            elif budget == '5':
                queryset = queryset.filter(
                    Q(lowest_price__gte=10000) | Q(highest_price__gte=10000)
                )


        # 並べ替えのオプションに基づいてクエリセットを並べ替え
        if sort_by == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sort_by == 'highest_rating':
            queryset = queryset.annotate(average_score=Avg('review__score')).order_by('-average_score')
        elif sort_by == 'lowest_price':
            queryset = queryset.order_by('lowest_price')
        elif sort_by == 'highest_price':
            queryset = queryset.order_by('-lowest_price')


        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['form'] = StoreSearchForm(self.request.GET)
        return context

'''ページネーション設定'''
def paginate_queryset(request, queryset, count):
    
    paginator = Paginator(queryset, count)
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    return page_obj

def post_index(request):
    post_list = Store.objects.all()
    page_obj = paginate_queryset(request, post_list, 1)
    context = {
        'post_list': page_obj.object_list,
        'page_obj': page_obj,
    }
    return render(request, 'tabelog/storelist.html', context)

def post_reserve(request):
    post_list = Reservation.objects.all()
    page_obj = paginate_queryset(request, post_list, 1)
    context = {
        'post_list': page_obj.object_list,
        'page_obj': page_obj,
    }
    return render(request, 'tabelog/reservation_list.html', context)

def post_review(request):
    post_list = Review.objects.all()
    page_obj = paginate_queryset(request, post_list, 1)
    context = {
        'post_list': page_obj.object_list,
        'page_obj': page_obj,
    }
    return render(request, 'tabelog/review_list.html', context)

def post_favorite(request):
    post_list = Favorite.objects.all()
    page_obj = paginate_queryset(request, post_list, 1)
    context = {
        'post_list': page_obj.object_list,
        'page_obj': page_obj,
    }
    return render(request, 'tabelog/favorite_list.html', context)



'''店舗詳細ページ'''
class StoreDetailView(generic.DetailView):
    model = Store
    template_name = 'tabelog/store_detail.html'
    context_object_name = 'store'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        store_id = self.kwargs['pk']
        reviews = Review.objects.filter(store_id=store_id)
        context['average_score'] = reviews.aggregate(Avg('score'))['score__avg'] or 0
        context['review_count'] = reviews.count()
        context['store'] = get_object_or_404(Store, pk=self.kwargs['pk'])
        return context


'''予約ページ'''
class ReservationView(PremiumUserRequiredMixin, FormView):
    template_name = 'tabelog/reservation.html'
    form_class = ReservationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        store_id = self.kwargs['pk']
        reviews = Review.objects.filter(store_id=store_id)
        context['average_score'] = reviews.aggregate(Avg('score'))['score__avg'] or 0
        context['review_count'] = reviews.count()
        context['store'] = get_object_or_404(Store, pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        reservation = form.save(commit=False)
        reservation.store = get_object_or_404(Store, pk=self.kwargs['pk'])
        reservation.user = self.request.user
        reservation.save()
        return redirect('tabelog:store_detail', pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse('tabelog:store_detail', kwargs={'pk': self.kwargs['pk']})


'''予約変更'''
class ReservationUpdateView(PremiumUserRequiredMixin, generic.UpdateView):
    model = Reservation
    form_class = ReservationForm
    template_name = 'tabelog/reservation_update.html'

    def form_valid(self, form):
        try:
            reservation = form.save(commit=False)
            reservation.reserved_date = form.cleaned_data['reserved_date']
            reservation.reserved_time = form.cleaned_data['reserved_time']
            reservation.number_of_people = form.cleaned_data['number_of_people']
            reservation.save()
            messages.success(self.request, "予約が正常に更新されました。")
            return redirect('tabelog:reservation_list', pk=self.request.user.pk)
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)

    def get_initial(self):
        initial = super().get_initial()
        reservation = self.get_object()
        initial['reserved_date'] = reservation.reserved_date
        initial['reserved_time'] = reservation.reserved_time.strftime("%H:%M")
        initial['number_of_people'] = reservation.number_of_people
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reservation = self.get_object()
        store = reservation.store
        reviews = Review.objects.filter(store=store)
        average_score = reviews.aggregate(Avg('score'))['score__avg'] or 0
        review_count = reviews.count()

        context['reservation'] = reservation
        context['average_score'] = average_score
        context['review_count'] = review_count
        context['store'] = store
        context['times'] = [
            "11:00", "11:30", "12:00", "12:30", "13:00", "13:30", "14:00", "14:30",
            "15:00", "15:30", "16:00", "16:30", "17:00", "17:30", "18:00", "18:30",
            "19:00", "19:30", "20:00", "20:30", "21:00", "21:30", "22:00", "22:30",
            "23:00", "23:30"
        ]
        context['people'] = [str(i) for i in range(1, 26)] + ["25人以上", "50人以上"]
        return context





'''予約一覧ページ'''
class ReservationListView(PremiumUserRequiredMixin, generic.ListView):
    model = Reservation
    template_name = 'tabelog/reservation_list.html'
    context_object_name = 'reservations'
    paginate_by = 10  # 1ページに表示する予約の数


    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user).order_by('reserved_date')


'''予約キャンセル'''
class ReservationDeleteView(PremiumUserRequiredMixin, generic.DeleteView):
    model = Reservation
    success_url = reverse_lazy('tabelog:reservation_list')  # 削除後のリダイレクト先を指定

    def get_success_url(self):
        return reverse_lazy('tabelog:reservation_list', kwargs={'pk': self.request.user.pk})


'''レビュー一覧'''
class ReviewListView(generic.ListView):
    model = Review
    template_name = 'tabelog/review_list.html'
    context_object_name = 'reviews'
    paginate_by = 10

    def get_queryset(self):
        store = get_object_or_404(Store, pk=self.kwargs['pk'])
        return Review.objects.filter(store=store).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        store_id = self.kwargs['pk']
        reviews = Review.objects.filter(store_id=store_id)
        context['average_score'] = reviews.aggregate(Avg('score'))['score__avg'] or 0
        context['review_count'] = reviews.count()
        context['store'] = get_object_or_404(Store, pk=store_id)
        return context
    

'''レビュー投稿'''
class ReviewCreateView(PremiumUserRequiredMixin, generic.CreateView):
    model = Review
    form_class = ReviewForm
    template_name = 'tabelog/review_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.store = get_object_or_404(Store, pk=self.kwargs['pk'])
        form.save()
        return redirect('tabelog:store_detail', pk=self.kwargs['pk'])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        store_id = self.kwargs['pk']
        reviews = Review.objects.filter(store_id=store_id)
        context['average_score'] = reviews.aggregate(Avg('score'))['score__avg'] or 0
        context['review_count'] = reviews.count()
        context['store'] = get_object_or_404(Store, pk=self.kwargs['pk'])
        return context

'''レビュー編集'''
class ReviewUpdateView(PremiumUserRequiredMixin, generic.UpdateView):
    model = Review
    form_class = ReviewForm
    template_name = 'tabelog/review_form.html'

    def get_success_url(self):
        return reverse_lazy('tabelog:review_list', kwargs={'pk': self.object.store.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        store_id = self.object.store.pk
        reviews = Review.objects.filter(store_id=store_id)
        context['average_score'] = reviews.aggregate(Avg('score'))['score__avg'] or 0
        context['review_count'] = reviews.count()
        context['store'] = self.object.store
        return context



'''レビュー削除'''
class ReviewDeleteView(PremiumUserRequiredMixin, generic.DeleteView):
    model = Review
    success_url = reverse_lazy('tabelog:review_list')  # 'tabelog:'プレフィックスを追加

    def get_success_url(self):
        return reverse_lazy('tabelog:review_list', kwargs={'pk': self.object.store.pk})

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)
    

'''お気に入り一覧'''
class FavoriteListView(PremiumUserRequiredMixin, generic.ListView):
    model = Favorite
    template_name = 'tabelog/favorite_list.html'
    context_object_name = 'favorites'
    
    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)


'''お気に入り追加'''
class AddFavoriteView(PremiumUserRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        store = get_object_or_404(Store, pk=pk)
        Favorite.objects.get_or_create(user=request.user, store=store)
        return redirect('tabelog:store_detail', pk=pk)

'''お気に入り削除'''
class RemoveFavoriteView(PremiumUserRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        store = get_object_or_404(Store, pk=pk)
        favorite = get_object_or_404(Favorite, user=request.user, store=store)
        favorite.delete()
        return redirect('tabelog:favorite_list', pk=request.user.pk)



'''サインアップ完了'''
class SignupDone(generic.TemplateView):
    template_name = 'tabelog/signup_done.html'

'''パスワード変更'''
class PasswordChange(PasswordChangeView):
    form_class = MyPasswordChangeForm
    success_url = reverse_lazy('tabelog:password_change_done')
    template_name = 'tabelog/signup.html'

    # contextデータ作成
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["process_name"] = "パスワード変更"
        return context



'''Stripe設定'''
stripe.api_key = settings.STRIPE_SECRET_KEY


    

class SubscriptionView(TemplateView):
    template_name = 'tabelog/subscription.html'
    
    def get(self, request):
        form = PaymentForm()
        return render(request, 'tabelog/subscription.html', {'form': form, 'stripe_key': settings.STRIPE_PUBLISHABLE_KEY})

    def post(self, request):
        form = PaymentForm(request.POST)
        if form.is_valid():
            token = form.cleaned_data['stripe_token']
            try:
                # Stripe顧客を作成
                customer = stripe.Customer.create(
                    email=request.user.mail_address,
                    source=token
                )
                
                # サブスクリプションを作成
                subscription = stripe.Subscription.create(
                    customer=customer.id,
                    items=[
                        {"price": "price_1PRjIzEeOXAXQMHKS2QpR0Mn"}  # Stripeダッシュボードで作成した価格ID
                    ],
                )

                # サブスクリプション情報を保存
                Subscription.objects.create(
                    user=request.user,
                    stripe_subscription_id=subscription.id
                )

                # ユーザーのmember_typeを有料に変更
                request.user.member_type = '2'
                request.user.save()
                
                return redirect('tabelog:index')
            except stripe.error.StripeError as e:
                return render(request, 'tabelog/subscription.html', {'form': form, 'stripe_key': settings.STRIPE_PUBLISHABLE_KEY, 'error': str(e)})

        return render(request, 'tabelog/subscription.html', {'form': form, 'stripe_key': settings.STRIPE_PUBLISHABLE_KEY})

from django.views import View
from django.shortcuts import render, redirect
import stripe
from django.conf import settings
from .models import Subscription

class UnsubscribeView(View):
    template_name = 'tabelog/unsubscribe.html'
    
    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        try:
            # ユーザーのサブスクリプションを全て取得
            subscriptions = Subscription.objects.filter(user=request.user)
            if subscriptions.exists():
                for subscription in subscriptions:
                    stripe.Subscription.delete(subscription.stripe_subscription_id)
                    subscription.delete()
                
                # ユーザーのmember_typeを無料に変更
                request.user.member_type = '1'  # 無料
                request.user.save()

                return redirect('tabelog:index')
            else:
                return render(request, self.template_name, {'error': 'サブスクリプションが見つかりませんでした。'})
        except stripe.error.StripeError as e:
            return render(request, self.template_name, {'error': str(e)})


class DeleteAccountView(LoginRequiredMixin, View):
    template_name = 'tabelog/delete_account.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        user = request.user
        
        # クレジットカード情報の削除
        try:
            subscription = Subscription.objects.filter(user=user)
            for sub in subscription:
                stripe.Subscription.delete(sub.stripe_subscription_id)
                sub.delete()
        except Subscription.DoesNotExist:
            pass
        
        # 予約データの削除
        Reservation.objects.filter(user=user).delete()

        # お気に入りデータの削除
        Favorite.objects.filter(user=user).delete()

        # レビューデータの削除
        Review.objects.filter(user=user).delete()

        # ユーザーデータの削除
        user.delete()

        # ログアウト
        logout(request)
        
        return redirect(reverse_lazy('tabelog:index'))


class UserUpdateView(generic.UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'tabelog/update_user.html'

    def get_success_url(self):
        return reverse_lazy('tabelog:member', kwargs={'pk': self.request.user.pk})

    def get_object(self):
        return self.request.user



class index(LoginRequiredMixin, generic.TemplateView):
    """メニュービュー"""
    template_name = 'tabelog/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) # 継承元のメソッドCALL
        context["form_name"] = "top"
        return context


class PasswordChange(LoginRequiredMixin, PasswordChangeView):
    """パスワード変更ビュー"""
    success_url = reverse_lazy('tabelog:password_change_done')
    template_name = 'tabelog/password_change.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) # 継承元のメソッドCALL
        context["form_name"] = "password_change"
        return context


class PasswordChangeDone(LoginRequiredMixin,PasswordChangeDoneView):
    """パスワード変更しました"""
    template_name = 'tabelog/password_change_done.html'

# --- ここから追加
class PasswordReset(PasswordResetView):
    """パスワード変更用URLの送付ページ"""
    subject_template_name = 'tabelog/mail_template/reset/subject.txt'
    email_template_name = 'tabelog/mail_template/reset/message.txt'
    template_name = 'tabelog/password_reset_form.html'
    success_url = reverse_lazy('tabelog:password_reset_done')


class PasswordResetDone(PasswordResetDoneView):
    """パスワード変更用URLを送りましたページ"""
    template_name = 'tabelog/password_reset_done.html'


class PasswordResetConfirm(PasswordResetConfirmView):
    """新パスワード入力ページ"""
    success_url = reverse_lazy('tabelog:password_reset_complete')
    template_name = 'tabelog/password_reset_confirm.html'


class PasswordResetComplete(PasswordResetCompleteView):
    """新パスワード設定しましたページ"""
    template_name = 'tabelog/password_reset_complete.html'







class CustomPasswordResetView(PasswordResetView):
    template_name = 'tabelog/password_reset_form.html'
    email_template_name = 'tabelog/password_reset_email.html'
    subject_template_name = 'tabelog/password_reset_subject.txt'
    success_url = reverse_lazy('tabelog:password_reset_done')

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'tabelog/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'tabelog/password_reset_confirm.html'
    success_url = 'tabelog/password_reset_complete'

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'tabelog/password_reset_complete.html'