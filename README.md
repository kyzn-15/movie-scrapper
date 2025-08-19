# 🎬 Movie Scrapper

A powerful web-based movie scraper application built with Flask that extracts movie download links from various sources and provides direct streaming downloads.

## ✨ Features

- **Smart Link Extraction**: Automatically finds Buzzheavier links from movie pages
- **Multi-Format Support**: Supports various video formats (MP4, MKV, AVI, MOV, WMV, FLV, M4V)
- **Direct Streaming**: Streams movie downloads directly to users without storing files locally
- **Intelligent File Detection**: Automatically detects file size, format, and generates proper filenames
- **Modern Web Interface**: Clean and responsive web UI for easy interaction
- **Real-time Processing**: Processes movie URLs in real-time with detailed progress information
- **Enhanced Movie Information**: Fetches and displays comprehensive movie details including poster, rating, genres, cast, and description
- **Interactive Progress Tracking**: Visual progress bar with real-time status updates during scraping process
- **Loading States & Animations**: Smooth loading animations and placeholder content for better user experience
- **Responsive Design**: Mobile-friendly interface with Bootstrap 5 and custom CSS animations

## 🚀 How It Works

The application follows a sophisticated multi-step process:

1. **URL Input**: User provides a movie page URL
2. **Buzzheavier Link Extraction**: Scrapes the page to find Buzzheavier download links
3. **Flashbang Link Discovery**: Extracts Flashbang download links from Buzzheavier pages
4. **File Information Retrieval**: Gets file details (size, format, content-type) without downloading
5. **Movie Metadata Extraction**: Fetches additional movie information (title, poster, rating, genres, cast, etc.)
6. **Direct Streaming**: Streams the movie file directly to the user's browser

## 🛠️ Technology Stack

- **Backend**: Python Flask
- **Web Scraping**: BeautifulSoup4, Requests
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **UI Framework**: Bootstrap 5.1.3
- **Icons**: Font Awesome 6.0.0
- **File Handling**: Werkzeug utilities
- **HTTP Processing**: Advanced session management with custom headers
- **CSS Animations**: Custom keyframes and transitions

## 📋 Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- Modern web browser with JavaScript enabled
- Internet connection for CDN resources (Bootstrap, Font Awesome)

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
│   ├── script.js        # Frontend JavaScript (enhanced functionality)
│   └── style.css        # Custom styling and animations
├── templates/           # HTML templates
│   └── index.html       # Main page template with enhanced UI
└── README.md            # This file
```

## 🎯 Usage

### Basic Usage

1. **Open the application** in your web browser
2. **Enter a movie URL** in the input field
3. **Click "Analisis & Siapkan Download"** to analyze the URL
4. **Watch real-time progress** as the system extracts information
5. **Review comprehensive movie details** including poster, rating, genres, and cast
6. **Click "Download Film Sekarang"** to start streaming the movie

### Enhanced Features

#### 🎭 Movie Information Display
- **Film Poster**: High-quality movie poster with hover effects
- **Rating System**: 5-star rating display with numerical value
- **Genre Tags**: Colorful genre badges with gradient styling
- **Cast & Crew**: Director and main cast information
- **Movie Metadata**: Release date, duration, country, and type
- **Description**: Scrollable movie synopsis

#### 📊 Progress Tracking
- **Real-time Status**: Live updates during the scraping process
- **Progress Bar**: Animated progress bar with percentage display
- **Step-by-step Updates**: Clear indication of current processing stage
- **Loading Animations**: Spinning icons and smooth transitions

#### 🎨 User Experience
- **Loading States**: Placeholder content while fetching data
- **Responsive Layout**: Mobile-optimized design
- **Interactive Elements**: Hover effects and smooth animations
- **Alert System**: User-friendly notifications and error messages

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
- **Description**: Main application page with enhanced UI
- **Response**: HTML template with interactive scraper interface
- **Features**: Responsive design, loading states, progress tracking

### `POST /api/get_download_info`
- **Description**: Extract download information and movie metadata from a movie URL
- **Request Body**: JSON with `film_url` field
- **Response**: JSON with comprehensive information including:
  - Film title and metadata
  - Buzzheavier link
  - Flashbang link
  - Filename and file size
  - Content type
  - Download URL
  - Movie poster and rating information

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

### Frontend Configuration

#### CSS Customization
```css
/* Custom color scheme */
:root {
    --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    --success-gradient: linear-gradient(45deg, #28a745, #20c997);
}

/* Animation settings */
.pulse {
    animation: pulse 2s infinite;
}

.loading-spinner {
    animation: spin 1s ease-in-out infinite;
}
```

#### JavaScript Features
- **Progress Simulation**: Realistic loading states with configurable delays
- **Error Handling**: Comprehensive error management with user feedback
- **Data Population**: Dynamic content loading and placeholder management
- **Responsive Interactions**: Touch-friendly mobile interactions

## 🔒 Security Features

- **Input Validation**: URL validation and sanitization
- **File Security**: Secure filename generation using Werkzeug
- **Session Management**: Flask secret key for secure sessions
- **Error Handling**: Comprehensive error handling and user feedback
- **XSS Protection**: Safe HTML rendering and content sanitization

## 🚨 Error Handling

The application includes robust error handling for:
- Invalid URLs
- Network timeouts
- Missing download links
- File access issues
- Scraping failures
- API communication errors
- Frontend JavaScript errors

## 📊 Performance Features

- **Streaming Downloads**: No local storage required
- **Connection Management**: Efficient HTTP session handling
- **Timeout Management**: Configurable timeouts for various operations
- **Memory Optimization**: Streaming responses to minimize memory usage
- **Lazy Loading**: Progressive content loading for better performance
- **CDN Integration**: Fast loading of external resources

## 🎨 UI/UX Features

### Visual Enhancements
- **Gradient Backgrounds**: Modern gradient color schemes
- **Card-based Layout**: Clean, organized information display
- **Hover Effects**: Interactive elements with smooth transitions
- **Loading Animations**: Spinning icons and progress indicators
- **Responsive Grid**: Bootstrap-based responsive layout system

### Interactive Elements
- **Progress Tracking**: Real-time progress updates
- **Status Messages**: Clear feedback during operations
- **Alert System**: User notifications and error messages
- **Button States**: Loading and disabled states for buttons
- **Form Validation**: Real-time input validation

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

4. **UI not loading properly**
   - Ensure JavaScript is enabled in your browser
   - Check if CDN resources are accessible
   - Clear browser cache and cookies

5. **Progress bar stuck**
   - Check browser console for JavaScript errors
   - Verify network connectivity
   - Try refreshing the page

### Debug Mode

Enable debug mode for detailed error information:
```python
if __name__ == '__main__':
    app.run(debug=True)
```

### Browser Console

Check browser console (F12) for:
- JavaScript errors
- Network request failures
- API response issues
- Frontend debugging information

## 🔧 Development

### Frontend Development
- **HTML Structure**: Semantic HTML5 with Bootstrap classes
- **CSS Styling**: Custom animations and responsive design
- **JavaScript**: ES6+ features with async/await support
- **Bootstrap Integration**: Responsive grid system and components

### Backend Integration
- **API Design**: RESTful endpoints with JSON responses
- **Error Handling**: Comprehensive error management
- **Session Management**: Secure user session handling
- **File Processing**: Streaming file downloads

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines
- Follow existing code style and structure
- Test new features thoroughly
- Update documentation for new features
- Ensure responsive design compatibility
- Test across different browsers and devices

## ⚠️ Disclaimer

This application is for educational purposes only. Please ensure you have the right to download any content and comply with local laws and regulations regarding digital content.

## 📞 Support

If you encounter any issues or have questions:
1. Check the troubleshooting section above
2. Review the error messages in the application
3. Check the console logs for debugging information
4. Open an issue in the repository
5. Check browser console for frontend errors

## 🔄 Updates

Stay updated with the latest features and improvements by:
- Watching the repository
- Checking for new releases
- Following the changelog
- Monitoring commit history for new features

## 📱 Browser Compatibility

- **Chrome**: 90+ (Recommended)
- **Firefox**: 88+
- **Safari**: 14+
- **Edge**: 90+
- **Mobile Browsers**: iOS Safari 14+, Chrome Mobile 90+

## 🚀 Future Enhancements

Planned features for upcoming versions:
- **User Accounts**: Personal download history and favorites
- **Batch Processing**: Multiple URL processing
- **Advanced Filtering**: File size, quality, and format filters
- **Download Queue**: Background download management
- **API Rate Limiting**: Enhanced scraping protection
- **Mobile App**: Native mobile application

---

**Happy Movie Scraping! 🎬✨**
