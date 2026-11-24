import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.engines.image.ela import error_level_analysis
from app.engines.image.noise import noise_consistency_analysis
from app.engines.image.frequency import frequency_analysis
from PIL import Image
import tempfile


def _make_image(path):
    Image.new("RGB", (256, 256), color=(120, 130, 140)).save(path, "JPEG")


def test_ela_runs():
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        _make_image(f.name)
        result = error_level_analysis(f.name)
        assert result["available"] is True
        assert 0 <= result["score"] <= 1


def test_noise_analysis_runs():
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        _make_image(f.name)
        result = noise_consistency_analysis(f.name)
        assert result["available"] is True


def test_frequency_analysis_runs():
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        _make_image(f.name)
        result = frequency_analysis(f.name)
        assert result["available"] is True
