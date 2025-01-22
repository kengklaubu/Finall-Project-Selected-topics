# Easy Parking Project

## ขั้นตอนการติดตั้ง

1. ติดตั้ง Python และ MariaDB บนเครื่องของคุณ
2. Run CMD as administrator และใช้คำสั่งด้านล่าง
```
   net start MariaDB
```
3. Clone โปรเจคนี้:
   ```bash
   git clone -b Mockupdata https://github.com/your-repo/easy-parking.git
   cd Easy_Parking
   ```
## Firststep Use comands 
```
pip install -r requirements.txt
```

## load data commands 
```
python manage.py load_mockup_data
```
##  Dont forget to net start MariaDB on CMD 

