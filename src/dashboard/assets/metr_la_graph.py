import random

nodes = [{"data": {"id": str(i), "label": f"Node {i}"}} for i in range(1, 21)]

edges = [
    {
        "data": {
            "source": str(random.randint(1, 20)),
            "target": str(random.randint(1, 20)),
        }
    }
    for _ in range(30)
]

default_elements = nodes + edges