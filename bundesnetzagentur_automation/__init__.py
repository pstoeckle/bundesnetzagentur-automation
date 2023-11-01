from importlib.resources import read_text
from json import loads
from os import unlink
from pathlib import Path
from re import compile as re_compile
from typing import Optional

from helium import ENTER, TAB, click, kill_browser, press, start_chrome, write
from jsonschema import validate
from typer import Argument, Option, Typer, pause

app = Typer()

_LINK = re_compile(
    r"([-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*))"
)

_CONFIGURATION_SCHEMA = loads(
    read_text("bundesnetzagentur_automation", "configuration.schema.json")
)


@app.command()
def report_sms_phishing(
    configration_file: Path = Argument(..., help=""),
    phishing_sms_number: str = Argument(..., help="The SMS number."),
    text_file: Path = Argument(..., help="", dir_okay=False, exists=True),
    date_received: str = Argument(..., help=""),
    clean_up: bool = Option(False, "--clean-up", "-c", is_flag=True),
    receiver_sms_number: Optional[str] = Option(
        None, "--receiver-sms", "-r", help="The SMS number."
    ),
) -> None:
    """
    Report SMS phishing.
    """

    config = loads(configration_file.read_text())
    validate(instance=config, schema=_CONFIGURATION_SCHEMA)
    own_sms_number = (
        config["email"] if receiver_sms_number is None else receiver_sms_number
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
    click("Name:*")
    write(config["name"])
    click("Vorname:*")
    write(config["firstname"])
    click("Straße:*")
    write(config["street"])
    click("Hausnummer:*")
    write(config["number"])
    click("Postleitzahl:*")
    write(config["zip"])
    click("Ort:*")
    write(config["city"])
    click("E-Mail Adresse:*")
    write(config["email"])
    click("Wiederholung der E-Mail Adresse:*")
    write(config["email"])
    click("Weiter")

    # Page 3
    print("Enter captcha")
    pause()

    kill_browser()
    if clean_up:
        unlink(text_file)


if __name__ == "__main__":
    app()
