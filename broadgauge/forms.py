"""Forms using WTF-forms.
"""
import web
from wtforms import (
    Form,
    DateField, IntegerField, StringField, TextAreaField,
    validators)


class MultiDict(web.storage):
    """wtforms expect the formdate to be a multi-dict instance with getall method.
    This is a hack to make it work with web.py apps.
    """
    def getall(self, name):
        if name in self:
            return [self[name]]
        else:
            return []


class BaseForm(Form):
    def __init__(self, formdata=None, **kwargs):
        formdata = formdata and MultiDict(formdata) or None
        Form.__init__(self, formdata, **kwargs)


class TrainerSignupForm(BaseForm):
    name = StringField('Name', [validators.Required()])
    phone = StringField('Phone', [validators.Required()])
    city = StringField('City', [validators.Required()])
    # No need to have email as it is alreday available from session


class OrganizationSignupForm(BaseForm):
    name = StringField('Name', [validators.Required()])
    city = StringField('City', [validators.Required()])
    role = StringField('Role', [validators.Required()])

class TrainerEditProfileForm(BaseForm):
    name = StringField('Name', [validators.Required()])
    phone = StringField('Phone', [validators.Required()])
    city = StringField('City', [validators.Required()])
    website = StringField('Website', [])
    bio = TextAreaField('Bio', [])

class NewWorkshopForm(BaseForm):
    title = StringField('Title', [validators.Required()])
    description = TextAreaField('Description', [validators.Required()])
    expected_participants = IntegerField('Expected number of pariticipants', [validators.Required()])
    preferred_date = DateField('Preferred Date', [validators.Required()])
