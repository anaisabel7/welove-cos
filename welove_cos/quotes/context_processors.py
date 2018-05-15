
COMMON_ORIGIN = "City Of Sound"
TYPE_OF_SOURCE = 'song'


def quotes_processor(request):
    quotes_context = {
        'common_origin': COMMON_ORIGIN,
        'type_of_source': TYPE_OF_SOURCE,
    }
    return {'quotes_context': quotes_context}
