import pandas as pd
from prettytable import PrettyTable, TableStyle, ALL, NONE

from flightmanagement.repositories.flight_repository import FlightRepository

class ReportService:

    def __init__(self, conn):
        self.conn = conn
        self._flight_repository = FlightRepository(self.conn)

    def search_flights(self, search_text: str | None):
        data = self._flight_repository.get_flight_summary_list()
        df = pd.json_normalize(data)

        if search_text is not None:
            mask = df.apply(lambda row: row.astype(str).str.contains(search_text, case=False).any(), axis=1)

            # Filtered dataframe
            filtered_df = df[mask]
            print(self.get_results_view(filtered_df))
        else:
            print(self.get_results_view(df))
    
    def get_results_view(self, df) -> str:
                
        # Initialise the table
        table = PrettyTable([
            "ID",
            "Flight no.",
            "Aircraft",
            "From",
            "To",
            "Pilots",
            "Dept. (scheduled)",
            "Arr. (scheduled)",
            "Status"
            ],
        )        
        
        # Populate table rows
        for i, row in df.iterrows():

            # Format and combine some fields for readability and to reduce table width
            origin = f"{row['origin_location']}\n({row['origin_town_or_city']})"
            destination = f"{row['destination_location']}\n({row['destination_town_or_city']})"
            pilots = f"{row['captain_name']} (c)\n{row['first_officer_name']} (fo)\n{row['relief_pilots'].replace(", ", "\n")}"
            departure = f"{row['scheduled_departure'].replace(' ', '\n')}"
            arrival = f"{row['scheduled_arrival'].replace(' ', '\n')}"

            table.add_row([
                row["flight_id"],
                row["flight_number"],
                row["aircraft_registration"],
                origin,
                destination,
                pilots,
                departure,
                arrival,
                row['status']
            ])

        # Set table formatting
        table.set_style(TableStyle.SINGLE_BORDER)
        table.align = "l"
        table.max_width = 20
        table.hrules = ALL
        table.vrules = NONE
        
        indented_table = ""
        for row in table.get_string().split("\n"):
            indented_table += (" " * 5) + row + "\n"
        
        return str(indented_table)