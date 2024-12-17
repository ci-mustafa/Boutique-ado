from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from django_countries.fields import CountryField

# Define the UserProfile model
class UserProfile(models.Model):
    """
    A user profile model for maintaining default delivery information
    and tracking order history associated with a user.
    """

    # Link this profile to a Django User instance using a one-to-one relationship
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Optional default phone number for the user
    default_phone_number = models.CharField(
        max_length=20,  # Maximum length of 20 characters
        null=True,      # Field is allowed to have a NULL value in the database
        blank=True      # Field is allowed to be left blank in forms
    )

    # Country field using the django_countries package
    default_country = CountryField(
        blank_label='Country *',  # Label displayed in the dropdown for blank options
        null=True,                # Field is allowed to have a NULL value in the database
        blank=True                # Field is allowed to be left blank in forms
    )

    # Optional default postcode for the user
    default_postcode = models.CharField(
        max_length=20,  # Maximum length of 20 characters
        null=True,
        blank=True
    )

    # Optional default town or city
    default_town_or_city = models.CharField(
        max_length=40,  # Maximum length of 40 characters
        null=True,
        blank=True
    )

    # Optional default street address (line 1)
    default_street_address1 = models.CharField(
        max_length=80,  # Maximum length of 80 characters
        null=True,
        blank=True
    )

    # Optional default street address (line 2)
    default_street_address2 = models.CharField(
        max_length=80,  # Maximum length of 80 characters
        null=True,
        blank=True
    )

    # Optional default county or state
    default_county = models.CharField(
        max_length=80,  # Maximum length of 80 characters
        null=True,
        blank=True
    )

    def __str__(self):
        """
        Return the username of the associated User as the string representation
        of the UserProfile instance.
        """
        return self.user.username


# Signal to automatically create or update a UserProfile when a User is saved
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Create or update the user profile whenever a User instance is created or saved.
    """
    if created:
        # If the User instance is newly created, create an associated UserProfile
        UserProfile.objects.create(user=instance)

    # For existing User instances, save any updates to the associated UserProfile
    instance.userprofile.save()



