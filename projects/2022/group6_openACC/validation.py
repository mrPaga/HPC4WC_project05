# script to evaluate the difference between gpu output data and original cpu output data
import os as os
from glob import glob
import numpy as np
import matplotlib.pyplot as plt
 
# list of all filenames
cpu_file = sorted(glob("data/out_field_orig_0128.dat"))
gpu_files = sorted(glob("data/out_field_acc*_0128.dat"))
out_files = cpu_file + gpu_files

cpu_result_file = sorted(glob("data/result_orig_0128.txt"))
gpu_result_files = sorted(glob("data/result_acc*_0128.txt"))
result_files = cpu_result_file + gpu_result_files

# function to read data arrays generated by stencil2d (taken from the day 1 notebook 02-stencil-program.ipynb)
def read_field_from_file(filename="out_field-ver.dat", num_halo=None):
    (rank, nbits, num_halo, nx, ny, nz) = np.fromfile(filename, dtype=np.int32, count=6)
    offset=(3 + rank) * 32 // nbits
 
    data = np.fromfile(\
                        filename, dtype=np.float32 if nbits == 32 else np.float64,\
                        count=nz * ny * nx + offset
                    )

    if rank == 3:
        return np.reshape(data[offset:], (nz, ny, nx))
    else:
        return np.reshape(data[offset:], (ny, nx))

# import all versions of out_field
out_fields = []
for file in out_files:
    out_fields.append(read_field_from_file(file))

# print some basic information about the different versions
print("\n")
for index, out in enumerate(out_fields):
    if index == 0:
        print(\
                out_files[index].split("_")[2], ":",\
                "\t\t max =", np.around(np.max(out), 3),\
                "\t min =", np.around(np.min(out), 3)\
            )
    else:
        print(\
                out_files[index].split("_")[2], ":",\
                "\t max =", np.around(np.max(out), 3),\
                "\t min =", np.around(np.min(out), 3)\
            )
print("\n")

# import the runtimes of all versions
times = []
for file in result_files:
    lines = open(file).readlines()
    exec(" ".join(lines[(-3):None]))
    times.append(data[0, (-1)])

# evaluate the difference of gpu output to original cpu output
tolerance = 1e-06   # threshold for two values to be close
cpu_out_file = out_files[0].split("_")[2]
t_cpu = np.around(times[0], 6)

for index, out in enumerate(out_fields):
    if index == 0:
        continue
    else:
        out_file = out_files[index].split("_")[2]
        t_out = np.around(times[index], 6)
        is_close = np.allclose(out, out_fields[0], atol = tolerance)
        print(\
                "|", out_file, "-", cpu_out_file, "| <=", tolerance, ":", is_close,\
                "\t\t",\
                "(", out_file, ":", t_out, "s", ",", cpu_out_file, ":", t_cpu, "s", ")"\
            )
print("\n")

# plot initial condition and final result
fig = plt.figure(figsize = (12, 24))
for index in range(1, len(out_files)):
    ax_cpu = fig.add_subplot(len(out_files), 2, 2*index - 1)   # nrow, ncol, nplot
    ax_cpu.imshow(out_fields[0][20, :, :])
    ax_cpu.set_title(("CPU" + " " + "output"))

    ax_gpu = fig.add_subplot(len(out_files), 2, 2*index)   # nrow, ncol, nplot
    ax_gpu.imshow(out_fields[index][20, :, :])
    ax_gpu.set_title((out_files[index].split("_")[2] + " " + "output"))
fig.savefig("plots/validation.pdf", format="pdf", dpi=600, bbox_inches="tight", pad_inches=0.5)


