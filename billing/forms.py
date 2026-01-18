from django import forms

class OfficeEmailRequestForm(forms.Form):
    contact_name = forms.CharField(label="Contact Name", max_length=100)
    contact_email = forms.EmailField(label="Contact Email")
    organization = forms.CharField(label="Organization Name", max_length=100)
    domain = forms.CharField(label="Desired Email Domain", max_length=100)
    users = forms.IntegerField(label="Number of Mailboxes Needed", min_value=1)
    notes = forms.CharField(label="Additional Notes", required=False, widget=forms.Textarea)
