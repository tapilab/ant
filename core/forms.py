from django import forms

class ConfigForm(forms.Form):
    google_sheet_url = forms.CharField(label='Google Sheet URL', max_length=300)
