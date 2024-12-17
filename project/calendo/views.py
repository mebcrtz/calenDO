import io
import json
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, FileResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from datetime import time
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify
from django.urls import reverse
from reportlab.pdfgen import canvas
from PIL import Image, ImageDraw, ImageFont

from .forms import *
from .models import *

'''AUTHENTICATION VIEWS'''
def signup_page(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully!')
            return redirect('login')
    context = {'form': form}
    return render(request, 'auth/signup.html', context)

def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('calendo-dashboard')
        else:
            messages.error(request, 'Username or password is incorrect.')
    return render(request, 'auth/login.html', {})

def logout_user(request):
    logout(request)
    return redirect('login')


# Dashboard View
@login_required
def dashboard(request):
    # Fetch schedules and tasks grouped by sections
    schedules = Schedule.objects.filter(user=request.user)
    tasks = Task.objects.filter(user=request.user)

    # Group tasks by section
    sections_and_tasks = {}
    for task in tasks:
        if task.section not in sections_and_tasks:
            sections_and_tasks[task.section] = []
        sections_and_tasks[task.section].append(task)

    context = {
        'schedules': schedules,
        'sections_and_tasks': sections_and_tasks,
    }
    return render(request, 'dashboard.html', context)

'''TO-DO VIEWS'''
@login_required(login_url='login')
def todo_index(request):
    tasks = Task.objects.filter(user=request.user)
    sections_and_tasks = {}
    for task in tasks:
        if task.section not in sections_and_tasks:
            sections_and_tasks[task.section] = []
        sections_and_tasks[task.section].append(task)
    return render(request, 'todo/todo-index.html', {'sections_and_tasks': sections_and_tasks})


def create_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user  # Ensure task is associated with the current user
            task.save()
            # Get the redirect path or fallback to the default view
            redirect_path = request.POST.get('redirect_to', 'todo_index')
            return redirect(redirect_path)
    else:
        form = TaskForm()
    return render(request, 'modal.html', {'form': form})

def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    notes = Note.objects.filter(task=task).order_by('-timestamp')
    notes_data = [{'content': note.content, 'timestamp': note.timestamp.strftime('%B %d, %Y %I:%M %p')} for note in notes]
    task_data = {
        'task_name': task.task_name,
        'description': task.description,
        'due_date': task.due_date.strftime('%Y-%m-%d'),
        'section': task.section,
        'priority': task.priority,
        'notes': notes_data
    }
    return JsonResponse(task_data)

def add_note(request):
    if request.method == 'POST':
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body)
            task_id = data.get('task_id')
            content = data.get('notes')

            # Validate the required fields
            if not task_id or not content:
                return JsonResponse({'error': 'Task ID and content are required.'}, status=400)

            # Fetch the task and create the note
            task = Task.objects.get(id=task_id)
            note = Note.objects.create(task=task, content=content, timestamp=timezone.now())
            formatted_date = note.timestamp.strftime('%B %d, %Y %I:%M %p')  # Example: December 16, 2024, 09:28 AM

            return JsonResponse({
                'id': note.id,
                'content': note.content,
                'timestamp': formatted_date  # Return formatted date
            })

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON.'}, status=400)
        except Task.DoesNotExist:
            return JsonResponse({'error': 'Task not found.'}, status=404)
    return JsonResponse({'error': 'Invalid request method.'}, status=400)

def delete_task(request, task_id):
    if request.method == 'DELETE':
        task = get_object_or_404(Task, id=task_id)
        task.delete()
        return HttpResponse(status=204)
    return HttpResponse('Invalid request', status=400)

@login_required(login_url='login')
def update_task(request):
    if request.method == "POST":
        task_id = request.POST.get("task_id")
        if not task_id:
            return redirect('todo_index')

        try:
            # Fetch the task to be updated
            task = get_object_or_404(Task, id=task_id, user=request.user)

            # Update task fields with data from the form
            task.task_name = request.POST.get("task_name", task.task_name)
            task.description = request.POST.get("description", task.description)
            task.due_date = request.POST.get("due_date", task.due_date)
            task.section = request.POST.get("section", task.section)
            task.priority = request.POST.get("priority", task.priority)
            task.save()
        except Task.DoesNotExist:
            messages.error(request, "Task not found.")

        redirect_path = request.POST.get('redirect_to', 'todo_index')
        return redirect(redirect_path)
    return redirect('todo_index')

def set_priority(request):
    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        priority = request.POST.get('priority')
        try:
            task = Task.objects.get(id=task_id)
            task.priority = priority
            task.save()
        except Task.DoesNotExist:
            return JsonResponse({"error": "Task not found"}, status=404)
    return redirect('todo_index')

def set_priority(request):
    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        priority = request.POST.get('priority')
        try:
            task = Task.objects.get(id=task_id)
            task.priority = priority
            task.save()
            return redirect('todo_index')
        except Task.DoesNotExist:
            return HttpResponse('Task not found', status=404)
    return HttpResponse('Invalid request', status=400)

def list_view(request):
    # Organize tasks by section
    tasks = Task.objects.filter(user=request.user)
    sections_and_tasks = {}
    for task in tasks:
        if task.section not in sections_and_tasks:
            sections_and_tasks[task.section] = []
        sections_and_tasks[task.section].append(task)
    return render(request, 'todo/list-view.html', {'sections_and_tasks': sections_and_tasks})

'''CALENDAR VIEWS'''
def get_current_week_dates():
    """Get the dates for the current week's Monday through Sunday."""
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())  # Monday of the current week
    return {
        day_name: (start_of_week + timedelta(days=i)).date()
        for i, day_name in enumerate(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
    }

@login_required(login_url='login')
def calendar_index(request, schedule_name=None):
    schedules = Schedule.objects.filter(user=request.user)
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    # Get the first schedule or None if no schedules exist
    first_schedule = schedules.first()
    schedule = first_schedule if schedule_name is None else get_object_or_404(Schedule, slug=schedule_name, user=request.user)

    # Default to an empty list if no schedule is available
    items = schedule.items.prefetch_related('occurrences__days_of_week') if schedule else []

    # Get current week dates
    current_week_dates = get_current_week_dates()

    # Prepare items with exact dates for occurrences
    event_list = []
    for item in items:
        for occurrence in item.occurrences.all():
            occurrence.days = [day.name for day in occurrence.days_of_week.all()]
            for day_name in occurrence.days:
                if day_name in current_week_dates:
                    event_date = current_week_dates[day_name]
                    event_list.append({
                        'title': item.item_name,
                        'start': f"{event_date}T{occurrence.start_time}",
                        'end': f"{event_date}T{occurrence.end_time}",
                    })

    return render(request, "calendar/calendar-index.html", {
        "schedules": schedules,
        "schedule": schedule,
        "schedule_slug": schedule.slug if schedule else None,  # Handle None case
        "first_schedule": first_schedule,
        "items": items,
        "days_of_week": days_of_week,
        "events": event_list,  # Pass the calculated events to the template
    })


def create_schedule(request):
    if request.method == "POST":
        schedule_name = request.POST.get("schedule_name")
        if schedule_name:
            Schedule.objects.create(
                schedule_name=schedule_name,
                user=request.user
            )
            return redirect("calendar_index")
        else:
            return redirect("calendar_index")
    return render(request, "create_schedule.html")


def add_schedule_item(request, schedule_name):
    schedule = get_object_or_404(Schedule, slug=schedule_name, user=request.user)

    if request.method == "POST":
        item_name = request.POST.get("itemName")
        item_type = request.POST.get("itemType")
        notes = request.POST.get("notes", "")
        days = request.POST.getlist("days[]")
        start_times = request.POST.getlist("startTime[]")
        end_times = request.POST.getlist("endTime[]")

        # Validation: Ensure all required fields are provided
        if not item_name or not days or not start_times or not end_times:
            messages.error(request, "All fields are required!")
            return redirect(reverse('schedule_detail', kwargs={'schedule_name': schedule.slug}))

        # Create the Item object
        item = Item.objects.create(
            schedule=schedule,
            item_name=item_name,
            type=item_type,
            notes=notes
        )

        # Ensure alignment between days and time slots
        if len(days) != len(start_times) or len(days) != len(end_times):
            messages.error(request, "Mismatch between selected days and time slots!")
            return redirect(reverse('schedule_detail', kwargs={'schedule_name': schedule.slug}))

        # Loop to create occurrences for each day and time pair
        for day, start_time, end_time in zip(days, start_times, end_times):
            day_of_week, _ = DayOfWeek.objects.get_or_create(name=day)

            # Create ItemOccurrence for this day and time
            occurrence = ItemOccurrence.objects.create(
                item=item,
                start_time=start_time,
                end_time=end_time
            )
            occurrence.days_of_week.add(day_of_week)

        # Success message and redirect
        messages.success(request, "Item added successfully!")
        return redirect(reverse('schedule_detail', kwargs={'schedule_name': schedule.slug}))

    # Fallback redirect for GET requests
    return redirect(reverse('schedule_detail', kwargs={'schedule_name': schedule.slug}))


def update_item_details(request, schedule_name, pk):
    if request.method == 'POST':
        item_id = pk  # Use `pk` from the URL
        item = get_object_or_404(Item, id=item_id)

        item.item_name = request.POST.get('itemName')
        item.type = request.POST.get('itemType')
        item.notes = request.POST.get('notes')
        item.save()

        # Delete and recreate occurrences
        item.occurrences.all().delete()
        days = request.POST.getlist('days[]')
        start_time = request.POST.get('startTime')
        end_time = request.POST.get('endTime')

        if days and start_time and end_time:
            occurrence = ItemOccurrence.objects.create(
                item=item,
                start_time=start_time,
                end_time=end_time
            )
            for day in days:
                day_of_week, _ = DayOfWeek.objects.get_or_create(name=day)
                occurrence.days_of_week.add(day_of_week)

        return redirect("schedule_detail", schedule_name=schedule_name)


def remove_schedule_item(request, pk):
    item = get_object_or_404(Item, pk=pk, schedule__user=request.user)
    if request.method == "POST":
        schedule_name = item.schedule.slug
        item.delete()
        return redirect("schedule_detail", schedule_name=schedule_name)
    return redirect("schedule_detail", schedule_name=item.schedule.slug)


def delete_schedule(request, schedule_name):
    if request.method == "POST":
        schedule = get_object_or_404(Schedule, slug=schedule_name, user=request.user)
        schedule.delete()
        return redirect("calendar_index")
    else:
        return redirect("calendar_index")


def export_schedule(request, schedule_name, file_type):
    schedule = get_object_or_404(Schedule, slug=schedule_name, user=request.user)
    items = schedule.items.prefetch_related('occurrences__days_of_week').all()

    # Helper function to sort days from Monday to Sunday
    def sort_days(occurrence):
        # Sort days of the week starting from Monday
        days = [day.name for day in occurrence.days_of_week.all()]
        days_of_week_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        sorted_days = sorted(days, key=lambda x: days_of_week_order.index(x))
        return ', '.join(sorted_days)

    if file_type == 'pdf':
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Title (Top of the PDF)
        title = Paragraph(f"<b>Schedule: {schedule.schedule_name}</b>", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))  # Add some space

        # Table Header
        data = [["Item Name", "Type", "Notes", "Occurrences"]]
        for item in items:
            occurrences_text = []
            if item.occurrences.exists():
                for occurrence in item.occurrences.all():
                    days = sort_days(occurrence)  # Sort days from Monday to Sunday
                    # Convert to 12-hour format with AM/PM
                    time_range = f"{occurrence.start_time.strftime('%I:%M %p')} - {occurrence.end_time.strftime('%I:%M %p')}"
                    occurrences_text.append(f"{days}: {time_range}")
            else:
                occurrences_text.append("No occurrences specified.")
            data.append([item.item_name, item.get_type_display(), item.notes, '\n'.join(occurrences_text)])

        # Table Style
        table = Table(data, colWidths=[100, 100, 200, 200])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Add grid lines for cell borders
        ]))
        story.append(table)

        # Build the PDF
        doc.build(story)
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=f"{schedule.schedule_name}.pdf")

    elif file_type in ['jpg', 'png']:
        image_format = 'JPEG' if file_type == 'jpg' else 'PNG'

        # Canvas Dimensions
        img_width, img_height = 1000, max(600, len(items) * 50 + 150)
        img = Image.new('RGB', (img_width, img_height), color=(240, 248, 255))  # Background color
        d = ImageDraw.Draw(img)

        # Fonts
        try:
            title_font = ImageFont.truetype("arial.ttf", 36)
            header_font = ImageFont.truetype("arial.ttf", 18)
            item_font = ImageFont.truetype("arial.ttf", 14)
        except IOError:
            # Fallback to a default PIL font
            title_font = ImageFont.load_default()
            header_font = ImageFont.load_default()
            item_font = ImageFont.load_default()

        # Title
        d.rectangle([0, 0, img_width, 80], fill=(70, 130, 180))  # Title background
        d.text((20, 20), f"Schedule: {schedule.schedule_name}", fill=(255, 255, 255), font=title_font)

        # Table Header
        header_y = 100
        header_padding = 10
        table_header = ["Item Name", "Type", "Notes", "Occurrences"]
        column_widths = [250, 150, 300, 250]  # Set column widths

        # Header row with background color
        d.rectangle([0, header_y, img_width, header_y + 40], fill=(70, 130, 180))
        for i, header in enumerate(table_header):
            d.text((column_widths[i] // 2 + sum(column_widths[:i]) - len(header) * 4, header_y + header_padding),
                   header, fill=(255, 255, 255), font=header_font)

        # Table Rows
        row_y = header_y + 40
        row_padding = 10

        for idx, item in enumerate(items):
            d.rectangle([0, row_y, img_width, row_y + 40])  # Add a rectangle for each row

            # Prepare occurrences with sorted days
            occurrences_text = []
            if item.occurrences.exists():
                for occurrence in item.occurrences.all():
                    days = sort_days(occurrence)  # Sort days from Monday to Sunday
                    # Convert to 12-hour format with AM/PM
                    time_range = f"{occurrence.start_time.strftime('%I:%M %p')} - {occurrence.end_time.strftime('%I:%M %p')}"
                    occurrences_text.append(f"{days}: {time_range}")
            else:
                occurrences_text.append("No occurrences specified.")

            # Row data including occurrences with days and AM/PM times
            row_data = [
                item.item_name,
                item.get_type_display(),
                item.notes,
                '\n'.join(occurrences_text)  # Now includes sorted days and time range
            ]

            # Draw row text
            for i, cell in enumerate(row_data):
                d.text((column_widths[i] // 2 + sum(column_widths[:i]) - len(cell) * 4, row_y + row_padding), cell, fill=(0, 0, 0), font=item_font)

            # Draw borders around each cell
            for i in range(len(column_widths)):
                # Vertical lines
                d.line([sum(column_widths[:i]), row_y, sum(column_widths[:i]), row_y + 40], fill=(0, 0, 0), width=2)
            # Bottom border for each row
            d.line([0, row_y + 40, img_width, row_y + 40], fill=(0, 0, 0), width=2)

            row_y += 40  # Move to the next row

        # Draw the final vertical line on the right side
        d.line([img_width - 1, header_y, img_width - 1, row_y], fill=(0, 0, 0), width=2)

        # Save the image
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG' if file_type == 'jpg' else 'PNG')
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=f"{schedule.schedule_name}.{file_type}")

    else:
        return redirect("schedule_detail", schedule_name=schedule_name)
