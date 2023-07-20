import csv
import json
import time
from datetime import datetime
from io import StringIO

from django.conf import settings
from django.db import IntegrityError, DataError
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.decorators import parser_classes
from rest_framework.parsers import MultiPartParser, FormParser

from apps.core.exceptions import ResourceNotFound
from apps.core.serializers import response_200, error_response, custom_response, response_400
from apps.profiles.models import People
from apps.profiles.serializer import PersonSerializer, UUIDSerializer
from apps.profiles.service import ProfileService

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
        # request_body=LoginRequestSerializer,
        manual_parameters=[ip_header_param, user_agent_header_param],
        responses={400: error_response,
                   # 200: custom_response('Logged In User', LoggedInUserSerializer)
                   },
        operation_summary="Login Api",
        tags=["Auth APIs"],
    )
    def login(self, request):
        """
        Api to Login
        """
        body = request.data
        ip = self._get_ip(request)
        user_agent = self._get_user_agent(request)
        # try:
        #     response = AuthenticationService.login_with_email_id_password(body, ip, user_agent)
        # except (
        #     RequestValidationError,
        #     InvalidCredentialException,
        #     RequestValidationException,
        # ) as e:
        #     return response_400(e)
        return response_200({'niki': 'baby'})

    @swagger_auto_schema(
        responses={400: error_response,
                   200: custom_response('List of People', PersonSerializer)
                   },
        operation_summary="List of People",
        tags=["People APIs"],
    )
    def list_people(self, request):
        all_people = People.objects.all().exclude(account_status='DELETED').order_by('account_status', 'first_name')
        serializer = PersonSerializer(instance=all_people, many=True)
        return response_200(serializer.data)


    @swagger_auto_schema(
    responses={400: error_response,
               200: custom_response('List of People', PersonSerializer)
               },
    operation_summary="List of People",
    tags=["People APIs"],
    )
    def produce_email(self, request):
        import json
        from kafka import KafkaProducer
        USER_EMAIL_KAFKA_TOPIC = "user_email"
        producer = KafkaProducer(bootstrap_servers='localhost:29092')
        users = People.objects.all()
        print("Gonna start listening")
        for user in users:
            print("Ongoing transaction..")
            user_id = user.mobile
            user_email = user.email
            data = {
                "customer_id": user_id,
                "customer_email": user_email,
            }
            d = json.dumps(data).encode("utf-8")
            print(d)
            print("Successful transaction..")
            producer.send(USER_EMAIL_KAFKA_TOPIC, d)



        # topic = 'your_topic_name'  # Replace with the desired Kafk1a topic name
        # data = {
        #     "order_id": 1,
        #     "user_id": f"tom_",
        #     "total_cost": 111,
        #     "items": "burger,sandwich",
        # }
        # producer.send(topic, value=data.encode())
        producer.flush()
        producer.close()
        return response_200({'Data Generated': 'Done'})

    @swagger_auto_schema(
        responses={400: error_response,
                   200: custom_response('List of People', PersonSerializer)
                   },
        manual_parameters=[person_id],
        operation_summary="Delete a Person",
        tags=["People APIs"],
    )
    def delete_people(self, request, person_id):
        try:
            person_id = UUIDSerializer.validate_and_map({'id': person_id})['id']
            deleted_person = ProfileService().delete_profile(person_id)
            return response_200(PersonSerializer(instance=deleted_person).data)
        except ResourceNotFound as e:
            return response_400(e)

    @swagger_auto_schema(
        request_body=PersonSerializer(),
        manual_parameters=[person_id],
        responses={400: error_response,
                   200: custom_response('Update Person', PersonSerializer)
                   },
        operation_summary="Update a Person",
        tags=["People APIs"],
    )
    def update_people(self, request, person_id):
        try:
            person_id = UUIDSerializer.validate_and_map({'id': person_id})['id']
            new_data = json.loads(request.body.decode('utf-8'))
            person = ProfileService().update_profile(person_id, new_data)
            return response_200(PersonSerializer(instance=person).data)
        except (ResourceNotFound, IntegrityError, DataError) as e:
            return response_400(e)

    @swagger_auto_schema(
        request_body=PersonSerializer(),
        responses={400: error_response,
                   200: custom_response('Add Person', PersonSerializer)
                   },
        operation_summary="Add a Person",
        tags=["People APIs"],
    )
    def add_people(self, request):
        try:
            new_person = json.loads(request.body.decode('utf-8'))
            person = ProfileService().add_profile(new_person)
            return response_200(PersonSerializer(instance=person).data)
        except ResourceNotFound as e:
            return response_400(e)


class UploadCSVData(viewsets.ViewSet):
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        manual_parameters=[csv_file],
        operation_summary="Upload CSV",
        operation_description="Upload a file",
        tags=["People APIs"],
    )
    def upload_csv(self, request):
        uploaded_file = request.FILES.get(csv_file.name)
        try:
            records_count = ProfileService().read_and_process_csv(uploaded_file)
            return response_200({'records': records_count})
        except Exception as e:
            return response_400({'Error': e})
