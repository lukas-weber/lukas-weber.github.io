import jinja2
import yaml
import re
import copy

jinja_latex_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader("./"),
    block_start_string="\B{",
    block_end_string="}",
    variable_start_string="\V{",
    variable_end_string="}",
    comment_start_string="\#{",
    comment_end_string="}",
    line_statement_prefix="%%",
    line_comment_prefix="%#",
    trim_blocks=True,
    autoescape=False,
)


def texify_mathml(text: str) -> str:
    text2 = re.sub(r"<mml:mn>(\d+)</mml:mn>", r"\\textsubscript{\1}", text)
    return re.sub("</?mml:.*?>", "", text2)


def generate(site_data: dict, cv_file: str, template_file: str, output_file: str):

    with open(cv_file, "r") as f:
        cv_data = yaml.safe_load(f)

    data = copy.deepcopy({**site_data, **cv_data})

    for work in data["works"]:
        work["title"] = texify_mathml(work["title"])

    subs = jinja_latex_env.get_template(template_file).render(**data)

    with open(output_file, "w") as f:
        f.write(subs)
