from datetime import datetime, date

def parse_mail_date(date_str: str) -> date:
    """
    Extracts date from '24.12.25 um 07:11 Uhr'
    """
    raw_date = date_str.split(" um ")[0]
    return datetime.strptime(raw_date, "%d.%m.%y").date()

def parse_german_mail_date(title: str) -> date:
    """
    Example:
        pass
    'Donnerstag, den 25.12.2025 um 10:25 Uhr'
    """
    raw = title.split(" den ")[1].split(" um ")[0]
    return datetime.strptime(raw, "%d.%m.%Y").date()