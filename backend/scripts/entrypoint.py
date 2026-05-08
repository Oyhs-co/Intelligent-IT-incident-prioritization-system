import subprocess
import sys
import os

def run_command(cmd, check=True, optional=False, discard_stderr_on_fail=False):
    """Run a command and handle errors like set -e"""
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout, end='')
        if not discard_stderr_on_fail and result.stderr:
            print(result.stderr, end='', file=sys.stderr)
        return result
    except subprocess.CalledProcessError as e:
        if optional:
            if discard_stderr_on_fail:
                # Discard stderr as requested
                print("[entrypoint] Seeds omitidos o ya ejecutados")
            else:
                print(f"[entrypoint] Command failed (optional): {e}", file=sys.stderr)
                if e.stderr:
                    print(e.stderr, end='', file=sys.stderr)
            return None
        else:
            print(f"[entrypoint] Command failed with exit code {e.returncode}", file=sys.stderr)
            if e.stdout:
                print(e.stdout, end='')
            if not discard_stderr_on_fail and e.stderr:
                print(e.stderr, end='', file=sys.stderr)
            sys.exit(e.returncode)

def main():
    print("[entrypoint] Inicializando base de datos...")
    run_command("python scripts/init_db.py")
    
    print("[entrypoint] Ejecutando seeds (opcional)...")
    # This simulates: python scripts/seed_data.py 2>/dev/null || echo "[entrypoint] Seeds omitidos o ya ejecutados"
    run_command("python scripts/seed_data.py", optional=True, discard_stderr_on_fail=True)
    
    print("[entrypoint] Iniciando servidor...")
    # Use os.execvp to replace the current process like exec in bash
    port = os.environ.get("PORT", "8000")
    uvicorn_cmd = ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", port]
    try:
        os.execvp(uvicorn_cmd[0], uvicorn_cmd)
    except FileNotFoundError:
        print("[entrypoint] uvicorn not found", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()