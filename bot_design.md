## Ide
---
* Ide utama dari bot ini adalah menerima notifikasi dari upwork job feed yang datanya berasal dari RSS.  

## Design Bot
---
* Sementara ini bot hanya akan memiliki dua **command**, yaitu: `/start` dan `/stop`. Perintah `/start` sendiri hanya akan berguna sebagai sinyal jika `user` dengan `id` tertentu mendaftarkan diri dan bersedia menerima pemberitahuan berdasarkan data yang di-*input* oleh user melalui perintah `/search` atau `/add_search` (kelak). Sedangkan perintah `/stop` sendiri adalah kebalikan dari perintah `/start` yaitu berfungsi untuk berhenti menerima pemberitahuan dari bot.

## Goals
---
* User yang melakukan subscribtion pada bot akan menerima pemberitahuan job berdasarkan criteria pencarian. Namun sementara ini mode pencarian yang lebih advance secara tidak langsung hanya bisa dilakukan melalui python script. Pengembangan lebih lanjut akan dipikirkan kemudian.