from .models import Message

COMMON_ORIGIN = "City Of Sound"
TYPE_OF_SOURCE = 'song'


def quotes_processor(request):
    quotes_context = {
        'common_origin': COMMON_ORIGIN,
        'type_of_source': TYPE_OF_SOURCE,
    }
    return {'quotes_context': quotes_context}


def message_processor(request):
    try:
        displayed_message = Message.objects.filter(
            displayed=True)[0].message_text
    except IndexError:
        displayed_message = None
    message_context = {
        'message': displayed_message
    }
    return {'message_context': message_context}
