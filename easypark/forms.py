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

from django import forms
from .models import ParkingLocation
from django.utils.text import slugify

class ParkingLocationForm(forms.ModelForm):
    class Meta:
        model = ParkingLocation
        fields = ['name', 'slug', 'description', 'total_spots', 'available_spots', 'camera_url', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full p-2.5 border border-gray-300 rounded-md', 'placeholder': 'ชื่อสถานที่'}),
            'slug': forms.TextInput(attrs={'class': 'w-full p-2.5 border border-gray-300 rounded-md', 'placeholder': 'Slug (URL)'}),
            'description': forms.Textarea(attrs={'class': 'w-full p-2.5 border border-gray-300 rounded-md', 'placeholder': 'รายละเอียดสถานที่', 'rows': 3}),
            'total_spots': forms.NumberInput(attrs={'class': 'w-full p-2.5 border border-gray-300 rounded-md', 'placeholder': 'จำนวนช่องจอดทั้งหมด'}),
            'available_spots': forms.NumberInput(attrs={'class': 'w-full p-2.5 border border-gray-300 rounded-md', 'placeholder': 'จำนวนช่องจอดที่ว่าง'}),
            'camera_url': forms.URLInput(attrs={'class': 'w-full p-2.5 border border-gray-300 rounded-md', 'placeholder': 'URL ของกล้องวงจรปิด'}),
            'image': forms.ClearableFileInput(attrs={'class': 'w-full p-2.5 border border-gray-300 rounded-md'}),
        }

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if not slug:
            slug = slugify(self.cleaned_data.get('name'))
        return slug

