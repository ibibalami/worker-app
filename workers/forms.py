from django import forms

class LocationForm(forms.Form):
    latitude = forms.FloatField(label='Latitude')
    longitude = forms.FloatField(label='Longitude')

from django import forms

class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField(label="Select Excel file")
