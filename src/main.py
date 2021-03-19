import sys
import os
import logging
from keboola import docker
from marketorestpython.client import MarketoClient
from datetime import datetime, timedelta
import functions as fces
import logging_gelf.handlers
import logging_gelf.formatters  # noqa
"__author__ = 'Radim Kasparek kasrad'"
"__credits__ = 'Keboola Drak"
"__component__ = 'Marketo Extractor'"

"""
Python 3 environment
"""


sys.tracebacklimit = None

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S")


logger = logging.getLogger()
logging_gelf_handler = logging_gelf.handlers.GELFTCPSocketHandler(
    host=os.getenv('KBC_LOGGER_ADDR'),
    port=int(os.getenv('KBC_LOGGER_PORT'))
)
logging_gelf_handler.setFormatter(
    logging_gelf.formatters.GELFFormatter(null_character=True))
logger.addHandler(logging_gelf_handler)

# removes the initial stdout logging
logger.removeHandler(logger.handlers[0])


COMPONENT_VERSION = '0.0.12'
logging.info(f'kds-team.ex-marketo version: {COMPONENT_VERSION}')

# Destination to fetch and output files and tables
DEFAULT_TABLE_INPUT = "/data/in/tables/"
DEFAULT_FILE_INPUT = "/data/in/files/"

DEFAULT_FILE_DESTINATION = "/data/out/files/"
DEFAULT_TABLE_DESTINATION = "/data/out/tables/"

# Access the supplied rules
cfg = docker.Config('/data/')
params = cfg.get_parameters()
logging.info("params read")

# enter Client ID from Admin > LaunchPoint > View Details
# fill in Munchkin ID, typical format 000-AAA-000
# enter Client ID and Secret from Admin > LaunchPoint > View Details

client_id = cfg.get_parameters()["#client_id"]
munchkin_id = cfg.get_parameters()["#munchkin_id"]
client_secret = cfg.get_parameters()["#client_secret"]
method = cfg.get_parameters()["method"]
desired_fields_tmp = cfg.get_parameters()["desired_fields"]
since_date = cfg.get_parameters()["since_date"]  # YYYY-MM-DD
until_date = cfg.get_parameters()["until_date"]  # YYYY-MM-DD
filter_column = cfg.get_parameters()["filter_column"]
filter_field = cfg.get_parameters()["filter_field"]
dayspan = cfg.get_parameters()["dayspan"]
desired_fields = [i.strip() for i in desired_fields_tmp.split(",")]

logging.info("Desired fields: %s" % str(desired_fields))
logging.info("Since date: %s" % since_date)
logging.info("Until date: %s" % until_date)
logging.info("Filter column: %s" % filter_column)
logging.info("Filter field: %s" % filter_field)
logging.info("Dayspan: %s" % dayspan)

# Get proper list of tables
in_tables = cfg.get_input_tables()
out_tables = cfg.get_expected_output_tables()
out_files = cfg.get_expected_output_files()
logging.info("IN tables mapped: " + str(in_tables))
logging.info(filter_column)

# Preset data parameters if not specified
if since_date == '' and dayspan != '':
    since_date = str((datetime.utcnow() - timedelta(days=int(dayspan)))
                     .date())
    until_date = str(datetime.utcnow().date())

if len(in_tables) == 0:
    in_tables = [{'destination': 'placeholder'}]
else:
    pass


# main


def main():
    """
    Main execution script.
    """
    mc = MarketoClient(munchkin_id, client_id, client_secret)
    logging.info('Reading Marketo')
    if method == 'extract_leads_by_ids':
        fces.extract_leads_by_ids(output_file=DEFAULT_TABLE_DESTINATION + 'leads_by_ids.csv',
                                  source_file=DEFAULT_TABLE_INPUT +
                                  in_tables[0]['destination'],
                                  fields=desired_fields,
                                  mc_object=mc)

    elif method == 'extract_leads_by_filter':
        fces.extract_leads_by_filter(output_file=DEFAULT_TABLE_DESTINATION + 'leads_by_filter.csv',
                                     source_file=DEFAULT_TABLE_INPUT +
                                     in_tables[0]['destination'],
                                     filter_on=filter_field,
                                     filter_values_column=filter_column,
                                     fields=desired_fields,
                                     mc_object=mc)

    elif method == 'get_deleted_leads':
        fces.get_deleted_leads(output_file=DEFAULT_TABLE_DESTINATION + 'deleted_leads.csv',
                               since_date=since_date,
                               mc_object=mc)

    elif method == 'get_lead_changes':
        fces.get_lead_changes(output_file=DEFAULT_TABLE_DESTINATION + 'lead_changes.csv',
                              fields=desired_fields,
                              since_date=since_date,
                              until_date=until_date,
                              mc_object=mc)

    elif method == 'get_lead_activities':
        fces.get_lead_activities(output_file=DEFAULT_TABLE_DESTINATION + 'lead_activites.csv',
                                 source_file=DEFAULT_TABLE_INPUT +
                                 in_tables[0]['destination'],
                                 since_date=since_date,
                                 until_date=until_date,
                                 mc_object=mc)

    elif method == 'get_companies' and len(in_tables):
        fces.get_companies(output_file=DEFAULT_TABLE_DESTINATION + 'companies.csv',
                           source_file=DEFAULT_TABLE_INPUT +
                           in_tables[0]['destination'],
                           filter_on=filter_field,
                           filter_values_column=filter_column,
                           fields=desired_fields,
                           mc_object=mc)

    elif method == 'get_campaigns' and len(in_tables) != 0:
        fces.get_campaigns(
            output_file=DEFAULT_TABLE_DESTINATION + 'campaigns.csv',
            source_file=DEFAULT_TABLE_INPUT +
            in_tables[0]['destination'],
            mc_object=mc,
            filter_values_column=filter_column)

    elif method == 'get_campaigns' and len(in_tables) == 0:
        fces.get_campaigns(
            output_file=DEFAULT_TABLE_DESTINATION + 'campaigns.csv',
            mc_object=mc,
            filter_values_column=filter_column)

    elif method == 'get_activity_types':
        fces.get_activity_types(output_file=DEFAULT_TABLE_DESTINATION + 'activity_types.csv',
                                mc_object=mc)


def validate_user_parameters():
    # 1 - Component cannot accepy more than one table as input table
    if len(in_tables) > 1:
        logging.error('Please do not use more than one table as input table.')
        sys.exit(1)

    # 2 - ensure there is a configuration
    if params == {}:
        logging.error(
            'Empty configuration. Please configure your configuration.')
        sys.exit(1)

    # 3 - Ensure the reequired credentials are entered
    if munchkin_id == '' or client_id == '' or client_secret == '':
        logging.error(
            'Credentials are missing: [Munchkin ID token], [Client ID Token], [Client Secret Token]')
        sys.exit(1)

    # 4 - Ensure input date parameters are valid
    if since_date != '' and dayspan != '':
        logging.error("Please add either since_date or dayspan, not both.")
        sys.exit(1)


if __name__ == "__main__":

    validate_user_parameters()
    main()

    logging.info("Component [kdsteam.ex-marketo] finished.")
