REM Activate the conda environment
call C:\Users\avalon\Miniconda3\condabin\conda.bat activate venv-policheckbert

REM Run the Python scripts in parallel

D:

cd 5-Code\AVS-ComplianceAnalysis

start Python comp_analysis.py

start Python policy_download.py

start Python privacy_extract.py

cd ..\..\4-VAPrivComp-BERT

start Python PatternExtractionNotebook.py

pause




