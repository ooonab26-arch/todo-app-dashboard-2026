import random
from flask import Blueprint, render_template, redirect, url_for
from flask import request
from task import Task
from flask_login import login_required, current_user
from models import db, Task, User, Visit, Waitlist, TaskActivityLog
# import datetime
import datetime

# Create a blueprint
main_blueprint = Blueprint('main', __name__)


def log_visit(page, user_id):
    """Log a visit to a page by a user."""
    visit = Visit(page=page, user=user_id)
    db.session.add(visit)
    db.session.commit()

def log_waitlist(email):
    """Log a waitlist signup for an email."""
    waitlist = Waitlist(email=email)
    db.session.add(waitlist)
    db.session.commit()

def log_task_activity(action_type, description, user_id):
    """Log a task activity."""
    log_entry = TaskActivityLog(action_type=action_type, description=description, user=user_id)
    db.session.add(log_entry)

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

@main_blueprint.route('/invitation', methods=['GET', 'POST'])
def invitation():
    log_visit(page='invitation', user_id=current_user.id if current_user.is_authenticated else None)

    if request.method == 'POST':
        email = request.form['email']
        # Here you would send a verification email and add to waitlist
        print(f"Sending invitation to {email}")
        #log waitlist signup at this point
        log_waitlist(email)
    
    return render_template('invitation.html')


@main_blueprint.route('/todo', methods=['GET', 'POST'])
@login_required
def todo():
    log_visit(page='todo', user_id=current_user.id if current_user.is_authenticated else None)
    return render_template('todo.html')


@main_blueprint.route('/dashboard', methods=['GET', 'POST'])
# @login_required
def dashboard():
    today = datetime.datetime.now(datetime.timezone.utc).date()
    week_ago = today - datetime.timedelta(days=6)
    last_week_start = today - datetime.timedelta(days=13)

    #User stats
    total_users = User.query.count()
    total_tasks = Task.query.count()
    new_users = User.query.filter(User.date_created >= datetime.datetime.now() - datetime.timedelta(days=7)).count()
    new_users_all = User.query.filter(User.date_created >= datetime.datetime.now() - datetime.timedelta(days=7)).all()

    #Visit stats
    visits_today = Visit.query.filter(db.func.date(Visit.timestamp) == db.func.date(today)).count()
    total_visits = Visit.query.count()
    recent_visits = Visit.query.order_by(Visit.timestamp.desc()).limit(15).all()
    error_logs = Visit.query.filter(Visit.page.in_(['login-failure', 'state-not-found', 'State-mismatch'])).limit(10).all()

    #Waitlist stats
    waitlist_signups = Waitlist.query.filter(db.func.date(Waitlist.timestamp) >= week_ago).count()
    waitlist_all = Waitlist.query.all()

    #Chart Data
    chart_days = []
    this_week_data = []
    last_week_data = []
    user_last_week_data = []
    user_this_week_data = []

    for day in range(7):
        d = week_ago + datetime.timedelta(days=day)
        old_d = last_week_start + datetime.timedelta(days=day)

        chart_days.append(d.strftime("%a"))
        this_week_data.append(Visit.query.filter(Visit.page == "index", db.func.date(Visit.timestamp) == d).count())
        last_week_data.append(Visit.query.filter(Visit.page == "index", db.func.date(Visit.timestamp) == old_d).count())
        user_this_week_data.append(User.query.filter(db.func.date(User.date_created) == d).count())
        user_last_week_data.append(User.query.filter(db.func.date(User.date_created) == old_d).count())
    
    #Bar Chart Data
    pages_stats = db.session.query(Visit.page, db.func.count(Visit.id)).filter(db.func.date(Visit.timestamp) == today).group_by(Visit.page).all()
    page_labels = [page[0] for page in pages_stats]
    page_counts = [page[1] for page in pages_stats]

    

    return render_template('admin.html',
        date=datetime.datetime.now().strftime("%B %d, %Y"),
        total_visits=total_visits,
        total_users=total_users,   
        total_tasks=total_tasks,
        error_logs=error_logs,
        new_users=new_users, 
        new_users_all=new_users_all,      
        waitlist_signups=waitlist_signups,
        waitlist_all=waitlist_all,
        visits_today=visits_today,    
        productivity_change=0.6,   # add real number
        visits=recent_visits,           
        chart_week=chart_days,   
        week_visits=this_week_data,   
        two_week_visits=last_week_data,  
        week_users=user_this_week_data,
        two_week_users=user_last_week_data,
        page_labels=page_labels,
        page_counts=page_counts
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

    #log the task creation at this point
    log_task_activity(action_type="task_created", description=new_task.title, user_id=current_user.id if current_user.is_authenticated else None)
    db.session.commit()
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

    #log the task toggle at this point
    log_task_activity(action_type="task_toggled", description=f"Task {task.id} toggled to {task.status}", user_id=current_user.id if current_user.is_authenticated else None)
    db.session.commit()

    return {"task": task.to_dict()}, 200


@main_blueprint.route('/remove/<int:task_id>')
@login_required
def remove(task_id):
    task = Task.query.get(task_id)

    if task is None:
        return redirect(url_for('main.todo'))
    
    #log the task removal at this point
    log_task_activity(action_type="task_removed", description=f"Task {task.id} removed", user_id=current_user.id if current_user.is_authenticated else None)
    db.session.delete(task)
    db.session.commit()

    return redirect(url_for('main.todo'))