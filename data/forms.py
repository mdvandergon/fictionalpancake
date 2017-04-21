from django import forms

class PredictForm(forms.Form):
    text = forms.CharField(max_length=1000, required=True,
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'required': True, 'placeholder': 'Say something...'}))
