from flightmanagement.repositories.base_repository import BaseRepository

class ReportRepository(BaseRepository):
    """
    Repository responsible for read queries across the database schema
    to retrieve and transform data for use in user reports.

    The repository relies on the BaseRepository class for connection handling,
    query execution and exception handling.
    """

    def __init__(self, conn):
        super().__init__(conn)

    def pilot_flight_hours_summary(self) -> list[dict]:
        """
        This report summarises the total flight hours, total number of flights and breakdown
        of number of flights as different pilot roles for each pilot on a month by month
        basis.

        The query is constructed by using the WITH clause to define several temporary result sets:

            1. 'months': this query generates a list of each month and year that is represented
               in EITHER the `flights` table or the `flight_time_logs` table. This ensures that
               months reflected in one but not the other are captured. The distinct year and month
               are selected from each table, and joined with a UNION to get a single
               de-duplicated result set.
            
            2. 'pilots': this query returns a row representing each pilot in the database, with
               staff_member_id and name.

            3. 'flight_hours': this aggregation query returns the sum of flight hours
               in the `flight_time_logs` table, grouped by the month and year portions
               of the effective date and the staff_member_id (representing the pilot).

            4. 'captain_flights': this aggregation query returns a count of the records
               in the `flights` table, grouped by the captain_id (again representing the
               pilot) and the year and month portions of the flight's departure date.

            5. 'first_officer_flights': this aggregation query returns a count of the records
               in the `flights` table, grouped by the first_officer_id (again representing the
               pilot) and the year and month portions of the flight's departure date.

            6. 'relief_pilot_flights': this aggregation query returns a count of the records
               in the `flight_time_logs` table, grouped by the staff_member_id (again representing the
               pilot), and joined via flight_id to the flights table in order to again group
               by the year and month portions of the related flight's departure date.
        
        The 'months' and 'pilots' result sets are then cross joined to give the Cartesian
        product of the two, resulting in one row for every unique pilot/month/year combination. This forms the backbone
        of the query, as those are the reporting groupings that we're looking for, and it ensures that
        every combination will be represented as a row even if there are no reporting metrics that
        currently apply to it.

        The other four result sets have already each been transformed into a format where the
        combination of year, month and pilot forms the unique key for each row. We can then join each
        of them to the month/pilot backbone by linking on those three fields, and therefore include
        the associated metrics on the relevant row. Using LEFT JOINs means that every month/pilot
        row remains visible even if not represented in one, several or any of the metric result sets.

        In the select portion of the main query, a CASE statement is used to convert numeric months
        to more human-readable month names. The coalesce() function is also used to replace any NULL
        values with empty strings, again for readability reasons. Descriptive names are used for the
        temporary result sets, but these are replaced by short aliases (a, b, c, d) in the main query
        to make it more readable. The month is cast to an integer in the sort statement to ensure
        numeric rather than text sorting on that field.

        Returns a list of dictionaries representing the data in each row returned by the query.
        
        """

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
            flight_hours_by_month_and_pilot AS (
                SELECT
                    staff_member_id,
                    strftime('%Y', effective_date) AS year,
                    strftime('%m', effective_date) AS month,
                    SUM(flight_hours) AS total_hours
                FROM flight_time_logs
                GROUP BY staff_member_id, year, month
            ),
            captain_flights_by_month_and_pilot AS (
                SELECT
                    captain_id,
                    count(flight_id) AS flight_count,
                    strftime('%Y', scheduled_departure_date) AS year,
                    strftime('%m', scheduled_departure_date) AS month
                FROM flights
                    GROUP BY captain_id, year, month
            ),
            first_officer_flights_by_month_and_pilot AS (
                SELECT
                    first_officer_id,
                    count(flight_id) AS flight_count,
                    strftime('%Y', scheduled_departure_date) AS year,
                    strftime('%m', scheduled_departure_date) AS month
                FROM flights
                    GROUP BY first_officer_id, year, month
            ),
            relief_pilot_flights_by_month_and_pilot AS (
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

                round(coalesce(a.total_hours, 0), 1) AS flight_hours_logged,
                (
                    coalesce(b.flight_count, 0)
                    + coalesce(c.flight_count, 0)
                    + coalesce(d.flight_count, 0)
                ) AS total_flights,

                coalesce(b.flight_count, 0) AS flights_as_captain,
                coalesce(c.flight_count, 0) AS flights_as_first_officer,
                coalesce(d.flight_count, 0) AS flights_as_relief

            FROM months, pilots
            LEFT JOIN flight_hours_by_month_and_pilot a ON
                a.staff_member_id = pilots.staff_member_id
                AND a.month = months.month
                AND a.year = months.year
            LEFT JOIN captain_flights_by_month_and_pilot b ON
                b.captain_id = pilots.staff_member_id
                AND b.year = months.year
                AND b.month = months.month
            LEFT JOIN first_officer_flights_by_month_and_pilot c ON
                c.first_officer_id = pilots.staff_member_id
                AND c.year = months.year
                AND c.month = months.month
            LEFT JOIN relief_pilot_flights_by_month_and_pilot d ON
                d.staff_member_id = pilots.staff_member_id
                AND d.year = months.year
                AND d.month = months.month
            ORDER BY months.year DESC, CAST(months.month AS INTEGER) DESC
            """
        )
        return self._rows_to_dicts(rows)
    
    def flight_statistics(self) -> list[dict]:
        """
        This report summarises on a monthly basis metrics about differences between confirmed departures
        and arrivals against the scheduled times.

        The query is constructed firstly by using the WITH clause to create a temporary
        result set 'flight_delays', which provides a row per flight with calculations of the time
        differences between the scheduled time and confirmed time for departure and arrival.
        Using a temporary result set here means that these calculation outputs can be included once and
        reused by the different metrics (average, max, min) in the main query, avoiding having to including
        the calculations again for each metric, which significantly simplifies the query.

        The main query is then fairly simple, grouping the results by year and month, and using
        the aggregation functions AVG, MIN and MAX to provide the statistics. The CASE statement is used
        to convert the numeric months into more human-readable month names. The month is cast to an integer
        in the sort statement to ensure numeric rather than text sorting on that field.

        Returns a list of dictionaries representing the data in each row returned by the query.
        """

        rows = self._execute_fetchall(
            """
            WITH flight_delays AS (
                SELECT
                    flight_id,
                    strftime('%Y', scheduled_departure_date) AS year,
                    strftime('%m', scheduled_departure_date) AS month_numeric,

                    (
                        strftime('%s', confirmed_departure_date || confirmed_departure_time)
                    - strftime('%s', scheduled_departure_date || scheduled_departure_time)
                    ) / 60.0 AS departure_delay_minutes,

                    (
                        strftime('%s', confirmed_arrival_date || confirmed_arrival_time)
                    - strftime('%s', scheduled_arrival_date || scheduled_arrival_time)
                    ) / 60.0 AS arrival_delay_minutes
                FROM flights
                WHERE flight_status = 'Arrived'
            )
            SELECT
                COUNT(flight_id) AS total_flights,
                year,

                CASE month_numeric
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

                ROUND(AVG(departure_delay_minutes), 2) AS avg_departure_delay,
                ROUND(MIN(departure_delay_minutes), 2) AS min_departure_delay,
                ROUND(MAX(departure_delay_minutes), 2) AS max_departure_delay,

                ROUND(AVG(arrival_delay_minutes), 2) AS avg_arrival_delay,
                ROUND(MIN(arrival_delay_minutes), 2) AS min_arrival_delay,
                ROUND(MAX(arrival_delay_minutes), 2) AS max_arrival_delay

            FROM flight_delays
            GROUP BY year, month_numeric
            ORDER BY year DESC, CAST(month_numeric AS INTEGER) DESC
            """
        )
        return self._rows_to_dicts(rows)
    
    def aircraft_statistics(self) -> list[dict]:
        """
        This report summarises on a monthly basis the number of flights completed, in progress
        and scheduled for each individual aircraft.

        The basis of this query is the `vw_flight_summary` view, with flights grouped by year, month
        and aircraft. There is an inner join to the `vw_aircraft` view in order to retrieve the aircraft status.
        
        Flight counts for the different flight statuses (grouped into 'completed', 'in progress'
        and 'scheduled' categories) are calculated using a combination of COUNT functions and conditional
        CASE statements. This means that for each of the status-specific count columns, the count is only
        incremented by one if the statement is true, which is a neat way of applying row-level conditions
        to aggregations.
        
        A CASE statement is also used to convert the numeric months into more human-readable month names, which
        also requires stripping the numeric month of the date field using the strftime() function. This is repeated
        and the resulting month cast to an integer in the sort statement to ensure numeric rather than text sorting
        on that field.

        The main query is then fairly simple, grouping the results by year and month, and using
        the aggregation functions AVG, MIN and MAX to provide the statistics. The CASE statement is used
        to convert the numeric months into more human-readable month names. The month is cast to an integer
        in the sort statement to ensure numeric rather than text sorting on that field.

        Returns a list of dictionaries representing the data in each row returned by the query.
        """

        rows = self._execute_fetchall(
            """
            SELECT
                f.aircraft_registration,
                a.aircraft_status,
                f.aircraft_type,
                strftime('%Y', f.scheduled_departure_date) AS year,
                CASE strftime('%m', f.scheduled_departure_date)
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
                        WHEN f.flight_status = 'Arrived' THEN 1
                    END
                ) AS completed_flights,
                COUNT(
                    CASE
                        WHEN f.flight_status <> 'Scheduled' AND f.flight_status <> 'Arrived' THEN 1
                    END
                ) AS in_progress_flights,
                COUNT(
                    CASE
                        WHEN f.flight_status = 'Scheduled' THEN 1
                    END
                ) AS scheduled_flights
            FROM vw_flight_summary f
            INNER JOIN vw_aircraft a ON a.registration = f.aircraft_registration
            GROUP BY year, month, f.aircraft_registration
            ORDER BY year DESC, CAST(strftime('%m', f.scheduled_departure_date) AS INTEGER) DESC, f.aircraft_registration
            """
        )
        return self._rows_to_dicts(rows)

    def _rows_to_dicts(self, rows: list) -> list[dict]:
        result_list = []
        for row in rows:
            result_list.append(dict(row))

        return result_list