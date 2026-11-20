-- ============================================================================
-- SKEMA BASIS DATA SUPABASE
-- PORTAL AKADEMIK DEPARTEMEN TEKNIK ELEKTRO FTUI
-- ============================================================================

-- 1. Buat Tabel Aspirasi
CREATE TABLE IF NOT EXISTS aspirasi (
    id BIGSERIAL PRIMARY KEY,
    nama TEXT NOT NULL,
    kategori TEXT NOT NULL,
    pesan TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Nonaktifkan Row Level Security (RLS) untuk kemudahan akses read/write portal akademik
ALTER TABLE aspirasi DISABLE ROW LEVEL SECURITY;

-- 3. Masukkan Data Awal (Seed Data)
INSERT INTO aspirasi (nama, kategori, pesan) VALUES
('Ahmad Raihan (Teknik Elektro 2024)', 'Fasilitas Laboratorium', 'Mohon peremajaan osiloskop digital di Lab Telekomunikasi Gedung I-CELL FTUI karena beberapa display sudah redup.'),
('Siti Nurhaliza (Teknik Komputer 2023)', 'Akademik', 'Jadwal asistensi praktikum Jaringan Komputer mohon disesuaikan agar tidak bentrok dengan kuliah Sistem Tertanam.'),
('Budi Santoso (Teknik Elektro 2025)', 'Layanan Mahasiswa', 'Terima kasih atas tersedianya modul praktikum dan template dokumen akademik yang dapat diunduh langsung lewat portal ini.');
