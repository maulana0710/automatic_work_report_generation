# Laporan Mingguan  
**Periode: 2 – 6 Juni 2026**

---

## Ringkasan Umum

Periode ini mencakup pengembangan fitur dan perbaikan bug pada tiga platform: Omnichannel (Web & Backend), dan Wansis Vendor (Mobile). Fokus utama meliputi penambahan cron job auto selesai pesanan, notifikasi perubahan status, perbaikan filter dan query di BRT Plaza, perubahan struktur response topup, penambahan fitur ekspedisi opsional, serta penambahan status Request Cancel di frontend dan backend.

---

## Detail Pekerjaan

### Selasa, 2 Juni 2026

**Frontend - Omnichannel (Web)**
- Perbaikan cetak label yang layout-nya rusak ketika part number dan part name terlalu panjang

**Backend - Omnichannel**
- Penambahan cron job untuk auto selesai orderan yang sudah melebihi 2 hari dari barang terkirim
- Penambahan notifikasi untuk orderan yang berpindah status seperti Belum Bayar → Lunas, E-Wallet Masuk, dan Request Cancel
- Pengecualian pada checkRates Biteship untuk company_id yang null akan mendapatkan potongan ongkir 1kg, karena versi Mobile dan Web Wansis Vendor belum mengirimkan company_id, sedangkan checkRates dari BRT Plaza akan selalu mengirimkan company_id
- Penambahan validasi supaya parent tidak masuk ke log stok

---

### Rabu, 3 Juni 2026

**Frontend - Omnichannel (Web)**
- Perbaikan notifikasi uang masuk dan request cancel yang tidak menampilkan toast, melainkan hanya muncul di tab notifikasi
- Perbaikan filter di halaman list penjualan BRT Plaza dengan menambahkan search di dropdown masing-masing filter
- Perubahan filter pick range date di list penjualan BRT Plaza
- Penambahan unit test dan dokumentasi

**Backend - Omnichannel**
- Perbaikan cron job untuk auto selesai pesanan
- Penambahan cron job auto selesai ke API sehingga dapat di-trigger melalui endpoint
- Fix merge conflict akibat rebase branch master yang sudah memiliki perubahan, dengan cara merge branch master ke branch yang akan di-merge
- Penambahan unit test dan dokumentasi

---

### Kamis, 4 Juni 2026

**Wansis Vendor (Mobile)**
- Perubahan struktur response topup
- Penambahan params pada pengambilan data topup
- Penambahan safe area di main supaya fitur tidak tertutup oleh button navigasi bawaan perangkat

**Backend - Omnichannel**
- Penambahan update profile ketika ada user BRT Plaza baru yang langsung mengisi alamat karena sudah diwajibkan mengisi alamat terlebih dahulu
- Pemangkasan logic auto selesai pada distribusi e-wallet

**Umum**
- Penambahan milestone dan issue di GitLab untuk perubahan Wansis Vendor, mencakup perbaikan struktur response item topup dan penambahan safe area di main
- Penambahan milestone dan issue di GitLab untuk perubahan backend, mencakup cron job auto selesai, notifikasi, dan efisiensi logic

---

### Jumat, 5 Juni 2026

**Wansis Vendor (Mobile)**
- Penambahan fitur list ekspedisi opsional dan penyimpanan ekspedisi opsional
- Refactor fitur Pembelian ke BRT

**Frontend - Bug dan Fitur**
- Penambahan summary status card Request Cancel

**Backend - Bug dan Fitur**
- Perbaikan query penyimpanan alamat yang secara otomatis mengedit profil user baru yang belum memiliki nomor telepon, alamat, provinsi, kota, dan kecamatan
- Penambahan query untuk menampilkan pesanan yang berstatus Request Cancel

**Umum**
- Penambahan issue untuk fitur "Pilih Ekspedisi Opsional" di Wansis Vendor Mobile

---

### Sabtu, 6 Juni 2026

**Frontend - Fitur**
- Penambahan status summary card baru Request Cancel untuk menampilkan data penjualan BRT Plaza yang mengajukan Request Cancel

**Backend - Bug dan Fitur**
- Perbaikan query penampilan semua data penjualan dari BRT Plaza dengan kondisi company_id kosong
- Perbaikan query penghitungan penjualan BRT Plaza untuk status summary
- Penambahan query untuk menampilkan data yang berstatus Request Cancel

---

## Rekap Pekerjaan

| Kategori | Jumlah Item |
|---|---|
| Penambahan Fitur | 14 |
| Perbaikan Bug / Logic | 8 |
| Perubahan Logic / UI | 5 |
| Dokumentasi / Manajemen | 3 |
| **Total** | **30** |
