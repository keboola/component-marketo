import csv
import pandas as pd
# from marketorestpython.client import MarketoClient
import json
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S")


def get_tables(in_tables):
    """
    Evaluate input and output table names.
    Only taking the first one into consideration!
    """

    # input file
    table = in_tables[0]
    in_name = table["full_path"]
    in_destination = table["destination"]
    logging.info("Data table: " + str(in_name))
    logging.info("Input table source: " + str(in_destination))

    return in_name


def get_output_tables(out_tables):
    """
    Evaluate output table names.
    Only taking the first one into consideration!
    """

    # input file
    table = out_tables[0]
    in_name = table["full_path"]
    in_destination = table["source"]
    logging.info("Data table: " + str(in_name))
    logging.info("Input table source: " + str(in_destination))

    return in_name


def output_file(output_model, file_out="data.json"):
    """
    Save output data as CSV (pandas)
    """

    # with open(file_out, "w", encoding="utf-8") as csvfile:
    with open(file_out, 'w') as jsonfile:
        json.dump(output_model, jsonfile)

    jsonfile.close()


def extract_leads_by_ids(output_file, source_file, mc_object,
                         fields=['id', 'firstName', 'lastName', 'email',
                                 'updatedAt', 'createdAt', 'Do Not Call Reason']):
    """
    Extracts leads by lead_id.
    The input file needs to contain a column with
    """

    with open(source_file, mode='rt', encoding='utf-8') as in_file,\
            open(output_file, mode='w', encoding='utf-8') as out_file:

        leads = []
        lazy_lines = (line for line in in_file)
        reader = csv.DictReader(lazy_lines, lineterminator='\n')

        for lead_record in reader:
            lead_detail = mc_object.execute(method='get_lead_by_id',
                                            id=lead_record["lead_id"])
            if len(lead_detail) > 0:
                leads.append(lead_detail[0])

        keys = (fields)
        dict_writer = csv.DictWriter(out_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(leads)


def extract_leads_by_filter(output_file,
                            source_file,
                            mc_object,
                            filter_on,
                            filter_values_column,
                            fields=['id', 'firstName', 'lastName', 'email',
                                    'updatedAt', 'createdAt', 'Do Not Call Reason']):
    """
    Extracts leads based on filters
    source_file -  needs to contain a column with the values to input
    to the filter
    filter_values_column - the column in the source file that contains
    the values to input to the filter
    filter_on- specifies the field in API (e.g. "email")
    fields - the fields in API that will be returned
    """

    with open(source_file, mode='rt', encoding='utf-8') as in_file,\
            open(output_file, mode='w', encoding='utf-8') as out_file:

        leads = []
        lazy_lines = (line for line in in_file)
        reader = csv.DictReader(lazy_lines, lineterminator='\n')

        filter_values_list = []
        for lead_record in reader:
            filter_values_list.append(lead_record[filter_values_column])

        leads = mc_object.execute(method='get_multiple_leads_by_filter_type',
                                  filterType=filter_on,
                                  filterValues=filter_values_list,
                                  fields=fields,
                                  batchSize=None)

        if len(leads) > 0:
            print('%i leads extracted', len(leads))
        else:
            print('No leads match the criteria!')

        keys = (fields)
        dict_writer = csv.DictWriter(out_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(leads)


def get_companies(output_file,
                  source_file,
                  mc_object,
                  filter_on,
                  filter_values_column,
                  fields=['id', 'firstName', 'lastName', 'email', 'updatedAt',
                          'createdAt', 'Do Not Call Reason']):
    """
    filterType can be: externalCompanyId, id, externalSalesPersonId, company

    Extracts companies based on filters
    source_file -  needs to contain a column with the values to input
    to the filter
    filter_values_column - the column in the source file that contains
    the values to input to the filter
    filter_on- specifies the field in API (e.g. "company")
    fields - the fields in the API that will be returned
    """

    with open(source_file, mode='rt', encoding='utf-8') as in_file,\
            open(output_file, mode='w', encoding='utf-8') as out_file:

        companies = []
        lazy_lines = (line for line in in_file)
        reader = csv.DictReader(lazy_lines, lineterminator='\n')

        filter_values_list = []
        for company_record in reader:
            filter_values_list.append(company_record[filter_values_column])

        companies = mc_object.execute(method='get_companies',
                                      filterType=filter_on,
                                      filterValues=filter_values_list,
                                      fields=fields,
                                      batchSize=None)

        if len(companies) > 0:
            print('%i companies extracted', len(companies))
        else:
            print('No companies match the criteria!')

        keys = (fields)
        dict_writer = csv.DictWriter(out_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(companies)


def get_lead_activities(output_file,
                        source_file,
                        mc_object,
                        since_date,
                        until_date):
    """
    source file: has to contain columns 'activity_type_ids' and 'lead_ids'. These
    must contain the values corresponding for the query.
    output file: will contain columns based on the fields in extracted responses
    - it can definitely happen that different runs will produce different number of columns!!
    since_date
    until_date
    """

    activity_type_ids = list(pd.read_csv(source_file,
                                         skipinitialspace=True,
                                         usecols=['activity_type_ids']).iloc[:, 0])
    lead_ids = list(pd.read_csv(source_file,
                                skipinitialspace=True,
                                usecols=['lead_ids']).iloc[:, 0])

    lead_ids = [str(int(i)) for i in lead_ids if str(i) != 'nan']
    activity_type_ids = [str(int(i))
                         for i in activity_type_ids if str(i) != 'nan']

    results = mc_object.execute(method='get_lead_activities',
                                activityTypeIds=activity_type_ids,
                                nextPageToken=None,
                                sinceDatetime=since_date,
                                untilDatetime=until_date,
                                batchSize=None,
                                listId=None,
                                leadIds=lead_ids)

    if len(results) == 0:
        print('No results!')
        return

    unique_keys = []
    for i in results:
        try:
            for j in i['attributes']:
                i[j['name']] = j['value']

            i.pop('attributes', None)

            unique_keys.extend(list(i.keys()))
        except KeyError:
            pass

    unique_keys = list(set(unique_keys))

    with open(output_file, mode='w', encoding='utf-8') as out_file:

        keys = (unique_keys)
        dict_writer = csv.DictWriter(out_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(results)


def get_lead_changes(output_file,
                     fields,
                     since_date,
                     until_date,
                     mc_object):
    """
    this function takes very long to run
    output file: will contain columns based on the fields in extracted responses
     - it can definitely happen that different runs will produce different number of columns!!
    since_date
    until_date
    fields: list of field names to return changes for, field names can be
     retrieved with the Describe Lead API
    """
    logging.info('function get_lead_changes started')
    results = mc_object.execute(method='get_lead_changes',
                                fields=fields,
                                nextPageToken=None,
                                sinceDatetime=since_date,
                                untilDatetime=until_date,
                                batchSize=None,
                                listId=None)
    logging.info(str(len(results)) + ' results fetched')
    if len(results) == 0:
        print('No results!')
        return

    unique_keys = []
    for i in results:

        try:
            for j in i['attributes']:
                i[j['name']] = j['value']

            i.pop('attributes', None)

        except KeyError:
            pass

        try:
            for l in range(len(i['fields'])):
                i['name'] = i['fields'][l]['name']
                i[("newValue_{}").format(i['name'])] = i['fields'][l]['newValue']
                i['oldValue' + '_' + i['name']] = i['fields'][l]['oldValue']

            i.pop('fields', None)

        except KeyError:
            pass

        except TypeError:
            pass

        unique_keys.extend(list(i.keys()))

    unique_keys = list(set(unique_keys))

    with open(output_file, mode='w', encoding='utf-8') as out_file:

        fieldnames = ['leadId', 'activityDate', 'activityTypeId']
        results_trimmed = [0] * len(results)
        for i in range(len(results)):
            results_trimmed[i] = {
                your_key: results[i][your_key] for your_key in fieldnames}

        dict_writer = csv.DictWriter(out_file, fieldnames)
        dict_writer.writeheader()
        dict_writer.writerows(results_trimmed)


def get_deleted_leads(output_file,
                      since_date,
                      mc_object):
    """
    output file: will contain first and last name, Marketo ID and time of deletion,
    but no additional Lead attributes
    since_date
    """

    results = mc_object.execute(method='get_deleted_leads',
                                nextPageToken=None,
                                sinceDatetime=since_date,
                                batchSize=None)

    if len(results) == 0:
        print('No results!')
        return

    with open(output_file, mode='w', encoding='utf-8') as out_file:

        keys = ['id',
                'marketoGUID',
                'leadId',
                'activityDate',
                'activityTypeId',
                'campaignId',
                'primaryAttributeValueId',
                'primaryAttributeValue',
                'attributes']
        dict_writer = csv.DictWriter(out_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(results)


def get_opportunities(output_file,
                      source_file,
                      mc_object,
                      filter_on,
                      filter_values_column,
                      fields=['id', 'firstName', 'lastName', 'email',
                              'updatedAt', 'createdAt', 'Do Not Call Reason']):
    """
    Returns opportunities based on a filter and set of values.
    source_file -  needs to contain a column with the values to input
    to the filter
    output_file -
    filter_values_column - the column in the source file that contains
    the values to input to the filter
    filter_on- specifies the field in API (e.g. "email")
    fields - the fields in the API that will be returned
    """

    with open(source_file, mode='rt', encoding='utf-8') as in_file,\
            open(output_file, mode='w', encoding='utf-8') as out_file:

        leads = []
        lazy_lines = (line for line in in_file)
        reader = csv.DictReader(lazy_lines, lineterminator='\n')

        filter_values_list = []
        for lead_record in reader:
            filter_values_list.append(lead_record[filter_values_column])

        leads = mc_object.execute(method='get_opportunities',
                                  filterType=filter_on,
                                  filterValues=filter_values_list,
                                  fields=fields,
                                  batchSize=None)

        if len(leads) > 0:
            print('%i leads extracted', len(leads))
        else:
            print('No leads match the criteria!')

        keys = (fields)
        dict_writer = csv.DictWriter(out_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(leads)


def get_campaigns(output_file,
                  mc_object,
                  filter_values_column,
                  source_file='blankblank.csv'):
    '''
    extract all the campaigns, if id argument is left blank, all campaigns are
    retrieved
    '''

    try:
        with open(source_file, mode='rt', encoding='utf-8') as in_file,\
                open(output_file, mode='w', encoding='utf-8') as out_file:

            logging.info('Extracting specific campaigns based on id.')

            lazy_lines = (line for line in in_file)
            reader = csv.DictReader(lazy_lines, lineterminator='\n')

            id_values_list = []
            for record in reader:
                id_values_list.append(record[filter_values_column])

            results = mc_object.execute(method='get_multiple_campaigns',
                                        id=id_values_list
                                        )

            if len(results) > 0:
                logging.info('%i campaigns extracted', len(results))
            else:
                logging.info('No campaigns match the criteria!')

            keys = ['id', 'name', 'description', 'type', 'programName',
                    'programId', 'workspaceName', 'createdAt', 'updatedAt', 'active']
            dict_writer = csv.DictWriter(out_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(results)

    except FileNotFoundError:
        results = mc_object.execute(method='get_multiple_campaigns')
        logging.info('No input file specified, extracting all campaigns.')

        if len(results) > 0:
            print('%i campaigns extracted', len(results))
        else:
            print('No campaigns match the criteria!')

        keys = ['id', 'name', 'description', 'type', 'programName',
                'programId', 'workspaceName', 'createdAt', 'updatedAt', 'active']

        with open(output_file, mode='w', encoding='utf-8') as out_file:
            dict_writer = csv.DictWriter(out_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(results)


def get_activity_types(output_file,
                       mc_object):
    """
    Returns a list of available activity types in the target instance,
    along with associated metadata of each type
    """
    activity_types = mc_object.execute(method='get_activity_types')

    if len(activity_types) > 0:
        print('%i activities found', len(activity_types))
    else:
        print('No activities found!')

    with open(output_file, mode='w', encoding='utf-8') as out_file:
        keys = ['attributes', 'description', 'id', 'name', 'primaryAttribute']
        dict_writer = csv.DictWriter(out_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(activity_types)
