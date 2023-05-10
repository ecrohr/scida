# some script allowing us to copy HDF5 test files, but truncating fields to length 1
import os.path

import h5py
import typer

from astrodask import load
from astrodask.io import walk_hdf5file

app = typer.Typer()


@app.command()
def create_hdf5_testfile(src: str, dst: str):
    if os.path.isdir(src):
        # we support multi-file hdf5 files via our load() function
        ds = load(src)
        src = ds.file.filename
    tree = {}
    walk_hdf5file(src, tree)
    grps = tree["groups"]
    datasets = tree["datasets"]
    attrs = tree["attrs"]
    with h5py.File(dst, "w") as f:
        for k in grps:
            if k == "/":
                continue
            f.create_group(k)
        with h5py.File(src, "r") as g:
            for path, shape, dtype in datasets:
                shape_new = (1,)
                if len(shape) > 1:
                    shape_new = (1,) + shape[1:]
                f.create_dataset(path, shape=shape_new, dtype=dtype, data=g[path][0])
        for path, dct in attrs.items():
            for k in dct:
                f[path].attrs[k] = dct[k]


if __name__ == "__main__":
    app()
