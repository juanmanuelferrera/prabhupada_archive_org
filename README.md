# Archive.org Uploader for Author Material

Automated script to upload books, videos, and audiovisual material from a specific author to Archive.org.

**🎉 NEW! Graphical interface included for easier use.**

## 🙏 Credits and Acknowledgments

This project is inspired by the original work of **[Bandali](https://kelar.org/~bandali/home.html)**, who created a script for mirroring Protesilaos' videos to Internet Archive. His pioneering implementation demonstrated the feasibility of automating content uploads to Archive.org using Python and the `internetarchive` library.

**References:**
- [Mirroring Protesilaos' videos to Internet Archive](https://kelar.org/~bandali/2025/07/25/protesilaos-videos-archive.html) - Original script by Bandali for Protesilaos
- [Bandali's Homepage](https://kelar.org/~bandali/home.html) - Author's personal page

**Differences from Bandali's original work:**
- This project focuses on general author material (not just videos)
- Includes a complete graphical interface
- Supports multiple file types (books, audio, video, images)
- Implements automatic organization with "Uploaded" folder
- Includes collection management from the GUI

Thanks to Bandali for his contribution to the free software ecosystem and for sharing his knowledge with the community.

## 🚀 Features

- **Automated upload** of multiple file types
- **Automatic metadata** based on author and file type
- **Progress system** that allows resuming interruptions
- **Detailed logging** for error tracking
- **Support for multiple formats**: PDF, EPUB, MP3, MP4, etc.
- **Automatic organization**: uploaded files are moved to "Uploaded" folder

## 📦 Installation

### 1. Clone or download the files
\`\`\`bash
# If you have git
git clone <repository-url>
cd archive-uploader

# Or download files manually
\`\`\`

### 2. Run the installation script
\`\`\`bash
chmod +x setup_archive_uploader.sh
./setup_archive_uploader.sh
\`\`\`

### 3. Configure Archive.org credentials
\`\`\`bash
ia configure
\`\`\`
Follow the instructions to configure your Archive.org account.

## 🖥️ Graphical Interface (GUI)

### Launch the GUI:
\`\`\`bash
# Option 1: Launch script
./lanzar_gui.sh

# Option 2: Directly with Python
python3 archive_uploader_gui.py
\`\`\`

### GUI Features:
- **Intuitive interface** with buttons and menus
- **Visual directory selection**
- **File list** with detailed information
- **Real-time progress bar**
- **Integrated activity log**
- **Control buttons** (Start, Stop, Help)

## 📖 Basic Usage

\`\`\`bash
python3 archive_uploader.py /path/to/material "Author Name"
\`\`\`

### Examples

\`\`\`bash
# Upload books from an author
python3 archive_uploader.py ~/Documents/books "Carlos Fuentes"

# Upload conference videos
python3 archive_uploader.py ~/Videos/conferences "Eduardo Galeano"

# Upload material to a specific collection
python3 archive_uploader.py ~/Audio/podcasts "Gabriel García Márquez" --collection opensource
\`\`\`

## 🔧 Advanced Options

### Script Arguments

- \`directory\`: Directory with material to upload
- \`author\`: Author name
- \`--collection\`: Collection on Archive.org (default: opensource)
- \`--resume\`: Resume from the last processed file

### Supported Formats

**Books:**
- PDF, EPUB, MOBI, TXT, DOC, DOCX

**Audio:**
- MP3, WAV, FLAC, M4A, OGG

**Video:**
- MP4, AVI, MKV, MOV, WEBM

**Images:**
- JPG, JPEG, PNG, GIF, TIFF

## 📂 Automatic Organization

### "Uploaded" Folder
After successfully uploading each file, the system automatically:

1. **Creates an "Uploaded" folder** in the original directory
2. **Moves the uploaded file** to this folder
3. **Avoids duplicates** by adding timestamp if necessary
4. **Excludes already uploaded files** in future scans

### Advantages:
- ✅ **Automatic organization** of material
- ✅ **Prevents duplicate uploads**
- ✅ **Facilitates resumption** if interrupted
- ✅ **Visual control** of what has been uploaded

### Example structure:
\`\`\`
MyMaterial/
├── book1.pdf          # To upload
├── video1.mp4         # To upload
├── audio1.mp3         # To upload
└── Uploaded/          # Automatically created folder
    ├── book1.pdf      # Already uploaded
    └── video1.mp4     # Already uploaded
\`\`\`

## 📁 File Structure

### System Files:
- \`archive_uploader.py\` - Main script (command line)
- \`archive_uploader_gui.py\` - Graphical interface
- \`setup_archive_uploader.sh\` - Installation script
- \`lanzar_gui.sh\` - GUI launcher
- \`README.md\` - Documentation

### Automatically Created Files:
- \`.archive_progress.json\`: Saved progress (allows resuming)
- \`.archive_upload.log\`: Detailed activity log

## 🎯 Automatic Metadata

The script automatically generates:

- **Title**: Based on filename
- **Author**: The specified name
- **Date**: Current date
- **License**: Creative Commons BY-SA 4.0
- **Language**: Spanish (configurable)
- **Media type**: Automatically detected

### Example of generated metadata:

\`\`\`json
{
  "title": "El Laberinto De La Soledad",
  "creator": "Octavio Paz",
  "collection": "opensource",
  "mediatype": "texts",
  "language": "es",
  "licenseurl": "https://creativecommons.org/licenses/by-sa/4.0/",
  "date": "2025-01-15",
  "description": "Material by Octavio Paz: El Laberinto De La Soledad",
  "subject": ["Octavio Paz", "books", "opensource"]
}
\`\`\`

## 🔄 Resume Interrupted Process

If the process is interrupted, you can resume it:

\`\`\`bash
python3 archive_uploader.py /path/to/material "Author Name" --resume
\`\`\`

The script will automatically detect already uploaded files and continue from where it left off.

## 📊 Progress Monitoring

### View progress in real time:
\`\`\`bash
tail -f .archive_upload.log
\`\`\`

### View already processed files:
\`\`\`bash
cat .archive_progress.json | jq '.'
\`\`\`

## ⚠️ Important Considerations

### Archive.org Limits
- **Maximum file size**: 100GB
- **Speed limit**: Respects API limits
- **Daily quota**: Check your account limits

### File Organization
- **Descriptive names**: Filenames are used to generate titles
- **Folder structure**: Script processes subdirectories recursively
- **Avoid special characters**: Use simple names for better results

### Custom Metadata
To customize metadata, edit the \`generate_metadata()\` function in the script:

\`\`\`python
def generate_metadata(self, file_path: Path, mediatype: str) -> Dict:
    # Customize metadata here
    metadata = {
        'title': file_path.stem.replace('_', ' ').title(),
        'creator': self.author_name,
        'collection': self.collection,
        # Add custom fields here
        'custom_field': 'custom_value'
    }
    return metadata
\`\`\`

## 🐛 Troubleshooting

### Error: "internetarchive library not found"
\`\`\`bash
pip3 install internetarchive
\`\`\`

### Error: "requests library not found"
\`\`\`bash
pip3 install requests
\`\`\`

### Authentication error
\`\`\`bash
ia configure
\`\`\`

### Permission error
\`\`\`bash
chmod +x archive_uploader.py
\`\`\`

### File too large
- Verify the file doesn't exceed 100GB
- Consider splitting large files

## 📈 Comparison with Original Script

| Feature | Original Script | This Script |
|---------|-----------------|-------------|
| Complexity | High (YouTube + Markdown) | Medium (Local files) |
| Configuration | Complex | Simple |
| Metadata | From Markdown | Automatic |
| Progress | JSONL | JSON |
| Logging | Advanced | Basic |
| Usage | Specific | General |

## 🤝 Contributions

To improve the script:

1. Fork the repository
2. Create a branch for your feature
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This script is under MIT license. See LICENSE file for details.

## 🙏 Acknowledgments

- **Bandali** - For his pioneering work in [mirroring videos to Internet Archive](https://kelar.org/~bandali/2025/07/25/protesilaos-videos-archive.html)
- **Internet Archive** - For providing the \`internetarchive\` library and platform
- **Protesilaos Stavrou** - For his educational and philosophical content that inspired Bandali's original work
- **Free software community** - For maintaining and improving the tools used

---

**Note**: This script is for educational and preservation use. Make sure you have the necessary rights to upload material to Archive.org.
