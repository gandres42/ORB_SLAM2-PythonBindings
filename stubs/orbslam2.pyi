"""Type stubs for the ``orbslam2`` Boost.Python extension module.

These are maintained by hand (Boost.Python does not emit usable signatures for
automatic stub generators) and installed alongside the compiled ``orbslam2.so``
so editors / type checkers can offer autocomplete and signature help.

Keep this in sync with the bindings registered in ``src/ORBSlamPython.cpp``.
"""

from __future__ import annotations

from typing import Any

import numpy as np

class Sensor(int):
    """Input sensor mode passed to :class:`System`."""

    MONOCULAR: Sensor
    STEREO: Sensor
    RGBD: Sensor
    name: str
    names: dict[str, Sensor]
    values: dict[int, Sensor]

class TrackingState(int):
    """Tracker state reported by :meth:`System.get_tracking_state`."""

    SYSTEM_NOT_READY: TrackingState
    NO_IMAGES_YET: TrackingState
    NOT_INITIALIZED: TrackingState
    OK: TrackingState
    LOST: TrackingState
    name: str
    names: dict[str, TrackingState]
    values: dict[int, TrackingState]

# A keyframe / trajectory entry: (timestamp, then a row-major 3x4 camera-to-world
# pose) i.e. (t, r00, r01, r02, tx, r10, r11, r12, ty, r20, r21, r22, tz).
Pose = tuple[float, float, float, float, float, float, float, float, float, float, float, float, float]
# A map point in world coordinates: (x, y, z).
Point3 = tuple[float, float, float]

class System:
    """Python wrapper around ``ORB_SLAM2::System``."""

    def __init__(
        self,
        vocab_file: str,
        settings_file: str,
        sensor: Sensor = ...,
        agent_name: str = ...,
    ) -> None: ...
    def initialize(self) -> bool:
        """Construct the underlying ORB_SLAM2 system. Call once before tracking."""
        ...
    def is_running(self) -> bool: ...
    def reset(self) -> None: ...
    def shutdown(self) -> None: ...

    # --- Tracking -----------------------------------------------------------
    # process_*: image(s) are passed as numpy arrays (HxW or HxWx3, uint8;
    # depth as float32). Returns True if a pose was estimated for the frame.
    def process_image_mono(self, image: np.ndarray, timestamp: float) -> bool: ...
    def process_image_stereo(self, left_image: np.ndarray, right_image: np.ndarray, timestamp: float) -> bool: ...
    def process_image_rgbd(self, image: np.ndarray, depth_image: np.ndarray, timestamp: float) -> bool: ...
    # load_and_process_*: read the image(s) from disk, then track.
    def load_and_process_mono(self, image_file: str, timestamp: float) -> bool: ...
    def load_and_process_stereo(self, left_image_file: str, right_image_file: str, timestamp: float) -> bool: ...
    def load_and_process_rgbd(self, image_file: str, depth_image_file: str, timestamp: float) -> bool: ...

    # --- Outputs ------------------------------------------------------------
    def get_tracking_state(self) -> TrackingState: ...
    def get_num_features(self) -> int: ...
    def get_num_matched_features(self) -> int: ...
    def get_keyframe_points(self) -> list[Pose]: ...
    def get_trajectory_points(self) -> list[Pose]:
        """Keyframe trajectory (this fork does not expose the per-frame tracker)."""
        ...
    def get_tracked_mappoints(self) -> list[Point3]: ...
    def get_high_quality_mappoints(self) -> list[Point3]:
        """Current high-quality map points (this fork's HQ-manager feature)."""
        ...
    def pop_new_high_quality_mappoints(self) -> list[Point3]:
        """High-quality map points promoted since the last call (clears the queue)."""
        ...

    # --- Configuration ------------------------------------------------------
    def set_mode(self, mode: Sensor) -> None: ...
    def set_use_viewer(self, use_viewer: bool) -> None: ...
    def set_agent_name(self, name: str) -> None:
        """Set the multi-agent name. Takes effect on the next initialize()."""
        ...
    def save_settings(self, settings: dict[str, Any]) -> bool: ...
    def load_settings(self) -> dict[str, Any]: ...
    @staticmethod
    def save_settings_file(settings: dict[str, Any], settings_filename: str) -> bool: ...
    @staticmethod
    def load_settings_file(settings_filename: str) -> dict[str, Any]: ...
