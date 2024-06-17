from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Store, Category, Reservation, Review, Favorite
# Register your models here.


class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('mail_address', 'password')}),
        ('Personal info', {'fields': ('name', 'furigana', 'postal_code', 'address', 'phone_number', 'member_type')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'created_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('mail_address', 'name', 'furigana', 'postal_code', 'address', 'phone_number', 'member_type', 'password1', 'password2'),
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    list_display = ('mail_address', 'name', 'is_staff', 'is_superuser')
    search_fields = ('mail_address', 'name')
    ordering = ('mail_address',)



@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'lowest_price', 'highest_price', 'opening_time', 'closing_time', 'seating_capacity')
    search_fields = ('name', 'address', 'category__name')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class ReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'store', 'reserved_date', 'reserved_time', 'number_of_people')
    search_fields = ('user__mail_address', 'store__name')

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('store', 'user', 'score', 'comment', 'created_at')
    search_fields = ('store__name', 'user__name', 'comment')


admin.site.register(User, UserAdmin)
admin.site.register(Reservation, ReservationAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Favorite)