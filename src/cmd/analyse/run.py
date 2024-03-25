import itertools
from difflib import SequenceMatcher

import pandas
from pyvis.network import Network


class StrSimSet:
    def __init__(self, ratio: float):
        self._simset = set()
        self._filter_ratio = ratio

    def fill_from_list(self, data: list[str]):
        for el in data:
            self.add(el)

    def add(self, el: str) -> str:
        sim = self.get(el)
        if sim is not None:
            return sim

        self._simset.add(el)

        return el

    def get(self, el: str):
        simitems = list(filter(
            lambda s: self.similar(s, el) >= self._filter_ratio,
            self._simset,
        ))

        if len(simitems) == 0:
            return None

        return simitems[0]

    def as_set(self) -> set[str]:
        return self._simset

    @ staticmethod
    def similar(a: str, b: str) -> float:
        return SequenceMatcher(None, a, b).ratio()


def transform_refs(s: str) -> list[str]:
    try:
        return list(s.split("-::-"))
    except BaseException:
        return []


def load_raw(filename: str) -> pandas.DataFrame:
    data = pandas.read_csv(filename)

    data.columns = [
        "title",
        "references",
    ]

    data["references"] = data["references"].apply(transform_refs)

    return data


def normalize(data: pandas.DataFrame):
    print(data.info())
    print(data.head(10))

    return data


def to_graph(data: pandas.DataFrame):
    all_raw_nodes = [
        *data["title"],
        *list(itertools.chain(*data["references"])),
    ]

    print("all_raw_nodes", len(all_raw_nodes))

    sim_set = StrSimSet(0.8)

    for i in range(len(all_raw_nodes)):
        item = all_raw_nodes[i]
        el = sim_set.add(item)
        all_raw_nodes[i] = el

    raw_nodes = set(all_raw_nodes)

    print("raw_nodes", len(raw_nodes))

    node_id_mapping = {title: i for i, title in enumerate(raw_nodes)}

    nodes = [{"id": id, "title": title}
             for title, id in node_id_mapping.items()]

    edges = []
    for _, row in data.iterrows():
        title = sim_set.get(str(row["title"]))
        links = row["references"]
        for link in links:
            link = sim_set.get(link)
            edges.append({
                "from": node_id_mapping[title],
                "to": node_id_mapping[link]
            })

    net = Network(
        bgcolor="#ffffff",
        height="750px",
        width="100%",
        select_menu=True,
        filter_menu=True,
    )
    net.show_buttons(filter_="physics")

    print(f"node count: {len(nodes)}")
    for node in nodes:
        print(node, len(
            list(filter(
                lambda s: s["to"] == node["title"], edges
            )),
        ))
        net.add_node(
            node["id"],
            node["title"],
            value=len(
                list(filter(
                    lambda s: s["from"] == node["title"], edges
                )),
            ),
        )

    print(f"edge count: {len(edges)}")
    for edge in edges:
        net.add_edge(
            edge["from"],
            edge["to"],
        )

    return net


def main():
    data = load_raw("~/Documents/pp/elib-parser/data/sample.csv")

    data = normalize(data)

    graph = to_graph(data)

    graph.write_html("sample.html")


if __name__ == "__main__":
    main()
