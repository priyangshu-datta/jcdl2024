import re

import pydash as py_


def sub_ci(x, y):
    return py_.partial(re.sub, x, y, flags=re.I)


def sub_cs(x, y):
    return py_.partial(re.sub, x, y)


emoticons = r"\(>\.>\)|\(\^\.\^ゞ\)|\(\^_\^\)Y|:\-\)|;\-@|;\-\^|\(>\.<\)\(\^\.\^\)|\(\^_\-\)/\~\~|:\^|;\(|\(\^_\^\)/|\(ToT\)|:\-\^|\(\^\^ゞ|:\-=|:\-\#|;\-\[|\(>_>\)|:\-D|\(>\.<\)|\(\^o\^\)丿|:\-\.|:P|\(\^_\^\)\-☆|\(\^_\^\)w|;\\|:\-o|;\-C|;\-S|\(\^_\^\)v|:\-C|\(>\.<\)b|\(\*_\*\)|\(\-_\-;\)|;P|;=|\(\^_\-\)b|\(\^o\^\)|:\-P|:\#|\(\*\^\.\^\*\)|>:\[|\(\^_\-\)/\~|:\$|\(\^ω\^\)|:\-\{|:'\-\(|\(\^_\-\)\-☆|\(\-_\-\)|x\-\)|:\-X|:X|\(\*O\*\)|\(\*\^_\^\*\)|\(<_<\)|\(ーー;\)|;\-\#|:\*|;\-P|;\-!|:@|\(\^_\-\)Y|:/|\(\^_\-\)W|:\-0|\(\~_\~\)|;/|:!|;\-D|X\-\)|;\-/|;\-=|\(@_@\)|\(°\~°\)|\(\^_\^メ\)|:'\(|8\-\)|\(°u°\)|;\-\(|:\-\(|:\\|:D|;\-\\|\(>_<\)|\(\^ε\^\)|\(\^_\^\)b|:O|\(\^з\^\)|:\-\&|:=|O:\-\)|\(\^\.\^\)|:\-!|;'\-\)|\('\-'\)|\(\._\.\)|:\-<|;O|\(\^人\^\)|\(\^_\^\)|\(°\-°\)|:'\)|;\-\)|\(\^\-\^\)|;\-\$|\(\^\-\^\)b|\(,_,\)|\(\^_\-\)w|;\-\&|;D|:\-\||\(°_°\)|:S|:\-\\|>:D|;\-\{|\(\^\.\^\)y|\(\^_\-\)d|\(°\.°\)|\(\^_\^\)/\~|:\-\[|:\-/|\(\^_\^\*\)|:\&|;\-<|;'\)|:\)|;\)|;\*|\(\^_\-\)|:\-O|;'\-\(|:\-S|;\-O|:\(|B\-\)|\(\~_\^\)|;@|\(\^\-\^ゝ゛\)|\(\^_\^\)W|;\^|;S|\(°o°\)|\(\^O\^\)|\(\*o\*\)|\(>﹏<\)|;\||;\&|\(\^_\^\)/\~\~|:\||>:\)|\(\^_\-\)/|:\-\*|0:\-\)|;\$|;!|;\-\||;\#|\(\^_\^'\)|:\-\$|:\-@|\(≧∇≦\)|\(T_T\)|\(\*\^0\^\*\)|;\-\*"
abbr_to_slug_cs = {
    r"([A-Z][a-z]+)\.(?: ?(\d+) ?\.( [A-Z]))": r"\1[dot] \2[dot] \3",  # Fig. 6. The | Fig. 6.ctct
    # r"([A-Z][a-z]+) ?(\d+)\. ?( [A-Z])": r"\1 \2[dot] \3", # Fig 12. Fxdswawef
    r"([A-Z][a-z]+)\.": r"\1[dot]",  # Sentence with one word that starts with captial letter.
}
abbr_to_slug_ci = {
    r"et\.? al\.": "[etal]",
    r"vs\.": "[vs]",
    r"etc\.": "[etc]",
    r"Eq\.": "[Eq]",
}
slug_to_abbr = {
    r"\[dot\]": ".",
    r"\[etc\]": "etc.",
    r"\[vs\]": "vs.",
    r"\[fig\]": "fig",
    r"\[tab\]": "tab",
    r"\[ie\]": "i.e.",
    r"\[sec\]": "sec.",
    r"\[eq\]": "eq.",
    r"\[eg\]": "e.g.",
    r"\[ellipsis\]": "...",
    r"\[aka\]": "a.k.a.",
    r"\[etal\]": "et al.",
}
general = [
    r"\( *(?:[a-zA-Z_& \.,*-]+\d{4};?)+ *\)",  # citations (Asic et al., 1234)
    r" ?\[\d+( ?, ?\d+)*\]( ?,? ?\[\d+( ?, ?\d+)*\])*",  # citations [1,2]; [1]
    r"\(\d+\)( ?, ?\(\d+\))*",  # equation numbers (1), (2)
    r"[αβγδεζηθικλμνξοπρστυφχψωΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ]",
]


def utf_to_ascii(text: str):
    return text.encode("ascii", "ignore").decode("utf-8")


def intermediate_text_processor(text: str) -> str:
    return py_.flow(
        py_.deburr,
        utf_to_ascii,
        sub_ci(
            r"((([A-Za-z]{3,9}:(?:\/\/)?)(?:[-;:&=\+\$,\w]+@)?[A-Za-z0-9.-]+|(?:www.|[-;:&=\+\$,\w]+@)[A-Za-z0-9.-]+)((?:\/[\+~%\/.\w\-_]*)?\??(?:[-\+=&;%@.\w_]*)#?(?:[.\!\/\\w]*))?)",
            "",
        ),
        lambda x: py_.reduce_(
            py_.chain(re.findall(r"\b(?:[a-zA-Z]+\.){1,}[a-zA-Z]\.", x))
            .apply(set)
            .map_(lambda x: (re.sub(r"\.", r"\.", x), re.sub(r"\.", "[dot]", x)))
            .from_pairs()
            .value()
            .items(),
            lambda p, c: re.sub(c[0], c[1], p),
            x,
        ),  # a.k.a. i.i.d. e.g. i.e.
        *py_.map_(general, lambda x: sub_ci(x, "")),
        sub_ci(emoticons, ""),
        sub_ci(r",\. ([A-Z0-9])", r". \1"),  # cwercwer,. The -> cwercwer. The
        sub_ci(r",\. ?([a-z0-9])", r", \1"),  # cwercwer,. cewrc -> cwercwer, cwerc
        sub_ci(r"(\w+)@(\w+)\.(\w+)", r"\1@\2[dot]"),
        sub_ci(r"[\"'] *(.*)([\.\!\?]) *[\"']", r'"\1\"\2'),
        sub_ci(r" *([\.,:])", r"\1"),
        sub_ci(r"\.{3}", "[ellipsis]"),
        sub_ci(r"\.{2}", "."),
        sub_ci(r"\.{4,}", ""),
        sub_ci(r"(?:, ?){2,}", ""),
        sub_ci(r"([^ \(\.,])\(", r"\1 ("),
        sub_ci(r"\)([^ \)\.,:])", r") \1"),
        sub_ci(r"\/{2,} ", ""),
        sub_ci(r"(\d+)(?:\.(\d+))+", r"\1[dot]\2"),
        *py_.map_(abbr_to_slug_cs.items(), lambda x: sub_cs(x[0], x[1])),
        *py_.map_(abbr_to_slug_ci.items(), lambda x: sub_ci(x[0], x[1])),
        sub_ci(r"(?:\[dot] ){2,}", "[dot]"),
        sub_ci(
            r"arXiv:(\d+)\.(\w+) ?(?:\[(\w+)\.(\w+)\])?", r"arXiv:\1[dot]\2 [\3[dot]\4]"
        ),
        sub_ci(r"\(([^\)]*?)\.([^\)]*?)\)", r"(\1[dot]\2)"),
        sub_ci(r"\[([^\]]*?)\.([^\]]*?)\]", r"[\1[dot]\2]"),
        sub_ci(r"\{([^\}]*?)\.([^\}]*?)\}", r"{\1[dot]\2}"),
        sub_ci(r"\"([^\"]*?)\.([^\"]*?)\"", r"\"\1[dot]\2\""),
        sub_ci(r"\'([^\']*?)\.([^\']*?)\'", r"'\1[dot]\2'"),
        sub_ci(r"\b\d+(\.\d+)*", lambda match: match.group(0).replace(".", "[dot]")),
        py_.strings.clean,
        sub_ci(r" \)", ")"),
        sub_ci(r"\( ", "("),
    )(  # type: ignore
        text
    )


def intermediate_text_splitter(text: str) -> list[str]:
    return py_.flow(
        lambda text: text[:-5] + "." if text[-5:] == "[dot]" else text,
        py_.partial(re.findall, r"[^\.\!\?]*[\.\!\?]"),
        # lambda _text_arr: py_.tap(_text_arr, lambda x: print(x[-1])),
        lambda _text_arr: py_.map_(_text_arr, lambda _: _.strip()),
        # lambda x: py_.tap(x, lambda _: print(' '.join(_)+"\n\n"+text+"\n\n")),
        py_.partial(py_.reject, predicate=lambda x: len(x.split(" ")) < 4),
        *py_.map_(
            slug_to_abbr.items(), lambda x: lambda y: py_.map_(y, sub_ci(x[0], x[1]))
        ),
        lambda x: py_.map_(x, lambda y: py_.strings.trim(y)),
    )(text)  # type: ignore


def sentence_splitter(text: str) -> list[str]:
    return py_.flow(intermediate_text_processor, intermediate_text_splitter)(text)
