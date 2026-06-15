from django import forms
from book.models import Book
from .models import Reservation


class ReservationForm(forms.ModelForm):
    dni = forms.CharField(required=True, max_length=20)
    name = forms.CharField(required=True, max_length=100)
    book = forms.ModelChoiceField(queryset=Book.objects.all(), required=True)
    start_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    end_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    class Meta:
        model = Reservation
        fields = ['dni', 'name', 'book', 'start_date', 'end_date']

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_date')
        end = cleaned_data.get('end_date')
        if start and end and end <= start:
            raise forms.ValidationError('End date must be after start date.')
        return cleaned_data
