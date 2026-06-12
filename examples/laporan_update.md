# Laporan Pembaruan Aplikasi Wansis Store

**Periode:** Juni 2026

---

## A. Fitur & Perbaikan (Terlihat oleh Pengguna)

### 1. Status Order pada Detail Pesanan

Ditambahkan tampilan status pesanan pada halaman Detail Pesanan yang menampilkan
progres **Payment**, **Prepare**, dan **Packing** berdasarkan response API.
Bagian "Timeline Detail" dirombak menjadi **progress bercabang (step-by-step)**:

- Tiap tahap (Pembayaran → Prepare → Packing) memiliki titik indikator dan garis penghubung.
- Tahap Prepare & Packing menampilkan rincian tiap barang beserta status qty
  (selesai / parsial / belum) sebagai acuan pemenuhan parsial.
- Nama status (mis. Ongoing, Pending, Complete) ditampilkan di bawah judul tiap tahap.
- Garis Prepare → Packing berwarna kuning bila packing sudah berjalan padahal
  prepare belum selesai.

<!-- TODO: tambahkan gambar -->
![Gambar 1.1 – Status Payment, Prepare, Packing pada detail pesanan](img/juni/1.%20Tampilan%20Tracking%20Pesanan%20Dengan%20Status%20Selesai.png)

![Gambar 1.2 – Tracking Pesanan Dengan Kondisi Parsial](img/juni/2.%20Tampilan%20Tracking%20Pesanan%20Dengan%20Kondisi%20Parsial%20Prepare%20Dan%20Packing.png)

![Gambar 1.3 – Tracking Pesanan Dengan Kondisi Normal](img/juni/3.%20Tampilan%20Tracking%20Tanpa%20Partial.png)

---

### 2. Validasi Input DP (Down Payment)

Input nominal DP kini **disembunyikan secara otomatis** untuk pengguna dengan
tipe pembayaran `purchasePaymentType` **4 (Tempo)** atau **5 (DP)**, sehingga
form pembayaran hanya menampilkan kolom yang relevan dengan tipe akun pengguna.

<!-- TODO: tambahkan gambar -->
![Gambar 2.1 – Form pembayaran tanpa input DP untuk tipe Tempo/DP](img/juni/5.%20Tampilan%20User%20Login%20Yang%20Memiliki%20Status%20Purchase%20Payment%204%20Atau%205.png)

---

### 3. Sumber Limit Pembelian

Perhitungan limit pembelian dipindahkan ke **endpoint finance saldo v2**.
Ditambahkan field **`limitActual`** dan **`limitToday`** sehingga informasi
limit yang ditampilkan lebih akurat dan terbaru.

<!-- TODO: tambahkan gambar -->
![Gambar 3.1 – Informasi limit pembelian terbaru](img/juni/6.%20Tampilan%20Tempo%20Yang%20Telah%20Menggunakan%20Endpoint%20Baru.png)

---

### 4. Perbaikan Kecamatan pada Edit Profil

Diperbaiki bug di mana **kecamatan tidak muncul dan tidak dapat diperbarui**
pada halaman Edit Profil. Sekarang kecamatan tampil dengan benar dan dapat diubah.

<!-- TODO: tambahkan gambar -->
![Gambar 4.1 – Kecamatan pada Edit Profil setelah perbaikan](img/juni/4.%20Tampilan%20Kecamatan%20Yang%20Kembali%20Tampil.png)

---

## B. Peningkatan Teknis (Di Balik Layar)

### 5. Refactor Konsistensi Layering

Penyeragaman alur akses data antar fitur agar mengikuti pola yang sama
(**Presentation → Repository → Datasource**):

- **Vendor Registration:** menghapus pemanggilan API langsung di layar,
  dialihkan ke repository yang sudah tersedia.
- **Pembelian BRT:** layar create memakai repository (bukan datasource langsung).
- **Warehouse Company:** ditambahkan layer `data/` & `domain/` yang mendelegasikan
  ke repository bersama (`shared/`).

### 6. Pembersihan Kode

Perapihan kode pada fitur **Auth, Profile, Stock, Wallet, Tracking**, serta
penyederhanaan entity & model di direktori `shared/` agar lebih mudah dipelihara.

### 7. Pembaruan Dokumentasi

Dokumentasi **README** disinkronkan dengan struktur proyek terkini.

---

*Dokumen ini disusun sebagai ringkasan pembaruan aplikasi.*
