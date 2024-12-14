from django import forms
from .models import CustomUser
from django.core.exceptions import ValidationError

class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        help_text="รหัสผ่านต้องมีอย่างน้อย 8 ตัวอักษร ประกอบด้วยตัวพิมพ์ใหญ่และตัวเลข"
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput,
        label="Confirm Password",  # ชื่อฟิลด์ให้ตรงกับการยืนยันรหัสผ่าน
        help_text="กรุณายืนยันรหัสผ่านของคุณ"
    )

    class Meta:
        model = CustomUser  # ใช้ CustomUser แทน User
        fields = ['username', 'password', 'first_name', 'last_name', 'email']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')

        # ตรวจสอบการยืนยันรหัสผ่าน
        if password != password2:
            raise ValidationError("รหัสผ่านไม่ตรงกัน")

        return cleaned_data
