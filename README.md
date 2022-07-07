# CalendrierCollecteDechets

This tool exports an ICS file with all the events extracted from the calendar of garbage collection provided by the commune of Frisange in Luxembourg.
The resulting file can be imported in Google Calendar, Apple Calendar, etc.

The calendar PDFs can be found at: https://frisange.lu/vivre-a-frisange/environnement/collecte-des-dechets/

## Installation

```
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

## Execution example:

`python create_calendar.py --url https://frisange.lu/wp-content/uploads/2022/05/Sidor_calendrier-ecologique_juillet-decembre-2022.pdf`