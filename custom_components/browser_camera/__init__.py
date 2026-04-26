from __future__ import annotations

import streamlit.components.v1 as components


_component_func = components.declare_component(
    "browser_camera_drag_crop_v4",
    path=str((__import__("pathlib").Path(__file__).parent / "frontend").resolve()),
)


def browser_camera(
    *,
    key: str,
    label: str = "Camera",
    height: int = 420,
    preferred_facing_mode: str = "environment",
) -> dict | None:
    return _component_func(
        key=key,
        label=label,
        height=height,
        preferredFacingMode=preferred_facing_mode,
        componentVersion="drag-crop-v4",
        default=None,
    )
