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

import librosa
import numpy as np
import soundfile as sf

# Try to import aubio - optional dependency
try:
    import aubio

    AUBIO_AVAILABLE = True
except ImportError:
    AUBIO_AVAILABLE = False

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

    def to_dict(self) -> dict[str, str | float]:
        """Convert to dictionary for serialization."""
        return {"key": self.key, "mode": self.mode.value, "confidence": self.confidence}


@dataclass
class AudioFeatures:
    """Container for audio analysis features."""

    bpm: float = 0.0
    key: KeyResult = None
    energy: float = 0.0
    danceability: float = 0.0
    loudness: float = 0.0
    spectral_centroid: float = 0.0
    zero_crossing_rate: float = 0.0
    onset_strength: float = 0.0
    beats: list[float] = None
    segments: list[dict] = None

    def __post_init__(self):
        if self.key is None:
            self.key = KeyResult()
        if self.beats is None:
            self.beats = []
        if self.segments is None:
            self.segments = []

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "bpm": self.bpm,
            "key": self.key.to_dict(),
            "energy": self.energy,
            "danceability": self.danceability,
            "loudness": self.loudness,
            "spectral_centroid": self.spectral_centroid,
            "zero_crossing_rate": self.zero_crossing_rate,
            "onset_strength": self.onset_strength,
            "beats": self.beats,
            "segments": self.segments,
        }


class AudioAnalyzer:
    """Handles audio analysis tasks."""

    # Standard tuning frequency (A4 = 440Hz)
    A4_FREQ = 440.0

    # Note names for key detection
    NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

    # Camelot wheel mapping for harmonic mixing
    CAMELOT_WHEEL = {
        "A": {"1A": "B", "1B": "A"},
        "B": {"1A": "A", "1B": "B", "2A": "A#", "2B": "C"},
        "C": {"1A": "A#", "1B": "C", "2A": "B", "2B": "C#"},
        "C#": {"1A": "B", "1B": "C#", "2A": "C", "2B": "D"},
        "D": {"1A": "C#", "1B": "D", "2A": "C#", "2B": "D#"},
        "D#": {"1A": "D", "1B": "D#", "2A": "D", "2B": "E"},
        "E": {"1A": "D#", "1B": "E", "2A": "D#", "2B": "F#"},
        "F": {"1A": "E", "1B": "F#", "2A": "F", "2B": "G"},
        "F#": {"1A": "F", "1B": "F#", "2A": "F#", "2B": "G#"},
        "G": {"1A": "F#", "1B": "G", "2A": "G", "2B": "A"},
        "G#": {"1A": "G", "1B": "G#", "2A": "G#", "2B": "A#"},
        "A#": {"1A": "A", "1B": "A#", "2A": "A#", "2B": "C"},
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

        # Initialize aubio objects if available
        self._tempo = None
        self._pitch = None

        if AUBIO_AVAILABLE:
            try:
                self._tempo = aubio.tempo("default", 2048, hop_size, sample_rate)
                self._pitch = aubio.pitch("yin", 4096, hop_size, sample_rate)
                self._pitch.set_unit("midi")
                self._pitch.set_silence(-40)
                logger.info(f"Initialized AudioAnalyzer with aubio (sample_rate={sample_rate})")
            except Exception as e:
                logger.warning(f"Failed to initialize aubio: {e}. Using librosa fallback.")
                self._tempo = None
                self._pitch = None
        else:
            logger.info("Initialized AudioAnalyzer with librosa-only (aubio not available)")

    async def analyze_file(self, file_path: str | Path) -> AudioFeatures:
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

            # Convert to float32
            y = y.astype(np.float32)

        except Exception as e:
            logger.error(f"Error loading audio file {file_path}: {e!s}")
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
            self._detect_beats(y, sr),
        ]

        # Run all analyses concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Error in audio analysis: {result!s}")
                continue

            if isinstance(result, tuple) and result[0] == "bpm":
                features.bpm = result[1]
            elif isinstance(result, KeyResult):
                features.key = result
            elif isinstance(result, tuple) and result[0] == "energy":
                features.energy = result[1]
            elif isinstance(result, tuple) and result[0] == "spectral_centroid":
                features.spectral_centroid = result[1]
            elif isinstance(result, tuple) and result[0] == "zero_crossing_rate":
                features.zero_crossing_rate = result[1]
            elif isinstance(result, tuple) and result[0] == "onsets":
                features.onset_strength = result[1]
            elif isinstance(result, list):
                features.beats = result

        # Calculate danceability (simplified)
        features.danceability = self._calculate_danceability(features.bpm, features.energy, features.onset_strength)

        logger.info(f"Completed analysis of {file_path}")
        return features

    async def _detect_bpm(self, y: np.ndarray, sr: int) -> tuple[str, float]:
        """Detect BPM of the audio."""
        try:
            bpm = 0.0

            # Try aubio first if available
            if self._tempo is not None:
                self._tempo.reset()
                frames = range(0, len(y), self.hop_size)
                for i in frames:
                    samples = y[i : i + self.hop_size]
                    if len(samples) < self.hop_size:
                        break
                    self._tempo(samples)
                bpm = float(self._tempo.get_bpm())

            # Fallback to librosa if aubio fails or unavailable
            if bpm <= 0 or bpm > 250:
                logger.debug("Using librosa for BPM detection")
                onset_env = librosa.onset.onset_strength(y=y, sr=sr)
                bpm = float(librosa.beat.tempo(onset_envelope=onset_env, sr=sr)[0])

            return "bpm", max(60.0, min(200.0, bpm))  # Clamp to reasonable range

        except Exception as e:
            logger.warning(f"BPM detection failed: {e!s}")
            return "bpm", 120.0  # Default BPM

    async def _detect_key(self, y: np.ndarray, sr: int) -> KeyResult:
        """Detect the musical key of the audio using chroma features."""
        try:
            # Use librosa chroma for key detection (more reliable than aubio pitch)
            chroma = librosa.feature.chroma_cqt(y=y, sr=sr)

            # Sum chroma bins across time
            chroma_sum = np.sum(chroma, axis=1)

            # Find dominant pitch class
            dominant_pitch = int(np.argmax(chroma_sum))
            note_name = self.NOTES[dominant_pitch]

            # Simple major/minor detection using chroma correlation
            # Major template: root, major third, fifth
            # Minor template: root, minor third, fifth
            major_template = np.zeros(12)
            minor_template = np.zeros(12)
            major_template[[0, 4, 7]] = 1  # C, E, G for major
            minor_template[[0, 3, 7]] = 1  # C, Eb, G for minor

            # Roll templates to match detected root
            major_rolled = np.roll(major_template, dominant_pitch)
            minor_rolled = np.roll(minor_template, dominant_pitch)

            # Correlate with chroma
            major_corr = np.corrcoef(chroma_sum, major_rolled)[0, 1]
            minor_corr = np.corrcoef(chroma_sum, minor_rolled)[0, 1]

            mode = KeyMode.MAJOR if major_corr > minor_corr else KeyMode.MINOR
            confidence = float(max(major_corr, minor_corr))

            return KeyResult(note_name, mode, max(0.0, min(1.0, confidence)))

        except Exception as e:
            logger.warning(f"Key detection failed: {e!s}")
            return KeyResult()

    async def _analyze_energy(self, y: np.ndarray, sr: int) -> tuple[str, float]:
        """Calculate the energy of the audio signal."""
        try:
            # Calculate RMS energy
            energy = np.sqrt(np.mean(y**2))
            # Convert to dB
            energy_db = 10 * np.log10(energy + 1e-10)
            return "energy", float(energy_db)
        except Exception as e:
            logger.warning(f"Energy calculation failed: {e!s}")
            return "energy", 0.0

    async def _analyze_spectral_centroid(self, y: np.ndarray, sr: int) -> tuple[str, float]:
        """Calculate the spectral centroid (brightness) of the audio."""
        try:
            # Compute spectrogram
            stft_magnitude = np.abs(librosa.stft(y))
            # Calculate spectral centroid
            centroid = np.sum(stft_magnitude * np.arange(stft_magnitude.shape[0])[:, np.newaxis]) / (
                np.sum(stft_magnitude) + 1e-10
            )
            # Normalize by Nyquist frequency
            normalized_centroid = float(centroid / (sr / 2))
            return "spectral_centroid", normalized_centroid
        except Exception as e:
            logger.warning(f"Spectral centroid calculation failed: {e!s}")
            return "spectral_centroid", 0.0

    async def _analyze_zero_crossing_rate(self, y: np.ndarray, sr: int) -> tuple[str, float]:
        """Calculate the zero-crossing rate of the audio."""
        try:
            # Calculate zero-crossing rate
            zcr = float(np.mean(0.5 * np.abs(np.diff(np.sign(y)))))
            return "zero_crossing_rate", zcr
        except Exception as e:
            logger.warning(f"Zero-crossing rate calculation failed: {e!s}")
            return "zero_crossing_rate", 0.0

    async def _analyze_onsets(self, y: np.ndarray, sr: int) -> tuple[str, float]:
        """Analyze the onset strength of the audio."""
        try:
            # Calculate onset envelope
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            # Return mean onset strength
            return "onsets", float(np.mean(onset_env))
        except Exception as e:
            logger.warning(f"Onset analysis failed: {e!s}")
            return "onsets", 0.0

    async def _detect_beats(self, y: np.ndarray, sr: int) -> list[float]:
        """Detect beat positions in the audio."""
        try:
            # Use librosa for beat detection
            _tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            beat_times = librosa.frames_to_time(beats, sr=sr)
            return [float(t) for t in beat_times]
        except Exception as e:
            logger.warning(f"Beat detection failed: {e!s}")
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
            logger.warning(f"Danceability calculation failed: {e!s}")
            return 0.5

    def get_harmonic_matches(self, key: str, mode: str) -> list[str]:
        """
        Get harmonically compatible keys based on the Camelot wheel.

        Args:
            key: Root note (e.g., 'A', 'F#')
            mode: 'major' or 'minor'

        Returns:
            List of compatible keys
        """
        try:
            if not key or not mode or mode not in ["major", "minor"]:
                return []

            # Normalize key (remove 'b' and '#' for lookup)
            base_key = key[0].upper()
            if len(key) > 1 and key[1] in ["#", "b"]:
                base_key += key[1]

            if base_key not in self.CAMELOT_WHEEL:
                return []

            # Get compatible keys from Camelot wheel
            wheel_pos = self.CAMELOT_WHEEL[base_key]

            # Find all keys that are harmonically compatible
            compatible = []
            for pos, comp_key in wheel_pos.items():
                # Skip if the position doesn't match our mode
                if (mode == "major" and pos.endswith("B")) or (mode == "minor" and pos.endswith("A")):
                    continue
                compatible.append(comp_key)

            return compatible

        except Exception as e:
            logger.warning(f"Error finding harmonic matches: {e!s}")
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
            matches = analyzer.get_harmonic_matches(features.key.key, features.key.mode.value)
            if matches:
                print(f"\nHarmonically compatible keys: {', '.join(matches)}")

    except Exception as e:
        print(f"Error during analysis: {e!s}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(example_usage())
