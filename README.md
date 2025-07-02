# Easy Parking Project

## ขั้นตอนการติดตั้ง

1. ติดตั้ง Xampp บนเครื่องของคุณ

สามารถดาวโหลดได้จากลิ้งค์ด้านล่าง
 
```
https://www.apachefriends.org/download.html
```
2. Clone โปรเจคนี้:
   ```bash
   git clone -b main https://github.com/kengklaubu/Easy_Parking.git
   ```

## Download Data Mockup
สามารถดาวโหลดได้จากลิ้งค์ด้านล่าง
 

https://drive.google.com/drive/folders/1RG8kOw1wok6VPlOCsVyzghTKZauzojdB?usp=sharing


## ขั้นตอนการ Mockup Data
```
เมื่อดาวโหลด data มาแล้วให้ทำการสร้าง database ที่ชื่อว่า easyparking บน phpMyaAmin
จากนั้นให้ทำการ Import database ที่ดาวโหลดมา ลงไปใน database ที่สร้างไว้ก่อนหน้านี้

```

## Using this commands for run project
```
cd Easy_Parking
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```
