from curses import flash
from click import prompt
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from exam.forms import QuestionForm
from .models import ContactMessage, Course, Question, Result
from django.contrib.auth.models import User
from django.contrib import messages 
from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import Group
from django.contrib.auth import logout
from .forms import StudentSignUpForm
from .forms import TeacherSignUpForm
from .forms import CourseForm 
from django.db.models import Sum
import google.generativeai as genai
import json
import re
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.db.models import Avg
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from django.http import FileResponse
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from reportlab.lib import colors
from django.conf import settings
import os
from django.contrib.staticfiles import finders
from .predictor import predict_next_score
from .ai_generator import generate_questions_from_pdf, generate_questions_from_ai
from django.http import JsonResponse
from .ai_tutor import get_ai_tutor_response



def student_login(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(username=u, password=p)
        
        if user is not None:
            # Check if the user is in the STUDENT group
            if user.groups.filter(name='STUDENT').exists():
                login(request, user)
                return redirect('student-dashboard')
            else:
                messages.error(request, "Access Denied: You are not registered as a Student.")
        else:
            messages.error(request, "Invalid username or password.")
            
    return render(request, 'student_login.html')

def teacher_login(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(username=u, password=p)
        
        if user is not None:
            # Check if the user is in the TEACHER group
            if user.groups.filter(name='TEACHER').exists():
                login(request, user)
                return redirect('teacher-dashboard')
            else:
                messages.error(request, "Access Denied: You are not registered as a Teacher.")
        else:
            messages.error(request, "Invalid username or password.")
            
    return render(request, 'teacher_login.html')



def admin_add_course_view(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('teacher-dashboard')
    else:
        form = CourseForm()
    return render(request, 'admin_add_course.html', {'form': form})

def is_teacher(user):
    return user.groups.filter(name='TEACHER').exists()

@login_required
@user_passes_test(is_teacher,login_url='student-dashboard')
def teacher_dashboard(request):
    dict = {
        'total_student': User.objects.all().filter(groups__name='STUDENT').count(),
        'total_course': Course.objects.all().count(),
        'total_question': Question.objects.all().count(),
    }
    return render(request, 'teacher_dashboard.html', context=dict)



@login_required
def take_exam(request, pk):
    course = Course.objects.get(id=pk)
    questions = Question.objects.all().filter(course=course)
    
    if request.method == 'POST':
        selected_answers = request.POST
        score = 0
        for q in questions:
            # Check if student's answer matches DB answer
            if q.answer == selected_answers.get(str(q.id)):
                score += q.marks
        
        Result.objects.create(student=request.user, exam=course, marks=score)
        return redirect('student-dashboard')

    return render(request, 'take_exam.html', {'course': course, 'questions': questions})

@login_required
@user_passes_test(is_teacher)
def add_question_view(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Question added successfully!")
            return redirect('teacher-dashboard')
    else:
        form = QuestionForm()
    return render(request, 'add_question.html', {'form': form})





@login_required
def student_dashboard(request):
    # 1. Fetch data
    courses = Course.objects.all()
    results = Result.objects.filter(student=request.user).order_by('date')
    
    # 2. Data for the Chart (Performance Growth)
    # Humein labels (Exam Names) aur data (Marks) chahiye
    labels = [r.exam.course_name for r in results]
    scores = [r.marks for r in results]
    
    # Calculate Average Score (Optional for the stats card)
    avg_marks = results.aggregate(Avg('marks'))['marks__avg'] or 0
    predicted_score = predict_next_score(request.user)

    # 3. Context dictionary
    context = {
        'courses': courses,
        'results': results,
        'total_exams': results.count(),
        'total_course': courses.count(),
        'avg_marks': round(avg_marks, 1),

        # Predicted score for the next exam
        'predicted_score': predicted_score,
        
        # KEY ADDITIONS: JSON data for Chart.js
        'labels': json.dumps(labels),
        'scores': json.dumps(scores),
    }
    
    return render(request, 'student_dashboard.html', context)


def leaderboard_view(request):
    # Get total marks for each student and order them by highest first
    # We use Sum to aggregate marks if a student has taken multiple exams
    top_performers = Result.objects.values(
        'student__username', 'student__first_name', 'student__last_name'
    ).annotate(
        total_score=Sum('marks')
    ).order_by('-total_score')[:10]  # Get the Top 10

    return render(request, 'leaderboard.html', {'top_performers': top_performers})


def contactus_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Saving to Database
        ContactMessage.objects.create(name=name, email=email, subject=subject, message=message)
        
        messages.success(request, 'Your message has been sent successfully!')
        return redirect('contactus')
    
    return render(request, 'contactus.html')



@login_required
def download_result_pdf(request, pk):
    # 1. Pehle Result ko check karein ki exist karta hai ya nahi
    if request.user.is_staff:
        # Teacher kisi bhi ID ka result download kar sakta hai
        result = get_object_or_404(Result, id=pk)
    else:
        # Student sirf wahi result dekh sakta hai jo uska apna ho
        result = get_object_or_404(Result, id=pk, student=request.user)
    
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)

    # Design the PDF
    p.setFont("Helvetica-Bold", 24)
    p.drawString(2 * inch, 10 * inch, "Official Exam Result")
    
    p.setFont("Helvetica", 14)
    p.line(1 * inch, 9.5 * inch, 7.5 * inch, 9.5 * inch)
    
    # Use get_full_name if available for a more professional look
    name = result.student.get_full_name() or result.student.username
    
    p.drawString(1 * inch, 8.5 * inch, f"Student Name: {name}")
    p.drawString(1 * inch, 8.0 * inch, f"Exam: {result.exam.course_name}")
    p.drawString(1 * inch, 7.5 * inch, f"Score Obtained: {result.marks}")
    p.drawString(1 * inch, 7.0 * inch, f"Total Marks: {result.exam.total_marks}")
    p.drawString(1 * inch, 6.5 * inch, f"Date: {result.date.strftime('%Y-%m-%d %H:%M')}")

    # Add a Pass/Fail status to PDF
    # Purani status line ko isse replace karein:
    
    # 1. Calculation Logic (Dynamic 40% threshold)
    total = float(result.exam.total_marks)
    obtained = float(result.marks)
    passing_mark = total * 0.4
    status = "PASSED" if obtained >= passing_mark else "FAILED"

    # 2. Status Color Setting
    if status == "PASSED":
        p.setFillColorRGB(0, 0.5, 0)  # Dark Green
    else:
        p.setFillColorRGB(0.8, 0, 0)  # Red

    # 3. Status Draw karna
    p.setFont("Helvetica-Bold", 14)
    p.drawString(1 * inch, 6.0 * inch, f"Status: {status}")

    # 4. Color reset karein (taaki footer black hi rahe)
    p.setFillColorRGB(0, 0, 0)

    # Add a Footer
    p.setFont("Helvetica-Oblique", 10)
    p.drawString(1 * inch, 1 * inch, "Generated by Online Examination System - 2026")

    # Close the PDF object cleanly.
    p.showPage()
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers download it.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f'Result_{result.student.username}_{result.exam.course_name}.pdf')

@login_required
@user_passes_test(is_teacher)
def view_questions_view(request):
    questions = Question.objects.all().order_by('course')
    return render(request, 'view_questions.html', {'questions': questions})

@login_required
@user_passes_test(is_teacher)
def delete_question_view(request, pk):
    question = Question.objects.get(id=pk)
    question.delete()
    messages.info(request, "Question deleted successfully.")
    return redirect('view-questions')

def logout_view(request):
    logout(request)
    return redirect('home')



def about(request):
    return render(request, 'aboutus.html')

def student_signup(request):
    if request.method == 'POST':
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password']) # Hashes the password
            user.save()
            
            # Automatically assign to STUDENT group
            student_group, created = Group.objects.get_or_create(name='STUDENT')
            user.groups.add(student_group)
            
            messages.success(request, "Account created! You can now login.")
            return redirect('student-login')
    else:
        form = StudentSignUpForm()
    return render(request, 'student_signup.html', {'form': form})




def teacher_signup_view(request):
    if request.method == 'POST':
        form = TeacherSignUpForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])

            # Make this user a teacher
            user.is_staff = True

            user.save()

            # Add to Teacher group
            group, created = Group.objects.get_or_create(name='TEACHER')
            user.groups.add(group)

            return redirect('teacher-login')

    else:
        form = TeacherSignUpForm()

    return render(request, 'teacher_signup.html', {'form': form})




# Security Check
@login_required
def teacher_dashboard_view(request):
    if not request.user.groups.filter(name='TEACHER').exists():
        return redirect('student-dashboard')

    # Fetch Data for Stats and Course Table ONLY
    courses_list = Course.objects.all()
    questions_count = Question.objects.all().count()
    results_count = Result.objects.all().count()
    
    # We do NOT include 'results' here so the history stays hidden on the dashboard
    context = {
        'courses': courses_list,
        'total_courses': courses_list.count(),
        'total_questions': questions_count,
        'total_results': results_count,
    }
    
    return render(request, 'teacher_dashboard.html', context)

@login_required
def view_result_view(request):
    # Logic for the dedicated results page
    if request.user.is_staff:
        # Teachers see every student's history and violations
        results = Result.objects.all().select_related('student', 'exam').order_by('-date')
    else:
        # Students see only their own history
        results = Result.objects.filter(student=request.user).order_by('-date')
        
    return render(request, 'view_result.html', {'results': results})

def home(request):
    return render(request, 'home.html')

def base(request):
    return render(request, 'base.html')

@login_required
def view_result(request):
    results = Result.objects.all().filter(student=request.user)
    return render(request, 'view_result.html', {'results': results})

def view_students(request):
    students = User.objects.all().filter(groups__name='STUDENT')
    return render(request, 'view_students.html', {'students': students})

def view_courses(request):
    courses = Course.objects.all()
    return render(request, 'view_courses.html', {'courses': courses})



def delete_question(request, pk):
    question = Question.objects.get(id=pk)
    question.delete()
    return redirect('view-questions')

def edit_question(request, pk):
    question = Question.objects.get(id=pk)
    if request.method == 'POST':
        # Logic to update question based on form data
        pass
    return render(request, 'edit_question.html', {'question': question})



@login_required
def calculate_marks_view(request, pk):
    course = get_object_or_404(Course, id=pk)
    questions = Question.objects.filter(course=course)
    
    total_marks = 0
    
    for q in questions:
        # FIX: We must use the Question ID (q.id) to match the HTML 'name' attribute
        selected_ans_value = request.POST.get(str(q.id))
        
        # We need to find which option text (Option1, Option2...) was chosen
        # because the database stores the text (e.g., "Python"), not the label "Option1"
        selected_answer_text = None
        if selected_ans_value == "Option1":
            selected_answer_text = q.option1
        elif selected_ans_value == "Option2":
            selected_answer_text = q.option2
        elif selected_ans_value == "Option3":
            selected_answer_text = q.option3
        elif selected_ans_value == "Option4":
            selected_answer_text = q.option4

        # Compare the selected text with the actual answer in the database
        # We use .strip() to remove any accidental spaces
        if selected_answer_text and q.answer.strip() == selected_answer_text.strip():
            total_marks += q.marks
            
    # Get violation count
    violations_detected = request.POST.get('violation_count', 0)
            
    # Save the result
    Result.objects.create(
        student=request.user, 
        exam=course, 
        marks=total_marks,
        violations=violations_detected
    )
    
    messages.success(request, f'Exam for {course.course_name} submitted! Score: {total_marks}')
    return redirect('student-dashboard')
def admin_add_question_view(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('teacher-dashboard')
    else:
        form = QuestionForm()
    return render(request, 'admin_add_question.html', {'form': form})


def admin_view_question_view(request, pk):
    course = Course.objects.get(id=pk)
    questions = Question.objects.all().filter(course=course)
    return render(request, 'admin_view_question.html', {
        'course': course,
        'questions': questions
    })


# This must match the name used in urls.py (views.delete_result_view)
def delete_result_view(request, pk):
    result = get_object_or_404(Result, id=pk)
    result.delete()
    return redirect('teacher-dashboard')

# Configure your API Key


genai.configure(api_key=settings.GEMINI_API_KEY)
def generate_ai_questions_views(request): 
    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        topic = request.POST.get('topic')
        num_questions = request.POST.get('num_questions')
        course = Course.objects.get(id=course_id)
       

        prompt = f"""
        Generate {num_questions} multiple choice questions about {topic}.
        Return the result ONLY as a JSON list of objects with these keys:
        'question', 'option1', 'option2', 'option3', 'option4', 'answer'.
        The 'answer' must match one of the options exactly.
        """
        
        try:
            # Using gemini-pro for stability on older SDKs
            # Some environments require this specific alias
            model = genai.GenerativeModel("gemini-2.5-pro")
            response = model.generate_content(prompt)
            
            # --- STRONGER JSON EXTRACTION ---
            # This looks for the content between the first [ and the last ]
            content = response.text
            match = re.search(r'\[.*\]', content, re.DOTALL)
            
            if match:
                raw_json = match.group()
                data = json.loads(raw_json)

                for item in data:
                    Question.objects.create(
                        course=course,
                        marks=2,
                        question=item.get('question'),
                        option1=item.get('option1'),
                        option2=item.get('option2'),
                        option3=item.get('option3'),
                        option4=item.get('option4'),
                        answer=item.get('answer')
                    )
                return redirect('admin-view-question', pk=course.id)
            else:
                return render(request, 'error.html', {'message': "AI response did not contain a valid list."})

        except Exception as e:
            # Log the actual error to your terminal so you can see it
            print(f"AI Error: {e}")
            return render(request, 'error.html', {'message': f"Technical Error: {str(e)}"})

    courses = Course.objects.all()
    return render(request, 'ai_generate.html', {'courses': courses})




@login_required
def download_certificate(request, pk):
    result = get_object_or_404(Result, id=pk, student=request.user)
    
    # Passing Logic: 50% marks required for certificate
    if result.marks < (result.exam.total_marks * 0.5):
        return redirect('student-dashboard')

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=landscape(letter))
    width, height = landscape(letter)

    # 1. Background Border (Double Border for premium look)
    p.setStrokeColor(colors.darkblue)
    p.setLineWidth(3)
    p.rect(20, 20, width-40, height-40)
    p.setStrokeColor(colors.gold)
    p.setLineWidth(1)
    p.rect(25, 25, width-50, height-50)

    # 2. Add Logo (Center Top)
    # Make sure 'logo.png' exists in your static folder
    logo_relative_path = 'images/logo.png' 
    logo_path = finders.find(logo_relative_path)
    if os.path.exists(logo_path):
        p.drawImage(logo_path, width/2 - 40, height - 110, width=80, height=80, mask='auto')

    # 3. Main Headings
    p.setFillColor(colors.darkblue)
    p.setFont("Helvetica-Bold", 45)
    p.drawCentredString(width/2, height - 180, "CERTIFICATE OF COMPLETION")
    
    p.setFillColor(colors.black)
    p.setFont("Helvetica", 20)
    p.drawCentredString(width/2, height - 220, "This proudly presented to")

    # 4. Student Name
    p.setFillColor(colors.darkred)
    p.setFont("Helvetica-BoldOblique", 35)
    name = result.student.get_full_name() or result.student.username
    p.drawCentredString(width/2, height - 280, name.upper())

    # 5. Course & Score Details
    p.setFillColor(colors.black)
    p.setFont("Helvetica", 18)
    p.drawCentredString(width/2, height - 330, f"for successfully passing the online examination in")
    
    p.setFont("Helvetica-Bold", 24)
    p.drawCentredString(width/2, height - 370, result.exam.course_name.upper())

    p.setFont("Helvetica", 16)
    p.drawCentredString(width/2, height - 420, f"Achievement Score: {result.marks} / {result.exam.total_marks}")
    p.drawCentredString(width/2, height - 450, f"Issued on: {result.date.strftime('%d %B, %Y')}")

    # 6. Digital Signature Section
    # Yahan hum ek signature line aur text add karenge
    p.setStrokeColor(colors.black)
    p.setLineWidth(1)
    
    # Principal Signature Line
    p.line(100, 100, 250, 100)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(125, 80, "Exam Controller")

    # Controller Signature Line
    p.line(width - 250, 100, width - 100, 100)
    p.drawString(width - 200, 80, "Vice Chancellor")

    # Optional: Add a Digital Stamp/Seal
    p.setStrokeColor(colors.lightgrey)
    p.circle(width/2, 100, 40, stroke=1, fill=0)
    p.setFont("Helvetica-Bold", 8)
    p.drawCentredString(width/2, 105, "OFFICIAL")
    p.drawCentredString(width/2, 95, "SEAL")

    p.showPage()
    p.save()
    
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f'Certificate_{result.exam.course_name}.pdf')



# Update Course (Time, Marks, Name)
@login_required
def edit_course_view(request, pk):
    course = get_object_or_404(Course, id=pk)
    if request.method == 'POST':
        # Updating the object manually from the POST data
        course.course_name = request.POST.get('course_name')
        course.question_number = request.POST.get('question_number')
        course.total_marks = request.POST.get('total_marks')
        course.duration = request.POST.get('duration')
        course.save()
        return redirect('teacher-dashboard')
    
    return render(request, 'edit_course.html', {'course': course})

# Delete Course
@login_required
def delete_course_view(request, pk):
    course = get_object_or_404(Course, id=pk)
    course.delete()
    return redirect('teacher-dashboard')

# Delete Individual Question
@login_required
def delete_question_view(request, pk):
    question = get_object_or_404(Question, id=pk)
    course_id = question.course.id
    question.delete()
    return redirect('admin-view-question', course_id)



@login_required
def upload_pdf_questions(request):
    courses = Course.objects.all()
    if request.method == 'POST' and request.FILES.get('pdf_file'):
        course_id = request.POST.get('course_id')
        course = Course.objects.get(id=course_id)
        pdf_file = request.FILES['pdf_file']
        
        # Generate questions
        questions_data = generate_questions_from_pdf(pdf_file)
        
        if questions_data:
            for item in questions_data:
                Question.objects.create(
                    course=course,
                    question=item['question'],
                    option1=item['option1'],
                    option2=item['option2'],
                    option3=item['option3'],
                    option4=item['option4'],
                    answer=item['answer'],
                    marks=2
                )
            messages.success(request, f"Successfully extracted {len(questions_data)} questions from PDF!")
            return redirect('teacher-dashboard')
            
    return render(request, 'upload_pdf.html', {'courses': courses})


@login_required
def chat_with_tutor(request):
    if request.method == "POST":
        import json
        data = json.loads(request.body)
        user_message = data.get("message")
        
        bot_response = get_ai_tutor_response(request.user, user_message)
        
        return JsonResponse({"response": bot_response})
    return JsonResponse({"error": "Invalid request"}, status=400)