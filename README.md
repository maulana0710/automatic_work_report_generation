# Weekly Report Generator

Aplikasi web untuk menghasilkan laporan pekerjaan mingguan dalam format PDF dari file Markdown.

## Fitur

- **Upload Markdown** - Drag & drop atau pilih file .md
- **Multiple Files** - Gabungkan beberapa file MD menjadi satu laporan
- **Template System** - Gunakan template untuk format yang konsisten
- **Custom Styling** - CSS styling untuk tampilan PDF profesional
- **Preview** - Lihat preview HTML sebelum generate PDF
- **Auto Week Calculation** - Kalkulasi otomatis tanggal minggu

## Tech Stack

| Komponen | Teknologi |
|----------|-----------|
| Backend | FastAPI (Python) |
| Frontend | HTMX + Alpine.js |
| PDF Generation | WeasyPrint |
| Markdown Parser | Python-Markdown |
| Template Engine | Jinja2 |

## Instalasi

### Prasyarat

- Python 3.10+ (ARM64 untuk Apple Silicon)
- Homebrew (untuk macOS)

### Langkah Instalasi

1. **Clone repository**
   ```bash
   cd automatic_work_report_generation
   ```

2. **Install system dependencies (macOS)**
   ```bash
   brew install pango
   ```

3. **Buat virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Jalankan aplikasi**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

6. **Buka di browser**
   ```
   http://localhost:8000
   ```

## Penggunaan

### Via Web Interface

1. Buka `http://localhost:8000`
2. Upload file Markdown (drag & drop atau klik "Select Files")
3. Isi konfigurasi laporan:
   - Report Title
   - Week Number
   - Author Name
   - Department
4. Klik "Preview HTML" untuk melihat preview
5. Klik "Generate PDF" untuk mengunduh PDF

### Via API

#### Upload File

```bash
curl -X POST http://localhost:8000/api/upload \
  -F "files=@report.md"
```

Response:
```json
{
  "files": [
    {
      "file_id": "uuid-here",
      "original_name": "report.md",
      "size": 1234,
      "uploaded_at": "2024-12-30T10:00:00"
    }
  ],
  "message": "Successfully uploaded 1 file(s)"
}
```

#### Generate PDF

```bash
curl -X POST http://localhost:8000/api/reports/generate \
  -H "Content-Type: application/json" \
  -d '{
    "file_ids": ["uuid-here"],
    "template_name": "default_report.html",
    "css_files": ["default.css"],
    "variables": {
      "week_number": 1,
      "author_name": "John Doe",
      "department": "Engineering",
      "report_title": "Weekly Progress Report"
    }
  }'
```

Response:
```json
{
  "report_id": "uuid-here",
  "filename": "Weekly Progress Report_abc123.pdf",
  "size": 114962,
  "generated_at": "2024-12-30T10:00:00",
  "download_url": "/api/reports/uuid-here/download"
}
```

#### Download PDF

```bash
curl -O http://localhost:8000/api/reports/{report_id}/download
```

## API Reference

| Endpoint | Method | Deskripsi |
|----------|--------|-----------|
| `/` | GET | Web interface |
| `/health` | GET | Health check |
| `/api/upload` | GET | List uploaded files |
| `/api/upload` | POST | Upload MD files |
| `/api/upload/{file_id}` | DELETE | Delete file |
| `/api/upload/{file_id}/content` | GET | Get file content |
| `/api/templates` | GET | List templates |
| `/api/templates/styles` | GET | List CSS styles |
| `/api/reports` | GET | List generated reports |
| `/api/reports/generate` | POST | Generate PDF |
| `/api/reports/{id}/download` | GET | Download PDF |
| `/api/reports/{id}` | DELETE | Delete report |
| `/api/preview/html` | POST | HTML preview |
| `/api/preview/pdf` | POST | PDF preview (stream) |

## Struktur Proyek

```
automatic_work_report_generation/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI entry point
│   ├── config.py                  # Application settings
│   ├── api/
│   │   ├── routes/
│   │   │   ├── upload.py          # File upload endpoints
│   │   │   ├── templates.py       # Template management
│   │   │   ├── reports.py         # PDF generation
│   │   │   └── preview.py         # Preview endpoints
│   │   └── schemas/
│   │       ├── upload.py          # Upload models
│   │       ├── report.py          # Report models
│   │       └── template.py        # Template models
│   ├── core/
│   │   ├── file_manager.py        # File handling
│   │   ├── markdown_parser.py     # MD to HTML
│   │   ├── pdf_generator.py       # WeasyPrint wrapper
│   │   └── template_engine.py     # Jinja2 processing
│   └── services/
│       └── report_service.py      # Business logic
├── templates/
│   └── default_report.html        # PDF template
├── static/
│   └── css/pdf/
│       └── default.css            # PDF stylesheet
├── frontend/
│   └── index.html                 # Web UI
├── uploads/                       # Uploaded files (temp)
├── output/                        # Generated PDFs
├── requirements.txt
├── .gitignore
└── README.md
```

## Template Variables

Variabel yang tersedia dalam template:

| Variable | Deskripsi | Contoh |
|----------|-----------|--------|
| `week_number` | Nomor minggu | 52 |
| `week_start_date` | Tanggal awal minggu | December 23, 2024 |
| `week_end_date` | Tanggal akhir minggu | December 27, 2024 |
| `author_name` | Nama penulis | John Doe |
| `author_email` | Email penulis | john@example.com |
| `department` | Departemen | Engineering |
| `report_title` | Judul laporan | Weekly Progress Report |
| `generation_date` | Tanggal generate | December 30, 2024 |
| `content` | Konten HTML dari MD | `<h1>...</h1>` |
| `toc` | Table of Contents | `<ul>...</ul>` |
| `show_toc` | Tampilkan TOC | true/false |

## Combine Modes

Saat menggunakan multiple files:

| Mode | Deskripsi |
|------|-----------|
| `sequential` | File digabung berurutan dengan separator |
| `sectioned` | Setiap file menjadi section dengan header |
| `chaptered` | Setiap file menjadi chapter (page break) |

## Contoh Markdown Input

```markdown
# Weekly Progress Report

## Completed Tasks

- Implemented user authentication
- Fixed payment processing bug
- Updated API documentation

## In Progress

| Task | Status | ETA |
|------|--------|-----|
| Database optimization | 70% | Friday |
| Mobile integration | 50% | Next week |

## Code Changes

\`\`\`python
def calculate_metrics():
    return {"total": 100, "average": 50}
\`\`\`

## Blockers

1. Waiting for design approval
2. Need production access

## Next Week Goals

- Complete database optimization
- Start mobile app integration
```

## Kustomisasi

### Menambah Template Baru

1. Buat file HTML di `templates/`
2. Gunakan variabel Jinja2 seperti `{{ report_title }}`
3. Template akan otomatis muncul di dropdown

### Menambah CSS Style

1. Buat file CSS di `static/css/pdf/`
2. Style akan otomatis muncul di API `/api/templates/styles`

### Contoh Custom CSS

```css
@page {
    size: A4;
    margin: 2cm;

    @top-center {
        content: "Company Report";
    }

    @bottom-center {
        content: "Page " counter(page);
    }
}

body {
    font-family: 'Helvetica', sans-serif;
    font-size: 11pt;
}

h1 {
    color: #0066cc;
    border-bottom: 2px solid #0066cc;
}
```

## Troubleshooting

### WeasyPrint Error: cannot load library

Pastikan Pango terinstall:
```bash
brew install pango
```

### Architecture Mismatch (Apple Silicon)

Gunakan Python dari Homebrew:
```bash
/opt/homebrew/bin/python3 -m venv venv
```

### File Upload Gagal

- Pastikan file berekstensi `.md` atau `.markdown`
- Maksimal ukuran file: 10MB

###
Command untuk mengambil log git
git log --since="2025-12-22" --until="2025-12-24" > git-log-22-24-desember-2025.md 

## License

MIT License
