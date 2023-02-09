from parse_hdf5 import *

test_path = "/Users/felixbinder/Desktop/dominoes_all_movies/pilot_dominoes_0mid_d3chairs_o1plants_tdwroom_0000.hdf5"

file = load_h5(test_path)

print(file.keys())

print(get_label(test_path))

print(get_metadata_from_h5(test_path))