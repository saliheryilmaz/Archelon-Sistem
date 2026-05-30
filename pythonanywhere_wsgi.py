# ============================================================
# PythonAnywhere WSGI Dosyası
# Bu dosyanın içeriğini PythonAnywhere'deki WSGI dosyasına kopyala:
# /var/www/KULLANICIADI_pythonanywhere_com_wsgi.py
#
# KULLANICIADI kısmını kendi PythonAnywhere kullanıcı adınla değiştir!
# ============================================================

import sys
import os

# Proje dizinini Python path'e ekle
path = '/home/KULLANICIADI/Archelon-Sistem'
if path not in sys.path:
    sys.path.insert(0, path)

# Ortam değişkenlerini ayarla (.env yerine burada tanımlanır)
os.environ['SECRET_KEY'] = 'buraya-guclu-bir-secret-key-yaz-en-az-50-karakter'
os.environ['DEBUG'] = 'False'
os.environ['ALLOWED_HOSTS'] = 'KULLANICIADI.pythonanywhere.com'

# SQLite kullanmak istersen (ücretsiz plan için önerilir):
os.environ['DB_ENGINE'] = 'django.db.backends.sqlite3'
os.environ['DB_NAME'] = '/home/KULLANICIADI/Archelon-Sistem/db.sqlite3'

# MySQL kullanmak istersen (üstteki 2 satırı sil, alttakileri aç):
# os.environ['DB_ENGINE'] = 'django.db.backends.mysql'
# os.environ['DB_NAME'] = 'KULLANICIADI$archeon'
# os.environ['DB_USER'] = 'KULLANICIADI'
# os.environ['DB_PASSWORD'] = 'mysql_sifren'
# os.environ['DB_HOST'] = 'KULLANICIADI.mysql.pythonanywhere-services.com'
# os.environ['DB_PORT'] = '3306'

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'archeon.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
