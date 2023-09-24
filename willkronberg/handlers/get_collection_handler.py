from datetime import datetime
from typing import Any, Dict, List

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.data_classes import (
    APIGatewayProxyEvent,
    event_source,
)
from aws_lambda_powertools.utilities.typing import LambdaContext

from willkronberg.helpers import response_helpers
from willkronberg.models.record import RecordRelease
from willkronberg.services.discogs_service import DiscogsService

logger = Logger()
tracer = Tracer()


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler(capture_response=False)
@event_source(data_class=APIGatewayProxyEvent)
def get_collection_handler(event: APIGatewayProxyEvent, context: LambdaContext):
    """Returns a list of releases from Discogs that I own

    Parameters
    ----------
    event: APIGatewayProxyEvent, required
    context: LambdaContext, required

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict
    """

    try:
        discogs_service = DiscogsService()
        data = discogs_service.get_collection()

        releases: List[Dict[str, Any]] = []
        for item in data.releases:
            date_added = datetime.fromisoformat(item.date_added)

            release = RecordRelease(
                id=item.id,
                artists=item.basic_information.artists,
                cover_image=item.basic_information.thumb,
                date_added=date_added.strftime("%A %B %e, %Y"),
                title=item.basic_information.title,
                url=item.basic_information.master_url,
                year=item.basic_information.year,
            )
            releases.append(release.model_dump())

        return response_helpers.generate_success_response(releases)
    except Exception as e:
        logger.exception(e, stack_info=True)

        return response_helpers.generate_error_response(
            500, "An unexpected error has occurred."
        )
