from graph.nodes.booking_node import booking_node
from graph.nodes.clinic_Info_node import clinic_info_node
from graph.nodes.complaint_node import complaint_node
from graph.nodes.dirct_node import dirct_node
from graph.nodes.intent_node import intent_node
from graph.state import AgentState
from langgraph.graph import StateGraph, END

__agent_graph = None


def route_intent(state: AgentState) -> str:
   return state["intent"] # booking, clinic_info, complaint, direct




def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)
    # nodes
    graph.add_node("intent",intent_node)
    graph.add_node("booking",booking_node)
    graph.add_node("clinic_info",clinic_info_node)
    graph.add_node("complaint",complaint_node)
    graph.add_node("direct",dirct_node)
    # entry point
    graph.set_entry_point("intent")
    
    # intetn routing
    graph.add_conditional_edges(
     "intent",
        route_intent,
        {
            "booking": "booking",
            "clinic_info": "clinic_info",
            "complaint": "complaint",
            "direct": "direct"
        }     

   )
    
    graph.add_edge("booking",END)
    graph.add_edge("clinic_info",END)
    graph.add_edge("complaint",END)
    graph.add_edge("direct",END)

    return graph.compile() 

def get_agent_graph():
    global __agent_graph
    if __agent_graph is None:    
        __agent_graph = build_graph()   

    return __agent_graph    
