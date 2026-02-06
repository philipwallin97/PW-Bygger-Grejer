from __future__ import annotations

import html
import os
import re
from pathlib import Path


def prompt_non_empty(prompt: str) -> str:
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Fältet får inte vara tomt.")


def prompt_int(prompt: str, min_value: int = 0) -> int:
    while True:
        raw = input(prompt).strip()
        if not raw and min_value == 0:
            return 0
        try:
            value = int(raw)
        except ValueError:
            print("Skriv ett heltal.")
            continue
        if value < min_value:
            print(f"Talet måste vara minst {min_value}.")
            continue
        return value


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = value.replace("å", "a").replace("ä", "a").replace("ö", "o")
    value = re.sub(r"\s+", "_", value)
    value = re.sub(r"[^a-z0-9_]+", "", value)
    value = re.sub(r"_+", "_", value)
    return value.strip("_")


def confirm(prompt: str) -> bool:
    return input(f"{prompt} (j/n): ").strip().lower() in {"j", "ja", "y", "yes"}


def build_description_paragraphs(count: int) -> list[str]:
    paragraphs = []
    for idx in range(1, count + 1):
        text = prompt_non_empty(f"Beskrivningsrad {idx}: ")
        paragraphs.append(text)
    return paragraphs


def build_steps_with_images(step_count: int) -> list[list[str]]:
    steps: list[list[str]] = []
    for step_index in range(1, step_count + 1):
        print(f"\nSteg {step_index}")
        paragraph_count = prompt_int("Antal stycken i steget: ", min_value=1)
        step_paragraphs = []
        for p_index in range(1, paragraph_count + 1):
            step_paragraphs.append(prompt_non_empty(f"  Text {p_index}: "))
        steps.append(step_paragraphs)
    return steps


def build_centered_steps(paragraph_count: int) -> list[str]:
    paragraphs = []
    for idx in range(1, paragraph_count + 1):
        paragraphs.append(prompt_non_empty(f"Stegtext {idx}: "))
    return paragraphs


def render_html(
    slug: str,
    title: str,
    description_paragraphs: list[str],
    steps_mode: str,
    step_paragraphs: list[str] | None,
    step_groups: list[list[str]] | None,
) -> str:
    safe_title = html.escape(title)
    safe_description = " ".join(p.strip() for p in description_paragraphs if p.strip())
    safe_description_attr = html.escape(safe_description)

    description_html = "\n".join(
        f"                <p>{html.escape(p)}</p>" for p in description_paragraphs
    )

    steps_html = ""
    if steps_mode == "images" and step_groups is not None:
        rows = []
        for index, paragraphs in enumerate(step_groups, start=1):
            paragraphs_html = "\n".join(
                f"                        <p>{html.escape(p)}</p>" for p in paragraphs
            )
            rows.append(
                "                <div class=\"step-row\">\n"
                f"                    <img src=\"../images/projects/{slug}/step_{index}.jpg\" alt=\"Steg {index}\">\n"
                "                    <div class=\"step-text\">\n"
                f"{paragraphs_html}\n"
                "                    </div>\n"
                "                </div>"
            )
        steps_html = "\n\n".join(rows)
    elif steps_mode == "centered" and step_paragraphs is not None:
        paragraphs_html = "\n".join(
            f"                <p>{html.escape(p)}</p>" for p in step_paragraphs
        )
        steps_html = paragraphs_html

    steps_class = "project-steps"
    if steps_mode == "centered":
        steps_class += " centered-text"

    html_output = f"""<!DOCTYPE html>
<html lang=\"sv\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">    
    <meta name=\"description\" content=\"{safe_description_attr}\">        
    <meta property=\"og:image\" content=\"https://philipwallin.pw/images/projects/{slug}/main_2.jpg\">    
    <title>{safe_title} - Philip Wallin</title>    
    <link rel=\"icon\" type=\"image/x-icon\" href=\"../images/favicon.ico\">    
    <link rel=\"stylesheet\" href=\"../style.css\">
</head>
<body>
    <nav>
        <div class=\"logo\">
            <a href=\"../index.html\"><img src=\"../images/logo.png\" alt=\"Logo\"></a>
        </div>
        <ul class=\"nav-links\">
            <li><a href=\"../index.html\">Projekt</a></li>
            <li><a href=\"../om_mig.html\">Om mig</a></li>
        </ul>
    </nav>
    
    <section class=\"project-detail\">
        <h1>{safe_title}</h1>
        <div class=\"project-content\">
            <div class=\"project-description\">
{description_html}
            </div>
            <div class=\"project-images\">
                <img src=\"../images/projects/{slug}/main_1.jpg\" alt=\"{safe_title} bild 1\">
                <img src=\"../images/projects/{slug}/main_2.jpg\" alt=\"{safe_title} bild 2\">
                <img src=\"../images/projects/{slug}/main_3.jpg\" alt=\"{safe_title} bild 3\">
            </div>
            
            <h2>Hur den gjordes</h2>
            
            <div class=\"{steps_class}\">
{steps_html}
            </div>
        </div>
    </section>
    <!-- Cloudflare Web Analytics --><script defer src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{{"token": "f9bdf25e4d7c4efc8e16c66a618ee4c4"}}'></script><!-- End Cloudflare Web Analytics -->
</body>
</html>
"""
    return html_output


def main() -> None:
    repo_root = Path(__file__).resolve().parent
    projects_dir = repo_root / "projects"
    images_dir = repo_root / "images" / "projects"

    raw_slug = prompt_non_empty("Projektets namn (för fil/folder, t.ex. vaglampa): ")
    slug = slugify(raw_slug)
    if not slug:
        print("Kunde inte skapa ett giltigt projektnamn. Försök igen.")
        return

    print(f"Föreslaget projektnamn: {slug}")
    if not confirm("Vill du använda detta namn?"):
        print("Avbruten.")
        return

    html_path = projects_dir / f"{slug}.html"
    images_path = images_dir / slug

    if html_path.exists() and not confirm(f"Filen {html_path.name} finns redan. Skriv över?"):
        print("Avbruten.")
        return
    if images_path.exists() and not confirm(f"Mappen images/projects/{slug} finns redan. Fortsätt?"):
        print("Avbruten.")
        return

    title = prompt_non_empty("Titel: ")
    description_count = prompt_int("Antal beskrivningsrader: ", min_value=1)
    description_paragraphs = build_description_paragraphs(description_count)

    print("\nHur ska steg-sektionen se ut?")
    print("1) Steg med bilder")
    print("2) Bara text (centered-text)")
    mode_choice = ""
    while mode_choice not in {"1", "2"}:
        mode_choice = input("Välj 1 eller 2: ").strip()

    steps_mode = "images" if mode_choice == "1" else "centered"
    step_groups = None
    step_paragraphs = None

    if steps_mode == "images":
        step_count = prompt_int("Antal steg: ", min_value=1)
        step_groups = build_steps_with_images(step_count)
    else:
        step_paragraph_count = prompt_int("Antal textstycken i steg-sektionen: ", min_value=1)
        step_paragraphs = build_centered_steps(step_paragraph_count)

    html_output = render_html(
        slug=slug,
        title=title,
        description_paragraphs=description_paragraphs,
        steps_mode=steps_mode,
        step_paragraphs=step_paragraphs,
        step_groups=step_groups,
    )

    projects_dir.mkdir(parents=True, exist_ok=True)
    images_path.mkdir(parents=True, exist_ok=True)

    html_path.write_text(html_output, encoding="utf-8")

    print("\nKlart!")
    print(f"Skapade: {html_path}")
    print(f"Skapade mapp: {images_path}")
    print("Lägg till bilderna main_1.jpg, main_2.jpg, main_3.jpg och ev. step_#.jpg i mappen.")


if __name__ == "__main__":
    main()
