# TVA Friends: matrice di autorizzazione sulle regole PROPOSTE (simulatore Node, NON emulatore Firebase).
import subprocess,sys,os
r=subprocess.run(['node',os.path.join(os.environ.get('TVA_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'tests','friends_rules_matrix.js')],capture_output=True,text=True)
print(r.stdout); print(r.stderr); sys.exit(r.returncode)
