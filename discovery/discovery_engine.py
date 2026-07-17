class DiscoveryEngine:

    def __init__(self):
        self.hypotheses = []

    def add(self, name, value):
        self.hypotheses.append({
            "name": name,
            "value": value
        })

    def report(self):
        print("\n=== DISCOVERY ENGINE ===\n")
        for h in self.hypotheses:
            print(f"{h['name']}: {h['value']}")
