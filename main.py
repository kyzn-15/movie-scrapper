import os
import requests
from flask import Flask, render_template, request, jsonify, Response, flash, redirect, url_for, stream_template
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
import time
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Configuration - Tidak perlu folder download lagi
ALLOWED_EXTENSIONS = {'mp4', 'mkv', 'avi', 'mov', 'wmv', 'flv', 'm4v'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class FilmScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def extract_buzzheavier_link(self, film_url):
        """
        Mengekstrak link Buzzheavier dari halaman film dan title film
        """
        try:
            print(f"Mengakses URL film: {film_url}")
            response = self.session.get(film_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Ekstrak title film dari halaman
            film_title = None
            
            # Coba beberapa selector untuk title
            title_selectors = [
                'h1.entry-title',
                'h1.post-title', 
                'h1.title',
                '.entry-header h1',
                'title'
            ]
            
            for selector in title_selectors:
                title_element = soup.select_one(selector)
                if title_element:
                    film_title = title_element.get_text(strip=True)
                    break
            
            # Fallback: ambil dari URL
            if not film_title:
                film_title = film_url.split('/')[-2] if film_url.endswith('/') else film_url.split('/')[-1]
                film_title = film_title.replace('-', ' ').title()
            
            # Bersihkan title dari karakter yang tidak diinginkan untuk nama file
            if film_title:
                film_title = re.sub(r'[<>:"/\\|?*]', '', film_title)
                film_title = re.sub(r'\s+', ' ', film_title.strip())
                # Batasi panjang title untuk nama file
                if len(film_title) > 100:
                    film_title = film_title[:100].strip()
            
            print(f"Film title: {film_title}")
            
            # Cari div dengan class yang berisi link download
            download_box = soup.find('div', class_='bixbox mctn')
            if not download_box:
                download_box = soup.find('div', class_='dlbox')
            
            if download_box:
                # Cari semua link dalam download box
                links = download_box.find_all('a', href=True)
                for link in links:
                    href = link['href']
                    if 'buzzheavier.com' in href:
                        print(f"Link Buzzheavier ditemukan: {href}")
                        return href, film_title
            
            # Fallback: cari di seluruh halaman
            all_links = soup.find_all('a', href=True)
            for link in all_links:
                href = link['href']
                if 'buzzheavier.com' in href:
                    print(f"Link Buzzheavier ditemukan (fallback): {href}")
                    return href, film_title
                    
            return None, film_title
            
        except Exception as e:
            print(f"Error saat mengekstrak link Buzzheavier: {str(e)}")
            return None, None
    
    def find_flashbang_link(self, buzzheavier_url):
        """
        Mencari link flashbang dari halaman Buzzheavier
        """
        try:
            print(f"Mencari link flashbang di: {buzzheavier_url}")
            
            # Coba akses halaman preview terlebih dahulu
            preview_url = f"{buzzheavier_url}/preview" if not buzzheavier_url.endswith('/preview') else buzzheavier_url
            
            response = self.session.get(preview_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Cari tag video dengan src
            video_tag = soup.find("video")
            if video_tag and video_tag.get("src"):
                src = video_tag["src"]
                if "flashbang.sh/dl" in src:
                    print(f"Flashbang link ditemukan di video src: {src}")
                    return src
            
            # Cari di semua href
            for tag in soup.find_all(href=True):
                href = tag["href"]
                if "flashbang.sh/dl" in href:
                    print(f"Flashbang link ditemukan di href: {href}")
                    return href
            
            # Cari di semua src
            for tag in soup.find_all(src=True):
                src = tag["src"]
                if "flashbang.sh/dl" in src:
                    print(f"Flashbang link ditemukan di src: {src}")
                    return src
            
            # Jika tidak ditemukan di preview, coba akses halaman utama
            if preview_url != buzzheavier_url:
                response = self.session.get(buzzheavier_url, timeout=30)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Ulangi pencarian
                for tag in soup.find_all(['a', 'video', 'source', 'iframe'], src=True):
                    src = tag.get("src", "")
                    if "flashbang.sh/dl" in src:
                        print(f"Flashbang link ditemukan: {src}")
                        return src
                
                for tag in soup.find_all('a', href=True):
                    href = tag["href"]
                    if "flashbang.sh/dl" in href:
                        print(f"Flashbang link ditemukan: {href}")
                        return href
            
            return None
            
        except Exception as e:
            print(f"Error saat mencari link flashbang: {str(e)}")
            return None
    
    def get_file_info(self, flashbang_url, film_title=None):
        """
        Mendapatkan informasi file tanpa download
        """
        try:
            print(f"Mendapatkan info file dari: {flashbang_url}")
            
            # Coba GET request dulu untuk mendapatkan redirect dan info yang lebih akurat
            try:
                response = self.session.get(flashbang_url, timeout=30, allow_redirects=True, stream=True)
                response.raise_for_status()
                
                # Ambil info dari response
                file_size = int(response.headers.get('content-length', 0))
                content_type = response.headers.get('content-type', '')
                
                # Tutup connection untuk menghemat bandwidth
                response.close()
                
            except Exception as e:
                print(f"GET request failed, trying HEAD: {str(e)}")
                # Fallback ke HEAD request
                head_response = self.session.head(flashbang_url, timeout=30, allow_redirects=True)
                file_size = int(head_response.headers.get('content-length', 0))
                content_type = head_response.headers.get('content-type', '')
            
            # Tentukan extension dari content-type atau URL
            extension = '.mp4'  # default
            
            if 'video/mp4' in content_type:
                extension = '.mp4'
            elif 'video/x-msvideo' in content_type:
                extension = '.avi'
            elif 'video/quicktime' in content_type:
                extension = '.mov'
            elif 'video/x-ms-wmv' in content_type:
                extension = '.wmv'
            elif 'video/x-flv' in content_type:
                extension = '.flv'
            elif 'video/x-matroska' in content_type:
                extension = '.mkv'
            else:
                # Coba ambil dari URL
                parsed_url = urlparse(flashbang_url)
                url_path = parsed_url.path.lower()
                if '.mp4' in url_path:
                    extension = '.mp4'
                elif '.mkv' in url_path:
                    extension = '.mkv'
                elif '.avi' in url_path:
                    extension = '.avi'
                elif '.mov' in url_path:
                    extension = '.mov'
                elif '.wmv' in url_path:
                    extension = '.wmv'
                elif '.flv' in url_path:
                    extension = '.flv'
                elif '.m4v' in url_path:
                    extension = '.m4v'
            
            # Tentukan nama file berdasarkan title film
            if film_title:
                # Bersihkan title untuk nama file
                clean_title = re.sub(r'[<>:"/\\|?*]', '', film_title)
                clean_title = re.sub(r'\s+', '-', clean_title.strip())
                filename = f"{clean_title}{extension}"
            else:
                filename = f"movie{extension}"
            
            filename = secure_filename(filename)
            
            # Jika ukuran file masih 0, coba berbagai method
            if file_size == 0:
                try:
                    print("Mencoba alternative method untuk mendapatkan ukuran file...")
                    
                    # Method 1: Range request
                    partial_response = self.session.get(
                        flashbang_url, 
                        headers={'Range': 'bytes=0-1023'}, 
                        timeout=30,
                        allow_redirects=True
                    )
                    
                    content_range = partial_response.headers.get('content-range', '')
                    accept_ranges = partial_response.headers.get('accept-ranges', '')
                    
                    if content_range and '/' in content_range:
                        # Format: "bytes 0-1023/2048576"
                        total_size = content_range.split('/')[-1]
                        if total_size.isdigit():
                            file_size = int(total_size)
                            print(f"Ukuran file dari Range request: {file_size}")
                    
                    # Method 2: Jika masih 0, coba dengan stream=True
                    if file_size == 0:
                        stream_response = self.session.get(
                            flashbang_url, 
                            stream=True, 
                            timeout=10,
                            allow_redirects=True
                        )
                        content_length = stream_response.headers.get('content-length')
                        if content_length and content_length.isdigit():
                            file_size = int(content_length)
                            print(f"Ukuran file dari stream request: {file_size}")
                        
                        # Tutup connection
                        stream_response.close()
                    
                except Exception as e:
                    print(f"Alternative methods failed: {str(e)}")
                    # Tetap lanjutkan dengan file_size = 0
            
            print(f"File info - Name: {filename}, Size: {file_size} bytes, Extension: {extension}")
            
            return {
                'filename': filename,
                'size': file_size,
                'url': flashbang_url,
                'content_type': content_type
            }
            
        except Exception as e:
            print(f"Error saat mendapatkan info file: {str(e)}")
            return None
    
    def stream_download(self, flashbang_url, filename):
        """
        Stream download file langsung ke user
        """
        try:
            print(f"Memulai stream download dari: {flashbang_url}")
            
            response = self.session.get(flashbang_url, stream=True, timeout=60)
            response.raise_for_status()
            
            def generate():
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        yield chunk
            
            # Return response dengan proper headers untuk download
            return Response(
                generate(),
                headers={
                    'Content-Disposition': f'attachment; filename="{filename}"',
                    'Content-Type': 'application/octet-stream',
                    'Content-Length': response.headers.get('content-length', '')
                }
            )
            
        except Exception as e:
            print(f"Error saat stream download: {str(e)}")
            return None

# Initialize scraper
scraper = FilmScraper()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/get_download_info', methods=['POST'])
def get_download_info():
    """API endpoint untuk mendapatkan informasi download"""
    try:
        data = request.get_json()
        film_url = data.get('film_url', '').strip()
        
        if not film_url:
            return jsonify({'success': False, 'error': 'URL film tidak boleh kosong!'})
        
        # Validasi URL
        if not film_url.startswith('http'):
            film_url = 'http://' + film_url
        
        # Step 1: Extract Buzzheavier link dan title film
        buzzheavier_result = scraper.extract_buzzheavier_link(film_url)
        if not buzzheavier_result or not buzzheavier_result[0]:
            return jsonify({'success': False, 'error': 'Link Buzzheavier tidak ditemukan!'})
        
        buzzheavier_link, film_title = buzzheavier_result
        
        # Step 2: Find flashbang link
        flashbang_link = scraper.find_flashbang_link(buzzheavier_link)
        if not flashbang_link:
            return jsonify({'success': False, 'error': 'Link flashbang tidak ditemukan!'})
        
        # Step 3: Get file info dengan title film
        file_info = scraper.get_file_info(flashbang_link, film_title)
        if not file_info:
            return jsonify({'success': False, 'error': 'Tidak dapat mendapatkan informasi file!'})
        
        return jsonify({
            'success': True,
            'film_title': film_title,
            'buzzheavier_link': buzzheavier_link,
            'flashbang_link': flashbang_link,
            'filename': file_info['filename'],
            'file_size': file_info['size'],
            'content_type': file_info.get('content_type', ''),
            'download_url': url_for('direct_download', filename=file_info['filename'], url=flashbang_link)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/download')
def direct_download():
    """Direct download endpoint"""
    try:
        filename = request.args.get('filename')
        download_url = request.args.get('url')
        
        if not filename or not download_url:
            flash('Parameter tidak lengkap!', 'error')
            return redirect(url_for('index'))
        
        # Stream download langsung ke user
        download_response = scraper.stream_download(download_url, filename)
        if download_response:
            return download_response
        else:
            flash('Gagal mendownload file!', 'error')
            return redirect(url_for('index'))
            
    except Exception as e:
        flash(f'Error saat download: {str(e)}', 'error')
        return redirect(url_for('index'))

# Remove routes yang tidak diperlukan lagi
# - /scrape (diganti dengan /api/get_download_info)
# - /download/<filename> (diganti dengan /download)
# - /files (tidak diperlukan karena tidak ada penyimpanan lokal)
# - /api/scrape (diganti dengan /api/get_download_info)

if __name__ == '__main__':
    app.run(debug=True)