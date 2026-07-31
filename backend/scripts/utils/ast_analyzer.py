import ast
from pathlib import Path
from typing import Dict, List, Any

class AgentASTVisitor(ast.NodeVisitor):
    def __init__(self):
        self.metadata = {
            "tools": set(),
            "models": set(),
            "providers": set(),
            "prompts": set(),
            "memory": set(),
            "permissions": set(),
            "capabilities": set(),
            "workflows": set()
        }

    def visit_Call(self, node: ast.Call):
        # Look for StructuredTool.from_function or similar tool registrations
        if isinstance(node.func, ast.Attribute) and node.func.attr == 'from_function':
            if isinstance(node.func.value, ast.Name) and node.func.value.id == 'StructuredTool':
                for kw in node.keywords:
                    if kw.arg == 'name' and isinstance(kw.value, ast.Constant):
                        self.metadata["tools"].add(kw.value.value)
        
        # Look for model instantiation e.g. ChatOpenAI(model="...")
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            if 'Chat' in func_name or 'LLM' in func_name:
                self.metadata["providers"].add(func_name)
                for kw in node.keywords:
                    if kw.arg in ('model', 'model_name') and isinstance(kw.value, ast.Constant):
                        self.metadata["models"].add(kw.value.value)
                        
        # Also look for create_agent calls to extract models if passed directly
        if isinstance(node.func, ast.Name) and node.func.id == 'create_agent':
             for kw in node.keywords:
                 if kw.arg == 'system_prompt' and isinstance(kw.value, ast.Name):
                     self.metadata["prompts"].add(kw.value.id)
                 if kw.arg == 'model' and isinstance(kw.value, ast.Name):
                     # If model is passed as a variable, we just record the variable name reference
                     # In a full static analysis, we'd trace this back. 
                     # For our requirements, we just need to ensure the AST doesn't hide malicious changes.
                     pass

        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign):
        # Look for system prompts assignments
        for target in node.targets:
            if isinstance(target, ast.Name):
                if 'PROMPT' in target.id.upper():
                    if isinstance(node.value, ast.Constant):
                        self.metadata["prompts"].add(target.id)
        self.generic_visit(node)
        
    def visit_FunctionDef(self, node: ast.FunctionDef):
        # Look for decorators for tool or permission registrations
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
                if decorator.func.id == 'tool':
                    self.metadata["tools"].add(node.name)
        self.generic_visit(node)


def extract_agent_metadata(agent_dir: str) -> Dict[str, List[Any]]:
    """
    Parses Python files in the given agent directory and extracts
    code metadata (tools, models, prompts) using AST static analysis.
    """
    visitor = AgentASTVisitor()
    agent_path = Path(agent_dir)
    
    # Parse all python files in the agent directory (including subdirs like dev/)
    for py_file in agent_path.rglob("*.py"):
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=str(py_file))
                visitor.visit(tree)
        except Exception as e:
            print(f"Error parsing {py_file}: {e}")
            
    # Convert sets to sorted lists for deterministic comparison
    return {k: sorted(list(v)) for k, v in visitor.metadata.items()}
