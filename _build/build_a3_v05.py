# ett3 site · A3 · build v05 · packet v06 (D1 base plan, cover counts fixed); build_a3_v04 kept and reused
# python _build/build_a3_v05.py --manifest <path.json> [--release] [--check-live] [--shots]
import importlib.util, os
_s = importlib.util.spec_from_file_location("v4", os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_a3_v04.py"))
v4 = importlib.util.module_from_spec(_s); _s.loader.exec_module(v4)
v4.RELEASES.insert(0, ("a3-groundtruth-packet-v06", "A3 Ground Truth packet v06 (14 sheets, D1 base plan)"))  # same list object as b1 / b2 / b3
if __name__ == "__main__":
    v4.main()
