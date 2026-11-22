# Validasi regresi normal

Runner memeriksa fungsi HTTP normal, encoding teks tidak aktif, header, penolakan nama dokumen biasa di luar daftar, dan persistensi JSON setelah restart.
Hasil pelaksanaan tersimpan dalam hasil_regresi_normal.json (10 lulus, 0 gagal).

Prasyarat: Node.js, dependensi aplikasi sudah terpasang, Git dengan tag v2-patched, Python dan beautifulsoup4.
Dari akar repositori: python laporan/validasi/validasi_regresi_normal.py --repo .

Runner memakai salinan sementara, mengikat server ke 127.0.0.1, menonaktifkan Supabase, dan memulai JSON kosong.
Ini bukan uji eksekusi script peramban, pengujian cloud, atau jaminan keamanan seluruh aplikasi.
