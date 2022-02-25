from src.entities.event import post_event, subscribe
from src.entrypoints.abstract_vizualisation import AbstractVizualisation
from src.entrypoints.mpl_vizualisation import MplVizualisation
from src.entrypoints.vedo_vizualisation import VedoVisualisation
from src.utils.config import Config, Vizualiser, PlotLvl


class VizListener():

    def __init__(self, cfg: Config):
        self.cfg = cfg
        if cfg.VIZUALISER == Vizualiser.MATPLOTLIB:
            self.viz = MplVizualisation(cfg)
        else:
            self.viz = VedoVisualisation(cfg)

    # BUG: multi agents all post their lg events and overwrite eachother
    def handle_new_lg_event(self, lg):
        self.lg = lg

    def handle_figure_update_event(self, data):
        if self.cfg.PLOT_LVL == PlotLvl.ALL or self.cfg.PLOT_LVL == PlotLvl.INTERMEDIATE_ONLY:
            krm = data["krm"]
            agents = data["agents"]
            self.viz.figure_update(krm, agents, self.lg)

    def handle_figure_final_result_event(self, data):
        if self.cfg.PLOT_LVL == PlotLvl.RESULT_ONLY or self.cfg.PLOT_LVL == PlotLvl.ALL:
            krm = data["krm"]
            agents = data["agents"]
            self.viz.figure_final_result(krm, agents, self.lg)

    def setup_viz_event_handler(self):
        subscribe("new lg", self.handle_new_lg_event)
        subscribe("figure update", self.handle_figure_update_event)
        subscribe("figure final result", self.handle_figure_final_result_event)
