"""
Library Scanner for VirtualDJ-MCP

This module provides functionality to scan and manage the music library,
including track metadata extraction and library statistics.
"""
import asyncio
import hashlib
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Third-party imports
import mutagen
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.oggvorbis import OggVorbis

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class TrackInfo:
    """Dataclass to store track information."""
    file_path: str
    file_hash: str
    title: str = ""
    artist: str = ""
    album: str = ""
    genre: str = ""
    year: int = 0
    bpm: float = 0.0
    key: str = ""
    duration: float = 0.0
    bitrate: int = 0
    sample_rate: int = 0
    channels: int = 2  # Default to stereo
    file_size: int = 0
    last_modified: float = 0.0
    date_added: float = field(default_factory=time.time)
    play_count: int = 0
    last_played: float = 0.0
    rating: int = 0
    tags: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, any]:
        """Convert TrackInfo to dictionary."""
        return {
            'file_path': self.file_path,
            'file_hash': self.file_hash,
            'title': self.title,
            'artist': self.artist,
            'album': self.album,
            'genre': self.genre,
            'year': self.year,
            'bpm': self.bpm,
            'key': self.key,
            'duration': self.duration,
            'bitrate': self.bitrate,
            'sample_rate': self.sample_rate,
            'channels': self.channels,
            'file_size': self.file_size,
            'last_modified': self.last_modified,
            'date_added': self.date_added,
            'play_count': self.play_count,
            'last_played': self.last_played,
            'rating': self.rating,
            'tags': self.tags
        }

    @classmethod
    def from_dict(cls, data: Dict[str, any]) -> 'TrackInfo':
        """Create TrackInfo from dictionary."""
        track = cls(
            file_path=data['file_path'],
            file_hash=data['file_hash']
        )
        for key, value in data.items():
            if hasattr(track, key):
                setattr(track, key, value)
        return track

class LibraryScanner:
    """Handles scanning and managing the music library."""
    
    # Supported audio file extensions
    SUPPORTED_EXTENSIONS = {'.mp3', '.wav', '.flac', '.ogg', '.aac', '.m4a', '.wma', '.aiff', '.aif'}
    
    def __init__(self, library_path: Optional[str] = None):
        """Initialize the library scanner with the path to the music library."""
        from ..config import VDJConfig
        config = VDJConfig.from_env()

        if library_path is None:
            library_path = config.music_library_path or str(Path.home() / "Music")

        self.library_path = Path(library_path).expanduser().resolve()
        self.scan_progress_callback = None
        self.scan_cancelled = False

        if not self.library_path.exists():
            logger.warning(f"Library path does not exist: {self.library_path}. Creating it.")
            self.library_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"Initialized LibraryScanner with path: {self.library_path}")
    
    def set_progress_callback(self, callback):
        """Set a callback function to report scan progress."""
        self.scan_progress_callback = callback
    
    def cancel_scan(self):
        """Request cancellation of the current scan operation."""
        self.scan_cancelled = True
        logger.info("Scan cancellation requested")
    
    async def scan_directory(self, path: str = None, recursive: bool = True) -> List[TrackInfo]:
        """
        Scan a directory for audio files and extract metadata.
        
        Args:
            path: Directory path to scan (defaults to library root)
            recursive: Whether to scan subdirectories
            
        Returns:
            List of TrackInfo objects for found audio files
        """
        scan_path = Path(path) if path else self.library_path
        scan_path = scan_path.expanduser().resolve()
        
        if not scan_path.exists():
            raise FileNotFoundError(f"Scan path does not exist: {scan_path}")
        
        logger.info(f"Starting scan of directory: {scan_path}")
        self.scan_cancelled = False
        
        # Find all audio files
        audio_files = []
        if recursive:
            for ext in self.SUPPORTED_EXTENSIONS:
                if self.scan_cancelled:
                    logger.info("Scan was cancelled")
                    return []
                audio_files.extend(scan_path.glob(f'**/*{ext}'))
        else:
            for ext in self.SUPPORTED_EXTENSIONS:
                if self.scan_cancelled:
                    logger.info("Scan was cancelled")
                    return []
                audio_files.extend(scan_path.glob(f'*{ext}'))
        
        logger.info(f"Found {len(audio_files)} audio files to process")
        
        # Process files in chunks to avoid blocking the event loop
        tracks = []
        chunk_size = 10
        
        for i in range(0, len(audio_files), chunk_size):
            if self.scan_cancelled:
                logger.info("Scan was cancelled during processing")
                return tracks
                
            chunk = audio_files[i:i+chunk_size]
            tasks = [self.analyze_track(str(file)) for file in chunk]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Error processing file: {result}")
                elif result is not None:
                    tracks.append(result)
            
            # Report progress
            if self.scan_progress_callback:
                progress = min((i + len(chunk)) / len(audio_files), 1.0)
                self.scan_progress_callback(progress, f"Processed {i + len(chunk)} of {len(audio_files)} files")
        
        logger.info(f"Completed scan. Processed {len(tracks)} tracks")
        return tracks
    
    async def analyze_track(self, file_path: str) -> Optional[TrackInfo]:
        """
        Analyze a single audio file and extract metadata.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            TrackInfo object with metadata, or None if file is not a supported audio file
        """
        try:
            file_path = Path(file_path).expanduser().resolve()
            
            # Skip non-audio files
            if file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
                return None
            
            # Get basic file info
            stat = file_path.stat()
            file_hash = self._calculate_file_hash(file_path)
            
            # Create track info with basic file data
            track = TrackInfo(
                file_path=str(file_path),
                file_hash=file_hash,
                file_size=stat.st_size,
                last_modified=stat.st_mtime
            )
            
            # Extract metadata based on file type
            if file_path.suffix.lower() == '.mp3':
                await self._extract_mp3_metadata(file_path, track)
            elif file_path.suffix.lower() == '.flac':
                await self._extract_flac_metadata(file_path, track)
            elif file_path.suffix.lower() == '.ogg':
                await self._extract_ogg_metadata(file_path, track)
            else:
                # Fallback for other formats
                await self._extract_generic_metadata(file_path, track)
            
            # Extract additional metadata using mutagen
            await self._extract_metadata_with_mutagen(file_path, track)
            
            return track
            
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {str(e)}", exc_info=True)
            return None
    
    async def update_library_database(self, tracks: List[TrackInfo], db_path: str = None) -> Dict[str, any]:
        """
        Update the library database with scanned tracks.
        
        Args:
            tracks: List of TrackInfo objects to add/update
            db_path: Path to the database file (defaults to library root)
            
        Returns:
            Dictionary with update statistics
        """
        # This is a placeholder for database update logic
        # In a real implementation, this would update an SQLite or other database
        
        stats = {
            'total_tracks': len(tracks),
            'new_tracks': len(tracks),  # Simplified for this implementation
            'updated_tracks': 0,
            'failed_tracks': 0
        }
        
        logger.info(f"Updated library database with {len(tracks)} tracks")
        return stats
    
    async def get_library_stats(self) -> Dict[str, any]:
        """
        Get statistics about the music library.
        
        Returns:
            Dictionary containing library statistics
        """
        # This is a placeholder for actual statistics collection
        # In a real implementation, this would query the database
        
        return {
            'total_tracks': 0,
            'total_duration': 0,
            'total_size': 0,
            'artists': {},
            'genres': {},
            'years': {},
            'last_updated': datetime.now().isoformat()
        }
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of a file."""
        hash_md5 = hashlib.md5()
        with file_path.open('rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    async def _extract_mp3_metadata(self, file_path: Path, track: TrackInfo) -> None:
        """Extract metadata from MP3 files."""
        try:
            audio = MP3(file_path)
            track.duration = audio.info.length
            track.bitrate = audio.info.bitrate // 1000  # Convert to kbps
            track.sample_rate = audio.info.sample_rate
            track.channels = 2 if audio.info.channels == 2 else 1
            
            # Extract ID3 tags if available
            if hasattr(audio, 'tags') and audio.tags is not None:
                tags = audio.tags
                track.title = str(tags.get('TIT2', [''])[0] or '')
                track.artist = str(tags.get('TPE1', [''])[0] or '')
                track.album = str(tags.get('TALB', [''])[0] or '')
                track.genre = str(tags.get('TCON', [''])[0] or '')
                
                # Try to get year from TDRC (ID3v2.4) or TYER (ID3v2.3)
                year = ''
                if 'TDRC' in tags:
                    year = str(tags['TDRC'])
                elif 'TDRC:' in str(tags):
                    # Handle TDRC with text encoding
                    year = str(tags.get('TDRC', [''])[0] or '')
                elif 'TYER' in tags:
                    year = str(tags['TYER'])
                
                if year and year.isdigit():
                    track.year = int(year)
                
                # Try to get BPM if available
                if 'TBPM' in tags:
                    try:
                        track.bpm = float(tags['TBPM'].text[0])
                    except (ValueError, IndexError, AttributeError):
                        pass
                
                # Try to get musical key if available
                if 'TKEY' in tags:
                    track.key = str(tags['TKEY'])
                
        except Exception as e:
            logger.warning(f"Error extracting MP3 metadata from {file_path}: {str(e)}")
    
    async def _extract_flac_metadata(self, file_path: Path, track: TrackInfo) -> None:
        """Extract metadata from FLAC files."""
        try:
            audio = FLAC(file_path)
            track.duration = audio.info.length
            track.bitrate = audio.info.bitrate // 1000  # Convert to kbps
            track.sample_rate = audio.info.sample_rate
            track.channels = audio.info.channels
            
            # Extract Vorbis comments
            if hasattr(audio, 'tags') and audio.tags is not None:
                tags = audio.tags
                track.title = str(tags.get('title', [''])[0] or '')
                track.artist = str(tags.get('artist', [''])[0] or '')
                track.album = str(tags.get('album', [''])[0] or '')
                track.genre = str(tags.get('genre', [''])[0] or '')
                
                # Get year
                year = tags.get('date', [''])[0] or tags.get('year', [''])[0] or ''
                if year and year.isdigit() and len(year) >= 4:
                    track.year = int(year[:4])
                
                # Try to get BPM if available
                if 'bpm' in tags:
                    try:
                        track.bpm = float(tags['bpm'][0])
                    except (ValueError, IndexError):
                        pass
                
                # Try to get musical key if available
                if 'key' in tags:
                    track.key = str(tags['key'][0])
                
        except Exception as e:
            logger.warning(f"Error extracting FLAC metadata from {file_path}: {str(e)}")
    
    async def _extract_ogg_metadata(self, file_path: Path, track: TrackInfo) -> None:
        """Extract metadata from Ogg Vorbis files."""
        try:
            audio = OggVorbis(file_path)
            track.duration = audio.info.length
            track.bitrate = audio.info.bitrate // 1000  # Convert to kbps
            track.sample_rate = audio.info.sample_rate
            track.channels = audio.info.channels
            
            # Extract Vorbis comments
            if hasattr(audio, 'tags') and audio.tags is not None:
                tags = audio.tags
                track.title = str(tags.get('title', [''])[0] or '')
                track.artist = str(tags.get('artist', [''])[0] or '')
                track.album = str(tags.get('album', [''])[0] or '')
                track.genre = str(tags.get('genre', [''])[0] or '')
                
                # Get year
                year = tags.get('date', [''])[0] or tags.get('year', [''])[0] or ''
                if year and year.isdigit() and len(year) >= 4:
                    track.year = int(year[:4])
                
                # Try to get BPM if available
                if 'bpm' in tags:
                    try:
                        track.bpm = float(tags['bpm'][0])
                    except (ValueError, IndexError):
                        pass
                
                # Try to get musical key if available
                if 'key' in tags:
                    track.key = str(tags['key'][0])
                
        except Exception as e:
            logger.warning(f"Error extracting OGG metadata from {file_path}: {str(e)}")
    
    async def _extract_generic_metadata(self, file_path: Path, track: TrackInfo) -> None:
        """Extract basic metadata from unsupported audio formats."""
        try:
            # Use mutagen as a fallback for other formats
            audio = mutagen.File(file_path)
            if audio is None:
                return
                
            # Get basic audio properties
            if hasattr(audio.info, 'length'):
                track.duration = audio.info.length
            if hasattr(audio.info, 'bitrate'):
                track.bitrate = audio.info.bitrate // 1000  # Convert to kbps
            if hasattr(audio.info, 'sample_rate'):
                track.sample_rate = audio.info.sample_rate
            if hasattr(audio.info, 'channels'):
                track.channels = audio.info.channels
            
            # Try to get common tags
            if hasattr(audio, 'tags') and audio.tags is not None:
                tags = audio.tags
                
                # Common tag mappings
                tag_mappings = {
                    'title': ['title', 'TIT2', 'TITLE'],
                    'artist': ['artist', 'TPE1', 'ARTIST'],
                    'album': ['album', 'TALB', 'ALBUM'],
                    'genre': ['genre', 'TCON', 'GENRE'],
                    'year': ['year', 'date', 'TDRC', 'TYER', 'DATE']
                }
                
                # Helper to get the first available tag value
                def get_tag_value(tag_keys):
                    if not isinstance(tag_keys, list):
                        tag_keys = [tag_keys]
                    for key in tag_keys:
                        if key in tags:
                            value = tags[key]
                            if isinstance(value, list):
                                value = value[0] if value else ''
                            return str(value)
                    return ''
                
                # Map common tags
                track.title = get_tag_value(tag_mappings['title']) or track.title
                track.artist = get_tag_value(tag_mappings['artist']) or track.artist
                track.album = get_tag_value(tag_mappings['album']) or track.album
                track.genre = get_tag_value(tag_mappings['genre']) or track.genre
                
                # Handle year specially
                year_str = get_tag_value(tag_mappings['year'])
                if year_str and year_str.isdigit() and len(year_str) >= 4:
                    track.year = int(year_str[:4])
                
                # Try to get BPM if available
                bpm_str = get_tag_value(['bpm', 'BPM', 'TBPM'])
                if bpm_str:
                    try:
                        track.bpm = float(bpm_str)
                    except ValueError:
                        pass
                
                # Try to get musical key if available
                key_str = get_tag_value(['key', 'KEY', 'TKEY'])
                if key_str:
                    track.key = key_str
                
        except Exception as e:
            logger.warning(f"Error extracting generic metadata from {file_path}: {str(e)}")
    
    async def _extract_metadata_with_mutagen(self, file_path: Path, track: TrackInfo) -> None:
        """Extract metadata using mutagen as a fallback."""
        try:
            # This is a fallback method that uses mutagen directly
            # It's called after format-specific extractors to fill in any missing fields
            
            audio = mutagen.File(file_path)
            if audio is None:
                return
                
            # Only update fields that haven't been set yet
            if not track.title and 'title' in audio.tags:
                track.title = str(audio.tags['title'][0])
            if not track.artist and 'artist' in audio.tags:
                track.artist = str(audio.tags['artist'][0])
            if not track.album and 'album' in audio.tags:
                track.album = str(audio.tags['album'][0])
            if not track.genre and 'genre' in audio.tags:
                track.genre = str(audio.tags['genre'][0])
            
            # Additional metadata that might be useful
            if 'comment' in audio.tags:
                track.tags['comment'] = str(audio.tags['comment'][0])
            if 'composer' in audio.tags:
                track.tags['composer'] = str(audio.tags['composer'][0])
            if 'tracknumber' in audio.tags:
                track.tags['track_number'] = str(audio.tags['tracknumber'][0])
            if 'discnumber' in audio.tags:
                track.tags['disc_number'] = str(audio.tags['discnumber'][0])
            
        except Exception as e:
            logger.debug(f"Error in mutagen metadata fallback for {file_path}: {str(e)}")

# Example usage
async def example_usage():
    """Example of how to use the LibraryScanner class."""
    import os
    
    # Initialize scanner with your music library path
    library_path = os.path.expanduser("~/Music")
    scanner = LibraryScanner(library_path)
    
    # Example progress callback
    def progress_callback(progress: float, status: str):
        print(f"Progress: {progress:.1%} - {status}")
    
    scanner.set_progress_callback(progress_callback)
    
    try:
        # Scan the library
        print("Starting library scan...")
        tracks = await scanner.scan_directory(recursive=True)
        print(f"Scanned {len(tracks)} tracks")
        
        # Update the library database
        if tracks:
            stats = await scanner.update_library_database(tracks)
            print(f"Database updated: {stats}")
            
            # Get library statistics
            stats = await scanner.get_library_stats()
            print(f"Library statistics: {stats}")
            
    except KeyboardInterrupt:
        print("\nScan cancelled by user")
    except Exception as e:
        print(f"Error during scan: {str(e)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())
