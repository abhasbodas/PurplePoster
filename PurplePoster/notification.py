#!/usr/bin/python

from PurplePoster import settings
from django.core.management import setup_environ
setup_environ(settings)

from django.db import connection
from EventManager.models import *

def getNotifications():
	cursor = connection.cursor()
	cursor.execute('''
		SELECT
	   		UA.userpreference_id userPreferenceID, 
	  		A.actorName EntityName, P.id PosterID, 'A' flag
		FROM        EventManager_userpreference_actor UA
		INNER JOIN  EventManager_actor A
		ON          A.id = UA.actor_ID
		INNER JOIN  EventManager_movie_actor MA
		ON          MA.actor_id = UA.actor_ID
		INNER JOIN  EventManager_movie M
		ON          M.id = MA.movie_ID 
		INNER JOIN  EventManager_purpleposter P
		ON          M.id = P.movie_ID
		WHERE       P.startTime = CURDATE() + 1
		UNION
		SELECT      UM.userpreference_id, M.name, P.id, 'M' flag
		FROM        EventManager_userpreference_movie UM
		INNER JOIN  EventManager_movie M
		ON          M.id = UM.movie_ID
		INNER JOIN  EventManager_purpleposter P
		ON          M.id = P.movie_ID
		WHERE       P.startTime = CURDATE() + 1
		UNION
		SELECT      UP.userpreference_id, P.alias, P.id, 'P' flag
		FROM        EventManager_userpreference_purplePoster UP
		INNER JOIN  EventManager_purpleposter P
		ON          P.id = UP.purpleposter_ID
		WHERE       P.startTime = CURDATE() + 1
		UNION
		SELECT      UA.userpreference_id, '', P.id, 'L' flag
		FROM        EventManager_userpreference_area UA
		INNER JOIN  EventManager_location L
		ON          UA.location_id = L.id
		INNER JOIN  EventManager_purpleposter P
		ON          P.Locationlat >= L.lat - 0.07 AND L.lat + 0.07
		AND         P.Locationlon BETWEEN L.lon - 0.07 AND L.lon + 0.07
		WHERE       P.startTime = CURDATE() + 1
	''')
	
	alertsByUser = {}
	for (prefid, alertname, posterid, flag) in cursor.fetchall():	
		user = UserPreference.objects.get(pk=prefid).user
		
		if user not in alertsByUser:
			alertsByUser[user] = {
				'user': user,
				'actorAlerts': [],
				'locationAlerts': [],
				'movieAlerts': [],
				'posterAlerts': []
			}
		email = alertsByUser[user]
		
		alertSets = {
			'A': email['actorAlerts'],
			'M': email['movieAlerts'],
			'L': email['locationAlerts'],
			'P': email['posterAlerts']
		}
		
		notification = Alert(posterid, alertname)
		alertSets[flag].append(notification)
		
	return alertsByUser
	
class Alert(object):
	def __init__(self, posterid, name):
		self.poster = PurplePoster.objects.get(pk=posterid)
		self.name = name

from django.template import Context
from django.template.loader import get_template

from django.core.mail import EmailMultiAlternatives

html_email_template = get_template('email.html')
plain_text_template = get_template('emailnohtml.txt')

def render_email(ctx, from_, to):
	c = Context(ctx)
	htmlbody = html_email_template.render(c)
	textbody = plain_text_template.render(c)
	msg = EmailMultiAlternatives(
		'New PurplePosters you might be interested in!',
		textbody,
		from_,
		[to]
	)
	msg.attach_alternative(htmlbody, "text/html")
	return msg
	
'''
def render_email(user, movieAlerts, posterAlerts, actorAlerts, locationAlerts):
	# reeeealy want to use templates for this
	
	email = {
		'to': [user.email],
		'subject': 'New PurplePosters you might be interested in!',
		'body': ''
	}
	
	def write(s):
		email['body'] += s + '\n'
	
	for (poster, moviename) in movieAlerts:
		write('movie %s' % poster)
		
	for (poster, pname) in posterAlerts:
		write('poster %s' % poster)
		
	for (poster, aname) in actorAlerts:
		write('actor %s in %s' % (aname, poster))
		
	return email
'''
	
from django.core.mail import send_mail

if __name__ == "__main__":
	emails = getNotifications()
	for alert in emails.values():
		email = render_email(alert, 
			'PurplePoster <purpleposter@jpochtar.cs.columbia.edu>', 
			alert['user'].email
		)
		email.send()		
	
	
	
