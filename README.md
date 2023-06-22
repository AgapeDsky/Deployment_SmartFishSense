# Deployment_SmartFishSense
Model untuk deployment ada di folder Model_TA. Model perlu diunduh dan dipindahkan ke direktori yang sesuai dengan yang dituliskan pada program.

Program utama ada di file src_TA_mongodb_revised.py

## Cara Menjalankan Program
1. Jalankan server pada mongodb. Ganti uri mongodb di src_TA_mongodb_revised.py
2. Nyalakan program di Raspberry Pi: python src_TA_mongodb_revised.py. Untuk kemudahan, Raspberry Pi sudah diatur supaya langsung memulai program ketika selesai booting dan terkoneksi dengan internet. Jika tidak ada koneksi internet, program tidak akan menyala, jadi pastikan dulu Raspberry Pi terkoneksi.

## Manual Produk
SmartFishSense adalah alat pendeteksian nafsu makan ikan berbasis kecerdasan buatan multi-modal deep learning. SmartFishSense mampu mendeteksi perilaku ikan di kolam saat pemberian makan dan memberi penilaian perihal nafsu makan ikan (apakah ikan lapar atau tidak). SmartFishSense memiliki keluaran yang bisa dihubungkan ke perangkat pemberi pakan dan melakukan pemberian pakan secara otomatis berdasarkan waktu dan tingkat kelaparan ikan. Selain itu, SmartFishSense juga terkoneksi dengan jaringan internet sehingga memudahkan pengoperasian secara daring.

### Mekanisme kerja
Mekanisme kerja dari produk cukup sederhana. Produk yang menyala akan melakukan pendeteksian terhadap nafsu makan ikan dan memberikan pakan ikan melalui perangkat pemberian pakan yang terpisah. 

- Setelah produk dinyalakan, produk akan menunggu selama beberapa jam (parameter ini bisa diatur) untuk memberikan stimulus pakan. 
- Setelah pemberian stimulus, apabila ikan dianggap lapar, pemberian pakan akan dilakukan dan diulang sampai ikan merasa kenyang. Setelah ikan kenyang, program akan kembali menunggu beberapa jam untuk kembali memberikan stimulus.

Pendeteksian tingkat kelaparan ikan hanya dilakukan produk saat setelah stimulus diberikan.

### Instalasi
Instalasi produk pertama kali dilakukan oleh operator. Calon pengguna hanya perlu memastikan ketersediaan hal-hal berikut:

1. Adanya koneksi internet yang stabil di daerah pemasangan
2. Ada sumber listrik yang bisa digunakan untuk menyalakan produk (menggunakan port USB)

Instalasi pada dasarnya hanya dilakukan dengan melakukan pairing dengan koneksi internet dan penempatan alat, jadi ini bisa dikerjakan sendiri apabila casing dibuka.

### Menyalakan Produk
Untuk menyalakan produk, pengguna hanya perlu menyolokkan kabel USB ke port USB yang sudah disediakan. Jika produk sudah menyala, indikator pada kamera akan menyala (indikator bisa dilihat langsung di dekat lensa kamera). Perlu diingat bahwasannya produk hanya bisa berjalan apabila koneksi internet ada. Oleh karena itu, walaupun produk sudah menyala, pendeteksian tidak akan dilakukan bila tidak ada koneksi internet yang tersedia.

### Antarmuka
Terdapat beberapa antarmuka yang tersedia pada casing produk, antara lain 2 buah tombol dan 2 buah lampu LED indikator.

Dua buah tombol antara lain:
- Tombol "RUN". Tombol berwarna merah dan terletak di bagian atas. Fungsi: memaksa sistem melakukan pendeteksian ketika sistem sedang dalam waktu tunggu.
- Tombol "RESET". Tombol berwarna kuning dan terletak di bagian bawah tombol merah. Fungsi: memaksa sistem masuk ke waktu tunggu kembali.

Dua buah indikator lampu antara lain:
- Lampu biru (atas): Apabila menyala, artinya tingkat kelaparan ikan tinggi. Apabila mati, tingkat kelaparan ikan rendah
- Lampu merah (bawah): Apabila menyala, produk sedang berada dalam proses pemberian pakan dan pendeteksian. Apabila mati, produk sedang berada pada waktu tunggu.

### Mematikan Produk
Produk tidak boleh dimatikan secara langsung dengan mencabut kabel dari port USB. Berikut ini langkah-langkah rekomendasi untuk mematikan produk:

1. Tekan tombol "RUN" dan "RESET" pada antarmuka offline secara bersamaan selama 3 detik
2. Setelah itu, tunggu lampu indikator kamera (indikator bisa dilihat langsung di dekat lensa kamera) mati
3. Setelah indikator kamera mati, kabel sudah bisa dicabut dari port USB
