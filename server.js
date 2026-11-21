// Portal Layanan Akademik Departemen Teknik Elektro FTUI
// Halaman: /dokumen (baca dokumen akademik) dan /aspirasi (kotak aspirasi mahasiswa)

require('dotenv').config();
const express = require('express');
const path = require('path');
const fs = require('fs');
const { createClient } = require('@supabase/supabase-js');

const app = express();
const PORT = process.env.PORT || 3000;

app.set('view engine', 'ejs');
app.set('views', __dirname);
app.use(express.urlencoded({ extended: true }));

// Header keamanan: batasi sumber konten dan blokir framing/sniffing
app.use((req, res, next) => {
  res.setHeader('Content-Security-Policy', "default-src 'self'");
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('X-Content-Type-Options', 'nosniff');
  next();
});

// Penyimpanan aspirasi: Supabase kalau .env diisi, kalau tidak pakai aspirasi.json
const supabase = process.env.SUPABASE_URL
  ? createClient(process.env.SUPABASE_URL, process.env.SUPABASE_ANON_KEY)
  : null;
const JSON_FILE = path.join(__dirname, 'aspirasi.json');

async function ambilAspirasi() {
  if (supabase) {
    const { data } = await supabase.from('aspirasi').select('*').order('id', { ascending: false });
    return data || [];
  }
  return JSON.parse(fs.readFileSync(JSON_FILE, 'utf8')).reverse();
}

async function simpanAspirasi(aspirasi) {
  if (supabase) {
    await supabase.from('aspirasi').insert(aspirasi);
    return;
  }
  const list = JSON.parse(fs.readFileSync(JSON_FILE, 'utf8'));
  list.push({ id: Date.now(), ...aspirasi, created_at: new Date().toISOString() });
  fs.writeFileSync(JSON_FILE, JSON.stringify(list, null, 2));
}

app.get('/', (req, res) => res.redirect('/dokumen'));

// Daftar dokumen resmi yang boleh dibuka
const DOKUMEN_RESMI = [
  'panduan_kurikulum_2026.txt',
  'kalender_akademik_gasal.txt',
  'tata_tertib_laboratorium.txt'
];

// Halaman dokumen: hanya melayani berkas dari daftar resmi (anti path traversal)
app.get('/dokumen', (req, res) => {
  const file = req.query.file || 'panduan_kurikulum_2026.txt';
  const aman = path.basename(file); // buang komponen ../ dari input

  let isi = null;
  let status = 200;
  if (DOKUMEN_RESMI.includes(aman)) {
    isi = fs.readFileSync(path.join(__dirname, 'docs', aman), 'utf8');
  } else {
    status = 403; // berkas di luar daftar resmi ditolak
  }

  res.status(status).render('dokumen', { title: 'Dokumen Akademik', menu: 'dokumen', file, isi });
});

// Halaman aspirasi: menampilkan dan menyimpan aspirasi mahasiswa
app.get('/aspirasi', async (req, res) => {
  const list = await ambilAspirasi();
  res.render('aspirasi', { title: 'Aspirasi Mahasiswa', menu: 'aspirasi', list, terkirim: req.query.terkirim });
});

app.post('/aspirasi', async (req, res) => {
  const { nama, kategori, pesan } = req.body;
  await simpanAspirasi({ nama, kategori, pesan });
  res.redirect('/aspirasi?terkirim=1');
});

// File tampilan (css, gambar, font) diambil dari folder ini
app.get('/:file', (req, res, next) => {
  if (!/\.(css|png|svg|woff2)$/.test(req.params.file)) return next();
  res.sendFile(req.params.file, { root: __dirname });
});

app.listen(PORT, () => console.log(`Server berjalan di http://localhost:${PORT}`));
