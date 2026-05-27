"""
dream3d_to_ebsd_txt.py
----------------------
Converts a DREAM.3D voxel file (.dream3d) to the EBSD .txt format
used by append_salt.py (EBSD_IC_*.txt style).

Header format (one key per two lines):
    # KEY: value
    #

Data columns (space-separated):
    phi1  phi2  phi3  x  y  z  feature_id  P_id  symmetry

Usage:
    python dream3d_to_ebsd_txt.py input.dream3d [output.txt]

The data container and symmetry value can be overridden:
    python dream3d_to_ebsd_txt.py input.dream3d --container SyntheticVolumeDataContainer --symmetry 24
"""

import sys
import h5py
import numpy as np
from pathlib import Path

# Default HDF5 paths (matched from inspect output)
DEFAULT_CONTAINER  = "SyntheticVolumeDataContainer"
DEFAULT_SYMMETRY   = "24"   # Oh / cubic — change if needed
DEFAULT_P_ID       = "0"


def convert(dream3d_path: str, output_path: str = None,
            container: str = DEFAULT_CONTAINER,
            symmetry: str = DEFAULT_SYMMETRY):

    input_path = Path(dream3d_path)
    if output_path is None:
        output_path = str(input_path.with_suffix(".txt"))

    with h5py.File(dream3d_path, "r") as f:
        base = f[f"DataContainers/{container}"]

        # --- Geometry ---
        geom      = base["_SIMPL_GEOMETRY"]
        dims      = geom["DIMENSIONS"][()]          # (NX, NY, NZ)  int64
        origin    = geom["ORIGIN"][()]              # (ox, oy, oz)  float32
        spacing   = geom["SPACING"][()]             # (sx, sy, sz)  float32

        NX, NY, NZ = int(dims[0]), int(dims[1]), int(dims[2])
        ox, oy, oz = float(origin[0]), float(origin[1]), float(origin[2])
        sx, sy, sz = float(spacing[0]), float(spacing[1]), float(spacing[2])

        # --- Cell data ---
        cell        = base["CellData"]
        euler       = cell["EulerAngles"][()]       # (NZ, NY, NX, 3) float32
        feature_ids = cell["FeatureIds"][()]        # (NZ, NY, NX, 1) int32

    print(f"Grid       : NX={NX}  NY={NY}  NZ={NZ}  ({NX*NY*NZ:,} voxels)")
    print(f"Origin     : {ox}, {oy}, {oz}")
    print(f"Spacing    : {sx}, {sy}, {sz}")

    # Coordinate arrays (voxel centres)
    X_vals = ox + sx * np.arange(NX)
    Y_vals = oy + sy * np.arange(NY)
    Z_vals = oz + sz * np.arange(NZ)

    # --- Build header dict (matches append_salt.py regex: # KEY: value) ---
    H = {}
    H["X_MIN"]    = str(float(X_vals[0]))
    H["X_MAX"]    = str(float(X_vals[-1]))
    H["X_STEP"]   = str(sx)
    H["X_DIM"]    = str(NX)
    H["Y_MIN"]    = str(float(Y_vals[0]))
    H["Y_MAX"]    = str(float(Y_vals[-1]))
    H["Y_STEP"]   = str(sy)
    H["Y_DIM"]    = str(NY)
    H["Z_MIN"]    = str(float(Z_vals[0]))
    H["Z_MAX"]    = str(float(Z_vals[-1]))
    H["Z_STEP"]   = str(sz)
    H["Z_DIM"]    = str(NZ)
    H["Symmetry_1"] = symmetry

    header_lines = []
    for key, val in H.items():
        header_lines.append(f"# {key}: {val}\n#\n")
    header_str = "".join(header_lines)

    print(f"Writing to : {output_path}")

    with open(output_path, "w") as out:
        out.write(header_str)

        # Iterate Z → Y → X to match DREAM.3D storage order
        # euler shape: (NZ, NY, NX, 3),  feature_ids: (NZ, NY, NX, 1)
        for iz in range(NZ):
            z = Z_vals[iz]
            for iy in range(NY):
                y = Y_vals[iy]
                for ix in range(NX):
                    x = X_vals[ix]
                    phi1, phi2, phi3 = euler[iz, iy, ix]
                    fid = int(feature_ids[iz, iy, ix, 0])
                    line = (f"{phi1} {phi2} {phi3} "
                            f"{x} {y} {z} "
                            f"{fid} {DEFAULT_P_ID} {symmetry}\n")
                    out.write(line)

    total = NX * NY * NZ
    print(f"Done. {total:,} voxels written.")
    return output_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    dream3d_file = args[0]
    out_file     = None
    container    = DEFAULT_CONTAINER
    symmetry     = DEFAULT_SYMMETRY

    i = 1
    while i < len(args):
        if args[i] == "--container" and i + 1 < len(args):
            container = args[i + 1]; i += 2
        elif args[i] == "--symmetry" and i + 1 < len(args):
            symmetry = args[i + 1]; i += 2
        else:
            out_file = args[i]; i += 1

    convert(dream3d_file, out_file, container, symmetry)