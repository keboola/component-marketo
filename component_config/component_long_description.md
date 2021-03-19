This component allows KBC to get data from a few endpoints of the [Marketo REST API](http://developers.marketo.com/rest-api/). It relies heavily on package [marketorestpython](https://github.com/jepcastelein/marketo-rest-python).

## API Limitations
[Marketo API Limit](http://developers.marketo.com/rest-api/marketo-integration-best-practices/)

## Configurations

1. Munchkin ID token
    - Can be obtained in `Admin` > `Web Service` menu in the REST API section

2. Client ID

3. Client Secret

4. Desired Fields
    - Specifying the columns you want to extract
    - Values are required to be comma seperated 
    - Relevant to the endpoints below
        1. `extract_leads_by_ids`
        2. `extract_leads_by_filter`
        3. `get_lead_changes`
        4. `get_companies`

5. Method
    1. `extract_leads_by_ids`
    2. `extract_leads_by_filter`
    3. `get_deleted_leads`
    4. `get_lead_changes`
    5. `get_lead_activities`
    6. `get_companies`
    7. `get_campaigns`
    8. `get_activity_types`

6. Since Date (From)
    - Specifing the date range of the extraction
    - Relevant to the endpoints below
        1. `get_deleted_leads`
        2. `get_lead_changes`
        3. `get_lead_activities`

7. Until Date (To)
    - Specifing the date range of the extraction
    - Relevant to the endpoints below
        1. `get_lead_changes`
        2. `get_lead_activities`

8. Filter Column
    - Denotes the column in the input file that contains the values you want to filter
    - Relevant to the endpoints below
        1. `extract_leads_by_filter`
        2. `get_campaigns`

9. Field to filter on
    - The API fields you want to filter on

10. How many days back you want to go?
    - Alternative to `Since Date`. The `Until Date` is automatically set to current date if this field is used
