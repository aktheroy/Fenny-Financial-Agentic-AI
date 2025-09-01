import os
from pathlib import Path


def create_structure(base_path: str):
    structure = [
        "backend/app/api/__init__.py",
        "backend/app/api/chat.py",
        "backend/app/api/health.py",
        "backend/app/core/__init__.py",
        "backend/app/core/config.py",
        "backend/app/core/dependencies.py",
        "backend/app/core/logger.py",
        "backend/app/agents/__init__.py",
        "backend/app/agents/state.py",
        "backend/app/agents/workflow.py",
        "backend/app/agents/nodes.py",
        "backend/app/rag/__init__.py",
        "backend/app/rag/loader.py",
        "backend/app/rag/vector_store.py",
        "backend/app/rag/retriever.py",
        "backend/app/models/__init__.py",
        "backend/app/models/chat.py",
        "backend/app/models/agent.py",
        "backend/app/main.py",
        "config/__init__.py",
        "config/settings.yaml",
        "config/prompts/rag_system.j2",
        "config/prompts/agent_system.j2",
        "data/documents/.gitkeep",
        "data/vector_db/.gitkeep",
        ".env",
        "requirements.txt",
        "Dockerfile",
        "run.py"
    ]

    for path in structure:
        full_path = os.path.join(base_path, path)
        Path(full_path).parent.mkdir(parents=True, exist_ok=True)

        if path.endswith('/'):  # If it's a directory
            continue
        elif not os.path.exists(full_path):
            with open(full_path, 'w') as f:
                if full_path.endswith('.py'):
                    f.write('"""Module docstring"""\n\n')
                elif full_path.endswith('.yaml'):
                    f.write('# Configuration settings\n')
                elif full_path.endswith('.j2'):
                    f.write('{# Prompt template #}\n')
                elif full_path.endswith('.gitkeep'):
                    f.write('')
                else:
                    # Empty file for other types
                    pass


if __name__ == "__main__":
    base_dir = os.getcwd()  # Create in current directory
    create_structure(base_dir)
    print("Structure created successfully!")
