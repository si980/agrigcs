import traceback, os
log_file = os.path.join(os.path.dirname(__file__), "builder_exec.log")
try:
    with open(log_file, "w") as f:
        f.write("STARTING BUILDER SCRIPT\n")
    script_path = os.path.join(os.path.dirname(__file__), "build_agrigcs_realistic_prototype.py")
    with open(script_path, "r", encoding="utf-8") as f:
        code = f.read()
    exec(code)
    with open(log_file, "a") as f:
        f.write("BUILDER SCRIPT COMPLETED SUCCESSFULLY\n")
except Exception as e:
    with open(log_file, "a") as f:
        f.write("BUILDER EXCEPTION: " + traceback.format_exc() + "\n")
