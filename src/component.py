'''
Template Component main class.

'''


from kbc.env_handler import KBCEnvHandler
import logging

KEY_PROJECT_ID = 'project_id'
KEY_API_TOKEN = '#api_token'
KEY_PERIOD_FROM = 'period_from'
KEY_PERIOD_TO = 'period_to'
KEY_RELATIVE_PERIOD = 'relative_period'


KEY_MAND_PERIOD_GROUP = [KEY_PERIOD_FROM, KEY_PERIOD_TO]
KEY_MAND_DATE_GROUP = [KEY_RELATIVE_PERIOD, KEY_MAND_PERIOD_GROUP]

MANDATORY_PARS = [KEY_PROJECT_ID, KEY_API_TOKEN, KEY_MAND_DATE_GROUP]

APP_VERSION = '0.0.1'


class Component(KBCEnvHandler):

    def __init__(self, debug=False):
        KBCEnvHandler.__init__(self, MANDATORY_PARS)
        # override debug from config
        if(self.cfg_params.get('debug')):
            debug = True

        self.set_default_logger('DEBUG' if debug else 'INFO')
        logging.info('Running version %s', APP_VERSION)
        logging.info('Loading configuration...')

        try:
            self.validateConfig()
        except ValueError as e:
            logging.error(e)
            exit(1)

    def run(self, debug=False):
        '''
        Main execution code
        '''
        params = self.cfg_params  # noqa


"""
        Main entrypoint
"""
if __name__ == "__main__":
    comp = Component()
    comp.run()
