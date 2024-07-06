from pathlib import Path
from helper.basics import chcksum
from helper.goauth import GenerativeServiceClient as GenerativeServiceClient
from helper.vectorDB import ChromaPersist as ChromaPersist
from helper.extract_datasets import extract_datasets as extract_datasets

from urllib.request import urlopen
from bs4 import BeautifulSoup as bs4
from grobid_client.grobid_client import GrobidClient


def download_pdf_helper(url):
    buffer = urlopen(url).read()
    return {"id": chcksum(buffer), "buffer": buffer}


def xml2title(path: Path):
    with open(path, "r") as f:
        paper = bs4(f, features="xml")

    if paper.title == None:
        return path.name.replace(".grobid.tei.xml", "")

    return paper.title.get_text()


def pdf2xml(grobid_client: GrobidClient, input_path: Path, output_path: Path):
    grobid_client.process(
        "processFulltextDocument",
        input_path=input_path,
        output=output_path,
        consolidate_header=False,
    )

    return [
        {"id": path.name.replace(".grobid.tei.xml", ""), "title": xml2title(path)}
        for path in output_path.glob("*.grobid.tei.xml")
    ]


def xml2text(path: Path):
    with open(path, "r") as f:
        paper = bs4(f, features="xml")

    if paper.body == None:
        return ""

    for tag in paper.body.select("ref, figure, note"):
        tag.decompose()

    return paper.body.get_text("\n", True)
