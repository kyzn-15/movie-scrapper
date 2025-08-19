# 🎬 Movie Scrapper

A powerful web-based movie scraper application built with Flask that extracts movie download links from various sources and provides direct streaming downloads.

## ✨ Features

- **Smart Link Extraction**: Automatically finds Buzzheavier links from movie pages
- **Multi-Format Support**: Supports various video formats (MP4, MKV, AVI, MOV, WMV, FLV, M4V)
- **Direct Streaming**: Streams movie downloads directly to users without storing files locally
- **Intelligent File Detection**: Automatically detects file size, format, and generates proper filenames
- **Modern Web Interface**: Clean and responsive web UI for easy interaction
- **Real-time Processing**: Processes movie URLs in real-time with detailed progress information

## 🚀 How It Works

The application follows a sophisticated multi-step process:

1. **URL Input**: User provides a movie page URL
2. **Buzzheavier Link Extraction**: Scrapes the page to find Buzzheavier download links
3. **Flashbang Link Discovery**: Extracts Flashbang download links from Buzzheavier pages
4. **File Information Retrieval**: Gets file details (size, format, content-type) without downloading
5. **Direct Streaming**: Streams the movie file directly to the user's browser

## 🛠️ Technology Stack

- **Backend**: Python Flask
- **Web Scraping**: BeautifulSoup4, Requests
- **Frontend**: HTML5, CSS3, JavaScript
- **File Handling**: Werkzeug utilities
- **HTTP Processing**: Advanced session management with custom headers

## 📋 Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- Modern web browser

## 🔧 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Movie-Scrapper
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

   If you don't have a requirements.txt file, install the required packages manually:
   ```bash
   pip install flask requests beautifulsoup4 werkzeug
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

4. **Open your browser**
   Navigate to `http://localhost:5000`

## 📁 Project Structure

```
Movie Scrapper/
├── main.py              # Main Flask application
├── static/              # Static assets
│   ├── script.js        # Frontend JavaScript
│   └── style.css        # Styling
├── templates/           # HTML templates
│   └── index.html       # Main page template
└── README.md            # This file
```

## 🎯 Usage

### Basic Usage

1. **Open the application** in your web browser
2. **Enter a movie URL** in the input field
3. **Click "Get Download Info"** to analyze the URL
4. **Review the extracted information** (title, file size, format)
5. **Click "Download"** to start streaming the movie

### Supported URL Formats

The application can handle various movie page formats:
- Direct movie page URLs
- URLs with or without `http://` prefix
- Various movie website structures

### File Format Support

- **MP4** - Most common format
- **MKV** - High-quality video container
- **AVI** - Legacy video format
- **MOV** - Apple QuickTime format
- **WMV** - Windows Media format
- **FLV** - Flash video format
- **M4V** - iTunes video format

## 🔍 API Endpoints

### `GET /`
- **Description**: Main application page
- **Response**: HTML template with the scraper interface

### `POST /api/get_download_info`
- **Description**: Extract download information from a movie URL
- **Request Body**: JSON with `film_url` field
- **Response**: JSON with extracted information including:
  - Film title
  - Buzzheavier link
  - Flashbang link
  - Filename
  - File size
  - Content type
  - Download URL

### `GET /download`
- **Description**: Stream download a movie file
- **Query Parameters**: 
  - `filename`: Name of the file to download
  - `url`: Direct download URL
- **Response**: Streaming file download

## ⚙️ Configuration

### Environment Variables

The application uses a secret key for session management:
```python
app.secret_key = 'your-secret-key-here'
```

### Allowed File Extensions

Configure supported video formats in the `ALLOWED_EXTENSIONS` set:
```python
ALLOWED_EXTENSIONS = {'mp4', 'mkv', 'avi', 'mov', 'wmv', 'flv', 'm4v'}
```

### User Agent

Custom User-Agent for web scraping:
```python
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
```

## 🔒 Security Features

- **Input Validation**: URL validation and sanitization
- **File Security**: Secure filename generation using Werkzeug
- **Session Management**: Flask secret key for secure sessions
- **Error Handling**: Comprehensive error handling and user feedback

## 🚨 Error Handling

The application includes robust error handling for:
- Invalid URLs
- Network timeouts
- Missing download links
- File access issues
- Scraping failures

## 📊 Performance Features

- **Streaming Downloads**: No local storage required
- **Connection Management**: Efficient HTTP session handling
- **Timeout Management**: Configurable timeouts for various operations
- **Memory Optimization**: Streaming responses to minimize memory usage

## 🐛 Troubleshooting

### Common Issues

1. **"Link Buzzheavier tidak ditemukan"**
   - Check if the movie URL is correct
   - Ensure the website structure hasn't changed
   - Try different movie pages

2. **"Link flashbang tidak ditemukan"**
   - The Buzzheavier page structure may have changed
   - Check if the movie is still available

3. **Download fails**
   - Check your internet connection
   - Verify the file is still accessible
   - Try refreshing the page

### Debug Mode

Enable debug mode for detailed error information:
```python
if __name__ == '__main__':
    app.run(debug=True)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## ⚠️ Disclaimer

This application is for educational purposes only. Please ensure you have the right to download any content and comply with local laws and regulations regarding digital content.

## 📞 Support

If you encounter any issues or have questions:
1. Check the troubleshooting section above
2. Review the error messages in the application
3. Check the console logs for debugging information
4. Open an issue in the repository

## 🔄 Updates

Stay updated with the latest features and improvements by:
- Watching the repository
- Checking for new releases
- Following the changelog

---

**Happy Movie Scraping! 🎬✨** # movie-scrapper
