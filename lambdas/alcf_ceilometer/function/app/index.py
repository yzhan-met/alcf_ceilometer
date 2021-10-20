"""alcf_ceilometer"""

from aws_lambda_powertools import Logger

LOGGER = Logger(child=True)
@LOGGER.inject_lambda_context(log_event=True)
def main(event, context):
    """Main handler

    Args:
        event (dict): contains information from the invoking service
        context (dict): not used
    """    
    pass
