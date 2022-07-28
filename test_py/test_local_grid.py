from src.domain.entities.local_grid import LocalGrid

import numpy as np
import pytest

from src.configuration.config import cfg


def test_local_grid_init():
    lg = LocalGrid((0, 0), np.array([]))
    assert lg.length_in_m == lg.cell_size_in_m * lg.length_num_cells


def test_world_coord_in_local_grid():
    lg = LocalGrid((9, 9), np.array([]))
    a = (10, 10)
    assert lg.is_inside(a) is True


def test_world_coord_not_in_local_grid():
    lg = LocalGrid((9, 9), np.array([]))
    a = (16, 10)
    assert lg.is_inside(a) is False


def test_calc_length_num_cells():
    lg = LocalGrid((9, 9), np.array([]))

    assert lg.length_num_cells == cfg.LG_LENGTH_IN_M / cfg.LG_CELL_SIZE_M

def test_transformation_back_to_back():
    lg = LocalGrid((10, 10), np.array([]))
    a = (10, 10)
    b = lg.world_coords2cell_idxs(a)
    assert a == pytest.approx(lg.cell_idx2world_coords(b), 0.1)
