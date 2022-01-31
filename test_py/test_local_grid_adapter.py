from knowledge_roadmap.data_providers.local_grid_adapter import LocalGridAdapter

import os
from knowledge_roadmap.utils.coordinate_transforms import img_axes2world_axes
from PIL import Image
import numpy as np


def test_sim_calc_total_img_length_in_m():
    map_img = np.zeros((100, 100))
    lga = LocalGridAdapter(50,420, 50/2026)
    assert (1, 1) == lga.sim_calc_total_img_length_in_m(map_img, 0.01)

def test_sim_calc_total_img_length_in_m_real_map():
    full_path = os.path.join('resource', 'villa_holes_closed.png')

    upside_down_map_img = Image.open(full_path)
    map_img = img_axes2world_axes(upside_down_map_img)
    cell_size = 0.01
    lga = LocalGridAdapter(50,420, 50/2026)
    Lx = map_img.shape[0] * cell_size
    Ly = map_img.shape[1] * cell_size
    assert (Lx, Ly) == lga.sim_calc_total_img_length_in_m(map_img, cell_size)

def test_sim_calc_total_img_length_in_m2():
    map_img = np.zeros((500, 100))
    lga = LocalGridAdapter(50,420, 50/2026)
    assert (5, 1) == lga.sim_calc_total_img_length_in_m(map_img, 0.01)

def test_calc_cells_per_m():
    map_img = np.zeros((100, 100))
    lga = LocalGridAdapter(50,420, 50/2026)
    assert (50, 50) == lga.sim_calc_cells_per_m(map_img, (2, 2))

def test_sim_calc_cell_size_in_m():
    map_img = np.zeros((400, 300))
    lga = LocalGridAdapter(50,420, 50/2026)
    assert (0.1, 0.1) == lga.sim_calc_cell_size_in_m(map_img, (40,30))