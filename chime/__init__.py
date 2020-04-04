import boto3
import os
from typing import Dict, Tuple
import uuid

def get_client_from_env():
  return get_client(os.environ['CHIME_API_KEY'], os.environ['CHIME_API_SECRET'])

def get_client(key: str, secret: str):
  return boto3.client('chime', aws_access_key_id=key, aws_secret_access_key=secret)

def create_meeting(client, unique_id: str=None, region='ap-southeast-1', notifications: dict=None) -> Tuple:
  unique_id = unique_id or str(uuid.uuid4())
  notifications = notifications or {}
  return (unique_id, client.create_meeting(
    ClientRequestToken=unique_id,
    MediaRegion=region,
    NotificationsConfiguration=notifications
  ))

def create_attendee(client, meeting_id, unique_id: str=None):
  """Create an attendee

  Return
  ------
  unique_id, attendee: {'AttendeeId': '914c1ed5-9287-429d-9b83-bdb6d1640fd8',
  'ExternalUserId': 'e67aaf51-ecd6-4983-bc66-95e213c76bbc',
  'JoinToken': 'OTE0YzFlZDUtOTI4Ny00MjlkLTliODMtYmRiNmQxNjQwZmQ4OjBiYzM3NGY5LTBkNDYtNGNlMS05ODY5LTZjNzExMWVkZGI5Mw'}
  """
  unique_id = unique_id or str(uuid.uuid4())
  response = client.create_attendee(MeetingId=meeting_id, ExternalUserId=unique_id)
  return unique_id, response['Attendee']