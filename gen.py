import csv
import re


with open("tube.csv") as f:
    moves = list(csv.reader(f))[1:]

map = {}


def graph_add(g, k, v):
    if k not in g:
        g[k] = set()
    g[k].add(v)


def link(a, b, line):
    graph_add(map, a, (b, line))
    graph_add(map, b, (a, line))


for (line, from_station, to_station) in moves:
    link(from_station, to_station, line)
    link(to_station, from_station, line)


def canon(name):
    n = (
        name.replace(" ", "_")
        .replace(".", "_")
        .replace("'s", "")
        .replace("(", "_")
        .replace(")", "_")
        .replace("/", "_")
        .replace("-", "_")
    )
    n = re.sub(r"_+", "_", n)
    n = re.sub("^_", "", n)
    n = re.sub("_$", "", n)
    return n.lower()  # re.sub(r"\(.*\)", "", n)


with open("src/lib.rs", "w") as f:
    for (station, conns) in sorted(map.items()):
        dests = {}
        lines = {}
        for (dest, line) in conns:
            graph_add(dests, dest, line)
            graph_add(lines, line, dest)

        f.write(f"pub mod {canon(station)} {{\n")
        f.write(f"//! {station}\n//!\n")
        f.write(f"//! # Served By\n")
        for line in sorted(lines):
            f.write(f"//! - {line}\n")

            graph_add(lines, line, dest)
        f.write("//!\n")
        f.write(f"//! # Connections\n")
        for (dest, vias) in sorted(dests.items()):
            f.write(f"//! - [{dest}](crate::{canon(dest)}) via {', '.join(vias)}\n")

        for dest in sorted(dests):
            f.write(f"pub use crate::{canon(dest)};\n")

        f.write("}\n")
