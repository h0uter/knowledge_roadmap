from src.configuration.config import Config
from src.domain.entities.local_grid import LocalGrid
from src.domain.entities.object_types import ObjectTypes
from src.domain.services.abstract_agent import AbstractAgent
from src.domain.services.tosg import TOSG


# BUG: on the real robot sometimes impossible shortcuts are added.
def add_shortcut_edges_between_wps_on_lg(
    lg: LocalGrid, tosg: TOSG, agent: AbstractAgent, cfg: Config
):
    close_nodes = tosg.get_nodes_of_type_in_margin(
        lg.world_pos, cfg.WP_SHORTCUT_MARGIN, ObjectTypes.WAYPOINT
    )
    shortcut_candidate_positions = []
    for node in close_nodes:
        if node != agent.at_wp:
            shortcut_candidate_positions.append(tosg.get_node_data_by_node(node)["pos"])

    if shortcut_candidate_positions:
        for point in shortcut_candidate_positions:
            at_cell = lg.length_num_cells / 2, lg.length_num_cells / 2
            to_cell = lg.world_coords2cell_idxs(point)
            is_collision_free, _ = lg.is_collision_free_straight_line_between_cells(
                at_cell, to_cell
            )
            if is_collision_free:
                from_wp = agent.at_wp
                to_wp = tosg.get_node_by_pos(point)

                if not tosg.G.has_edge(from_wp, to_wp):
                    tosg.add_waypoint_diedge(from_wp, to_wp)
