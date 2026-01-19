"""
Web scraping service for PapaCambridge.
Moved from scripts/web_data.py - refactored for FastAPI.
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote

from app.core.models import LinkClass


def get_exam_classes(url: str, pattern: str):
    """
    Get all subjects for a qualification.
    
    Parameters:
    url (str): The URL to the qualification page
    pattern (str): Pattern used to identify valid links
    
    Returns:
    List of LinkClass objects
    """
    print('Fetching Exam links...')
    page = requests.get(url).text
    soup = BeautifulSoup(page, "html.parser")
    exams = []
    
    # Find all links that contain the pattern and look like subject links
    all_links = soup.find_all('a', href=True)
    for a in all_links:
        href = a.get('href', '')
        text = a.text.strip()
        
        # Check if this is a subject link
        if pattern in href.lower() and ('-' in href or text):
            # Make sure it's a relative link to a subject page
            if href.startswith('papers/caie/') or href.startswith('/papers/caie/'):
                # Fix URL - if href is relative, make it absolute
                if href.startswith('/'):
                    full_url = 'https://pastpapers.papacambridge.com' + href
                elif href.startswith('papers/'):
                    full_url = 'https://pastpapers.papacambridge.com/' + href
                else:
                    full_url = urljoin(url, href)
                exams.append(LinkClass(text, full_url))
                print(f"Found: {text}")
    
    print(f'Finished fetching {len(exams)} Exam links')
    return exams


def get_exam_seasons(url: str):
    """
    Get all seasons (years) for a subject.
    
    Parameters:
    url (str): The URL of the subject page
    
    Returns:
    List of LinkClass objects
    """
    print('Fetching exam seasons')
    page = requests.get(url).text
    soup = BeautifulSoup(page, "html.parser")
    exam_seasons = []
    
    # Find all links that look like season links
    all_links = soup.find_all('a', href=True)
    seen_seasons = set()
    
    for a in all_links:
        href = a.get('href', '')
        text = a.text.strip()
        
        # Check if this looks like a season link
        if (href.startswith('papers/caie/') or href.startswith('/papers/caie/')) and \
           any(keyword in text.lower() or keyword in href.lower() 
               for keyword in ['nov', 'june', 'march', 'may', 'oct', '202', '201']):
            # Fix URL - if href is relative, make it absolute
            if href.startswith('/'):
                full_url = 'https://pastpapers.papacambridge.com' + href
            elif href.startswith('papers/'):
                full_url = 'https://pastpapers.papacambridge.com/' + href
            else:
                full_url = urljoin(url, href)
            # Avoid duplicates
            if full_url not in seen_seasons:
                seen_seasons.add(full_url)
                exam_seasons.append(LinkClass(text, full_url))
                print(f'Found season: {text}')
    
    return exam_seasons


def get_exams(url: str):
    """
    Get all individual exam files for a season.
    
    Parameters:
    url (str): The URL of the season page
    
    Returns:
    List of LinkClass objects
    """
    print('Fetching individual exams...')
    page = requests.get(url).text
    soup = BeautifulSoup(page, "html.parser")
    exams = []
    
    # Find all download links that use download_file.php
    download_links = soup.find_all('a', href=lambda x: x and 'download_file.php' in x)
    
    for link in download_links:
        href = link.get('href', '')
        
        # Extract the file URL from the download_file.php parameter
        if 'files=' in href:
            # Decode the URL parameter
            file_url = unquote(href.split('files=')[1].split('&')[0])
            # Extract filename from URL
            exam_name = file_url.split('/')[-1]
            
            # Use the direct file URL for downloading
            exams.append(LinkClass(exam_name, file_url))
            print(f'Found exam file: {exam_name}')
    
    return exams
