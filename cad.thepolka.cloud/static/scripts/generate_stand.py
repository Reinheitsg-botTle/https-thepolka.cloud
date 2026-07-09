#!/usr/bin/env python3
"""
Parametric Phone/Tablet Stand
------------------------------
A single-part stand defined entirely by named variables (no magic numbers
in the geometry itself). Change the PARAMS dict, rerun, get a new model.

Same idea as a design-token system, applied to physical geometry:
the profile logic never changes, only the token values do.

Outputs (written to ../model/):
  stand.stl   - 3D-printable mesh
  stand.glb   - for the web viewer (model-viewer)
  stand.3mf   - alt print format
  profile.svg - 2D cross-section, for docs/README
"""

import math
import os
import numpy as np
from shapely.geometry import Polygon
import trimesh

# ---------------------------------------------------------------------------
# PARAMETERS (all dimensions in millimeters)
# ---------------------------------------------------------------------------
PARAMS = {
    "stand_width": 65,        # extrusion length -- how wide the stand is (fits phone width)
    "base_depth_min": 70,     # minimum front-to-back footprint, for stability
    "base_height": 8,         # thickness of the base slab
    "lip_height": 12,         # height of the front lip that catches the phone's bottom edge
    "lip_thickness": 6,       # front-to-back thickness of the lip wall
    "slot_width": 11,         # gap between lip and back support (phone thickness + case clearance)
    "back_height": 95,        # total height of the angled back support
    "back_thickness": 10,     # front-to-back thickness of the back support at its base
    "lean_angle_deg": 12,     # lean of the back support, measured from vertical (0 = upright, higher = more reclined)
    "fillet_facets": 8,       # smoothness of corner rounding (higher = smoother, more triangles)
    "corner_radius": 1.5,     # radius applied to sharp exterior corners
}


def build_profile(p):
    """Build the 2D side-profile polygon from PARAMS. Returns list of (x, y) points."""
    lean = math.radians(p["lean_angle_deg"])
    horizontal_run = (p["back_height"] - p["base_height"]) * math.tan(lean)

    x0 = 0.0                                   # front face of lip
    x1 = p["lip_thickness"]                    # inner face of lip / start of slot
    x2 = x1 + p["slot_width"]                  # front face of back support, at base
    x3 = x2 + horizontal_run                   # front face of back support, at top (leaned back)
    x4 = x3 + p["back_thickness"]              # back face of back support, at top
    x5 = x4 - horizontal_run                   # back face of back support, at base (parallel lean)
    x_max = max(x5, p["base_depth_min"])       # ensure base is deep enough to not tip over

    y0 = 0.0
    y_base = p["base_height"]
    y_lip = p["lip_height"]
    y_top = p["back_height"]

    points = [
        (x0, y0),          # front-bottom of lip
        (x0, y_lip),       # front-top of lip
        (x1, y_lip),       # back-top of lip
        (x1, y_base),      # down into the slot (phone rests here)
        (x2, y_base),      # floor of slot, front of back support
        (x3, y_top),       # up the leaned front face to the top
        (x4, y_top),       # across the top of the back support
        (x5, y_base),      # down the back face to base level
        (x_max, y_base),   # extend base slab to full footprint depth
        (x_max, y0),       # down to the ground at the back
        (x0, y0),          # close the loop along the bottom
    ]
    return points


def round_corners(points, radius, facets):
    """Apply a simple radius to each vertex by inserting an arc, for a friendlier print."""
    poly = Polygon(points).buffer(0)
    # shapely buffer trick: shrink then grow rounds convex corners without
    # touching the concave slot corner, keeping it crisp for the phone edge.
    rounded = poly.buffer(-radius, join_style="round").buffer(radius, join_style="round")
    return list(rounded.exterior.coords)


def main():
    out_dir = os.path.join(os.path.dirname(__file__), "..", "model")
    os.makedirs(out_dir, exist_ok=True)

    profile_pts = build_profile(PARAMS)
    rounded_pts = round_corners(profile_pts, PARAMS["corner_radius"], PARAMS["fillet_facets"])

    poly = Polygon(rounded_pts)
    mesh = trimesh.creation.extrude_polygon(poly, height=PARAMS["stand_width"])

    # center the model on the origin (nicer default framing in viewers)
    mesh.apply_translation(-mesh.bounds.mean(axis=0))

    mesh.export(os.path.join(out_dir, "stand.stl"))
    mesh.export(os.path.join(out_dir, "stand.glb"))
    mesh.export(os.path.join(out_dir, "stand.3mf"))

    # write the 2D profile as an SVG for the README / docs
    svg_path = os.path.join(out_dir, "profile.svg")
    xs = [pt[0] for pt in rounded_pts]
    ys = [pt[1] for pt in rounded_pts]
    w, h = max(xs) + 10, max(ys) + 10
    path_d = "M " + " L ".join(f"{x:.2f},{h - y:.2f}" for x, y in rounded_pts) + " Z"
    with open(svg_path, "w") as f:
        f.write(
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}">'
            f'<path d="{path_d}" fill="#e8e2d4" stroke="#2b2b2b" stroke-width="1.2"/></svg>'
        )

    print(f"Vertices: {len(mesh.vertices)}  Faces: {len(mesh.faces)}")
    print(f"Watertight: {mesh.is_watertight}")
    bx = mesh.bounds
    print(f"Bounding box (mm): {bx[1] - bx[0]}")
    print(f"Wrote: stand.stl, stand.glb, stand.3mf, profile.svg -> {out_dir}")


if __name__ == "__main__":
    main()
