# Archeon Yüzme Kulübü Sistemi

Django tabanlı yüzme kulübü üyelik ve randevu yönetim sistemi.

## Özellikler

- Kullanıcı kayıt / giriş sistemi
- 3 paket türü: Kursiyer (8), Özel Ders (12), Aqua Fitness (16) seans
- Admin paket atama — nakit alındıktan sonra el ile
- Randevu alındığında otomatik seans düşürme
- Randevu iptalinde otomatik seans iadesi
- Düşük seans uyarısı (≤2 kaldığında)
- Admin dashboard — üye, randevu, paket yönetimi

## Yerel Kurulum

```bash
# 1. Repoyu klonla
git clone <repo_url>
cd archeon

# 2. Sanal ortam
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# 3. Bağımlılıklar
pip install -r requirements.txt

# 4. .env dosyası
cp .env.example .env
# .env içini düzenle (SQLite için olduğu gibi bırak)

# 5. Migrationlar
python manage.py makemigrations
python manage.py migrate

# 6. Başlangıç verileri (paket türleri + admin)
python manage.py kurulum
# Admin: kullanıcı adı=admin, şifre=archeon123

# 7. Çalıştır
python manage.py runserver
```

Tarayıcıda aç: http://127.0.0.1:8000

## PythonAnywhere Deploy

```bash
# 1. GitHub'a push et
git push origin main

# 2. PythonAnywhere Bash konsolunda:
cd ~/archeon
git pull
pip install -r requirements.txt --user
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py kurulum

# 3. WSGI dosyasına ekle (/var/www/..._wsgi.py):
import os
os.environ['SECRET_KEY'] = 'gizli-anahtar'
os.environ['DEBUG'] = 'False'
os.environ['ALLOWED_HOSTS'] = 'kullaniciadi.pythonanywhere.com'
os.environ['DB_ENGINE'] = 'django.db.backends.mysql'
os.environ['DB_NAME'] = 'kullaniciadi$archeon'
os.environ['DB_USER'] = 'kullaniciadi'
os.environ['DB_PASSWORD'] = 'mysql_sifren'
os.environ['DB_HOST'] = 'kullaniciadi.mysql.pythonanywhere-services.com'

# 4. Static files → Web sekmesinde /static/ → /home/kullaniciadi/archeon/staticfiles/
```

## Roller

| Rol | Yapabilecekleri |
|-----|----------------|
| `member` | Paketlerini görür, randevu alır/iptal eder |
| `instructor` | Üye olarak kayıt olur, eğitmen seçiminde listelenir |
| `admin` | Her şeyi yönetir, paket atar, randevuları onaylar |

Admin rolü vermek için: Django Admin → Kullanıcılar → Rol: Admin
veya `is_staff=True` yapılırsa da admin rolü geçerli sayılır.
