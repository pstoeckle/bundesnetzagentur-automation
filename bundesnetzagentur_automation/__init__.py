"""Module to automate the interaction with the Bundesnetzagentur."""

from __future__ import annotations

from json import dumps as json_dumps
from pathlib import Path  # noqa: TC003
from re import compile as re_compile
from typing import Annotated

from helium import TAB
from helium import ComboBox
from helium import click
from helium import kill_browser
from helium import press
from helium import select
from helium import start_chrome
from helium import write
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic_yaml import parse_yaml_file_as
from typer import Argument
from typer import Option
from typer import Typer
from typer import pause

app = Typer()

_LINK = re_compile(
    r"([-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*))"
)


class Configuration(BaseModel):
    """Configuration for the Bundesnetzagentur automation."""

    phone: Annotated[
        str,
        Field(
            description="The phone number the phishing SMS was sent to.",
            pattern=r"^\+?[0-9]{1,3}[-\s]?[0-9]{1,14}$",
        ),
    ]
    title: Annotated[
        str | None,
        Field(
            description="The academic title of the person reporting the phishing SMS.",
            default=None,
        ),
    ]
    name: Annotated[
        str,
        Field(
            description="The last name of the person reporting the phishing SMS."
        ),
    ]
    firstname: Annotated[
        str,
        Field(
            description="The first name of the person reporting the phishing SMS."
        ),
    ]
    street: Annotated[
        str,
        Field(
            description="The street of the person reporting the phishing SMS."
        ),
    ]
    number: Annotated[
        str,
        Field(
            description="The house number of the person reporting the "
            "phishing SMS."
        ),
    ]
    zip: Annotated[
        str,
        Field(
            description="The postal code of the person reporting the "
            "phishing SMS.",
            pattern=r"^\d{5}$",
        ),
    ]
    city: Annotated[
        str,
        Field(description="The city of the person reporting the phishing SMS."),
    ]
    email: Annotated[
        str,
        Field(
            description="The email address of the person reporting the "
            "phishing SMS.",
            pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        ),
    ]

    model_config = ConfigDict(extra="forbid", frozen=True)


@app.command()
def report_sms_phishing(  # noqa: PLR0913
    configration_file: Path = Argument(..., help=""),  # noqa: B008
    phishing_sms_number: str = Argument(..., help="The SMS number."),
    text_file: Path = Argument(..., help="", dir_okay=False, exists=True),  # noqa: B008
    date_received: str = Argument(..., help=""),
    clean_up: bool = Option(False, "--clean-up", "-c", is_flag=True),  # noqa: FBT001, FBT003
    receiver_sms_number: str | None = Option(
        None, "--receiver-sms", "-r", help="The SMS number."
    ),
) -> None:
    """Report SMS phishing."""
    config = parse_yaml_file_as(Configuration, configration_file)
    own_sms_number = (
        config.phone if receiver_sms_number is None else receiver_sms_number
    )

    start_chrome(
        "https://www.bundesnetzagentur.de/_tools/RumitelStart/Form02SMS/node.html"
    )

    # Page 1
    click("SMS (Short Message Service) -Dienst")
    click("Nein")
    click("eine Absendernummer")
    press(TAB)
    write(phishing_sms_number)
    press(TAB)
    press(TAB)
    sms_text = text_file.read_text()
    current_match = _LINK.search(sms_text)
    if current_match is not None:
        write(current_match.group(1))
    press(TAB)
    write(own_sms_number)
    press(TAB)

    write(sms_text)
    press(TAB)
    write(date_received)
    click("Weiter")

    # Page 2
    if config.title is not None:
        select(ComboBox("Titel:"), config.title)

    click("Name:*")
    write(config.name)
    click("Vorname:*")
    write(config.firstname)
    click("Straße:*")
    write(config.street)
    click("Hausnummer:*")
    write(config.number)
    click("Postleitzahl:*")
    write(config.zip)
    click("Ort:*")
    write(config.city)
    click("E-Mail Adresse:*")
    write(config.email)
    click("Wiederholung der E-Mail Adresse:*")
    write(config.email)
    click("Weiter")

    # Page 3
    print("Enter captcha")
    pause()

    kill_browser()
    if clean_up:
        text_file.unlink()


from typer import Option


@app.command()
def generate_json_schema(
    output_file: Path = Option(  # noqa: B008
        "configuration_schema.json",
        dir_okay=False,
        writable=True,
        help="The output file for the JSON schema of the configuration.",
    ),
) -> None:
    """Generate JSON schema for the configuration."""
    config = Configuration.model_json_schema()
    with output_file.open("w", encoding="utf-8") as file:
        file.write(json_dumps(config, indent=4))
    print(f"JSON schema written to {output_file}")


if __name__ == "__main__":
    app()
