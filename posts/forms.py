from django import forms

from .models import Comment, Group, Post


class SearchForm(forms.Form):
    """Форма поиска"""
    query = forms.CharField(max_length=100,
                            label="Поиск по публикациям")


class GroupForm(forms.ModelForm):
    """Форма для редактирования сообщества."""
    class Meta():
        """Мета-класс формы."""
        model = Group
        fields = ("slug", "title", "description",)

    def clean_slug(self):
        """Валидация поля Идентификатор."""
        data = self.cleaned_data["slug"]
        if len(data) == 0:
            raise forms.ValidationError("Укажите идентификатор")
        return data

    def clean_title(self):
        """Валидация поля Текст."""
        data = self.cleaned_data["title"]
        if len(data) == 0:
            raise forms.ValidationError("Укажите название")
        return data

    def clean_description(self):
        """Валидация поля Описание."""
        data = self.cleaned_data["description"]
        if len(data) == 0:
            raise forms.ValidationError("Нужно написать хоть что-то")
        return data


class PostForm(forms.ModelForm):
    """Форма для редактирования записи."""
    class Meta():
        """Мета-класс формы."""
        model = Post
        fields = ("group", "text", "image",)
        error_messages = {
            "text": {"blank": "BLANK", "required": "REQUIRED"}
        }

    def clean_text(self):
        """Валидация поля Текст."""
        data = self.cleaned_data["text"]
        if len(data) == 0:
            raise forms.ValidationError("Нужно написать хоть что-то")
        return data


class GroupPostForm(PostForm):
    """Форма для создания записи без группы."""
    class Meta():
        """Мета-класс формы."""
        model = Post
        fields = ("text", "image",)


class CommentForm(forms.ModelForm):
    """Форма для добавления комментария."""
    class Meta():
        """Мета-класс формы."""
        model = Comment
        fields = ("text",)
        error_messages = {
            "text": {"blank": "BLANK", "required": "REQUIRED"}
        }
        widgets = {
            "text": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_text(self):
        """Валидация поля Текст."""
        data = self.cleaned_data["text"]
        if len(data) == 0:
            raise forms.ValidationError("Нужно написать хоть что-то")
        return data
