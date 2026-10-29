"""Run the WasteVisor smartphone demo through identify, recommend, complete, impact."""

import os
import sys
from pathlib import Path

import httpx

BACKEND_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_IMAGE = BACKEND_ROOT / "samples" / "smartphone_working.jpg"
BASE_URL = os.getenv("WASTEVISOR_API_URL", "http://127.0.0.1:8000")


def main() -> None:
    """Exercise the core API flow and print concise user-readable results."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    with httpx.Client(base_url=BASE_URL, timeout=30) as client:
        with SAMPLE_IMAGE.open("rb") as image_file:
            identify_response = client.post(
                "/api/identify",
                data={"sample_id": "smartphone_working"},
                files={"image": (SAMPLE_IMAGE.name, image_file, "image/jpeg")},
            )
        identify_response.raise_for_status()
        identification = identify_response.json()["identification"]
        print(f"WasteVisor identified: {identification['item']} ({identification['condition']})")
        if identification["needs_confirmation"]:
            raise RuntimeError(
                identification.get("safe_guidance", "Identification needs confirmation.")
            )

        recommendation_response = client.post(
            "/api/recommend",
            json={"item": identification["item"], "condition": identification["condition"]},
        )
        recommendation_response.raise_for_status()
        recommendation = recommendation_response.json()["recommended_actions"][0]
        print(f"Best next action: {recommendation['action_type']}")
        print(f"Why: {recommendation['why_best']}")
        for step in recommendation["next_steps"]:
            print(f"  - {step}")

        completion_response = client.post(
            "/api/actions/complete",
            json={
                "item": identification["item"],
                "condition": identification["condition"],
                "action_type": recommendation["action_type"],
            },
        )
        completion_response.raise_for_status()
        print("Action recorded.")

        impact_response = client.get("/api/impact")
        impact_response.raise_for_status()
        totals = impact_response.json()
        print("Estimated household totals:")
        print(f"  Diverted: {totals['kg_diverted']['value']:.3f} kg (estimate)")
        print(f"  CO2e saved: {totals['co2e_saved_kg']['value']:.2f} kg (estimate)")
        print(f"  Value recovered: ₹{totals['recovered_value_inr']['value']:.2f} (estimate)")


if __name__ == "__main__":
    try:
        main()
    except httpx.HTTPStatusError as exc:
        error = exc.response.json().get("error", {})
        raise SystemExit(
            f"WasteVisor demo API error ({error.get('code', exc.response.status_code)}): "
            f"{error.get('message', 'Request failed')}"
        ) from None
    except httpx.RequestError:
        raise SystemExit(
            f"Could not connect to WasteVisor at {BASE_URL}. Start the API server first."
        ) from None
