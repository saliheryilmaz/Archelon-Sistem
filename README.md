# Archeon Yüzme Kulübü Sistemi

Django tabanlı yüzme kulübü üyelik ve randevu yönetim sistemi.

## Özellikler

- Kullanıcı kayıt / giriş sistemi
- 3 paket türü: Kursiyer (8), Özel Ders (8), Deneme Dersi (1) seans
- Admin paket atama — nakit alındıktan sonra el ile
- Randevu alındığında otomatik seans düşürme
- Randevu iptalinde otomatik seans iadesi
- Düşük seans uyarısı (≤2 kaldığında)
- Admin dashboard — üye, randevu, paket yönetimi

## Roller

| Rol | Yapabilecekleri |
|-----|----------------|
| `member` | Paketlerini görür, randevu alır/iptal eder |
| `instructor` | Üye olarak kayıt olur, eğitmen seçiminde listelenir |
| `admin` | Her şeyi yönetir, paket atar, randevuları onaylar |

Admin rolü vermek için: Django Admin → Kullanıcılar → Rol: Admin
veya `is_staff=True` yapılırsa da admin rolü geçerli sayılır.
