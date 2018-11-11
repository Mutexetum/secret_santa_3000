from django.db import models


class User_s_santa(models.Model):
    REGION = (
        (0, 'РФ'),
        (1, 'Не РФ'),
        (2, '')
        )
    SEND_REGION = (
        (0, 'Только РФ'),
        (1, 'По всему миру'),
        (2, '')
        )    

    username = models.CharField(max_length=200, blank=True, null=True)
    user_id = models.CharField(max_length=200, blank=True, null=True)
    chat_id = models.CharField(max_length=200, blank=True, null=True)
    full_name = models.TextField(blank=True, null=True, default='')
    address = models.TextField(blank=True, null=True, default='')

    about_me = models.TextField(blank=True, null=True, default='')
    i_want = models.TextField(blank=True, null=True, default='')
    i_donnot_want = models.TextField(blank=True, null=True, default='')

    my_region = models.IntegerField(choices=REGION, default=2)
    ready_to_send_to = models.IntegerField(choices=SEND_REGION, default=2)

    my_santa = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True)
    next_step = models.TextField(blank=True, null=True, default='')
#    im_santa_for = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True)


    def __str__(self):
        return 'user {0}'.format(self.user_id)


class States(models.Model):
    application_closed = models.BooleanField(default=False)

    def __str__(self):
        return 'states '



class Notification(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    text = models.TextField(blank=True, null=True, default='')

    def __str__(self):
        return 'Notification sent to users {0}'.format(self.timestamp)
