from django import forms
from django.contrib.auth.models import User, Group
from .models import Chamado, Comentario, Setor


# cadastro de setores (usado em modal)
class SetorForm(forms.ModelForm):
    class Meta:
        model = Setor
        fields = ['nome']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ex: ti, rh, financeiro'
            }),
        }


# formulário principal do chamado
class ChamadoForm(forms.ModelForm):
    class Meta:
        model = Chamado
        fields = ['titulo', 'descricao', 'setor', 'prioridade', 'status', 'arquivo']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'setor': forms.Select(attrs={'class': 'form-select'}),
            'prioridade': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'arquivo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


# comentário / interacoes no chamado
class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['texto', 'arquivo']
        widgets = {
            'texto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'digite seu comentario...'
            }),
            'arquivo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


# criacao simples de usuário com grupo
class UsuarioComGrupoForm(forms.ModelForm):
    grupo = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        empty_label='selecione o perfil',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = User
        fields = ['username', 'email']


# cadastro completo de usuário (area de admin)
class UsuarioCompletoForm(forms.ModelForm):
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'nome'
        })
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'sobrenome'
        })
    )

    setor = forms.ModelChoiceField(
        queryset=Setor.objects.all(),
        empty_label='selecione o setor',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    grupo = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        empty_label='nivel de acesso',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    # senha opcional no cadastro
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password != password_confirm:
            raise forms.ValidationError('senhas nao conferem')

        return cleaned_data
