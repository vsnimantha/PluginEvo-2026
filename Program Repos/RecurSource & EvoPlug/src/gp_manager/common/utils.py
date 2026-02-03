import copy

def safe_copy(ind):
    """Try deep copy, fallback to shallow copy or original."""
    try:
        return copy.deepcopy(ind)
    except Exception as e:
        print(f"[DEBUG] deepcopy failed: {e}")
        try:
            return copy.copy(ind)
        except Exception as e2:
            print(f"[DEBUG] shallow copy also failed: {e2}")
            return ind  # final fallback
