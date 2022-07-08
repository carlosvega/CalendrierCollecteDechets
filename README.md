<img align="right" src="https://user-images.githubusercontent.com/1414389/177890722-7a44e595-6e3a-42d4-b6de-55ccc1419680.png" width="500"/>


# CalendrierCollecteDechets

This tool exports an ICS file with all the events extracted from the calendar of garbage collection provided by the commune of Frisange in Luxembourg.
The resulting file can be imported in Google Calendar, Apple Calendar, etc.

The calendar PDFs can be found at: https://frisange.lu/vivre-a-frisange/environnement/collecte-des-dechets/

By default the events are created for the day before collection. Use `--same-day` option to override this behaviour.

## Installation

```
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

## Execution examples:

### Use path to PDF file

`python create_calendar.py --pdf Sidor_calendrier-ecologique_juillet-decembre-2022.pdf`

### Use URL of the PDF

`python create_calendar.py --url https://frisange.lu/wp-content/uploads/2022/05/Sidor_calendrier-ecologique_juillet-decembre-2022.pdf`
