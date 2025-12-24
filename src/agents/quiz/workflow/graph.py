from langgraph.graph import StateGraph, END

from src.agents.quiz.workflow.nodes import (
    generate_questions_node,
    generate_category_metadata_node,
    persist_state_node,
    finalize_quiz_node,
)
from src.agents.quiz.workflow.state import QuizWorkflowState

def create_workflow_graph():
    """Create the LangGraph workflow graph."""
    # Create the graph with state schema
    workflow = StateGraph[QuizWorkflowState, None, QuizWorkflowState, QuizWorkflowState](QuizWorkflowState)
    
    # Add nodes
    workflow.add_node("generate_questions", generate_questions_node)
    workflow.add_node("persist_after_questions", persist_state_node)
    workflow.add_node("generate_metadata", generate_category_metadata_node)
    workflow.add_node("persist_after_metadata", persist_state_node)
    workflow.add_node("finalize", finalize_quiz_node)
    
    # Set entry point
    workflow.set_entry_point("generate_questions")
    
    # Define the flow (edges)
    workflow.add_edge("generate_questions", "persist_after_questions")
    workflow.add_edge("persist_after_questions", "generate_metadata")
    workflow.add_edge("generate_metadata", "persist_after_metadata")
    workflow.add_edge("persist_after_metadata", "finalize")
    workflow.add_edge("finalize", END)
    
    # Compile and return
    return workflow.compile()