from langgraph import graph
from langgraph.graph import StateGraph,START,END
from app.state import InterviewState
from app.agents.jd_parser import jd_parser_node
from app.agents.resume_matcher import resume_matcher_node
from app.agents.question_generator import question_generator_node
from app.agents.evaluator import evaluator_node
from app.agents.supervisor import supervisor_node,router

def build_graph():
    builder = StateGraph(InterviewState)

    builder.add_node("jd_parser",jd_parser_node)
    builder.add_node("resume_matcher",resume_matcher_node)
    builder.add_node("question_generator",question_generator_node)
    builder.add_node("evaluator",evaluator_node)
    builder.add_node("supervisor",supervisor_node)

    builder.add_edge(START,"supervisor")
    builder.add_conditional_edges("supervisor",router)

    builder.add_edge("jd_parser","supervisor")
    builder.add_edge("resume_matcher","supervisor")
    builder.add_edge("question_generator","supervisor")
    builder.add_edge("evaluator","supervisor")

    return builder.compile()

graph = build_graph()