from .models import StudentPrivate, Teacher
from django import forms
from django.contrib.auth.password_validation import validate_password
import re


class StudentPrivateForm(forms.ModelForm):
    """アカウント情報の変更フォーム"""
    
    # 単一フォームの検証
    def clean_first_name(self):
        """first_nameをバリデーションする """
        text = self.cleaned_data['first_name']
        if re.match(r'^\s*$', text):  # 入力が空ならエラー
            raise forms.ValidationError('この項目は必須です．')
        return text
    
    def clean_last_name(self):
        """last_nameをバリデーションする """
        text = self.cleaned_data['last_name']
        if re.match(r'^\s*$', text):  # 入力が空ならエラー
            raise forms.ValidationError('この項目は必須です．')
        return text
    
    def clean_first_name_kana(self):
        """first_name_kanaをバリデーションする """
        text = self.cleaned_data['first_name_kana']
        if re.match(r'^\s*$', text):  # 入力が空ならエラー
            raise forms.ValidationError('この項目は必須です．')
        return text

    def clean_last_name_kana(self):
        """last_name_kanaをバリデーションする """
        text = self.cleaned_data['last_name_kana']
        if re.match(r'^\s*$', text):  # 入力が空ならエラー
            raise forms.ValidationError('この項目は必須です．')
        return text

    def clean_first_name_eng(self):
        """first_name_engをバリデーションする """
        text = self.cleaned_data['first_name_eng']
        if re.match(r'^\s*$', text):  # 入力が空ならエラー
            raise forms.ValidationError('この項目は必須です．')
        return text
    
    def clean_last_name_eng(self):
        """last_name_engをバリデーションする """
        text = self.cleaned_data['last_name_eng']
        if re.match(r'^\s*$', text):  # 入力が空ならエラー
            raise forms.ValidationError('この項目は必須です．')
        return text
    
    def clean_alma_mater(self):
        """alma_materをバリデーションする """
        text = self.cleaned_data['alma_mater']
        if re.match(r'^\s*$', text):  # 入力が空ならエラー
            raise forms.ValidationError('この項目は必須です．')
        text = text.replace('工業高等専門学校', '高専')
        text = text.replace('高等専門学校', '高専')
        text = text.replace('高等学校', '高校')
        return text
    
    class Meta:
        model = StudentPrivate
        fields = ('avatar',
                  'username',
                  'last_name',
                  'first_name',
                  'last_name_kana',
                  'first_name_kana',
                  'last_name_eng',
                  'first_name_eng',
                  'status',
                  'student_id',
                  'assignment_year',
                  'assignment_month',
                  'graduation_year',
                  'graduation_month',
                  'alma_mater',
                  'company',
                  'private_email',
                  'phone_number',
                  'scholarship',
                  'thesis_b',
                  'thesis_m',
                  'thesis_d',
                  'kyash_qr',
                  'paypay_id'
                  )


class TeacherForm(forms.ModelForm):
    """アカウント情報の変更フォーム"""
    
    # 単一フォームの検証
    def clean_first_name(self):
        """first_nameをバリデーションする """
        text = self.cleaned_data['first_name']
        if re.match(r'^\s*$', text):  # 入力が空ならエラー
            raise forms.ValidationError('この項目は必須です．')
        return text
    
    def clean_last_name(self):
        """last_nameをバリデーションする """
        text = self.cleaned_data['last_name']
        if re.match(r'^\s*$', text):  # 入力が空ならエラー
            raise forms.ValidationError('この項目は必須です．')
        return text
    
    def clean_first_name_kana(self):
        """first_name_kanaをバリデーションする """
        text = self.cleaned_data['first_name_kana']
        if re.match(r'^\s*$', text):  # 入力が空ならエラー
            raise forms.ValidationError('この項目は必須です．')
        return text
    
    def clean_last_name_kana(self):
        """last_name_kanaをバリデーションする """
        text = self.cleaned_data['last_name_kana']
        if re.match(r'^\s*$', text):  # 入力が空ならエラー
            raise forms.ValidationError('この項目は必須です．')
        return text
    
    def clean_first_name_eng(self):
        """first_name_engをバリデーションする """
        text = self.cleaned_data['first_name_eng']
        if re.match(r'^\s*$', text):  # 入力が空ならエラー
            raise forms.ValidationError('この項目は必須です．')
        return text
    
    def clean_last_name_eng(self):
        """last_name_engをバリデーションする """
        text = self.cleaned_data['last_name_eng']
        if re.match(r'^\s*$', text):  # 入力が空ならエラー
            raise forms.ValidationError('この項目は必須です．')
        return text
    
    class Meta:
        model = Teacher
        fields = ('avatar',
                  'username',
                  'last_name',
                  'first_name',
                  'last_name_kana',
                  'first_name_kana',
                  'last_name_eng',
                  'first_name_eng',
                  'ieice_id',
                  'kyash_qr',
                  'paypay_id'
                  )


class StudentPrivateAddForm(forms.ModelForm):
    """アカウント追加フォーム"""
    username = forms.CharField(
        label='ユーザID',
        required=True,
    )
    password = forms.CharField(
        label='パスワード',
        widget=forms.PasswordInput,
        help_text='パスワードを入力してください．'
    )
    
    def clean_password(self):
        # パスワードのvalidation時に username と似た値を禁止するUserAttributeSimilarityValidatorを機能させるためにusernameを代入
        password = self.cleaned_data.get('password')
        self.instance.username = self.cleaned_data.get('username')
        validate_password(
            self.cleaned_data['password'],
            self.instance
        )  # デフォルトのパスワードvalidation
        return password
    
    def save(self, commit=True):
        student_private = super().save(commit=False)
        student_private.set_password(self.cleaned_data["password"])  # パスワードをハッシュにして代入
        if commit:
            student_private.save()
        return student_private
    
    class Meta:
        model = StudentPrivate
        fields = [
            'username',
            'password',
        ]
