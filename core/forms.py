from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, GoogleSheet

class ConfigForm(forms.Form):
    google_sheet_url = forms.CharField(label='Google Sheet URL', max_length=300)

    def __init__(self, *args, **kwargs):
        super(ConfigForm, self).__init__(*args, **kwargs)
        try:
            # Fetch the latest GoogleSheet object and set its URL as the initial value
            latest_sheet = GoogleSheet.objects.latest('id')
            self.fields['google_sheet_url'].initial = latest_sheet.url
        except GoogleSheet.DoesNotExist:
            # Handle the case where no GoogleSheet object exists
            self.fields['google_sheet_url'].initial = ''

class UserResetForm(forms.Form):

    answer = forms.CharField(label='', max_length=300)

class SetEmailAndPasswordForm(UserCreationForm):
    email = forms.EmailField(required=True)
    security_question = forms.CharField(required=True, max_length=200, help_text="For password reset. E.g., what street were you born on?")
    security_answer = forms.CharField(required=True, max_length=200, help_text="")

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2', 'security_question', 'security_answer')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.username = self.cleaned_data["email"]
        if commit:
            user.save()
            UserProfile.objects.update_or_create(user=user, 
                defaults={'security_question': self.cleaned_data['security_question'],
                          'security_answer': self.cleaned_data['security_answer']})
        return user
