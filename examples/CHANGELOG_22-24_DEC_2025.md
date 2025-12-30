# Changelog - 22 sampai 24 Desember 2025

## Ringkasan Perubahan

Periode ini mencakup berbagai perbaikan dan penambahan fitur pada modul **Purchase BRT**, perbaikan UI/UX, dan peningkatan validasi data.

---

## 24 Desember 2025

### 1. Perbaikan Item Topup dengan ID Berbeda
**Commit:** `56d3694`
**Author:** vicky maulana
**Waktu:** 17:31

**Deskripsi:**
- Memperbaiki item topup jika ID berbeda, sehingga sekarang bisa memilih multiple item
- Menambahkan validasi jika `maksimal_pembelian` sudah mencapai batas limit

---

### 2. Penambahan Fitur Item Topup
**Commit:** `8d3b742`
**Author:** vicky maulana
**Waktu:** 15:03

**Deskripsi:**
- Menambahkan fitur item topup
- Menampilkan pilihan items topup pada create purchase to BRT dan order detail bottom sheet
- Membuat validasi untuk "Pilih Mode" hanya untuk `price_grup = 4`

---

### 3. Update Environment untuk Staging dan Development
**Commit:** `75fbed5`
**Author:** vicky maulana
**Waktu:** 08:24

**Deskripsi:**
- Memperbarui konfigurasi environment untuk staging dan development

---

### 4. Merge Branch feat/purchase-brt-features ke Master
**Commit:** `b055129`
**Author:** vicky maulana
**Waktu:** 01:28

---

## 23 Desember 2025

### 1. Penambahan Response setelah Create Warehouse
**Commit:** `3a40fcd`
**Author:** vicky maulana
**Waktu:** 17:36

**Deskripsi:**
- Menambahkan get response setelah create warehouse
- Memasukkan "key" ke "warehouse" untuk payload create order

---

### 2. Penambahan Multiple Payment Confirmation
**Commit:** `03516de`
**Author:** vicky maulana
**Waktu:** 14:29

**Deskripsi:**
- Menambahkan fitur multiple payment confirmation

---

### 3. Perbaikan Snackbar pada Root Overlay
**Commit:** `66e6f61`
**Author:** vicky maulana
**Waktu:** 13:46

**Deskripsi:**
- Memperbaiki snackbar agar ditampilkan pada root overlay
- Jika ada dialog atau sheet, snackbar tidak akan tersembunyi

---

### 4. Perbaikan Order Detail Sheet dan Conditional Grouping
**Commit:** `3154ea9`
**Author:** vicky maulana
**Waktu:** 10:42

**Deskripsi:**
- Memperbaiki order detail sheet untuk menampilkan "Daftar Barang"
- Mengubah conditional pada create purchase BRT: jika `update_bonus=false` dan belum mendapat bonus item, maka tidak dilakukan grouping

---

### 5. Fitur Upload Bukti Pembayaran dan Perbaikan Navigasi
**Commit:** `217d179`
**Author:** vicky maulana
**Waktu:** 09:24

**Deskripsi:**
- Menghapus sheet jika user tap pada navigasi "Pesan" dan redirect ke route "purchase_brt"
- Menambahkan fitur untuk upload bukti pembayaran atau tempo jika user memiliki `purchase_payment_type: "4"`
- Menambahkan conditional: jika orders memiliki nilai "pay" tidak 0, maka fitur upload bukti pembayaran disembunyikan
- Mengubah semua harga menggunakan format currency helper

---

## 22 Desember 2025

### 1. Perbaikan Conditional untuk update_bonus
**Commit:** `8bf7134`
**Author:** vicky maulana
**Waktu:** 18:00

**Deskripsi:**
- Mengubah conditional: jika `update_bonus` adalah false, maka tidak dilakukan grouping dan tidak bisa di-group dengan item lain

---

### 2. Penanganan Bonus Item dengan Parent Berbeda
**Commit:** `2071628`
**Author:** vicky maulana
**Waktu:** 17:32

**Deskripsi:**
- Menambahkan handling untuk bonus item dengan parent berbeda tapi memiliki "kategori" yang sama
- Mengambil dari parent pertama terlebih dahulu, kemudian mengambil bonus dari parent kedua

---

### 3. Update pada Item Bonus dengan update_bonus false
**Commit:** `4fbf010`
**Author:** vicky maulana
**Waktu:** 17:15

**Deskripsi:**
- Jika parent item memiliki key `update_bonus` bernilai false:
  - Menampilkan item bonus child
  - Tidak bisa memilih item bonus
  - Tidak bisa mengubah mode dari bonus ke special price

---

### 4. Penambahan Validasi Regex untuk Nomor Telepon
**Commit:** `3564a80`
**Author:** vicky maulana
**Waktu:** 14:28

**Deskripsi:**
- Menambahkan regex untuk validasi nomor telepon

---

### 5. Penambahan Widget AppTextField Reusable
**Commit:** `35b02d8`
**Author:** vicky maulana
**Waktu:** 11:47

**Deskripsi:**
- Menambahkan `app_text_field` untuk auto submit/entering jika user tap di luar TextFormField
- Mengubah semua TextFormField untuk menggunakan widget reusable AppTextField

---

### 6. Update TextField Focus dan Berbagai Perbaikan
**Commit:** `097b829`
**Author:** vicky maulana
**Waktu:** 10:41

**Deskripsi:**
- Memperbarui TextField Focus untuk auto submit jika user click di luar field
- Menambahkan conditional untuk handle semua new customer atau new warehouse agar disimpan di session provider
- Membuat conditional: jika `update_bonus` adalah false, tidak bisa select bonus item dan tidak bisa change mode
- Menambahkan auth interceptor
- Menambahkan conditional: jika segment = 1 tapi "kategori" sama, maka auto grouping
- Menyembunyikan fitur "Wansis Kasir"

---

## Statistik Perubahan

| Kategori | Jumlah |
|----------|--------|
| Total Commits | 18 |
| File Baru | 5 |
| File Dimodifikasi | 40+ |
| Merge Commits | 4 |

---

## Fitur Utama yang Ditambahkan

1. **Item Topup Feature** - Fitur baru untuk item topup dengan pilihan dan validasi
2. **Multiple Payment Confirmation** - Konfirmasi pembayaran multiple
3. **Upload Bukti Pembayaran** - Fitur upload untuk pembayaran tempo
4. **Snackbar Service** - Layanan snackbar yang lebih baik dengan root overlay
5. **Session Event Service** - Layanan untuk mengelola session events
6. **AppTextField Widget** - Widget reusable untuk input text dengan auto-submit

## Perbaikan Bug

1. Perbaikan item topup dengan ID berbeda
2. Perbaikan snackbar yang tersembunyi di balik dialog/sheet
3. Perbaikan conditional grouping untuk bonus items
4. Perbaikan handling bonus item dengan parent berbeda
5. Validasi nomor telepon dengan regex

## Peningkatan UI/UX

1. Auto submit pada TextField saat user tap di luar
2. Format currency yang konsisten di seluruh aplikasi
3. Navigasi yang lebih baik pada menu "Pesan"
