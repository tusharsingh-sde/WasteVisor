"""Load and validate local WasteVisor demo fixtures."""

from pathlib import Path

from app.schemas.demo import DemoFixture

SAMPLES_DIRECTORY = Path(__file__).resolve().parents[2] / "samples"


def load_demo_fixtures() -> dict[str, DemoFixture]:
    """Load cached JSON fixtures and verify their corresponding sample images exist."""
    fixtures: dict[str, DemoFixture] = {}
    for fixture_path in sorted(SAMPLES_DIRECTORY.glob("*.json")):
        fixture = DemoFixture.model_validate_json(fixture_path.read_text(encoding="utf-8"))
        image_path = SAMPLES_DIRECTORY / fixture.image_filename
        if not image_path.is_file():
            raise FileNotFoundError(f"Demo sample image is missing: {fixture.image_filename}")
        if fixture.id in fixtures:
            raise ValueError(f"Duplicate WasteVisor demo sample ID: {fixture.id}")
        fixtures[fixture.id] = fixture
    return fixtures
