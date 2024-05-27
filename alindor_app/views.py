from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from PyPDF2 import PdfReader
import openai
import logging
import re

from .models import Candidate, JobDescription
from .serializers import CandidateSerializer, JobDescriptionSerializer

# Set the OpenAI API key
# openai.api_key = 'sk-proj-EHuASXsFy6RkWqqSahmpT3BlbkFJQBushXcrfiVVpCtsUnpT'

@api_view(['POST'])
@parser_classes([MultiPartParser])
def process_cv(request):
    """
    Handle a POST request to process a candidate's CV and job description.
    """
    # Retrieve the files from the request
    cv_file = request.FILES.get('cv_file')
    job_file = request.FILES.get('job_file')

    # Check if both files are provided
    if not cv_file or not job_file:
        return Response({'error': 'Both CV and job description files are required.'}, status=status.HTTP_400_BAD_REQUEST)

    # Read CV text from PDF file
    cv_text = ""
    try:
        reader = PdfReader(cv_file)
        for page in reader.pages:
            cv_text += page.extract_text()
    except Exception as e:
        logging.error(f"Error reading CV file: {e}")
        return Response({'error': 'Failed to read CV file.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Read job description text from PDF file
    job_text = ""
    try:
        reader = PdfReader(job_file)
        for page in reader.pages:
            job_text += page.extract_text()
    except Exception as e:
        logging.error(f"Error reading job description file: {e}")
        return Response({'error': 'Failed to read job description file.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Create the prompt for the OpenAI API
    prompt = f"Given the candidate's CV: {cv_text}\n\nAnd the job description: {job_text}\n\nEvaluate the candidate's suitability for the role. Provide a score from 1 to 10 and a 2-4 sentence explanation for the score."

    try:
        # Call the OpenAI API
        response = openai.ChatCompletion.create(
            model='gpt-4-turbo',
            messages=[
                {
                    'role': 'system',
                    'content': 'You are an expert hiring manager assessing candidates based on their CVs and job descriptions.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            max_tokens=150,
            temperature=0.7
        )
        print(response)
        # Process OpenAI's response
        ai_response = response['choices'][0]['message']['content'].strip()
        print("AI response: ",ai_response)

        # Parse the AI response
        # Use regular expressions to match score and explanation
        score_match = re.search(r'Score: (\d+)', ai_response, re.IGNORECASE)
        print("sm: ",score_match)

# Extract the score if a match is found
#         score = int(score_match.group(1)) if score_match else None
        explanation_match = re.search(r'Score: \d+\/10\s*([\s\S]+)', ai_response, re.IGNORECASE)
        print("...",explanation_match)
#         explanation_match = ai_response.strip()  

          # Extract explanation
        if explanation_match:
          explanation = explanation_match.group(1).strip()
        else:
          # If no match, take the entire response as explanation
          explanation = ai_response.strip()

        if score_match:
            score = score_match.group(1)
        else:
          #   logging.error(f"Failed to extract score from AI response: {ai_response}")
            return Response({'error': 'Failed to extract score from AI response, Please try again'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if explanation_match:
            explanation = explanation_match.group(1).strip()
        else:
          #   logging.error(f"Failed to extract explanation from AI response: {ai_response}")
            return Response({'error': 'Failed to extract explanation from AI response, Please try again'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Return the AI response as JSON
        return Response({
            'score': score,
            'explanation': explanation
          }, status=status.HTTP_200_OK)

    except Exception as e:
#         logging.error(f"Error with OpenAI API: {e}")
        return Response({'error': 'Failed to process the request'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
