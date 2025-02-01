from django.http import JsonResponse
# from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from .models import QuizData
import json

@csrf_exempt # Only for testing! Remove in production
def receive_data(request):
    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': 'Only POST requests are allowed'
        }, status=405)
    
    try:
        # Parse incoming JSON data
        data = json.loads(request.body)

        # Wrap database operations in a transaction
        with transaction.atomic():
            # Create new record
            quiz = QuizData.objects.create(
                title=data.get('title', 'Untitled')
                # Add other fields as needed
            )

        return JsonResponse({
            'status': 'success',
            'message': 'Data received and stored',
            'record_id': quiz.id
        })
    
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data'
        }, status=400)
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
