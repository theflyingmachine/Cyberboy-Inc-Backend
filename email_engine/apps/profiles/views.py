from django.conf import settings
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets

from apps.core.serializers import response_200, error_response, custom_response, response_400
from apps.profiles.serializer import PersonSerializer, UUIDSerializer

ip_header_param = openapi.Parameter(
    settings.IP_HEADER,
    openapi.IN_HEADER,
    description=f"Source IP",
    type=openapi.TYPE_STRING,
)

user_agent_header_param = openapi.Parameter(
    settings.USER_AGENT_HEADER,
    openapi.IN_HEADER,
    description=f"User Agent",
    type=openapi.TYPE_STRING,
)

person_id = openapi.Parameter(
    'person_id', openapi.IN_PATH, description='Person ID', type=openapi.TYPE_STRING
)

person_data = openapi.Parameter(
    'person_data', openapi.IN_BODY, description='Person data', type=openapi.TYPE_OBJECT
)

csv_file = openapi.Parameter(
    'csv_data', openapi.IN_FORM, description='Person data CSV', type=openapi.TYPE_FILE
)


class Profile(viewsets.ViewSet):

    def _get_ip(self, req):
        return req.headers.get(settings.IP_HEADER) or ''

    def _get_user_agent(self, req):
        return req.headers.get(settings.USER_AGENT_HEADER) or ''

    @swagger_auto_schema(
        responses={400: error_response,
                   200: custom_response('Process Email', PersonSerializer)
                   },
        operation_summary="Process Emails",
        tags=["People APIs"],
    )
    def process_email(self, request):
        import json
        from kafka import KafkaConsumer
        USER_EMAIL_KAFKA_TOPIC = "user_email"

        consumer = KafkaConsumer(
            USER_EMAIL_KAFKA_TOPIC,
            bootstrap_servers="kafka:29092"
        )

        print("Gonna start listening")
        for message in consumer:
            print("Ongoing transaction..")
            consumed_message = json.loads(message.value.decode())
            print(consumed_message)
            return response_200({'Data Received': consumed_message})
        return response_400({'Error': 'Something went wrong'})
