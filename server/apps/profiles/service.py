import csv
import hashlib
import os
from datetime import datetime
from io import StringIO

import requests
from django.conf import settings
from django.core.files.storage import FileSystemStorage

from apps.profiles.models import People


def generate_uuid_filename(uuid):
    image_filename = str(uuid) + ".png"
    return image_filename


class ProfileService:
    def delete_profile(self, person_uuid):
        person = People.get_person(person_uuid)
        person.account_status = 'DELETED'
        person.active = False
        person.save()
        return person

    def update_profile(self, person_uuid, new_data):
        # Set Account Status Disabled on Inactivate and Clean Data format
        new_data['first_name'] = new_data['first_name'].capitalize()
        new_data['middle_name'] = new_data['middle_name'].capitalize()
        new_data['last_name'] = new_data['last_name'].capitalize()
        new_data['gender'] = new_data['gender'].upper()
        new_data['email'] = new_data['email'].lower()
        new_data['account_status'] = 'ACTIVE' if new_data['active'] else 'DISABLED'

        People.objects.filter(id=person_uuid).update(**new_data)
        updated_person = People.objects.get(id=person_uuid)
        return updated_person

    def add_profile(self, person_data):
        new_person = People(**person_data)
        new_person.last_login = None
        new_person.account_status = 'PENDING'
        new_person.save()
        return new_person

    @staticmethod
    def get_profile_image(person):

        email_hash = hashlib.md5(person.email.encode()).hexdigest()
        profile_icon_url = f'https://www.gravatar.com/avatar/{email_hash}?s=300&d=404'

        # Send a GET request to the URL and get the image content
        response = requests.get(profile_icon_url)

        if response.status_code == 200:
            # Get the static file storage
            storage = FileSystemStorage(location=settings.STATIC_ROOT)

            # Define the file path where the image will be saved
            filename = generate_uuid_filename(person.id)
            file_path = os.path.join(settings.STATIC_ROOT, 'avatar', filename)
            # Save the image file
            try:
                with storage.open(file_path, "wb") as file:
                    file.write(response.content)
            except FileNotFoundError:
                os.makedirs(os.path.join(settings.STATIC_ROOT, 'avatar'))
                with storage.open(file_path, "wb") as file:
                    file.write(response.content)

    def read_and_process_csv(self, csv_file):
        # Read the file content as bytes
        csv_data = csv_file.read()
        # Decode the CSV data bytes into a string using the appropriate encoding
        csv_data_str = csv_data.decode(
            'utf-8')  # Replace 'utf-8' with the actual encoding if different

        # Create a file-like object from the CSV data string using StringIO
        csv_file = StringIO(csv_data_str)
        reader = csv.DictReader(csv_file, delimiter=',')
        People.objects.all().delete()
        records_count = 0
        for row in reader:
            name_parts = row['Name'].split(' ')
            first_name = name_parts[0]
            middle_name = ' '.join(name_parts[1:-1]) if len(name_parts) > 2 else ''
            last_name = name_parts[-1] if len(name_parts) > 1 else ''
            person = People(first_name=first_name.capitalize(),
                            middle_name=middle_name.capitalize(),
                            last_name=last_name.capitalize(),
                            dob=datetime.strptime(row['DOB'], "%d/%m/%Y").date(),
                            gender=row['Gender'].upper(),
                            sms_pref=row['sms_pref'],
                            email_pref=row['email_pref'],
                            email=row['EMail'].lower(),
                            mobile=row['Mobile'],
                            account_status='ACTIVE',
                            )
            person.save()
            self.get_profile_image(person)
            records_count += 1
        return records_count

#
# import json
# import time
#
# from kafka import KafkaProducer
#
# ORDER_KAFKA_TOPIC = "order_detail"
# ORDER_LIMIT = 15
#
# producer = KafkaProducer(bootstrap_servers="localhost:29092")
#
# print("Going to be generating order after 10 seconds")
# print("Will generate one unique order every 5 seconds")
# time.sleep(10)
#
# for i in range(ORDER_LIMIT):
#     data = {
#         "order_id": i,
#         "user_id": f"tom_{i}",
#         "total_cost": i,
#         "items": "burger,sandwich",
#     }
#
#     producer.send("order_details", json.dumps(data).encode("utf-8"))
#     print(f"Done Sending..{i}")
#     time.sleep(5)

# import json
#
# from kafka import KafkaConsumer
# from kafka import KafkaProducer
#
# ORDER_KAFKA_TOPIC = "order_details"
# ORDER_CONFIRMED_KAFKA_TOPIC = "order_confirmed"
#
# consumer = KafkaConsumer(
#     ORDER_KAFKA_TOPIC,
#     bootstrap_servers="localhost:29092"
# )
# producer = KafkaProducer(bootstrap_servers="localhost:29092")
#
# print("Gonna start listening")
# while True:
#     for message in consumer:
#         print("Ongoing transaction..")
#         consumed_message = json.loads(message.value.decode())
#         print(consumed_message)
#         user_id = consumed_message["user_id"]
#         total_cost = consumed_message["total_cost"]
#         data = {
#             "customer_id": user_id,
#             "customer_email": f"{user_id}@gmail.com",
#             "total_cost": total_cost
#         }
#         print("Successful transaction..")
#         producer.send(ORDER_CONFIRMED_KAFKA_TOPIC, json.dumps(data).encode("utf-8"))
