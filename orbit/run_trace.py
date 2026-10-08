import traceback
import sys
import os

log_file = r"c:\Users\Dell\OneDrive\Documents\gate for all\New folder\stitch_agrigcs_iot_command_platform\stitch_agrigcs_iot_command_platform\orbit\trace_run.log"

try:
    with open(log_file, "w") as f:
        f.write("TRACE_RUN_START\n")
        
    script_path = r"c:\Users\Dell\OneDrive\Documents\gate for all\New folder\stitch_agrigcs_iot_command_platform\stitch_agrigcs_iot_command_platform\orbit\build_agrigcs_master_v2.py"
    with open(script_path, "r", encoding="utf-8") as sf:
        code = sf.read()
        
    compiled = compile(code, script_path, 'exec')
    exec(compiled, {'__file__': script_path, '__name__': '__main__'})
    
    with open(log_file, "a") as f:
        f.write("TRACE_RUN_SUCCESS\n")
except Exception as e:
    with open(log_file, "a") as f:
        f.write("TRACE_RUN_ERROR:\n" + traceback.format_exc() + "\n")
