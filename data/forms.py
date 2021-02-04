from django.forms import ModelForm
from .models import TwitterStatus, TwitterUser

class TwitterStatusForm(ModelForm):

    class Meta:
        model = TwitterStatus
        fields = "__all__"

class TwitterUserForm(ModelForm):

    class Meta:
        model = TwitterUser
        fields = "__all__"