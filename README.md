# Portal Layanan Akademik DTE FTUI

Proyek Akhir Praktikum Keamanan Jaringan Komputer 2026, Kelompok 41 (topik A13).

- Marshal Aufa Diliyana (2406346913)
- Salsabila Maharani Mumtaz (2406348156)

Website tiruan tampilan ee.ui.ac.id dengan dua halaman:

| Halaman | Fungsi |
|---|---|
| `/dokumen?file=...` | Menampilkan isi dokumen akademik dari folder `docs/` |
| `/aspirasi` | Form dan daftar aspirasi mahasiswa |

Menu lain mengarah langsung ke ee.ui.ac.id.

## Menjalankan

```bash
npm install
cp .env.example .env   # isi SUPABASE_URL dan SUPABASE_ANON_KEY
npm start              # http://localhost:3000
```

Jika `.env` tidak diisi, aspirasi disimpan ke `aspirasi.json`. Tabel Supabase dibuat dengan `schema_supabase.sql`.

## Isi folder

| File | Isi |
|---|---|
| `server.js` | Seluruh logika server (Express) |
| `header.ejs`, `footer.ejs` | Bagian atas dan bawah setiap halaman |
| `dokumen.ejs`, `aspirasi.ejs` | Isi masing-masing halaman |
| `style.css` | Tampilan |
| `docs/` | Dokumen akademik yang ditampilkan |
| `*.png`, `*.svg`, `*.woff2`, `font-awesome.min.css` | Logo, gambar, font, dan ikon dari ee.ui.ac.id |

## Laporan akhir

[Laporan PDF](laporan/Laporan_PA_Pentest_Kelompok41.pdf) · [Laporan Word](laporan/Laporan_PA_Pentest_Kelompok41.docx)

Dokumentasi mencakup metode, hasil, analisis, perbaikan, pengujian ulang, dan batas bukti. Kondisi kode sebelum dan sesudah perbaikan ditandai dengan v1-initial dan v2-patched.
