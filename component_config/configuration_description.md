### Configurations

1. Desired Fields
    - Specifying the columns you want to extract
    - Relevant to the endpoints below
        1. `extract_leads_by_ids`
        2. `extract_leads_by_filter`
        3. `get_lead_changes`
        4. `get_companies`

2. Since Date (From)
    - Specifing the date range of the extraction
    - Relevant to the endpoints below
        1. `get_deleted_leads`
        2. `get_lead_changes`
        3. `get_lead_activities`

3. Until Date (To)
    - Specifing the date range of the extraction
    - Relevant to the endpoints below
        1. `get_lead_changes`
        2. `get_lead_activities`

4. Filter Column
    - Denotes the column in the input file that contains the values you want to filter
    - Relevant to the endpoints below
        1. `extract_leads_by_filter`
        2. `get_campaigns`

5. Field to filter on
    - The API fields you want to filter on

6. How many days back you want to go?
    - Alternative to `Since Date`. The `Until Date` is automatically set to current date if this field is used