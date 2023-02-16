import jinja2


def generate(site_data: dict, output_file: str):
    template_file = "templates/website.html"

    subs = (
        jinja2.Environment(loader=jinja2.FileSystemLoader("./"))
        .get_template(template_file)
        .render(**site_data)
    )

    with open(output_file, "w") as f:
        f.write(subs)
