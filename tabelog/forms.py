from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm
from django.contrib.auth import get_user_model
from .models import User, Reservation, Review
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import datetime, time


# ユーザーモデル取得
User = get_user_model()


'''ログイン用フォーム'''

class LoginForm(AuthenticationForm):

    # bootstrap対応
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label

            
'''サインアップ用フォーム'''
class SignupForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('name', 'furigana', 'mail_address', 'postal_code', 'address', 'phone_number', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

'''検索フォーム'''
class StoreSearchForm(forms.Form):
    keyword = forms.CharField(label='キーワード', max_length=100, required=False)


'''予約フォーム'''
class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['reserved_date', 'reserved_time', 'number_of_people']
        widgets = {
            'reserved_date': forms.DateInput(attrs={'type': 'date'}),
            'reserved_time': forms.TimeInput(attrs={'type': 'time'}),
            'number_of_people': forms.NumberInput(attrs={'min': '1'}),
        }

    def __init__(self, *args, **kwargs):
        self.store = kwargs.pop('store', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        reserved_date = cleaned_data.get("reserved_date")
        reserved_time = cleaned_data.get("reserved_time")

        if reserved_date and reserved_time:
            reserved_datetime = datetime.combine(reserved_date, reserved_time)
            reserved_datetime = timezone.make_aware(reserved_datetime, timezone.get_current_timezone())

            # 予約日時が現在より前の場合はエラー
            if reserved_datetime < timezone.now():
                raise ValidationError(_("予約日は本日以降の日付にしてください。"))
                

            # 営業時間のチェック
            if self.store:
                opening_time = self.store.opening_time
                closing_time = self.store.closing_time
                if not (opening_time <= reserved_time <= closing_time):
                    raise ValidationError(_("予約時間が営業時間外です。"))
                

            # 同じユーザーが同じ日時に予約しているかチェック
            if Reservation.objects.filter(
                user=self.user,
                reserved_date=reserved_date,
                reserved_time=reserved_time
            ).exists():
                raise ValidationError(_("この時間帯には既に予約があります。"))

        return cleaned_data


'''レビューフォーム'''
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['score', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 5, 'placeholder': ''}),
            'score': forms.RadioSelect(choices=[
                (1, '1'),
                (2, '2'),
                (3, '3'),
                (4, '4'),
                (5, '5')
            ])
        }



'''パスワード変更フォーム'''
class MyPasswordChangeForm(PasswordChangeForm):

    # bootstrap4対応で、classを指定
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class PaymentForm(forms.Form):
    stripe_token = forms.CharField()


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'furigana', 'mail_address', 'postal_code', 'address', 'phone_number']

