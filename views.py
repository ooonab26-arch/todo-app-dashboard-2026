import random
from flask import Blueprint, render_template, redirect, url_for
from flask import request
from task import Task
from flask_login import login_required, current_user
from models import db, Task, User, Visit, Waitlist, TaskEvent
# import datetime
import datetime
from sqlalchemy import func

# Create a blueprint
main_blueprint = Blueprint('main', __name__)


def log_visit(page, user_id):
    """Log a visit to a page by a user."""
    visit = Visit(page=page, user=user_id)
    db.session.add(visit)
    db.session.commit()

def log_task_event(action, user_id, task_id=None, task_title=None):
    """Log a task event (create, toggle, delete)."""
    event = TaskEvent(action=action, task_id=task_id, task_title=task_title, user_id=user_id)
    db.session.add(event)
    db.session.commit()

###############################################################################
# Routes
###############################################################################


@main_blueprint.route('/', methods=['GET'])
def index():
    log_visit(page='index', user_id=current_user.id if current_user.is_authenticated else None)

    # print all visits
    visits = Visit.query.all()
    for visit in visits:
        print(f"Visit: {visit.page}, User ID: {visit.user}, Timestamp: {visit.timestamp}")

    return render_template('index.html')

@main_blueprint.route('/invitation/', methods=['GET', 'POST'])
def invitation():

    if request.method == 'POST':
        email = request.form['email']
        waitlist_entry = Waitlist(email=email)
        db.session.add(waitlist_entry)
        db.session.commit()
        # Here you would send a verification email and add to waitlist
        print(f"Sending invitation to {email}")
    
    log_visit(page='invitation', user_id=current_user.id if current_user.is_authenticated else None)
    return render_template('invitation.html')


@main_blueprint.route('/todo/', methods=['GET', 'POST'])
@login_required
def todo():
    log_visit(page='todo', user_id=current_user.id)
    return render_template('todo.html')

def today_visit_count(day):
    return Visit.query.filter(
        Visit.page == 'index',
        func.date(Visit.timestamp) == day
    ).count()

@main_blueprint.route('/dashboard/', methods=['GET', 'POST'])
# @login_required
def dashboard():
    visits = Visit.query.all()
    visits_today = Visit.query.filter(func.date(Visit.timestamp) == datetime.date.today()).count()

    today = datetime.date.today()
    week_begins = today - datetime.timedelta(days=6) 
    new_users = User.query.filter(func.date(User.time_created) >= week_begins).count()
    waitlist_signups = Waitlist.query.filter(func.date(Waitlist.timestamp) >= week_begins).count()
    total_users = db.session.query(func.count(User.id)).scalar() or 0

    chart_week = []
    week_visits = []
    two_week_visits = []
    previous_week_begins = week_begins - datetime.timedelta(days=7)
    error_logs = Visit.query.filter(Visit.page.in_(['error-logging-in', 'incorrect-password','invalid-password', 'invalid-email' ])).limit(15).all()

    for i in range(7):
        current_day = week_begins + datetime.timedelta(days=i)
        previous_day = previous_week_begins + datetime.timedelta(days=i)

        chart_week.append(current_day.strftime("%a"))
        week_visits.append(today_visit_count(current_day))
        two_week_visits.append(today_visit_count(previous_day))

    week_notes = [random.randint(0, 15) for _ in range(7)]
    two_week_notes = [random.randint(0, 15) for _ in range(7)]

    total_visits = db.session.query(func.count(Visit.id)).scalar() or 0
    total_tasks = db.session.query(func.count(Task.id)).scalar() or 0
    
    latest_visits = Visit.query.order_by(Visit.timestamp.desc()).limit(15).all()

    total_users_by_page = db.session.query(Visit.page,func.count(Visit.id)).filter(func.date(Visit.timestamp) == datetime.date.today()).group_by(Visit.page).all()
    users_by_page_x = [row[0] for row in total_users_by_page ]
    users_by_page_y = [row[1] for row in total_users_by_page ]

    new_users_info = User.query.filter(func.date(User.time_created) >= week_begins).order_by(User.time_created.desc()).limit(10).all()
    waitlist_signups_info = Waitlist.query.filter(func.date(Waitlist.timestamp) >= week_begins).order_by(Waitlist.timestamp.desc()).limit(10).all()

    return render_template('admin.html',
                           date=datetime.datetime.now().strftime("%B %d, %Y"),
                           total_users=total_users,     # add real number
                           new_users=new_users,         # add real number
                           visits_today=visits_today,    # add real number
                           productivity_change=0.6,   # add real number
                           visits=visits,           # add real value
                           chart_week=chart_week,   # update list to show today as the last day in the chart
                           week_notes=week_notes,   # add real values
                           two_week_notes=two_week_notes,  # add real values
                           waitlist_signups=waitlist_signups,
                           week_visits=week_visits,
                           two_week_visits=two_week_visits,
                           total_visits=total_visits,
                           total_tasks=total_tasks,
                           latest_visits=latest_visits,
                           error_logs = error_logs,
                           users_by_page_x=users_by_page_x,
                           users_by_page_y=users_by_page_y,
                           new_users_info=new_users_info,
                           waitlist_signups_info=waitlist_signups_info
                           )



@main_blueprint.route('/api/v1/tasks', methods=['GET'])
@login_required
def api_get_tasks():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return {
        "tasks": [task.to_dict() for task in tasks]
    }


@main_blueprint.route('/api/v1/tasks', methods=['POST'])
@login_required
def api_create_task():
    data = request.get_json()
    new_task = Task(title=data['title'], user_id=current_user.id)
    db.session.add(new_task)
    db.session.commit()
    log_task_event(action='create', user_id=current_user.id, task_id=new_task.id, task_title=new_task.title)
    
    return {
        "task": new_task.to_dict()
    }, 201


@main_blueprint.route('/api/v1/tasks/<int:task_id>', methods=['PATCH'])
@login_required
def api_toggle_task(task_id):
    task = Task.query.get(task_id)

    if task is None:
        return {"error": "Task not found"}, 404

    task.toggle()
    db.session.commit()
    log_task_event(action='toggle', user_id=current_user.id, task_id=task.id, task_title=task.title)
    return {"task": task.to_dict()}, 200


@main_blueprint.route('/remove/<int:task_id>')
@login_required
def remove(task_id):
    task = Task.query.get(task_id)

    if task is None:
        return redirect(url_for('main.todo'))
    log_task_event(action='delete', user_id=current_user.id, task_id=task.id, task_title=task.title)   
    db.session.delete(task)
    db.session.commit()

    return redirect(url_for('main.todo'))