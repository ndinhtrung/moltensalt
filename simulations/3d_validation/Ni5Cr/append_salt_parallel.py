import numpy as np
import math
import re
import os
import time
from glob import glob

file_name = 'Ni5Cr_3.txt'
header_size = 26

salt_dim = "Z"
salt_thickness = 10  # um
bias = 1e-6

# ---------------------------------
# SLURM SETTINGS
# ---------------------------------
print("SLURM_ARRAY_TASK_ID =", os.environ.get("SLURM_ARRAY_TASK_ID"))
print("SLURM_ARRAY_TASK_COUNT =", os.environ.get("SLURM_ARRAY_TASK_COUNT"))
task_id = int(os.environ.get("SLURM_ARRAY_TASK_ID", 0))
n_tasks = int(os.environ.get("SLURM_ARRAY_TASK_COUNT", 1))

print(f"[Task {task_id}] Reading {file_name}...")

with open(file_name) as raw_file:
    header_list = [next(raw_file) for _ in range(header_size)]
    points = raw_file.read()

print(f"[Task {task_id}] File loaded.")

# ---------------------------------
# Parse header
# ---------------------------------
H_dict = {}

for line in header_list:
    F = re.match(r"# (.*): (.*)", line)
    if F:
        key, value = F.groups()
        H_dict[key] = value

H_dict[salt_dim + "_MAX"] = str(
    float(H_dict[salt_dim + "_MAX"]) + salt_thickness
)

N_dim_old = int(H_dict[salt_dim + "_DIM"])

N_dim_new = math.floor(
    (
        float(H_dict[salt_dim + "_MAX"])
        - float(H_dict[salt_dim + "_MIN"])
    )
    / float(H_dict[salt_dim + "_STEP"])
)

H_dict[salt_dim + "_DIM"] = str(N_dim_new)

# ---------------------------------
# Generate grid
# ---------------------------------
if salt_dim == "Z":

    X_vals = (
        float(H_dict["X_MIN"])
        + float(H_dict["X_STEP"])
        * np.arange(0, int(H_dict["X_DIM"]))
    )

    Y_vals = (
        float(H_dict["Y_MIN"])
        + float(H_dict["Y_STEP"])
        * np.arange(0, int(H_dict["Y_DIM"]))
        - bias
    )

    Z_vals = (
        float(H_dict["Z_MIN"])
        + float(H_dict["Z_STEP"])
        * np.arange(N_dim_old, int(H_dict["Z_DIM"]))
        - bias
    )

    H_dict["X_MIN"] = str(float(X_vals[0] - bias))
    H_dict["Y_MIN"] = str(float(Y_vals[0] - bias))
    H_dict["Z_MIN"] = str(float(H_dict["Z_MIN"]) - bias)

    H_dict["X_MAX"] = str(float(X_vals[-1] + bias))
    H_dict["Y_MAX"] = str(float(Y_vals[-1] + bias))
    H_dict["Z_MAX"] = str(float(Z_vals[-1] + bias))

G = np.vstack(np.meshgrid(X_vals, Y_vals, Z_vals)).reshape(3, -1).T

total = G.shape[0]

# ---------------------------------
# Split work
# ---------------------------------
chunk_size = math.ceil(total / n_tasks)

start = task_id * chunk_size
end = min(start + chunk_size, total)

print(f"[Task {task_id}] Processing indices {start}:{end}")

# ---------------------------------
# Generate chunk
# ---------------------------------
P_id = "0"
symmetry = H_dict["Symmetry_1"]
feature_id = "0"
phi1 = "0"
phi2 = "0"
phi3 = "0"

chunk_file = f"salt_chunk_{task_id:04d}.txt"

with open(chunk_file, "w") as f:

    for i in range(start, end):

        x, y, z = G[i]

        line = " ".join([
            phi1,
            phi2,
            phi3,
            str(x),
            str(y),
            str(z),
            feature_id,
            P_id,
            symmetry
        ])

        f.write(line + "\n")

print(f"[Task {task_id}] Wrote {chunk_file}")

# ---------------------------------
# Task 0 merges everything
# ---------------------------------
if task_id == 0:

    print("[Task 0] Waiting for all chunk files...")

    while True:

        chunk_files = sorted(glob("salt_chunk_*.txt"))

        if len(chunk_files) == n_tasks:
            break

        print(f"[Task 0] Found {len(chunk_files)}/{n_tasks} chunks")
        time.sleep(5)

    print("[Task 0] All chunks detected. Merging...")

    with open("salt_appended.txt", "w") as out_file:

        # Write header
        for key in H_dict.keys():
            out_file.write(f"# {key}: {H_dict[key]}\n#\n")

        # Write original points
        out_file.write(points)

        # Append chunk files
        for chunk in chunk_files:

            print(f"[Task 0] Appending {chunk}")

            with open(chunk, "r") as cf:
                out_file.write(cf.read())

    print("[Task 0] Finished writing salt_appended.txt")
    
    # Cleanup chunk files
    for chunk in chunk_files:
        os.remove(chunk)