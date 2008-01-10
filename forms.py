"""                                     .. 
                                 .,::;::::::
                           ..,::::::::,,,,:::      Jutda Helpdesk - A Django
                      .,,::::::,,,,,,,,,,,,,::     powered ticket tracker for
                  .,::::::,,,,,,,,,,,,,,,,,,:;r.        small enterprise
                .::::,,,,,,,,,,,,,,,,,,,,,,:;;rr.
              .:::,,,,,,,,,,,,,,,,,,,,,,,:;;;;;rr      (c) Copyright 2008
            .:::,,,,,,,,,,,,,,,,,,,,,,,:;;;:::;;rr
          .:::,,,,,,,,,,,,,,,,,,,,.  ,;;;::::::;;rr           Jutda
        .:::,,,,,,,,,,,,,,,,,,.    .:;;:::::::::;;rr
      .:::,,,,,,,,,,,,,,,.       .;r;::::::::::::;r;   All Rights Reserved
    .:::,,,,,,,,,,,,,,,        .;r;;:::::::::::;;:.
  .:::,,,,,,,,,,,,,,,.       .;r;;::::::::::::;:.
 .;:,,,,,,,,,,,,,,,       .,;rr;::::::::::::;:.   This software is released 
.,:,,,,,,,,,,,,,.    .,:;rrr;;::::::::::::;;.  under a limited-use license that
  :,,,,,,,,,,,,,..:;rrrrr;;;::::::::::::;;.  allows you to freely download this
   :,,,,,,,:::;;;rr;;;;;;:::::::::::::;;,  software from it's manufacturer and
    ::::;;;;;;;;;;;:::::::::::::::::;;,  use it yourself, however you may not
    .r;;;;:::::::::::::::::::::::;;;,  distribute it. For further details, see
     .r;::::::::::::::::::::;;;;;:,  the enclosed LICENSE file.
      .;;::::::::::::::;;;;;:,.
       .;;:::::::;;;;;;:,.  Please direct people who wish to download this
        .r;;;;;;;;:,.  software themselves to www.jutda.com.au.
          ,,,..

$Id$

"""

from django import newforms as forms
from helpdesk.models import Ticket, Queue, FollowUp
from django.contrib.auth.models import User
from datetime import datetime

class TicketForm(forms.Form):
    queue = forms.ChoiceField(label=u'Queue', required=True, choices=())

    title = forms.CharField(max_length=100, required=True,
                           widget=forms.TextInput(),
                           label=u'Summary of the problem')
    
    submitter_email = forms.EmailField(required=False,
                            label=u'Submitter E-Mail Address')
    
    body = forms.CharField(widget=forms.Textarea(),
                           label=u'Description of Issue', required=True)
    
    assigned_to = forms.ChoiceField(choices=(), required=False,
                           label=u'Case owner')

    priority = forms.ChoiceField(choices=Ticket.PRIORITY_CHOICES,
                            required=False,
                            initial='3',
                            label=u'Priority')
    
    def save(self, user):
        """
        Writes and returns a Ticket() object
        
        """
        q = Queue.objects.get(id=int(self.cleaned_data['queue']))
        t = Ticket( title=self.cleaned_data['title'], 
                    submitter_email=self.cleaned_data['submitter_email'],
                    created=datetime.now(),
                    status = Ticket.OPEN_STATUS,
                    queue = q,
                    description = self.cleaned_data['body'],
                    priority = self.cleaned_data['priority'],
                  )
        if self.cleaned_data['assigned_to']:
            try:
                u = User.objects.get(id=self.cleaned_data['assigned_to'])
                t.assigned_to = u
            except:
                t.assigned_to = None
        t.save()

        f = FollowUp(   ticket=t,
                        title='Ticket Opened',
                        date=datetime.now(),
                        public=True,
                        comment=self.cleaned_data['body'],
                        user=user,
                     )
        if self.cleaned_data['assigned_to']:
            f.title = 'Ticket Opened & Assigned to %s' % t.get_assigned_to

        f.save()

        return t
