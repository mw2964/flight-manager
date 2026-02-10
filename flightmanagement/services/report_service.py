import pandas as pd
from prettytable import PrettyTable, TableStyle, ALL, NONE
from flightmanagement.services.service_utils import format_table
from flightmanagement.repositories.report_repository import ReportRepository

class ReportService:

    def __init__(self, conn):
        self.conn = conn
        self._report_repository = ReportRepository(self.conn)

    def pilot_hours_report(self) -> str:
        data = self._report_repository.pilot_flight_hours_summary()
        df = pd.json_normalize(data)
        return self._get_pilot_hours_view(df)
    
    def flight_statistics_report(self) -> str:
        data = self._report_repository.flight_statistics()
        df = pd.json_normalize(data)
        return self._get_flight_statistics_view(df)
    
    def aircraft_statistics_report(self) -> str:
        data = self._report_repository.aircraft_statistics()
        df = pd.json_normalize(data)
        return self._get_aircraft_statistics_view(df)
    
    def _get_pilot_hours_view(self, df) -> str:
                
        # Initialise the table
        table = PrettyTable([
            "Staff member ID",
            "Pilot",
            "Year",
            "Month",
            "Flight hours logged",
            "Total flights",
            "Flights as captain",
            "Flights as first officer",
            "Flights as relief pilot"
            ],
        )
        
        # Populate table rows
        for i, row in df.iterrows():
            table.add_row([
                row["staff_member_id"],
                row["pilot_name"],
                row["year"],
                row["month"],
                self._zero_to_blank(row["flight_hours_logged"]),
                self._zero_to_blank(row["total_flights"]),
                self._zero_to_blank(row["flights_as_captain"]),
                self._zero_to_blank(row["flights_as_first_officer"]),
                self._zero_to_blank(row["flights_as_relief"])
            ])
        return format_table(table)

    def _get_flight_statistics_view(self, df) -> str:
                
        # Initialise the table
        table = PrettyTable([
            "Year",
            "Month",
            "Completed flights",
            "Ave. dept. delay (mins)",
            "Min. dept. delay (mins)",
            "Max. dept. delay (mins)",
            "Ave. arr. delay (mins)",
            "Min. arr. delay (mins)",
            "Max. arr. delay (mins)"
            ],
        )
        
        # Populate table rows
        for i, row in df.iterrows():
            table.add_row([
                row["year"],
                row["month"],
                row["total_flights"],
                row["avg_departure_delay"],
                row["min_departure_delay"],
                row["max_departure_delay"],
                row["avg_arrival_delay"],
                row["min_arrival_delay"],
                row["max_arrival_delay"]
            ])
        return format_table(table)

    def _get_aircraft_statistics_view(self, df) -> str:
                
        # Initialise the table
        table = PrettyTable([
            "Aircraft",
            "Status",
            "Type",
            "Year",
            "Month",
            "Flights (completed)",
            "Flights (in progress)",
            "Flights (scheduled)"
            ],
        )
        
        # Populate table rows
        for i, row in df.iterrows():
            table.add_row([
                row["aircraft_registration"],
                row["aircraft_status"],
                row["aircraft_type"],
                row["year"],
                row["month"],
                self._zero_to_blank(row["completed_flights"]),
                self._zero_to_blank(row["in_progress_flights"]),
                self._zero_to_blank(row["scheduled_flights"])
            ])
        return format_table(table)


    def _zero_to_blank(self, value) -> str:
        return '' if value == 0 else value