    def trend_of_sdk_table_tab(self):
        """
        Generates a report on the trend of SDK events over time.

        Returns:
            dict: A dictionary containing report content, actionable insights, and analysis logic.
        """

        query = """
        SELECT concat(db, '-', entity, '-', goal) as key, date(date) AS date, sum(event_count) as EVENT_COUNT
        from (
        SELECT *
        FROM metabase_cs.ads_analytics_airflow.sdk_data_trend
        WHERE date >= dateadd('day', -60, getdate())
        QUALIFY ROW_NUMBER() OVER (PARTITION BY db, entity, goal, date, event_source, event_name ORDER BY analytics_updated_at DESC) = 1
        order by date desc
        )
        GROUP BY key, date
        ORDER BY key, date
        """

        df = self.get_filtered_df(query)
        df_grouped = df.groupby(['KEY', 'DATE']).agg({'EVENT_COUNT': 'sum'}).reset_index()
        df_grouped.sort_values(by=['KEY', 'DATE'], inplace=True)

        fig = px.line(df_grouped, x="DATE", y="EVENT_COUNT", facet_col="KEY", facet_col_wrap=5,
              facet_row_spacing=0.04, # default is 0.07 when facet_col_wrap is used
              facet_col_spacing=0.04, # default is 0.03
              height=2500, 
              width=2000,
              title="Events Trend")
        fig.for_each_annotation(lambda a: a.update(text=a.text.replace("KEY=", "")))
        
        fig.update_yaxes(showticklabels=True)
        fig.update_xaxes(showticklabels=True)
        fig.update_yaxes(matches=None)
        
        content = fig

        # # Instantiate the CalloutSystem with the DataFrame
        # callout_system = CalloutSystem(df_grouped)
        # column_name = 'EVENT_COUNT'

        # # Calculate rolling stats for a specific column (e.g., 'TOTAL_GOAL_METS')
        # callout_system.calculate_rolling_stats(column_name)

        # # Run specific checks and update the callouts DataFrame
        # callout_system.check_drop_in_column(column_name, threshold=1.5)
        # callout_system.check_spike_in_column(column_name)
        # # callout_system.check_max_date_and_generate_callout(key_column='KEY')

        # # Filter for the last week
        # callout_system.filter_last_week()

        # # Retrieve the final callouts
        # result_df = callout_system.get_callouts()

        return self._generate_report(content=content, callouts_df=result_df)