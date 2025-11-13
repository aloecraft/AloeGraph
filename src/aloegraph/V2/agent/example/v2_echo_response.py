from aloegraph.V2.graph.v2_aloe_node import AloeNode, AloeEdge
from aloegraph.V2.v2_aloe_graph import V2AloeGraph, END
import aloegraph.V2.v2_base_model as v2_base_model


class EchoAgent(V2AloeGraph[v2_base_model.V2AloeConfig]):

    @AloeNode(is_entry=True)
    @AloeEdge(target="echo2")
    def echo1(self, state: v2_base_model.V2AloeConfig) -> v2_base_model.V2AloeConfig:
        self.reply_notifier.add_reply(f"> {state.user_message}")
        self.reply_notifier.add_reply(f"Hello from Echo1")
        state.__EDGE__ = "echo2"
        return state

    @AloeNode()
    @AloeEdge(target="echo3_interrupt")
    def echo2(self, state: v2_base_model.V2AloeConfig) -> v2_base_model.V2AloeConfig:
        self.reply_notifier.add_reply("Hello from Echo2")
        state.__EDGE__ = "echo3_interrupt"
        return state

    @AloeNode()
    @AloeEdge(target="echo4_resume", interrupt=True)
    def echo3_interrupt(self, state: v2_base_model.V2AloeConfig) -> v2_base_model.V2AloeConfig:
        self.reply_notifier.add_reply("Hello from echo3_interrupt")
        state.__EDGE__ = "echo4_resume"
        return state

    @AloeNode()
    @AloeEdge(target=END)
    def echo4_resume(self, state: v2_base_model.V2AloeConfig) -> v2_base_model.V2AloeConfig:
        self.reply_notifier.add_reply(f"> {state.user_message}")
        self.reply_notifier.add_reply("Hello from echo4_resume")
        state.__EDGE__ = END
        return state

    def __init__(self,
                 initial_state: v2_base_model.V2AloeConfig,
                 reply_notifier: v2_base_model.ChatNotifier):

        self.state = initial_state
        self.reply_notifier = reply_notifier
