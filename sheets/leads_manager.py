import logging
import gspread
from config import GOOGLE_SHEET_URL, get_google_credentials

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

LEADS_SHEET_NAME = "Leads"
LEADS_COLUMNS = ["Tarih", "Adı", "Soyadı", "Telefon Numarası", "Email Adresi", "Şehir"]


class LeadsManager:
    def __init__(self):
        self.worksheet = None
        self._connect()

    def _connect(self):
        creds = get_google_credentials(SCOPES)
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_url(GOOGLE_SHEET_URL)
        try:
            self.worksheet = spreadsheet.worksheet(LEADS_SHEET_NAME)
        except gspread.exceptions.WorksheetNotFound:
            self.worksheet = spreadsheet.add_worksheet(
                title=LEADS_SHEET_NAME, rows=5000, cols=6
            )
        self._ensure_headers()

    def _ensure_headers(self):
        try:
            first_row = self.worksheet.row_values(1)
            if not first_row or first_row[0] != LEADS_COLUMNS[0]:
                self.worksheet.update("A1:F1", [LEADS_COLUMNS])
        except Exception as e:
            logger.warning(f"Leads baslik kontrol hatasi: {e}")

    def append_leads(self, leads: list) -> int:
        if not leads:
            return 0
        try:
            email_col = self.worksheet.col_values(5)  # E = Email Adresi
            existing_emails = {e.lower().strip() for e in email_col[1:] if e.strip()}
        except Exception:
            existing_emails = set()

        rows = []
        for lead in leads:
            email = lead.get("email", "").lower().strip()
            if email and email in existing_emails:
                continue
            if email:
                existing_emails.add(email)
            rows.append([
                lead.get("date", ""),
                lead.get("first_name", ""),
                lead.get("last_name", ""),
                lead.get("phone", ""),
                lead.get("email", ""),
                lead.get("city", ""),
            ])

        if rows:
            self.worksheet.append_rows(rows, value_input_option="USER_ENTERED")
        return len(rows)

    def get_all_leads(self) -> list:
        try:
            values = self.worksheet.get_all_values()
        except Exception as e:
            logger.error(f"Leads okuma hatasi: {e}")
            return []
        if len(values) < 2:
            return []
        result = []
        for i, row in enumerate(values[1:], 2):
            result.append({
                "id": f"lead_{i}",
                "date":       row[0] if len(row) > 0 else "",
                "first_name": row[1] if len(row) > 1 else "",
                "last_name":  row[2] if len(row) > 2 else "",
                "phone":      row[3] if len(row) > 3 else "",
                "email":      row[4] if len(row) > 4 else "",
                "city":       row[5] if len(row) > 5 else "",
                "sheet_row":  i,
            })
        return result

    def delete_rows(self, row_indices: list) -> int:
        """Delete rows by sheet row number (1-based). Must delete in reverse order."""
        if not row_indices:
            return 0
        for row_idx in sorted(row_indices, reverse=True):
            try:
                self.worksheet.delete_rows(row_idx)
            except Exception as e:
                logger.error(f"Lead satir silme hatasi (satir {row_idx}): {e}")
        return len(row_indices)
