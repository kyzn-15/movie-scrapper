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

# Configuration
ALLOWED_EXTENSIONS = {'mp4', 'mkv', 'avi', 'mov', 'wmv', 'flv', 'm4v'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class FilmScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
    
    def extract_film_info(self, film_url):
        """
        Mengekstrak informasi film lengkap termasuk poster, genre, deskripsi, dll.
        """
        try:
            print(f"Mengakses URL film untuk info: {film_url}")
            response = self.session.get(film_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Inisialisasi film_info dictionary dengan default values
            film_info = {
                'title': 'Unknown Movie',
                'poster_url': 'https://via.placeholder.com/300x450/667eea/ffffff?text=No+Poster',
                'rating': '0.0',
                'status': 'Unknown',
                'release_date': 'Unknown',
                'duration': 'Unknown',
                'country': 'Unknown',
                'type': 'WEB-DL',
                'director': 'Unknown Director',
                'cast': 'Unknown Cast',
                'genres': ['Unknown'],
                'description': 'No description available.'
            }
            
            # Cari div dengan class 'single-info bixbox'
            single_info = soup.find('div', class_='single-info bixbox')
            
            if single_info:
                print("Found single-info bixbox div")
                
                # Extract poster image
                thumb_div = single_info.find('div', class_='thumb')
                if thumb_div:
                    img_tag = thumb_div.find('img')
                    if img_tag and img_tag.get('src'):
                        film_info['poster_url'] = img_tag['src']
                        print(f"Poster URL: {film_info['poster_url']}")
                
                # Extract title
                infox_div = single_info.find('div', class_='infox')
                if infox_div:
                    title_h2 = infox_div.find('h2')
                    if title_h2:
                        film_info['title'] = title_h2.get_text(strip=True)
                        print(f"Title: {film_info['title']}")
                    
                    # Extract rating
                    rating_div = infox_div.find('div', class_='rating')
                    if rating_div:
                        rating_strong = rating_div.find('strong')
                        if rating_strong:
                            rating_text = rating_strong.get_text(strip=True)
                            # Extract numeric rating from "Rating 6.9"
                            rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                            if rating_match:
                                film_info['rating'] = rating_match.group(1)
                                print(f"Rating: {film_info['rating']}")
                    
                    # Extract detailed info from spe class
                    info_content = infox_div.find('div', class_='info-content')
                    if info_content:
                        spe_div = info_content.find('div', class_='spe')
                        if spe_div:
                            spans = spe_div.find_all('span')
                            for span in spans:
                                text = span.get_text(strip=True)
                                
                                # Status
                                if 'Status:' in text or 'status' in text.lower():
                                    film_info['status'] = text.split(':', 1)[-1].strip()
                                
                                # Release date
                                elif 'Dirilis:' in text or 'release' in text.lower():
                                    film_info['release_date'] = text.split(':', 1)[-1].strip()
                                
                                # Duration
                                elif 'Durasi:' in text or 'duration' in text.lower():
                                    film_info['duration'] = text.split(':', 1)[-1].strip()
                                
                                # Country
                                elif 'Negara:' in text or 'country' in text.lower():
                                    country_link = span.find('a')
                                    if country_link:
                                        film_info['country'] = country_link.get_text(strip=True)
                                    else:
                                        film_info['country'] = text.split(':', 1)[-1].strip()
                                
                                # Type
                                elif 'Tipe:' in text or 'type' in text.lower():
                                    film_info['type'] = text.split(':', 1)[-1].strip()
                                
                                # Director
                                elif 'Sutradara:' in text or 'director' in text.lower():
                                    directors = []
                                    director_links = span.find_all('a')
                                    for link in director_links:
                                        directors.append(link.get_text(strip=True))
                                    if directors:
                                        film_info['director'] = ', '.join(directors)
                                    else:
                                        film_info['director'] = text.split(':', 1)[-1].strip()
                                
                                # Cast
                                elif 'Artis:' in text or 'cast' in text.lower() or 'actor' in text.lower():
                                    cast_members = []
                                    cast_links = span.find_all('a')
                                    for link in cast_links:
                                        cast_members.append(link.get_text(strip=True))
                                    if cast_members:
                                        film_info['cast'] = ', '.join(cast_members)
                                    else:
                                        film_info['cast'] = text.split(':', 1)[-1].strip()
                        
                        # Extract genres
                        genxed_div = info_content.find('div', class_='genxed')
                        if genxed_div:
                            genre_links = genxed_div.find_all('a')
                            genres = []
                            for link in genre_links:
                                genre_text = link.get_text(strip=True)
                                if genre_text:
                                    genres.append(genre_text)
                            if genres:
                                film_info['genres'] = genres
                                print(f"Genres: {film_info['genres']}")
                        
                        # Extract description
                        desc_div = info_content.find('div', class_='desc mindes')
                        if desc_div:
                            # Remove the colap span if exists
                            colap_span = desc_div.find('span', class_='colap')
                            if colap_span:
                                colap_span.decompose()
                            
                            desc_text = desc_div.get_text(strip=True)
                            if desc_text and len(desc_text) > 10:  # Ensure we have meaningful description
                                film_info['description'] = desc_text
                                print(f"Description: {film_info['description'][:100]}...")
            
            # Fallback untuk title jika tidak ditemukan
            if not film_info['title'] or film_info['title'] == 'Unknown Movie':
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
                        title_text = title_element.get_text(strip=True)
                        if title_text and len(title_text) > 2:
                            film_info['title'] = title_text
                            break
                
                # Ultimate fallback: ambil dari URL
                if not film_info['title'] or film_info['title'] == 'Unknown Movie':
                    url_parts = film_url.rstrip('/').split('/')
                    if url_parts:
                        film_info['title'] = url_parts[-1].replace('-', ' ').title()
            
            print(f"Final film info extracted: {film_info}")
            return film_info
            
        except Exception as e:
            print(f"Error saat mengekstrak info film: {str(e)}")
            # Return default info instead of None
            return {
                'title': 'Movie Download',
                'poster_url': 'https://via.placeholder.com/300x450/667eea/ffffff?text=Movie',
                'rating': '0.0',
                'status': 'Available',
                'release_date': '2024',
                'duration': 'Unknown',
                'country': 'Unknown',
                'type': 'WEB-DL',
                'director': 'Unknown',
                'cast': 'Unknown',
                'genres': ['Movie'],
                'description': 'Movie ready for download.'
            }
    
    def extract_buzzheavier_link(self, film_url):
        """
        Mengekstrak link Buzzheavier dari halaman film
        """
        try:
            print(f"Mengakses URL film untuk buzzheavier: {film_url}")
            response = self.session.get(film_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Multiple strategies to find buzzheavier link
            buzzheavier_patterns = [
                'buzzheavier.com',
                'buzzheavy.com',
                'buzz-heavy.com'
            ]
            
            # Strategy 1: Look in download boxes
            download_selectors = [
                'div.bixbox.mctn',
                'div.dlbox',
                'div.download-box',
                'div.single-download',
                '.download-links'
            ]
            
            for selector in download_selectors:
                download_box = soup.find('div', class_=selector.replace('div.', '').replace('.', ''))
                if download_box:
                    links = download_box.find_all('a', href=True)
                    for link in links:
                        href = link['href']
                        for pattern in buzzheavier_patterns:
                            if pattern in href:
                                print(f"Link Buzzheavier ditemukan di {selector}: {href}")
                                return href
            
            # Strategy 2: Look for any link containing buzzheavier
            all_links = soup.find_all('a', href=True)
            for link in all_links:
                href = link['href']
                for pattern in buzzheavier_patterns:
                    if pattern in href:
                        print(f"Link Buzzheavier ditemukan (fallback): {href}")
                        return href
            
            # Strategy 3: Look in script tags for embedded links
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string:
                    for pattern in buzzheavier_patterns:
                        if pattern in script.string:
                            # Try to extract URL from script
                            urls = re.findall(r'https?://[^\s"\']+' + pattern + r'[^\s"\']*', script.string)
                            if urls:
                                print(f"Link Buzzheavier ditemukan di script: {urls[0]}")
                                return urls[0]
                                
            print("Link Buzzheavier tidak ditemukan")
            return None
            
        except Exception as e:
            print(f"Error saat mengekstrak link Buzzheavier: {str(e)}")
            return None
    
    def find_flashbang_link(self, buzzheavier_url):
        """
        Mencari link flashbang dari halaman Buzzheavier
        """
        try:
            print(f"Mencari link flashbang di: {buzzheavier_url}")
            
            # Multiple URL variations to try
            urls_to_try = [
                buzzheavier_url,
                f"{buzzheavier_url.rstrip('/')}/preview",
                f"{buzzheavier_url.rstrip('/')}/download"
            ]
            
            for url in urls_to_try:
                try:
                    print(f"Trying URL: {url}")
                    response = self.session.get(url, timeout=30)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Strategy 1: Look for video tags with flashbang src
                    video_tags = soup.find_all("video")
                    for video in video_tags:
                        if video.get("src") and "flashbang.sh" in video["src"]:
                            print(f"Flashbang link ditemukan di video src: {video['src']}")
                            return video["src"]
                    
                    # Strategy 2: Look for source tags inside video
                    source_tags = soup.find_all("source")
                    for source in source_tags:
                        if source.get("src") and "flashbang.sh" in source["src"]:
                            print(f"Flashbang link ditemukan di source src: {source['src']}")
                            return source["src"]
                    
                    # Strategy 3: Look in all href attributes
                    for tag in soup.find_all(href=True):
                        href = tag["href"]
                        if "flashbang.sh" in href:
                            print(f"Flashbang link ditemukan di href: {href}")
                            return href
                    
                    # Strategy 4: Look in all src attributes
                    for tag in soup.find_all(src=True):
                        src = tag["src"]
                        if "flashbang.sh" in src:
                            print(f"Flashbang link ditemukan di src: {src}")
                            return src
                    
                    # Strategy 5: Look in script tags
                    scripts = soup.find_all('script')
                    for script in scripts:
                        if script.string:
                            flashbang_urls = re.findall(r'https?://[^\s"\']*flashbang\.sh[^\s"\']*', script.string)
                            if flashbang_urls:
                                print(f"Flashbang link ditemukan di script: {flashbang_urls[0]}")
                                return flashbang_urls[0]
                    
                except Exception as e:
                    print(f"Error trying URL {url}: {str(e)}")
                    continue
            
            print("Flashbang link tidak ditemukan di semua URL")
            return None
            
        except Exception as e:
            print(f"Error saat mencari link flashbang: {str(e)}")
            return None
    
    def get_file_info(self, flashbang_url, film_title=None):
        """
        Mendapatkan informasi file dengan multiple fallback methods
        """
        try:
            print(f"Mendapatkan info file dari: {flashbang_url}")
            
            file_size = 0
            content_type = 'video/mp4'
            
            # Method 1: HEAD request dengan timeout yang lebih pendek
            try:
                print("Trying HEAD request...")
                head_response = self.session.head(
                    flashbang_url, 
                    timeout=15,  # Reduced timeout
                    allow_redirects=True,
                    headers={'User-Agent': self.session.headers['User-Agent']}
                )
                
                print(f"HEAD response status: {head_response.status_code}")
                print(f"HEAD response headers: {dict(head_response.headers)}")
                
                if head_response.status_code in [200, 302, 301]:
                    content_length = head_response.headers.get('content-length')
                    if content_length and content_length.isdigit():
                        file_size = int(content_length)
                        print(f"File size from HEAD: {file_size} bytes")
                    
                    content_type = head_response.headers.get('content-type', 'video/mp4')
                    print(f"Content type from HEAD: {content_type}")
                
            except Exception as e:
                print(f"HEAD request failed: {str(e)}")
            
            # Method 2: Partial GET request dengan Range header
            if file_size == 0:
                try:
                    print("Trying partial GET request with Range header...")
                    partial_response = self.session.get(
                        flashbang_url, 
                        headers={
                            'Range': 'bytes=0-1023',
                            'User-Agent': self.session.headers['User-Agent']
                        }, 
                        timeout=20,
                        allow_redirects=True,
                        stream=True
                    )
                    
                    print(f"Partial GET status: {partial_response.status_code}")
                    print(f"Partial GET headers: {dict(partial_response.headers)}")
                    
                    if partial_response.status_code == 206:  # Partial Content
                        content_range = partial_response.headers.get('content-range', '')
                        print(f"Content-Range header: {content_range}")
                        
                        # Parse content-range: "bytes 0-1023/104857600"
                        if '/' in content_range:
                            total_size = content_range.split('/')[-1]
                            if total_size.isdigit():
                                file_size = int(total_size)
                                print(f"File size from Range: {file_size} bytes")
                    
                    elif partial_response.status_code == 200:  # Full content
                        content_length = partial_response.headers.get('content-length')
                        if content_length and content_length.isdigit():
                            file_size = int(content_length)
                            print(f"File size from full response: {file_size} bytes")
                    
                    # Update content type
                    content_type = partial_response.headers.get('content-type', content_type)
                    
                    # Close the response to avoid connection issues
                    partial_response.close()
                    
                except Exception as e:
                    print(f"Partial GET failed: {str(e)}")
            
            # Method 3: Try direct connection and read headers only
            if file_size == 0:
                try:
                    print("Trying direct connection method...")
                    # Just start the request and read headers
                    with self.session.get(
                        flashbang_url, 
                        stream=True, 
                        timeout=(10, 5),  # (connect timeout, read timeout)
                        allow_redirects=True
                    ) as response:
                        print(f"Direct connection status: {response.status_code}")
                        
                        if response.status_code == 200:
                            content_length = response.headers.get('content-length')
                            if content_length and content_length.isdigit():
                                file_size = int(content_length)
                                print(f"File size from direct connection: {file_size} bytes")
                            
                            content_type = response.headers.get('content-type', content_type)
                            
                except Exception as e:
                    print(f"Direct connection failed: {str(e)}")
            
            # If still no size, try to estimate from similar files or use reasonable default
            if file_size == 0:
                print("Could not determine file size, using estimation...")
                # Estimate based on content type and common file sizes
                if 'video' in content_type.lower():
                    file_size = 1073741824  # 1GB for video
                elif 'audio' in content_type.lower():
                    file_size = 104857600   # 100MB for audio
                else:
                    file_size = 524288000   # 500MB default
                print(f"Estimated file size: {file_size} bytes")
            
            # Determine file extension from content-type or URL
            extension = '.mp4'  # default
            
            content_type_map = {
                'video/mp4': '.mp4',
                'video/x-msvideo': '.avi',
                'video/quicktime': '.mov',
                'video/x-ms-wmv': '.wmv',
                'video/x-flv': '.flv',
                'video/x-matroska': '.mkv',
                'video/mp4v-es': '.m4v'
            }
            
            # Map content type to extension
            for ct, ext in content_type_map.items():
                if ct.lower() in content_type.lower():
                    extension = ext
                    break
            
            # Also check URL for extension hints
            parsed_url = urlparse(flashbang_url)
            url_path = parsed_url.path.lower()
            for ext in ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.m4v']:
                if ext in url_path:
                    extension = ext
                    break
            
            # Create clean filename
            if film_title:
                # Clean title for filename
                clean_title = re.sub(r'[<>:"/\\|?*]', '', str(film_title))
                clean_title = re.sub(r'\s+', '-', clean_title.strip())
                # Limit filename length
                if len(clean_title) > 100:
                    clean_title = clean_title[:100]
                filename = f"{clean_title}{extension}"
            else:
                filename = f"movie-download{extension}"
            
            filename = secure_filename(filename)
            
            print(f"Final file info - Name: {filename}, Size: {file_size} bytes ({file_size/(1024**3):.2f} GB), Extension: {extension}")
            
            return {
                'filename': filename,
                'size': file_size,
                'url': flashbang_url,
                'content_type': content_type
            }
            
        except Exception as e:
            print(f"Error saat mendapatkan info file: {str(e)}")
            # Return reasonable default info
            filename = 'movie-download.mp4'
            if film_title:
                clean_title = re.sub(r'[<>:"/\\|?*\s]+', '-', str(film_title))
                filename = f"{clean_title[:50]}.mp4"
            
            return {
                'filename': secure_filename(filename),
                'size': 1073741824,  # 1GB default
                'url': flashbang_url,
                'content_type': 'video/mp4'
            }
    
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
                    'Content-Length': response.headers.get('content-length', ''),
                    'Accept-Ranges': 'bytes'
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

def format_file_size(size_bytes):
    """Helper function untuk format ukuran file"""
    if not size_bytes or size_bytes == 0:
        return "Unknown"
    
    try:
        size_bytes = int(size_bytes)
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024**2:
            return f"{size_bytes/1024:.1f} KB"
        elif size_bytes < 1024**3:
            return f"{size_bytes/(1024**2):.1f} MB"
        else:
            return f"{size_bytes/(1024**3):.2f} GB"
    except (ValueError, TypeError):
        return "Unknown"

@app.route('/api/get_download_info', methods=['POST'])
def get_download_info():
    """API endpoint untuk mendapatkan informasi download dan film info"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'})
            
        film_url = data.get('film_url', '').strip()
        
        if not film_url:
            return jsonify({'success': False, 'error': 'URL film tidak boleh kosong!'})
        
        # Validasi URL
        if not film_url.startswith(('http://', 'https://')):
            film_url = 'http://' + film_url
        
        print(f"Processing URL: {film_url}")
        
        # Step 1: Extract film info (poster, genre, deskripsi, dll.)
        print("Step 1: Extracting film info...")
        film_info = scraper.extract_film_info(film_url)
        if not film_info:
            return jsonify({'success': False, 'error': 'Tidak dapat mengekstrak informasi film!'})
        
        # Step 2: Extract Buzzheavier link
        print("Step 2: Finding Buzzheavier link...")
        buzzheavier_link = scraper.extract_buzzheavier_link(film_url)
        if not buzzheavier_link:
            return jsonify({'success': False, 'error': 'Link Buzzheavier tidak ditemukan! Pastikan halaman memiliki link download.'})
        
        # Step 3: Find flashbang link
        print("Step 3: Finding flashbang link...")
        flashbang_link = scraper.find_flashbang_link(buzzheavier_link)
        if not flashbang_link:
            return jsonify({'success': False, 'error': 'Link download tidak ditemukan! Mungkin link sudah expired atau tidak valid.'})
        
        # Step 4: Get file info dengan title film
        print("Step 4: Getting file info...")
        file_info = scraper.get_file_info(flashbang_link, film_info['title'])
        if not file_info:
            return jsonify({'success': False, 'error': 'Tidak dapat mendapatkan informasi file!'})
        
        print("All steps completed successfully!")
        print(f"Final file info: {file_info}")
        
        # Prepare response with explicit file size information
        response_data = {
            'success': True,
            # Film information
            'film_info': {
                'title': film_info['title'],
                'poster_url': film_info['poster_url'],
                'rating': film_info['rating'],
                'status': film_info['status'],
                'release_date': film_info['release_date'],
                'duration': film_info['duration'],
                'country': film_info['country'],
                'type': film_info['type'],
                'director': film_info['director'],
                'cast': film_info['cast'],
                'genres': film_info['genres'],
                'description': film_info['description']
            },
            # Download information
            'film_title': film_info['title'],
            'filename': file_info['filename'],
            'file_size': file_info['size'],  # Raw size in bytes
            'file_size_formatted': format_file_size(file_info['size']),  # Formatted size
            'buzzheavier_link': flashbang_link,
            'flashbang_link': flashbang_link,
            'content_type': file_info.get('content_type', ''),
            'download_url': url_for('direct_download', filename=file_info['filename'], url=flashbang_link)
        }
        
        print(f"Sending response with file_size: {response_data['file_size']} bytes")
        print(f"Formatted file size: {response_data['file_size_formatted']}")
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"API Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Terjadi kesalahan server: {str(e)}'})

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

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500
    
if __name__ == '__main__':
    app.run(debug=True)