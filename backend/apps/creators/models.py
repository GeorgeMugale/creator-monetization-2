from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import URLValidator, MinValueValidator, MaxValueValidator

User = get_user_model()


class CreatorProfile(models.Model):
    """Extended profile model for creator users."""

    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
        ('banned', 'Banned'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='creator_profile')
    bio = models.TextField(blank=True, help_text='Creator bio or description')
    profile_image = models.ImageField(upload_to='creator_profiles/', blank=True, null=True)
    cover_image = models.ImageField(upload_to='creator_covers/', blank=True, null=True)
    website = models.URLField(blank=True, validators=[URLValidator()])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    followers_count = models.IntegerField(default=0)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    rating = models.FloatField(
        default=5.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        help_text='Creator rating from 0 to 5'
    )
    verified = models.BooleanField(default=False, help_text='Verified creator badge')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'creators_profile'
        verbose_name = 'Creator Profile'
        verbose_name_plural = 'Creator Profiles'
        ordering = ['-followers_count']

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - Creator"

    @property
    def is_verified(self):
        """Check if creator is verified."""
        return self.verified

    @property
    def is_suspended(self):
        """Check if creator is suspended."""
        return self.status == 'suspended'

    @property
    def is_banned(self):
        """Check if creator is banned."""
        return self.status == 'banned'

