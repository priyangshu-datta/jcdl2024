intext_citation_regex_1 = r"\( *(?:[\w& \.,*-]+\d{4};?)+ *\)"
intext_citation_regex_2 = r" \w+ et\.? al\."
inside_bracket_regex = r"\((.*?)\)"

reduce_sentence_space_keywords = [
    r"data(set|base)",
    r"anal(ytics|ysis)",
    r"resear(ch|ch paper)",
    r"stud(y|ies?)",
    r"exper(iment|iments?)",
    r"method(ology|ologies?)",
    r"collect(ion|ions?)",
    r"sampl(e|ing)",
    r"variabl(e|es?)",
    r"observ(ation|ations?)",
    r"surve(y|ys?)",
    r"popul(ation|ations?)",
    r"repositor(y|ies?)",
    r"databas(e|es?)",
    r"sourc(e|es?)",
    r"raw data",
    r"secondar(y|ies?)",
    r"primar(y|ies?)",
    r"min(e|ing)",
    r"proces(s|sing)",
    r"clean(ing|)",
    r"manipul(ation|ations?)",
    r"integrat(e|ion)",
    r"aggregat(e|ion)",
    r"visualiz(e|ation)",
    r"interpret(ation|ations?)",
    r"(used|employed|utilized) for (analysis|modeling|evaluation|research)",
    r"(trained|experimented) on",
    r"analy(zed|sis) (data|dataset)",
    r"(examined|derived|investigated|explored) (data|dataset)",
    r"(employed|modeled) with (data|dataset)",
    r"(evaluated|tested|compared) on",
    r"(referenced|applied) (dataset|data)",
    r"(accessed|reviewed) (data|dataset) from",
    r"data(-|\s)?set",
    r"task",
    r"challenge",
    r"(knowledge|data)\s*base",
    r"benchmark",
    r"(experiment|train|performance)[\sa-zA-Z0-9]+on",
    r"corpus",
    r"class",
    r"(train|test)[\sa-zA-Z0-9]+(set)?",
    r"evaluat(ed|ion)",
]

semantic_search_query = [
    "Data used in the study",
    "Dataset utilized for research",
    "Data collection methods",
    "Datasets examined in the paper",
    "Datasets referenced in the research",
    "Data sources investigated",
    "Dataset mentioned in the study",
    "Data utilized for analysis",
    "Data collection procedures",
    "Dataset discussed in the paper",
    "Data sources utilized",
    "Data sources referenced in the paper",
    "Datasets employed for investigation",
    "Datasets used as benchmarks",
    "Results of challenge",
    "Other datasets are",
    "Another dataset is"
]

prompt_LLM = """Extract all named datasets used or mentioned in the provided passages from a research paper as it is.
Do not change or modify the extracted dataset.
Please ensure that the output is in csv format and that only datasets with explicit names are included from the passages.
For clarity, a dataset refers to a collection of organized data points or records that serve a specific purpose.
Datasets are commonly utilized in various fields such as science, research, machine learning, statistics, economics, and more.
They can be structured or unstructured and are often referenced in research papers to support findings, validate hypotheses, or provide evidence for arguments.
Datasets may be explicitly mentioned within the passages, such as "We utilize the <Dataset> collected from <Source> for our analysis." or "The <Dataset> provided by <Provider> contains valuable information for our research."
Additionally, datasets can be constructed from other datasets through aggregation, transformation, or combination processes.
For instance, "We constructed our dataset by merging data from multiple sources, including <Dataset1> and <Dataset2>."
In some cases, the word "dataset" may be implicit, and datasets may be referred to by other terms such as "data collection", "data source", or "data repository".
Datasets are NOT methods. Methods are something which is applied. Datasets are used on methods. So, extract datasets and ignore methods.
Ensure that the extraction process focuses on identifying datasets with specific names and excludes general descriptions of data sources or collections. Datasets are alphanumeric words that may not have any meaning."""
