from __future__ import annotations

from pathlib import Path

import streamlit.components.v1 as components


_component_func = components.declare_component(
    "image_drag_cropper_v2",
    path=str((Path(__file__).parent / "frontend").resolve()),
)


def image_cropper(
    *,
    key: str,
    data_url: str,
    label: str = "Crop image",
    height: int = 460,
) -> dict | None:
    return _component_func(
        key=key,
        dataUrl=data_url,
        label=label,
        height=height,
        default=None,
    )
