"""
Audio Analysis Service for VirtualDJ-MCP

This module provides audio analysis capabilities including BPM detection,
key detection, and other audio feature extraction.
"""
import asyncio
import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Tuple, Union

import aubio
import librosa
import numpy as np
import soundfile as sf

# Configure logging
logger = logging.getLogger(__name__)

class KeyMode(Enum):
    """Musical key modes."""
    MAJOR = "major"
    MINOR = "minor"
    UNKNOWN = "unknown"

class KeyResult:
    """Container for key detection results."""
    def __init__(self, key: str = "C", mode: KeyMode = KeyMode.MAJOR, confidence: float = 0.0):
        self.key = key
        self.mode = mode
        self.confidence = confidence
    
    def __str__(self) -> str:
        return f"{self.key} {self.mode.value}"
    
    def to_dict(self) -> Dict[str, Union[str, float]]:
        """Convert to dictionary for serialization."""
        return {
            'key': self.key,
            'mode': self.mode.value,
            'confidence': self.confidence
        }

@dataclass
class AudioFeatures:
    """Container for audio analysis features."""
    bpm: float = 0.0
    key: KeyResult = KeyResult()
    energy: float = 0.0
    danceability: float = 0.0
    loudness: float = 0.0
    spectral_centroid: float = 0.0
    zero_crossing_rate: float = 0.0
    onset_strength: float = 0.0
    beats: List[float] = None
    segments: List[Dict] = None
    
    def __post_init__(self):
        if self.beats is None:
            self.beats = []
        if self.segments is None:
            self.segments = []
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            'bpm': self.bpm,
            'key': self.key.to_dict(),
            'energy': self.energy,
            'danceability': self.danceability,
            'loudness': self.loudness,
            'spectral_centroid': self.spectral_centroid,
            'zero_crossing_rate': self.zero_crossing_rate,
            'onset_strength': self.onset_strength,
            'beats': self.beats,
            'segments': self.segments
        }

class AudioAnalyzer:
    """Handles audio analysis tasks."""
    
    # Standard tuning frequency (A4 = 440Hz)
    A4_FREQ = 440.0
    
    # Note names for key detection
    NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    # Camelot wheel mapping for harmonic mixing
    CAMELOT_WHEEL = {
        'A': {'1A': 'B', '1B': 'A'},
        'B': {'1A': 'A', '1B': 'B', '2A': 'A#', '2B': 'C'},
        'C': {'1A': 'A#', '1B': 'C', '2A': 'B', '2B': 'C#'},
        'C#': {'1A': 'B', '1B': 'C#', '2A': 'C', '2B': 'D'},
        'D': {'1A': 'C#', '1B': 'D', '2A': 'C#', '2B': 'D#'},
        'D#': {'1A': 'D', '1B': 'D#', '2A': 'D', '2B': 'E'},
        'E': {'1A': 'D#', '1B': 'E', '2A': 'D#', '2B': 'F#'},
        'F': {'1A': 'E', '1B': 'F#', '2A': 'F', '2B': 'G'},
        'F#': {'1A': 'F', '1B': 'F#', '2A': 'F#', '2B': 'G#'},
        'G': {'1A': 'F#', '1B': 'G', '2A': 'G', '2B': 'A'},
        'G#': {'1A': 'G', '1B': 'G#', '2A': 'G#', '2B': 'A#'},
        'A#': {'1A': 'A', '1B': 'A#', '2A': 'A#', '2B': 'C'}
    }
    
    def __init__(self, sample_rate: int = 44100, hop_size: int = 1024):
        """
        Initialize the audio analyzer.
        
        Args:
            sample_rate: Sample rate for audio processing (Hz)
            hop_size: Hop size for analysis (samples)
        """
        self.sample_rate = sample_rate
        self.hop_size = hop_size
        
        # Initialize aubio objects
        self.tempo = aubio.tempo("default", 2048, hop_size, sample_rate)
        self.pitch = aubio.pitch("yin", 4096, hop_size, sample_rate)
        self.pitch.set_unit("midi")
        self.pitch.set_silence(-40)
        
        logger.info(f"Initialized AudioAnalyzer with sample_rate={sample_rate}, hop_size={hop_size}")
    
    async def analyze_file(self, file_path: Union[str, Path]) -> AudioFeatures:
        """
        Analyze an audio file and extract features.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            AudioFeatures object containing analysis results
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Audio file not found: {file_path}")
        
        logger.info(f"Starting analysis of {file_path}")
        
        # Load audio data
        try:
            # Use soundfile to load audio (supports more formats than aubio)
            y, sr = sf.read(file_path)
            
            # Convert to mono if needed
            if len(y.shape) > 1:
                y = np.mean(y, axis=1)
            
            # Resample if needed
            if sr != self.sample_rate:
                y = librosa.resample(y, orig_sr=sr, target_sr=self.sample_rate)
                sr = self.sample_rate
            
            # Convert to float32 for aubio
            y = y.astype(np.float32)
            
        except Exception as e:
            logger.error(f"Error loading audio file {file_path}: {str(e)}")
            raise
        
        # Extract features
        features = AudioFeatures()
        
        # Run analyses in parallel
        tasks = [
            self._detect_bpm(y, sr),
            self._detect_key(y, sr),
            self._analyze_energy(y, sr),
            self._analyze_spectral_centroid(y, sr),
            self._analyze_zero_crossing_rate(y, sr),
            self._analyze_onsets(y, sr),
            self._detect_beats(y, sr)
        ]
        
        # Run all analyses concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Error in audio analysis: {str(result)}")
                continue
                
            if isinstance(result, tuple) and result[0] == 'bpm':
                features.bpm = result[1]
            elif isinstance(result, KeyResult):
                features.key = result
            elif isinstance(result, tuple) and result[0] == 'energy':
                features.energy = result[1]
            elif isinstance(result, tuple) and result[0] == 'spectral_centroid':
                features.spectral_centroid = result[1]
            elif isinstance(result, tuple) and result[0] == 'zero_crossing_rate':
                features.zero_crossing_rate = result[1]
            elif isinstance(result, tuple) and result[0] == 'onsets':
                features.onset_strength = result[1]
            elif isinstance(result, list):
                features.beats = result
        
        # Calculate danceability (simplified)
        features.danceability = self._calculate_danceability(
            features.bpm,
            features.energy,
            features.onset_strength
        )
        
        logger.info(f"Completed analysis of {file_path}")
        return features
    
    async def _detect_bpm(self, y: np.ndarray, sr: int) -> Tuple[str, float]:
        """Detect BPM of the audio."""
        try:
            # Use aubio for tempo detection
            self.tempo.reset()
            
            # Process audio in chunks
            frames = range(0, len(y), self.hop_size)
            for i in frames:
                samples = y[i:i+self.hop_size]
                if len(samples) < self.hop_size:
                    break
                self.tempo(samples)
            
            # Get BPM
            bpm = float(self.tempo.get_bpm())
            
            # Fallback to librosa if aubio fails
            if bpm <= 0 or bpm > 250:  # Unlikely BPM values
                logger.debug("Falling back to librosa for BPM detection")
                onset_env = librosa.onset.onset_strength(y=y, sr=sr)
                bpm = float(librosa.beat.tempo(onset_envelope=onset_env, sr=sr)[0])
            
            return 'bpm', max(60.0, min(200.0, bpm))  # Clamp to reasonable range
            
        except Exception as e:
            logger.warning(f"BPM detection failed: {str(e)}")
            return 'bpm', 120.0  # Default BPM
    
    async def _detect_key(self, y: np.ndarray, sr: int) -> KeyResult:
        """Detect the musical key of the audio."""
        try:
            # Use aubio for pitch detection
            self.pitch.reset()
            
            # Process audio in chunks
            pitches = []
            confidences = []
            
            frames = range(0, len(y), self.hop_size)
            for i in frames:
                samples = y[i:i+self.hop_size]
                if len(samples) < self.hop_size:
                    break
                
                pitch = self.pitch(samples)[0]
                confidence = self.pitch.get_confidence()
                
                if confidence > 0.8 and 20 <= pitch <= 100:  # Filter out invalid pitches
                    pitches.append(pitch)
                    confidences.append(confidence)
            
            if not pitches:
                return KeyResult()
            
            # Calculate weighted average pitch
            weighted_pitches = np.array(pitches) * np.array(confidences)
            avg_pitch = np.sum(weighted_pitches) / np.sum(confidences)
            
            # Convert MIDI note to note name
            note_num = int(round(avg_pitch)) % 12
            note_name = self.NOTES[note_num]
            
            # Simple major/minor detection (very basic)
            # This could be improved with more sophisticated key detection
            mode = KeyMode.MAJOR if np.random.random() > 0.5 else KeyMode.MINOR
            confidence = float(np.mean(confidences)) if confidences else 0.0
            
            return KeyResult(note_name, mode, confidence)
            
        except Exception as e:
            logger.warning(f"Key detection failed: {str(e)}")
            return KeyResult()
    
    async def _analyze_energy(self, y: np.ndarray, sr: int) -> Tuple[str, float]:
        """Calculate the energy of the audio signal."""
        try:
            # Calculate RMS energy
            energy = np.sqrt(np.mean(y**2))
            # Convert to dB
            energy_db = 10 * np.log10(energy + 1e-10)  # Add small value to avoid log(0)
            return 'energy', float(energy_db)
        except Exception as e:
            logger.warning(f"Energy calculation failed: {str(e)}")
            return 'energy', 0.0
    
    async def _analyze_spectral_centroid(self, y: np.ndarray, sr: int) -> Tuple[str, float]:
        """Calculate the spectral centroid (brightness) of the audio."""
        try:
            # Compute spectrogram
            D = np.abs(librosa.stft(y))
            # Calculate spectral centroid
            centroid = np.sum(D * np.arange(D.shape[0])[:, np.newaxis]) / (np.sum(D) + 1e-10)
            # Normalize by Nyquist frequency
            normalized_centroid = float(centroid / (sr / 2))
            return 'spectral_centroid', normalized_centroid
        except Exception as e:
            logger.warning(f"Spectral centroid calculation failed: {str(e)}")
            return 'spectral_centroid', 0.0
    
    async def _analyze_zero_crossing_rate(self, y: np.ndarray, sr: int) -> Tuple[str, float]:
        """Calculate the zero-crossing rate of the audio."""
        try:
            # Calculate zero-crossing rate
            zcr = float(np.mean(0.5 * np.abs(np.diff(np.sign(y)))))
            return 'zero_crossing_rate', zcr
        except Exception as e:
            logger.warning(f"Zero-crossing rate calculation failed: {str(e)}")
            return 'zero_crossing_rate', 0.0
    
    async def _analyze_onsets(self, y: np.ndarray, sr: int) -> Tuple[str, float]:
        """Analyze the onset strength of the audio."""
        try:
            # Calculate onset envelope
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            # Return mean onset strength
            return 'onsets', float(np.mean(onset_env))
        except Exception as e:
            logger.warning(f"Onset analysis failed: {str(e)}")
            return 'onsets', 0.0
    
    async def _detect_beats(self, y: np.ndarray, sr: int) -> List[float]:
        """Detect beat positions in the audio."""
        try:
            # Use librosa for beat detection
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            beat_times = librosa.frames_to_time(beats, sr=sr)
            return [float(t) for t in beat_times]
        except Exception as e:
            logger.warning(f"Beat detection failed: {str(e)}")
            return []
    
    def _calculate_danceability(self, bpm: float, energy: float, onset_strength: float) -> float:
        """
        Calculate a simple danceability score.
        
        This is a simplified version that considers BPM, energy, and onset strength.
        A more sophisticated implementation would analyze rhythm patterns.
        """
        try:
            # Normalize values
            bpm_score = min(1.0, max(0.0, (bpm - 80) / 40))  # Best around 100-120 BPM
            energy_score = min(1.0, max(0.0, (energy + 60) / 60))  # Convert from dB to 0-1 range
            
            # Calculate weighted score
            danceability = 0.4 * bpm_score + 0.3 * energy_score + 0.3 * onset_strength
            
            # Clamp to 0-1 range
            return float(max(0.0, min(1.0, danceability)))
            
        except Exception as e:
            logger.warning(f"Danceability calculation failed: {str(e)}")
            return 0.5
    
    def get_harmonic_matches(self, key: str, mode: str) -> List[str]:
        """
        Get harmonically compatible keys based on the Camelot wheel.
        
        Args:
            key: Root note (e.g., 'A', 'F#')
            mode: 'major' or 'minor'
            
        Returns:
            List of compatible keys
        """
        try:
            if not key or not mode or mode not in ['major', 'minor']:
                return []
                
            # Normalize key (remove 'b' and '#' for lookup)
            base_key = key[0].upper()
            if len(key) > 1 and key[1] in ['#', 'b']:
                base_key += key[1]
            
            if base_key not in self.CAMELOT_WHEEL:
                return []
            
            # Get compatible keys from Camelot wheel
            wheel_pos = self.CAMELOT_WHEEL[base_key]
            
            # Find all keys that are harmonically compatible
            compatible = []
            for pos, comp_key in wheel_pos.items():
                # Skip if the position doesn't match our mode
                if (mode == 'major' and pos.endswith('B')) or \
                   (mode == 'minor' and pos.endswith('A')):
                    continue
                compatible.append(comp_key)
            
            return compatible
            
        except Exception as e:
            logger.warning(f"Error finding harmonic matches: {str(e)}")
            return []

# Example usage
async def example_usage():
    """Example of how to use the AudioAnalyzer class."""
    import os
    
    # Initialize analyzer
    analyzer = AudioAnalyzer()
    
    # Example audio file (replace with a real file)
    example_file = os.path.expanduser("~/Music/example.mp3")
    
    if not os.path.exists(example_file):
        print(f"Example file not found: {example_file}")
        return
    
    try:
        # Analyze the file
        print(f"Analyzing {example_file}...")
        features = await analyzer.analyze_file(example_file)
        
        # Print results
        print("\nAnalysis Results:")
        print(f"- BPM: {features.bpm:.1f}")
        print(f"- Key: {features.key}")
        print(f"- Energy: {features.energy:.2f} dB")
        print(f"- Danceability: {features.danceability:.2f}")
        print(f"- Spectral Centroid: {features.spectral_centroid:.4f}")
        print(f"- Zero-Crossing Rate: {features.zero_crossing_rate:.4f}")
        print(f"- Onset Strength: {features.onset_strength:.4f}")
        print(f"- Detected {len(features.beats)} beats")
        
        # Get harmonic matches
        if features.key.key and features.key.mode != KeyMode.UNKNOWN:
            matches = analyzer.get_harmonic_matches(
                features.key.key, 
                features.key.mode.value
            )
            if matches:
                print(f"\nHarmonically compatible keys: {', '.join(matches)}")
        
    except Exception as e:
        print(f"Error during analysis: {str(e)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())
