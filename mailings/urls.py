from django.urls import path

from mailings.apps import MailingsConfig
from mailings.views import RecipientCreateView, RecipientUpdateView, RecipientDetailView, RecipientDeleteView, \
    MessageCreateView, MessageUpdateView, MessageDetailView, MessageDeleteView, MailingCreateView, MailingUpdateView, \
    MailingDetailView, MailingDeleteView, HomePageView, MailingAttemptListView, SendMailingView, \
    MailingAttemptDetailView, MailingDisableView, MailingListView, RecipientListView, MessageListView, MailingBlockView

app_name = MailingsConfig.name

urlpatterns = [
    path("recipient/create/", RecipientCreateView.as_view(), name="recipient_create"),
    path("recipient/update/<int:pk>/", RecipientUpdateView.as_view(), name="recipient_update"),
    path("recipient/detail/<int:pk>/", RecipientDetailView.as_view(), name="recipient_detail"),
    path("recipient/delete/<int:pk>/", RecipientDeleteView.as_view(), name="recipient_delete"),
    path('recipients/', RecipientListView.as_view(), name='recipient_list'),
    path("message/create/", MessageCreateView.as_view(), name="message_create"),
    path("message/update/<int:pk>/", MessageUpdateView.as_view(), name="message_update"),
    path("message/detail/<int:pk>/", MessageDetailView.as_view(), name="message_detail"),
    path("message/delete/<int:pk>/", MessageDeleteView.as_view(), name="message_delete"),
    path('messages/', MessageListView.as_view(), name='message_list'),
    path("mailing/create/", MailingCreateView.as_view(), name="mailing_create"),
    path("mailing/update/<int:pk>/", MailingUpdateView.as_view(), name="mailing_update"),
    path("mailing/detail/<int:pk>/", MailingDetailView.as_view(), name="mailing_detail"),
    path("mailing/delete/<int:pk>/", MailingDeleteView.as_view(), name="mailing_delete"),
    path('mailing/disable/<int:pk>/', MailingDisableView.as_view(), name='disable_mailing'),
    path('mailings/', MailingListView.as_view(), name='mailing_list'),
    path('mailing/<int:pk>/block/', MailingBlockView.as_view(), name='mailing_block'),
    path("home/", HomePageView.as_view(), name="home"),
    path("attempts/list", MailingAttemptListView.as_view(), name="attempts_list"),
    path('attempt/<int:pk>/', MailingAttemptDetailView.as_view(), name='attempt_detail'),
    path("mailing/send/<int:pk>/", SendMailingView.as_view(), name="send_mailing"),
]
