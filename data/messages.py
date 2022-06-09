MESSAGES = {

    # base_commands

    'start': "Glad to see you!\n"
             "Select one of the available commands 👇",

    'menu': "Main menu, choose one of the available commands 👇",

    'help_admin': "<b>Available commands<b>\n\n"
                  "<b>Send notifications:</b>\n\n"
                  "/inform - <em>send notification to masters and/or customers</em>\n\n"
                  "<b>Manage masters:</b>\n\n"
                  "/add_master - <em>add new master</em>\n"
                  "/fire_master - <em>fire existing master</em>\n\n"
                  "<b>View statistics:</b>\n\n"
                  "/statistic - <em>view statistic</em>",

    'help_master': "<b>Available commands</b>\n\n"
                   "<b>Profile managing:</b>\n\n"
                   "/profile - <em>view personal profile</em>\n"
                   "/update_info - <em>update profile info</em>\n"
                   "/profile_photo - <em>upload profile photo</em>\n"
                   "/portfolio_photo - <em>upload portfolio photo</em>\n\n"
                   "<b>Timetable managing:</b>\n\n"
                   "/timetable - <em>view timetable</em>",

    'help_customer': "<b>Available commands</b>\n\n"
                     "/masters - <em>view list of masters, choose master, "
                     "continue with portfolio browsing or with booking chosen master</em>\n\n"
                     "/visits - <em>view your upcoming or previous visits, "
                     "you can chose upcoming visit and cancel it if needed</em>\n\n"
                     "/contact - <em>view contact information</em>",

    # contact_info

    'contact_info': "<b>{}</b>\n\n"
                    "📍 {}\n\n"
                    "🕑 {}\n\n"
                    "📞 {}",

    # customer_commands

    'master_list': "<b>Chose one of the available masters</b>\n",

    'alert_no_master': "Unfortunately, there are no masters added yet",

    'master_info': "<b>Name:</b> {}\n"
                   "<b>Info:</b> {}\n\n"
                   'Please take a look on the masters best works by pressing the <b>"Portfolio"</b> button\n\n'
                   'If you want to book this Master, please, press <b>"Book master"</b> button',

    'set_day': "You have decided to book <b>{}</b>\n"
               "Please choose the day!",

    'set_time': "<b>Note:</b>\n\n"
                "You are trying to view available slots on\n"
                "<b>{}</b> for <b>{}</b>\n"
                "Please, select the available one!",

    'alert_past': "You can't navigate to the past",

    'alert_day_off': "This is masters day off",

    'alert_booked': "This timeslot is already booked",

    'confirm_booking': "<b>Alert:</b>\n\n"
                       "You are trying to book <b>{}</b> on "
                       "<b>{}</b> at <b>{}:00</b>\n"
                       'Press the <b>"Confirm booking"</b> to proceed\n'
                       'or <b>"Cancel"</b> if you want to abort booking',

    'book_success': "<b>You have successfully booked {}!</b>\n"
                    "Pleased to see you on {} at {}:00",

    'book_notify_master': "<b>Notification:</b>\n\n"
                          "You have gotten a new booking\n\n"
                          "<b>Date:</b> {}\n"
                          "<b>Time:</b> {}:00\n"
                          "<b>Customer:</b> {}, {}",

    'alert_no_master_chat_id': "<b>Alert:</b>\n\n"
                               "Notification has not been sent! Masters telegram account is unavailable. "
                               "Please call us {}",

    'alert_duplication': "<b>Alert:</b>\n\n"
                         "You already have visit at this time! Browse your visits for more details\n"
                         "Please, chose another timeslot",

    'send_contact': 'Please send us your phone number by pressing <b>"Send contact"</b> button',

    'alert_no_photos': '{} has no portfolio photos yet',

    # customer_visits

    'upcoming_visits': "<b>Upcoming visits:</b>\n\n"
                       "<em>HINT: if you want to view details or cancel upcoming visit, click on needed one</em>",

    'alert_no_upcoming_visits': "Unfortunately, you have no upcoming visits\n\n {}",

    'archive': 'Press <b>"Archive"</b> to view previous visits\n\n'
               'Press <b>"Back"</b> to main menu',

    'alert_no_visits': "Unfortunately, you have no visits yet",

    'visit_detail': "<b>Master:</b> {}\n"
                    "<b>Date:</b> {}\n"
                    "<b>Time:</b> {}\n"
                    "<b>Master info:</b> {}",

    'visit_cancel_notify_master': "<b>Notification:</b>\n\n"
                                  "Customer has been canceled his visit\n\n"
                                  "Timeslot <b>{}, {}</b> is now free",

    'alert_visit_cancel_no_master_chat_id': "<b>Alert:</b>\n\n"
                                            "Notification about visit cancellation has not been "
                                            "sent to <b>{}</b> automatically\n\n"
                                            "Please, call <b>{}</b> to inform us about cancellation",

    'visit_cancel_success': "Visit has been successfully canceled",

    'previous_visits': "<b>Previous visits:</b>",

    'previous_visits_info': "\n\n<b>Master:</b> {}\n"
                            "<b>Date:</b> {}\n"
                            "<b>Time:</b> {}",

    'alert_no_previous_visits': "Unfortunately, you have no previous visits yet",

    # manage_masters

    'select_action': "Select action",

    'set_chat_id': "Enter master's telegram chat id\n\n"
                   "<em>HINT: use only numbers</em>",

    'reinstate': "<b>Notification:</b>\n\n"
                 "You have reinstate a fired employee",

    'set_name': "Enter master's full name\n\n"
                "<em>HINT: need to contain firstname and lastname</em>",

    'set_phone': "Enter master's phone number\n\n"
                 '<em>HINT: valid format "+380[phone number]"</em>',

    'set_info': "Enter master's info\n\n"
                "<em>HINT: up to 200 characters</em>",

    'add_master_success': "<b>Notification:</b>\n\n"
                          "Master has been successfully added",

    'select_master': "Select the master you want to fire",

    'fire_confirm': "Do you really want to fire this master?",

    'fire_notify_customer': "<b>Notification:</b>\n\n"
                            "The master {} is no longer working in our salon.\n"
                            "For this reason all your visits to this master were cancelled.\n"
                            "Please choose another one and book him.\n\n"
                            "We apologize for the inconvenience.",

    'alert_fire_no_master_chat_id': "<b>Alert:</b>\n\n"
                                    "Notification about visits cancellation due to the dismissal of the "
                                    "master has not been sent to <b>{}, "
                                    "phone number: {} </b> automatically.",

    'fire_master_success': "<b>Notification:</b>\n\n"
                           "Master has been successfully fired.",

    # master_profile

    'master_profile': "<b>Name:</b> {}\n"
                      "<b>Phone number:</b> {}\n"
                      "<b>Info:</b> {}",

    'profile_update_success': "Profile info has been successfully updated",

    'set_photo': "Attach a photo and send it\n\n"
                 "<em>HINT: takes only one photo</em>",

    'profile_photo_update_success': "Profile photo has been successfully uploaded",

    'portfolio_photo_upload_success': "Photo has been successfully added to your portfolio",

    # master_timetable

    'set_day_master': "Choose day to view your schedule",

    'day_schedule': "Here is your schedule on <b>{}</b>",

    'alert_day_off_master': "This is your day off. Enjoy!",

    'make_day_off_success': "You have successfully made day off! Enjoy it",

    'cancel_booking_confirm': "Do you want to cancel booking?",

    'master_book_timeslot_confirm': "You are trying to book {}:00 timeslot.\n"
                                    'Press the <b>"Confirm booking"</b> or <b>"Cancel"</b>',

    'master_visit_cancel_notify_customer': "<b>Notification:</b>\n\n"
                                        "Master has canceled your visit on\n"
                                        "<b>{}</b> at <b>{}</b>",

    'master_visit_cancel_success': "Visit has been successfully canceled",

    'customer_duplication_alert': "<b>Alert:</b>\n\n"
                                  "Customer already has visit at this time!\n"
                                  "Please, chose another timeslot",

    'set_customer_name': "Please enter customers name",

    'book_timeslot_success': "<b>You have successfully booked timeslot for {}!</b>\n"
                             "Wait to see him on {} at {}:00",

    # send_notifications

    'select_recipients': "Select recipients",

    'set_notification': "Enter the text of the notification\n\n"
                        "<em>HINT: can not be a command</em>",

    'check_notification': "Your notification is:\n\n"
                          '<em><b>"{}"</b></em>\n\n'
                          "Send this notification?",

    'change_notification': "Please, re-enter the text of the notification",

    'admin_notification': "<b>Notification from administrator:</b>\n\n"
                          '<em>"{}"</em>\n\n'
                          "Wish you a good day!",

    'alert_no_recipient_chat_id': "<b>Alert:</b>\n\n"
                              "Notification has not been sent to <b>{}</b>, phone number: <b>{}</b>",

    # other

    'notify_admins': "<b>Notification:</b>\n\n" "Bot is up and running",

    'customer_reminder': "<b>Reminder:</b>\n\n"
                         "You have upcoming visit in half an hour\n\n"
                         "We are looking forward to meeting you!",

    'alert_reminder_no_chat_id': "<b>Alert:</b>\n\n"
                                 "Reminder has not been sent to <b>{}</b>, "
                                 "phone number: <b>{}</b>",
}


def get_message(message_key: str):
    return MESSAGES[message_key]
