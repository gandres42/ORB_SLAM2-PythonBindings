# ORB_SLAM2-PythonBindings
A python wrapper for ORB_SLAM2. Originally written for the base version
([https://github.com/raulmur/ORB_SLAM2](https://github.com/raulmur/ORB_SLAM2)),
this copy has been updated to build against the
[shahaabshokouhi/ORB_SLAM2](https://github.com/shahaabshokouhi/ORB_SLAM2) fork
used by `uffda` (the fork that adds the high-quality / multi-agent map-point
features). It builds against Python 3.12 / Boost 1.83 and OpenCV 4.

### What changed for this fork

- **No ORB_SLAM2 source patch is required.** The fork already makes the map
  (`mpMap`) public and installs its headers/library with `make install`, so the
  old `orbslam-changes.diff` is no longer applied. As a consequence the bindings
  no longer have access to the (now-private) tracker, so:
  - `get_trajectory_points()` returns the **keyframe** trajectory rather than the
    full per-frame trajectory.
  - `get_num_features()` / `get_num_matched_features()` are derived from the most
    recently tracked frame's keypoints / map points.
- **New API exposed** to match the fork's features:
  - `get_high_quality_mappoints()` — the current high-quality map points as
    `(x, y, z)` tuples.
  - `pop_new_high_quality_mappoints()` — high-quality points promoted since the
    last call (clears the queue).
  - An optional **agent name** constructor argument (and `set_agent_name(name)`),
    forwarded to the ORB_SLAM2 `System` constructor for multi-agent SLAM.

## Installation

### Prerequisites

- The ORB_SLAM2 fork built **and** installed (`make install`), so its headers
  and `libORB_SLAM2.so` live under an install prefix (default `/usr/local`).
- The ORB_SLAM2 **source tree** must remain available: the fork's `make install`
  does not install the bundled `Thirdparty/` (DBoW2 / g2o) headers or their
  `.so` files, but the bindings need them to compile and link.
- ORB_SLAM2's compilation dependencies (Pangolin, Eigen3, OpenCV 4).
- Boost, specifically its python component matching your Python (e.g. `python312`).
- NumPy development headers (images are passed as numpy arrays, auto-converted to
  `cv::Mat`).

### Compilation

```
mkdir build
cd build
cmake .. -DORB_SLAM2_SOURCE_DIR=/path/to/ORB_SLAM2
make
make install
```

- `-DORB_SLAM2_SOURCE_DIR` must point at the built ORB_SLAM2 source tree
  (it contains `Thirdparty/DBoW2/lib/libDBoW2.so` etc.). It defaults to
  `/tmp/ORB_SLAM2`.
- If ORB_SLAM2 was installed somewhere other than `/usr/local`, also pass
  `-DORB_SLAM2_DIR=/your/install/prefix` (it should contain `include` and `lib`).
- The Python version and the matching Boost.Python component are detected
  automatically. The module is installed to
  `<prefix>/lib/python<X.Y>/site-packages`.

Because the installed `libORB_SLAM2.so` locates its own `libDBoW2.so` / `libg2o.so`
only via the loader path, the built module embeds an `RPATH` (old-style
`DT_RPATH`) pointing at the source tree's `Thirdparty` libs so it imports without
needing `LD_LIBRARY_PATH`. If you move the ORB_SLAM2 source tree, rebuild the
bindings (or add those `Thirdparty/.../lib` directories to your loader path).

Verify your installation by typing
```
python3
>>> import orbslam2
```
And there should be no errors.

### Examples

ORBSLAM2's examples have been re-implemented in python in the examples folder.
Run them with the same parameters as the ORBSLAM examples, i.e.:
```
python3 orbslam_mono_kitti.py [PATH_TO_ORBSLAM]/Vocabulary/ORBvoc.txt [PATH_TO_ORBSLAM]/Examples/Monocular/KITTI00-02.yaml [PATH_TO_KITTI]/sequences/00/
```

## License
This code is licensed under the BSD Simplified license, although it requires and links to ORB_SLAM2, which is available under the GPLv3 license

It uses pyboostcvconverter (https://github.com/Algomorph/pyboostcvconverter) by Gregory Kramida under the MIT licence (see pyboostcvconverter-LICENSE).

