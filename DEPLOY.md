# PythonAnywhere Deploy Rehberi

## 1. PythonAnywhere'de Bash Konsolu Aç

Dashboard → "New console" → Bash

## 2. Repoyu Klonla

```bash
git clone https://github.com/saliheryilmaz/Archelon-Sistem.git
cd Archelon-Sistem
```

## 3. Sanal Ortam Oluştur ve Bağımlılıkları Kur

```bash
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

> Not: `mysqlclient` kurulumu başarısız olursa:
> ```bash
> pip install mysqlclient --no-binary mysqlclient
> ```
> Hâlâ hata verirse SQLite kullan (ücretsiz planda sorunsuz çalışır).

## 4. Veritabanı ve Static Dosyalar

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py kurulum
```

## 5. Web App Oluştur

PythonAnywhere → **Web** sekmesi → **Add a new web app**

- Framework: **Manual configuration**
- Python version: **3.10**

## 6. WSGI Dosyasını Düzenle

Web sekmesinde "WSGI configuration file" linkine tıkla.
Dosyanın tüm içeriğini sil, `pythonanywhere_wsgi.py` dosyasının içeriğini yapıştır.

**`KULLANICIADI` yazan yerleri kendi kullanıcı adınla değiştir!**

## 7. Virtualenv Ayarla

Web sekmesinde "Virtualenv" alanına yaz:
```
/home/KULLANICIADI/Archelon-Sistem/venv
```

## 8. Static Files Ayarla

Web sekmesinde "Static files" bölümüne ekle:

| URL       | Directory                                          |
|-----------|----------------------------------------------------|
| `/static/`| `/home/KULLANICIADI/Archelon-Sistem/staticfiles/` |

## 9. Reload Et

Web sekmesinde yeşil **Reload** butonuna bas.

Sitenin adresi: `https://KULLANICIADI.pythonanywhere.com`

---

## Güncelleme (sonraki seferler)

```bash
cd ~/Archelon-Sistem
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

Sonra Web sekmesinden **Reload** bas.
