

def quotes_processor(request):
    quotes_context = {
        'common_origin': "City Of Sound",
        'type_of_source': 'song',
    }
    return {'quotes_context': quotes_context}
