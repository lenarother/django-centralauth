from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _
from oauth2_provider.models import AbstractApplication


User = get_user_model()


class Application(AbstractApplication):
    """Centralauth custom application model."""

    def save(self, *args, **kwargs):
        self.client_type = 'confidential'
        self.authorization_grant_type = 'authorization-code'
        self.skip_authorization = True
        super().save(*args, **kwargs)

    class Meta(AbstractApplication.Meta):
        verbose_name = _('Application')
        verbose_name_plural = _('Applications')


class ApplicationPermission(models.Model):
    """Model for holding all permissions available for application."""

    application = models.ForeignKey(
        Application, verbose_name=_('Application'), on_delete=models.CASCADE)
    repr = models.CharField(_('Name'), max_length=255)
    codename = models.CharField(_('Code name'), max_length=100)
    app_label = models.CharField(_('App label'), max_length=100)
    date_created = models.DateTimeField(_('Date (created)'), auto_now_add=True)

    class Meta:
        verbose_name = _('Application permission')
        verbose_name_plural = _('Application permissions')
        unique_together = ('application', 'codename', 'app_label')
        ordering = ('application', 'repr')

    def __str__(self):
        return '{0}: {1}'.format(self.application, self.repr)


class ApplicationPermissionGroup(models.Model):
    """Model for for managing groups of permissions.

    Permission groups are not synced with client Group objects.
    In client all permissions are handled on Permission object level.
    """

    name = models.CharField(_('Name'), max_length=255)
    application = models.ForeignKey(
        Application, verbose_name=_('Application'), on_delete=models.CASCADE)
    permissions = models.ManyToManyField(
        ApplicationPermission, verbose_name=_('Permissions'), blank=True)

    date_created = models.DateTimeField(_('Name'), auto_now_add=True)

    class Meta:
        verbose_name = _('Application permission group')
        verbose_name_plural = _('Application permission groups')
        unique_together = ('application', 'name')
        ordering = ('application', 'name')

    def __str__(self):
        return self.name


class ApplicationUser(models.Model):
    """Model for managing user permissions within application."""

    user = models.ForeignKey(
        User, verbose_name=_('User'), on_delete=models.CASCADE)
    application = models.ForeignKey(
        Application, verbose_name=_('Application'), on_delete=models.CASCADE)

    is_superuser = models.BooleanField(
        _('Superuser status'),
        default=False,
        help_text=_(
            'Designates that this user has all permissions without '
            'explicitly assigning them.'
        ),
    )
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    permissions = models.ManyToManyField(
        ApplicationPermission, verbose_name=_('Permissions'), blank=True)
    groups = models.ManyToManyField(
        ApplicationPermissionGroup, verbose_name=_('Groups'), blank=True)

    date_created = models.DateTimeField(_('Date (created)'), auto_now_add=True)

    class Meta:
        verbose_name = _('Application user')
        verbose_name_plural = _('Application users')
        unique_together = ('user', 'application')

    def __str__(self):
        return '{} ({})'.format(self.user, self.application)

    def get_permissions(self):
        """Combine all user permissions.

        Returns:
            list: list of ids of all user permissions.
        """
        result = set([
            (perm.app_label, perm.codename)
            for perm in self.permissions.all()
        ])

        for group in self.groups.all():
            for perm in group.permissions.all():
                result.add((perm.app_label, perm.codename))
        return list(result)
