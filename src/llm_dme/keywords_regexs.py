intext_citation_regex_1 = r"\( *(?:[\w& \.,*-]+\d{4};?)+ *\)"
intext_citation_regex_2 = r" \w+ et\.? al\."
inside_bracket_regex = r"\((.*?)\)"

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
