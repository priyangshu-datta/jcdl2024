import pymupdf as pypdf
from pathlib import Path
from random import random
import base64
import re


def annotate_pdf(pdf_path: Path, datasets: list[str]):
    doc: pypdf.Document = pypdf.open(pdf_path)

    color = {dataset: (random(), random(), 0) for dataset in datasets}

    for pi in range(doc.page_count):
        page = doc.load_page(pi)

        datasets_rects = {}

        for dataset in datasets:
            text_rects: list[pypdf.Rect] = pypdf.utils.search_for(page, f"{dataset}")
            buffer_text_px = 2
            datasets_rects[dataset] = []
            for rect in text_rects:
                m_rect = pypdf.Rect(
                    x0=rect.x0 - buffer_text_px,
                    x1=rect.x1 + buffer_text_px,
                    y0=rect.y0 + 2,
                    y1=rect.y1 - 2,
                )
                text = page.get_textbox(m_rect)

                if (
                    not (
                        re.match("[A-Za-z]", text[0]) and re.match("[A-Za-z]", text[-1])
                    )
                    or text[0] == dataset[0]
                    or text[-1] == dataset[-1]
                ):
                    datasets_rects[dataset].append(rect)

        dataset_objects = [
            {
                "dataset": dataset,
                "color": color[dataset],
                "rects": datasets_rects[dataset],
            }
            for dataset in datasets
        ]

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
