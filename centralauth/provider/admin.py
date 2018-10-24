from django import forms
from django.contrib import admin
from django.forms import models
from django.utils.translation import ugettext_lazy as _
from oauth2_provider.models import (
    get_access_token_model, get_application_model, get_grant_model, get_refresh_token_model)

from .models import ApplicationPermissionGroup, ApplicationUser


Application = get_application_model()


# Unregister not used admins.
admin.site.unregister(Application)
admin.site.unregister(get_grant_model())
admin.site.unregister(get_access_token_model())
admin.site.unregister(get_refresh_token_model())


class ApplicationPermissionGroupAdminForm(models.ModelForm):
    users = forms.ModelMultipleChoiceField(
        ApplicationUser.objects.none(),
        widget=admin.widgets.FilteredSelectMultiple(_('Users'), False),
        required=False,
    )

    class Meta:
        widgets = {
            'permissions': admin.widgets.FilteredSelectMultiple(_('Permissions'), False)
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['permissions'].queryset = (
                self.instance.application.applicationpermission_set.all())

            self.fields['users'].queryset = (
                self.instance.application.applicationuser_set.all())

            self.initial['users'] = self.instance.applicationuser_set.values_list(
                'pk', flat=True)


@admin.register(ApplicationPermissionGroup)
class ApplicationPermissionGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'application')
    list_filter = ('application',)
    search_fields = ('name', 'applicationuser__user__username')
    form = ApplicationPermissionGroupAdminForm
    fields = ('name', 'application')

    def get_fields(self, request, obj=None):
        if obj:
            return self.fields + ('users', 'permissions',)
        return self.fields

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('application',)
        return self.readonly_fields

    def get_inline_instances(self, request, obj=None):
        # Skip inlines in case of add forms (we pre-filter inlines based on instance).
        if obj is None:
            return []
        return super().get_inline_instances(request, obj)

    def save_related(self, request, form, *args, **kwargs):
        if 'users' in form.cleaned_data:
            form.instance.applicationuser_set.set(form.cleaned_data['users'])
        return super().save_related(request, form, *args, **kwargs)


class ApplicationUserAdminForm(models.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['groups'].queryset = (
                self.instance.application.applicationpermissiongroup_set.all())


@admin.register(ApplicationUser)
class ApplicationUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'application',)
    list_filter = ('application',)
    search_fields = ('user__username',)
    form = ApplicationUserAdminForm
    fields = ('user', 'application', 'is_superuser', 'is_staff', 'is_active')

    def get_fields(self, request, obj=None):
        if obj:
            return self.fields + ('groups',)
        return self.fields

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('application', 'user')
        return self.readonly_fields


class ApplicationUserInlineFormset(models.BaseInlineFormSet):

    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        if self.instance and self.instance.pk:
            kwargs['parent_instance'] = self.instance
        return kwargs


class ApplicationUserInlineForm(models.ModelForm):

    def __init__(self, *args, **kwargs):
        parent_instance = kwargs.pop('parent_instance', None)
        super().__init__(*args, **kwargs)
        if parent_instance:
            self.fields['groups'].queryset = (
                parent_instance.applicationpermissiongroup_set.all())


class ApplicationUserInline(admin.TabularInline):
    model = ApplicationUser
    formset = ApplicationUserInlineFormset
    form = ApplicationUserInlineForm
    exclude = ('permissions',)
    extra = 0


class ApplicationAdminForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['redirect_uris'].required = True
        self.fields['client_secret'].required = True


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'redirect_uris')
    form = ApplicationAdminForm
    fields = ('name', 'client_id', 'client_secret', 'redirect_uris')
    inlines = [ApplicationUserInline]

    def get_inline_instances(self, request, obj=None):
        if obj is None:
            return []
        return super().get_inline_instances(request, obj)
