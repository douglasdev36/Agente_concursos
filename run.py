"""
Script de entrada para iniciar a aplicação via linha de comando.
Execute: streamlit run run.py
"""
import subprocess
import sys
import os

if __name__ == "__main__":
    app_path = os.path.join(os.path.dirname(__file__), "app", "ui", "main_ui.py")
    subprocess.run([sys.executable, "-m", "streamlit", "run", app_path])
