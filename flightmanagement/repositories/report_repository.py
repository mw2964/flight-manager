from flightmanagement.repositories.base_repository import BaseRepository

class ReportRepository(BaseRepository):

    def __init__(self, conn):
        super().__init__(conn)

    def pilot_flight_hours_summary(self) -> list[dict]:
        rows = self._execute_fetchall(
            """
            WITH months AS (
                SELECT DISTINCT
                    strftime('%Y', effective_date) AS year,
                    strftime('%m', effective_date) AS month
                FROM flight_time_logs
                UNION
                SELECT DISTINCT
                    strftime('%Y', scheduled_departure_date) AS year,
                    strftime('%m', scheduled_departure_date) AS month
                FROM flights
                WHERE scheduled_departure_date < DATE('now')
            ),
            pilots AS (
                SELECT
                    staff_member_id,
                    first_name || ' ' || family_name AS pilot_name
                FROM
                    vw_staff_pilots
            ),
            flight_hours AS (
                SELECT
                    staff_member_id,
                    strftime('%Y', effective_date) AS year,
                    strftime('%m', effective_date) AS month,
                    SUM(flight_hours) AS total_hours
                FROM flight_time_logs
                GROUP BY staff_member_id, year, month
            ),
            captain_flights AS (
                SELECT
                    captain_id,
                    count(flight_id) AS flight_count,
                    strftime('%Y', scheduled_departure_date) AS year,
                    strftime('%m', scheduled_departure_date) AS month
                FROM flights
                    GROUP BY captain_id, year, month
            ),
            first_officer_flights AS (
                SELECT
                    first_officer_id,
                    count(flight_id) AS flight_count,
                    strftime('%Y', scheduled_departure_date) AS year,
                    strftime('%m', scheduled_departure_date) AS month
                FROM flights
                    GROUP BY first_officer_id, year, month
            ),
            relief_pilot_flights AS (
                SELECT
                    staff_member_id,
                    count(*) as flight_count,
                    strftime('%Y', f.scheduled_departure_date) AS year,
                    strftime('%m', f.scheduled_departure_date) AS month
                FROM flight_relief_pilots frp
                INNER JOIN flights f ON f.flight_id = frp.flight_id
                GROUP BY staff_member_id, year, month
            )
            SELECT
                pilots.staff_member_id,
                pilots.pilot_name,
                months.year,
                CASE months.month
                    WHEN '01' THEN 'January'
                    WHEN '02' THEN 'February'
                    WHEN '03' THEN 'March'
                    WHEN '04' THEN 'April'
                    WHEN '05' THEN 'May'
                    WHEN '06' THEN 'June'
                    WHEN '07' THEN 'July'
                    WHEN '08' THEN 'August'
                    WHEN '09' THEN 'September'
                    WHEN '10' THEN 'October'
                    WHEN '11' THEN 'November'
                    WHEN '12' THEN 'December'
                END AS month,
                round(coalesce(flight_hours.total_hours, 0), 1) AS flight_hours_logged,
                (
                    coalesce(captain_flights.flight_count, 0)
                    + coalesce(first_officer_flights.flight_count, 0)
                    + coalesce(relief_pilot_flights.flight_count, 0)
                ) AS total_flights,
                coalesce(captain_flights.flight_count, 0) AS flights_as_captain,
                coalesce(first_officer_flights.flight_count, 0) AS flights_as_first_officer,
                coalesce(relief_pilot_flights.flight_count, 0) AS flights_as_relief
            FROM months, pilots
            LEFT JOIN flight_hours ON
                flight_hours.staff_member_id = pilots.staff_member_id
                AND flight_hours.month = months.month
                AND flight_hours.year = months.year
            LEFT JOIN captain_flights ON
                captain_flights.captain_id = pilots.staff_member_id
                AND captain_flights.year = months.year
                AND captain_flights.month = months.month
            LEFT JOIN first_officer_flights ON
                first_officer_flights.first_officer_id = pilots.staff_member_id
                AND first_officer_flights.year = months.year
                AND first_officer_flights.month = months.month
            LEFT JOIN relief_pilot_flights ON
                relief_pilot_flights.staff_member_id = pilots.staff_member_id
                AND relief_pilot_flights.year = months.year
                AND relief_pilot_flights.month = months.month
            ORDER BY months.year DESC, CAST(months.month AS int) DESC
            """
        )
        return self._rows_to_dicts(rows)
    
    def flight_statistics(self) -> list[dict]:
        rows = self._execute_fetchall(
            """
            SELECT
                COUNT(flight_id) AS total_flights,
                strftime('%Y', scheduled_departure_date) AS year,
                CASE strftime('%m', scheduled_departure_date)
                    WHEN '01' THEN 'January'
                    WHEN '02' THEN 'February'
                    WHEN '03' THEN 'March'
                    WHEN '04' THEN 'April'
                    WHEN '05' THEN 'May'
                    WHEN '06' THEN 'June'
                    WHEN '07' THEN 'July'
                    WHEN '08' THEN 'August'
                    WHEN '09' THEN 'September'
                    WHEN '10' THEN 'October'
                    WHEN '11' THEN 'November'
                    WHEN '12' THEN 'December'
                END AS month,
                ROUND(
                    AVG(
                        strftime(
                            '%s',
                            confirmed_departure_date || confirmed_departure_time
                        ) - strftime(
                            '%s',
                            scheduled_departure_date || scheduled_departure_time
                        )     
                    ) / 60,
                    2
                ) AS departure_delay_minutes,
                ROUND(
                    AVG(
                        strftime(
                            '%s',
                            confirmed_arrival_date || confirmed_arrival_time
                        ) - strftime(
                            '%s',
                            scheduled_arrival_date || scheduled_arrival_time
                        )     
                    ) / 60,
                    2
                ) AS arrival_delay_minutes
            FROM flights
            WHERE flight_status = 'Arrived'
            GROUP BY year, month
            ORDER BY year DESC, CAST(strftime('%m', scheduled_departure_date) AS INTEGER) DESC
            """
        )
        return self._rows_to_dicts(rows)
    
    def aircraft_statistics(self) -> list[dict]:
        rows = self._execute_fetchall(
            """
            SELECT
                aircraft_registration,    
                strftime('%Y', scheduled_departure_date) AS year,
                CASE strftime('%m', scheduled_departure_date)
                    WHEN '01' THEN 'January'
                    WHEN '02' THEN 'February'
                    WHEN '03' THEN 'March'
                    WHEN '04' THEN 'April'
                    WHEN '05' THEN 'May'
                    WHEN '06' THEN 'June'
                    WHEN '07' THEN 'July'
                    WHEN '08' THEN 'August'
                    WHEN '09' THEN 'September'
                    WHEN '10' THEN 'October'
                    WHEN '11' THEN 'November'
                    WHEN '12' THEN 'December'
                END AS month,
                COUNT(
                    CASE
                        WHEN flight_status = 'Arrived' THEN 1
                    END
                ) AS completed_flights,
                COUNT(
                    CASE
                        WHEN flight_status <> 'Scheduled' AND flight_status <> 'Arrived' THEN 1
                    END
                ) AS in_progress_flights,
                COUNT(
                    CASE
                        WHEN flight_status = 'Scheduled' THEN 1
                    END
                ) AS scheduled_flights
            FROM vw_flight_summary
            GROUP BY year, month, aircraft_registration
            ORDER BY year DESC, CAST(strftime('%m', scheduled_departure_date) AS INTEGER) DESC, aircraft_registration
            """
        )
        return self._rows_to_dicts(rows)

    def _rows_to_dicts(self, rows: list) -> list[dict]:
        result_list = []
        for row in rows:
            result_list.append(dict(row))

        return result_list