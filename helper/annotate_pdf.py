import attrs
import pymupdf as pypdf
from pathlib import Path
from random import random
import base64


@attrs.define(frozen=True)
class Color:
    r: float
    g: float
    b: float

    def invert(self):
        return Color(1 - self.r, 1 - self.g, 0)

    def get(self):
        return self.r, self.g, self.b


def annotate_pdf(pdf_path: Path, datasets: list[str]):
    doc: pypdf.Document = pypdf.open(pdf_path)
    dataset_objects = [
        {
            "dataset": dataset,
            "color": (random(), random(), 0),
            "rects": pypdf.utils.search_for(page, f" {dataset} "),
        }
        for dataset in datasets
    ]

    for pi in range(doc.page_count):
        page = doc.load_page(pi)

        for obj in dataset_objects:
            for rect in obj["rects"]:
                annot = page.add_rect_annot(rect)
                # pypdf.utils.draw_rect(
                #     page,
                #     pypdf.Rect(
                #         x0=rect.tl[0],
                #         y0=rect.tl[1] - 9.5,
                #         x1=rect.tl[0] + 8,
                #         y1=rect.tl[1] + 1,
                #     ),
                #     fill=obj["color"],
                #     stroke_opacity=0,
                # )

                annot.set_colors(stroke=obj["color"], fill=obj["color"])
                annot.set_opacity(0.5)
                annot.update()

    annot_link = (
        f"data:application/pdf;base64,{base64.b64encode(doc.tobytes()).decode()}"
    )

    doc.close()

    return annot_link
