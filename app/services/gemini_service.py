"""Google Gemini AI Service for processing git logs into work reports."""

from typing import Optional
from app.config import settings
from app.core.file_manager import file_manager


class GeminiService:
    """Handles Google Gemini API interactions for AI processing."""

    def __init__(self):
        self.model = None
        self._initialize()

    def _initialize(self):
        """Initialize Gemini model if API key is configured."""
        if settings.gemini_api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.gemini_api_key)
                self.model = genai.GenerativeModel(settings.gemini_model)
            except Exception as e:
                print(f"Failed to initialize Gemini: {e}")
                self.model = None

    def is_configured(self) -> bool:
        """Check if Gemini API is properly configured."""
        return self.model is not None

    def process_gitlog(self, file_id: str) -> str:
        """
        Convert git log to detailed work report.

        Args:
            file_id: ID of the uploaded git log file

        Returns:
            Processed markdown content
        """
        if not self.is_configured():
            raise ValueError("Gemini API is not configured. Please set GEMINI_API_KEY in .env")

        content = file_manager.get_file_content(file_id)
        if not content:
            raise ValueError(f"File with ID {file_id} not found")

        prompt = """Kamu adalah technical writer Indonesia yang ahli dalam menulis laporan kerja.
Ubah git log berikut menjadi laporan kerja detail dalam Bahasa Indonesia yang profesional.

⚠️ ATURAN URUTAN WAKTU (SANGAT PENTING - WAJIB DIPATUHI):
- SELALU urutkan laporan secara KRONOLOGIS dari tanggal TERLAMA ke TERBARU
- Contoh urutan yang BENAR: 22 Desember → 23 Desember → 24 Desember
- Contoh urutan yang SALAH: 24 Desember → 23 Desember → 22 Desember
- ABAIKAN urutan dalam file input, SELALU susun ulang berdasarkan tanggal dari yang paling awal
- Dalam setiap tanggal, urutkan commit dari waktu paling pagi ke waktu paling malam

Format output sebagai Markdown dengan struktur:
1. **Judul utama** berisi periode tanggal dari git log
2. **Ringkasan Perubahan** - overview singkat dari semua perubahan
3. **Detail per Tanggal** - kelompokkan commit berdasarkan tanggal (DARI TANGGAL TERLAMA KE TERBARU):
   - Untuk setiap commit, buat section dengan:
     - Judul deskriptif yang mudah dipahami (BUKAN copy-paste pesan commit)
     - **Commit:** hash commit
     - **Author:** nama author
     - **Waktu:** jam commit
     - **Deskripsi:** jelaskan dengan detail apa yang dikerjakan, mengapa, dan dampaknya
4. **Statistik Perubahan** - ringkasan jumlah commit, kategori perubahan
5. **Fitur Utama yang Ditambahkan** - list fitur baru
6. **Perbaikan Bug** - list bug yang diperbaiki
7. **Peningkatan UI/UX** - jika ada

ATURAN LAINNYA:
- Tulis dalam Bahasa Indonesia yang profesional dan mudah dipahami
- Jangan gunakan istilah teknis yang terlalu rumit, jelaskan dengan bahasa sederhana
- Fokus pada VALUE dan DAMPAK dari setiap perubahan
- Buat deskripsi yang informatif, bukan hanya copy-paste pesan commit
- Jangan menampilkan daftar "File yang diubah" karena membuat pembaca bingung
- JANGAN menerjemahkan atau mengartikan singkatan yang merupakan nama project, fitur, atau perusahaan (contoh: BRT, API, SDK, dll). Biarkan singkatan tersebut apa adanya.
- Jika ada nama branch seperti "feat/purchase-brt" atau "fix/create-purchase-brt", "brt" adalah nama fitur/module, BUKAN singkatan yang perlu diartikan.

Git Log:
"""

        response = self.model.generate_content(prompt + content)
        return response.text

    def process_content(self, content: str, custom_prompt: str) -> str:
        """
        Process any content with custom prompt.

        Args:
            content: Text content to process
            custom_prompt: Custom instructions for AI

        Returns:
            Processed content
        """
        if not self.is_configured():
            raise ValueError("Gemini API is not configured")

        response = self.model.generate_content(f"{custom_prompt}\n\n{content}")
        return response.text


# Singleton instance - will initialize on first import
gemini_service = GeminiService()
