"""Helper functions to extract relevant data from HDF5 files."""
import h5py
import numpy as np

def load_h5(h5filepath):
    """Load HDF5 file."""
    return h5py.File(h5filepath, 'r')

def get_label(h5filepath, label = 'target_contacting_zone'):
    try:
        with h5py.File(h5filepath) as h5file:
            arr = []
            for key in h5file['frames'].keys():
                arr.append(np.array(h5file['frames'][key]['labels'][label]))

            return np.any(arr).item()
    except:
        return None

def get_metadata_from_h5(h5filepath):
    """Get metadata from HDF5 file.
    Read everything out of static that is not a group.
    """
    with h5py.File(h5filepath) as h5file:
        metadata = {}
        for key in h5file['static'].keys():
            try:
                datum = h5file['static'][key][()]
                if isinstance(datum, np.ndarray): # if ndarray, it'll cause problems later on
                    datum = datum.tolist()
                if isinstance(datum, bytes): # if bytes, it'll cause problems later on
                    datum = datum.decode('utf-8')
                # same if it is in a list
                if isinstance(datum, list):
                    datum = [d.decode('utf-8') if isinstance(d, bytes) else d for d in datum]
                metadata[key] = datum
            except:
                # we cannot read—might be a group
                pass
        return metadata