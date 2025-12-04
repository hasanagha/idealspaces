from django import forms

from speedyblog.models import Comment
from speedyblog.settings import SPEEDY_POST_MAX_LENGTH


class UserCommentForm(forms.ModelForm):
    comment = forms.CharField()

    class Meta:
        model = Comment
        fields = ["comment"]
        widgets = {
            'comment': forms.Textarea(attrs={'maxlength': SPEEDY_POST_MAX_LENGTH})
        }

    def clean_comment(self):
        comment = self.cleaned_data.get('comment')

        if comment:
            if not comment.strip():
                raise forms.ValidationError('Comment field is required.')

        return comment


class CommentForm(UserCommentForm):
    user_name = forms.CharField(label='Username')
    user_email = forms.EmailField(label='Email', required=False)

    class Meta:
        model = Comment
        fields = ("user_name", "user_email", "comment")
        widgets = {
            'comment': forms.Textarea(attrs={'maxlength': SPEEDY_POST_MAX_LENGTH})
        }

    def clean_user_name(self):
        user_name = self.cleaned_data.get('user_name')

        if user_name:
            if not user_name.strip():
                raise forms.ValidationError('Username is required.')

        return user_name
