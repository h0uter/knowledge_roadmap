from src.entities.abstract_agent import AbstractAgent
from src.entities.krm import KRM
from src.usecases.actions.abstract_action import AbstractAction
from src.utils.config import Config
from src.entities.local_grid import LocalGrid
from src.utils.event import post_event
from src.utils.my_types import EdgeType, NodeType


class ExploreFrontierAction(AbstractAction):
    def __init__(self, cfg: Config):
        super().__init__(cfg)

    def run(self, agent: AbstractAgent, krm: KRM, action_path):
        self.next_node = action_path[1]  # HACK: this is a hack, but it works for now
        next_node_data = krm.get_node_data_by_idx(action_path[1])
        agent.move_to_pos(next_node_data["pos"])

        # This is there so we can initialze by adding a frontier self edge on 0
        target_node_type = next_node_data["type"]

        at_destination = (
            len(
                krm.get_nodes_of_type_in_margin(
                    agent.get_localization(), self.cfg.ARRIVAL_MARGIN, target_node_type
                )
            )
            >= 1
        )
        self._log.debug(f"{agent.name}: at_destination: {at_destination}")

        if at_destination:
            self._log.debug(
                f"{agent.name}: Now the frontier is visited it can be removed to sample a waypoint in its place."
            )
            krm.remove_frontier(self.next_node)

            self.sample_waypoint_from_pose(agent, krm)
            lg = self.get_lg(agent)
            # XXX: this is my most expensive function, so I should try to optimize it
            self.obtain_and_process_new_frontiers(agent, krm, lg)
            # XXX: this is my 2nd expensive function, so I should try to optimize it
            self.prune_frontiers(krm)

            self.find_shortcuts_between_wps(lg, krm, agent)
            w_os = agent.look_for_world_objects_in_perception_scene()
            if w_os:
                for w_o in w_os:
                    krm.add_world_object(w_o.pos, w_o.name)
            post_event("new lg", lg)
            self.target_node = None
            self.action_path = None

    """Path Execution"""
    #############################################################################################
    def sample_waypoint_from_pose(self, agent: AbstractAgent, krm: KRM) -> None:
        """
        Sample a new waypoint at current agent pos, and add an edge connecting it to prev wp.
        this should be sampled from the pose graph eventually
        """
        # BUG:  this can make the agent teleport to a random frontier in the vicinty.
        # better would be to explicitly check if we reached the frontier we intended to reach.
        # and if we didnt to attempt to walk to it again. To attempt to actually expand the krm
        # with the intended frontier and not a random one
        # HACK: just taking the first one from the list is not neccessarily the closest

        wp_at_previous_pos_candidates = krm.get_nodes_of_type_in_margin(
            agent.previous_pos, self.cfg.PREV_POS_MARGIN, NodeType.WAYPOINT
        )

        if len(wp_at_previous_pos_candidates) == 0:
            self._log.debug(f"{agent.name}: No waypoint at previous pos.")
            return
        elif len(wp_at_previous_pos_candidates) >= 1:
            self._log.debug(
                f"{agent.name}: Multiple waypoints at previous pos, taking first one."
            )
            wp_at_previous_pos = wp_at_previous_pos_candidates[0]

            krm.add_waypoint(agent.get_localization(), wp_at_previous_pos)

        agent.localize_to_waypoint(krm)

    def obtain_and_process_new_frontiers(
        self, agent: AbstractAgent, krm: KRM, lg: LocalGrid,
    ) -> None:
        new_frontier_cells = lg.sample_frontiers_on_cellmap(
            radius=self.cfg.FRONTIER_SAMPLE_RADIUS_NUM_CELLS,
            num_frontiers_to_sample=self.cfg.N_SAMPLES,
        )
        self._log.debug(f"{agent.name}: found {len(new_frontier_cells)} new frontiers")
        for frontier_cell in new_frontier_cells:
            frontier_pos_global = lg.cell_idx2world_coords(frontier_cell)
            krm.add_frontier(frontier_pos_global, agent.at_wp)

    def prune_frontiers(self, krm: KRM) -> None:
        """obtain all the frontier nodes in krm in a certain radius around the current position"""

        waypoints = krm.get_all_waypoint_idxs()

        for wp in waypoints:
            wp_pos = krm.get_node_data_by_idx(wp)["pos"]
            close_frontiers = krm.get_nodes_of_type_in_margin(
                wp_pos, self.cfg.PRUNE_RADIUS, NodeType.FRONTIER
            )
            for frontier in close_frontiers:
                krm.remove_frontier(frontier)

    def find_shortcuts_between_wps(self, lg: LocalGrid, krm: KRM, agent: AbstractAgent):
        close_nodes = krm.get_nodes_of_type_in_margin(
            lg.world_pos, self.cfg.WP_SHORTCUT_MARGIN, NodeType.WAYPOINT
        )
        points = []
        for node in close_nodes:
            if node != agent.at_wp:
                points.append(krm.get_node_data_by_idx(node)["pos"])

        if points:
            for point in points:
                at_cell = lg.length_num_cells / 2, lg.length_num_cells / 2
                to_cell = lg.world_coords2cell_idxs(point)
                is_collision_free, _ = lg.is_collision_free_straight_line_between_cells(
                    at_cell, to_cell
                )
                if is_collision_free:
                    from_wp = agent.at_wp
                    to_wp = krm.get_node_by_pos(point)

                    krm.add_waypoint_diedge(from_wp, to_wp)

    # utitlies
    ############################################################################################
    def get_lg(self, agent: AbstractAgent) -> LocalGrid:
        lg_img = agent.get_local_grid_img()

        return LocalGrid(
            world_pos=agent.get_localization(), img_data=lg_img, cfg=self.cfg,
        )
