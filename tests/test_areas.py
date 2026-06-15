from app.ui.areas import build_area_dropdown_options, resolve_area_selection


def test_build_area_dropdown_options_includes_preferred_and_custom() -> None:
    options = build_area_dropdown_options(["Frazer Town", "Indiranagar"])

    assert "HSR Layout" in options
    assert "Indiranagar" in options
    assert "Frazer Town" in options
    assert options[-1] == "Other (type custom area)"


def test_resolve_area_selection_maps_labels_and_custom() -> None:
    assert resolve_area_selection("HSR Layout", "") == "HSR"
    assert resolve_area_selection("Indiranagar", "") == "Indiranagar"
    assert resolve_area_selection("Other (type custom area)", "  Sarjapur Road  ") == "Sarjapur Road"
