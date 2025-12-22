"""LangGraph workflow graph for interview sheet generation."""

from langgraph.graph import StateGraph, END

from src.agents.interview.workflow.state import InterviewWorkflowState
from src.agents.interview.workflow.nodes import (
    generate_metadata_node,
    generate_questions_node,
    generate_answers_node,
    persist_state_node,
    finalize_node
)


def create_workflow_graph() -> StateGraph:
    """Create the LangGraph workflow graph.
    
    Returns:
        Configured StateGraph
    """
    # Create the graph
    workflow = StateGraph(InterviewWorkflowState)
    
    # Add nodes
    workflow.add_node("generate_metadata", generate_metadata_node)
    workflow.add_node("persist_after_metadata", persist_state_node)
    workflow.add_node("generate_questions", generate_questions_node)
    workflow.add_node("persist_after_questions", persist_state_node)
    workflow.add_node("generate_answers", generate_answers_node)
    workflow.add_node("persist_after_answers", persist_state_node)
    workflow.add_node("finalize", finalize_node)
    
    # Define the flow
    workflow.set_entry_point("generate_metadata")
    
    workflow.add_edge("generate_metadata", "persist_after_metadata")
    workflow.add_edge("persist_after_metadata", "generate_questions")
    workflow.add_edge("generate_questions", "persist_after_questions")
    workflow.add_edge("persist_after_questions", "generate_answers")
    workflow.add_edge("generate_answers", "persist_after_answers")
    workflow.add_edge("persist_after_answers", "finalize")
    workflow.add_edge("finalize", END)
    
    # Compile the graph
    app = workflow.compile()
    
    return app

