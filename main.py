from pathlib import Path
from queue import Queue
from tempfile import TemporaryDirectory
from threading import Thread
from time import time

import pandas as pd
import pydash as py_
import streamlit as st
from grobid_client.grobid_client import GrobidClient
from streamlit.runtime.scriptrunner import add_script_run_ctx

from helper.annotate_pdf import annotate_pdf
from helper.basics import chcksum
from utils import download_pdf_helper, extract_datasets, pdf2xml, xml2text
import re
from helper.keywords_regexs import inside_bracket_regex

st.set_page_config(page_title="exData", page_icon="⛏️", layout="centered")

st.title("exData", anchor=False, help="extract Dataset Mentions from research articles")


def extract_datasets_process():
    while True:
        paper_id = st.session_state.task_list.get()
        full_text = xml2text(
            Path(st.session_state.tmpdir.name)
            .joinpath("xml", paper_id)
            .with_suffix(".grobid.tei.xml")
        )

        start = time()
        datasets = extract_datasets(full_text)

        refined_datasets: list[str] = []
        for dataset in datasets or []:
            if match := re.findall(inside_bracket_regex, dataset):
                match: list[str] = [m.strip() for m in match]
                refined_datasets = py_.union(
                    refined_datasets,
                    match,
                    [re.sub(rf"\({m}\)", "", dataset).strip() for m in match],
                )
            else:
                refined_datasets = py_.union(refined_datasets, [dataset])

        end = time()

        st.session_state.done_list.put(
            {"id": paper_id, "datasets": refined_datasets, "time_elapsed": end - start}
        )

        st.session_state.task_list.task_done()


if "task_list" not in st.session_state:
    st.session_state.task_list = Queue()

if "done_list" not in st.session_state:
    st.session_state.done_list = Queue()

if "n_tasks" not in st.session_state:
    st.session_state.n_tasks = 0

if "daemon" not in st.session_state:
    thread = Thread(target=extract_datasets_process, daemon=True)
    add_script_run_ctx(thread)
    thread.start()
    st.session_state.daemon = True

if "grobid_client" not in st.session_state:
    st.session_state.grobid_client = GrobidClient(
        grobid_server="https://kermitt2-grobid.hf.space",
        batch_size=1000,
        sleep_time=5,
        timeout=60,
    )

if "pdfs" not in st.session_state:
    st.session_state.pdfs = []

if "new_entry_flag" not in st.session_state:
    st.session_state.new_entry_flag = False

if "tmpdir" not in st.session_state:
    st.session_state.tmpdir = TemporaryDirectory(dir="cache")

if "disable_extract_btn" not in st.session_state:
    st.session_state.disable_extract_btn = False

if "submitted" not in st.session_state:
    st.session_state.submitted = False

if not (st.session_state.task_list.empty() and st.session_state.done_list.empty()):
    st.session_state.disable_extract_btn = True
else:
    st.session_state.disable_extract_btn = False

upload_pdfs = []
download_pdfs: list[str] = []

_ = """
UI elements
"""

input_type = st.selectbox(
    "Input type",
    ("PDF", "URL"),
    disabled=st.session_state.disable_extract_btn,
    label_visibility="hidden",
)


with st.form("file_form"):
    _ = """
        change UI element for getting Research Papers
    """
    match input_type:
        case "PDF":
            upload_label = "Upload Research Papers"
            st.info(upload_label)
            upload_pdfs = st.file_uploader(
                upload_label,
                accept_multiple_files=True,
                type="pdf",
                label_visibility="collapsed",
            )
        case "URL":
            st.info("Download Research Papers")
            download_pdfs = st.data_editor(
                pd.DataFrame([{"url": None}]),
                column_config={
                    "url": st.column_config.LinkColumn(
                        label="URL",
                        width="medium",
                        validate=r"^https://.+$",
                        display_text=r"^https://.+?/([^/]+?)$",
                    )
                },
                use_container_width=True,
                num_rows="dynamic",
            )["url"].to_list()

            download_pdfs = py_.map_(download_pdfs, lambda pdf: (pdf or "").strip())

    process_btn = st.form_submit_button(
        "Process Files", disabled=st.session_state.disable_extract_btn
    )

if not process_btn and len(st.session_state.pdfs) < 1:
    st.stop()

if "pdfs" in st.session_state:
    pdfs = py_.union(
        st.session_state.pdfs,
        [
            {"id": chcksum(pdf.getvalue()), "buffer": pdf.getvalue()}
            for pdf in py_.filter_(upload_pdfs)
        ]
        + [download_pdf_helper(url) for url in py_.filter_(download_pdfs)],
    )

    if len(pdfs) != len(st.session_state.pdfs):
        st.session_state.pdfs = pdfs
        st.session_state.new_entry_flag = True

Path(st.session_state.tmpdir.name).joinpath("pdf").mkdir(parents=True, exist_ok=True)
for pdf in st.session_state.pdfs:
    _ = """Save the pdfs locally in temporary directory."""
    with open(
        Path(st.session_state.tmpdir.name)
        .joinpath("pdf", pdf["id"])
        .with_suffix(".pdf"),
        "wb",
    ) as file:
        file.write(pdf["buffer"])

_ = """Convert the PDFs to XMLs"""
Path(st.session_state.tmpdir.name).joinpath("xml").mkdir(parents=True, exist_ok=True)
xmls = pdf2xml(
    st.session_state.grobid_client,
    Path(st.session_state.tmpdir.name).joinpath("pdf"),
    Path(st.session_state.tmpdir.name).joinpath("xml"),
)


if (
    "papers_df" not in st.session_state
    or st.session_state.papers_df.empty
    or st.session_state.new_entry_flag
):
    _ = """Prepare a Dataframe of the processed Papers"""
    if st.session_state.new_entry_flag:
        st.session_state.new_entry_flag = False
    st.session_state.papers_df = pd.DataFrame(
        data=[
            {
                "title": xml["title"],
                "status": "🔴",
                "datasets": [],
                "time_elapsed": 0.0,
                "download_link": "",
            }
            for xml in xmls
        ],
        index=[xml["id"] for xml in xmls],
    )

with st.form("paper_select"):
    _ = """Use the Dataframe from earlier to show the table."""
    event = st.dataframe(
        st.session_state.papers_df,
        column_config={
            "title": st.column_config.TextColumn("Title"),
            "status": st.column_config.TextColumn("Status"),
            "datasets": st.column_config.ListColumn("Datasets"),
            "time_elapsed": st.column_config.NumberColumn(
                "Time Elapsed", format="%.2fs"
            ),
            "download_link": st.column_config.LinkColumn(
                "Download Link", display_text="Download"
            ),
        },
        selection_mode="multi-row",
        hide_index=True,
        use_container_width=True,
        on_select="rerun",
    )
    st.session_state.submitted = st.form_submit_button(
        "Extract datasets", disabled=st.session_state.disable_extract_btn
    )

if st.session_state.submitted:
    st.session_state.disable_extract_btn = True
    paper_ids = st.session_state.papers_df.index[event.selection.rows].to_list()
    st.session_state.n_tasks = len(paper_ids)

    for paper_id in paper_ids:
        _ = """Put the tasks in a queue. And set the status of the task to pending."""
        st.session_state.task_list.put(paper_id)
        st.session_state.papers_df.at[paper_id, "status"] = "🟡"

    st.rerun()

while True:
    _ = """
        Number of tasks is set in __if submitted__ block.
        If there are tasks, then wait for the task to be completed, get() method is blocks the execution.
        After the task is completed reduce the number of tasks and set the result.
        Rerun the app to reflect the result.
        
        As this is wrapped in while True, it will wait for next task to get complete.
        However, if there are no task left the while True loop breaks.
        
    """
    if st.session_state.n_tasks > 0:
        result = st.session_state.done_list.get()
        st.session_state.n_tasks -= 1
        st.session_state.papers_df.at[result["id"], "status"] = "🟢"
        st.session_state.papers_df.at[result["id"], "datasets"] = result["datasets"]
        st.session_state.papers_df.at[result["id"], "time_elapsed"] = result[
            "time_elapsed"
        ]
        st.session_state.papers_df.at[result["id"], "download_link"] = annotate_pdf(
            Path(st.session_state.tmpdir.name)
            .joinpath("pdf", result["id"])
            .with_suffix(".pdf"),
            result["datasets"],
        )

        st.session_state.done_list.task_done()

        st.rerun()
    else:
        break

# Remove the temporary directory
st.session_state.tmpdir.cleanup()
